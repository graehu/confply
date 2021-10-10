import confply.log as log
import confply.cpp_compiler.config as config
import confply.cpp_compiler.options as options
import os
import ast
import json
import shlex
import shutil
import hashlib

tool = None
debug = "-g"
include = "-I"
define = "-D"
standard = "-std="
warnings = "-W"
no_warnings = "-w"
optimisation = "-O"
fPIC = "-fPIC"
link = "-l"
library = "-L "
build_object = "-c"
output_obj = "-o"
output_exe = "-o"
object_ext = ".o"
dependencies = "-MMD"
dependencies_output = "-MF"
exception_handling = ""
pass_to_linker = ""
lib_extension = ".a"
dll_extension = ".so"
parse_deps = lambda x: shlex.split(x)

def generate():
    object_path = os.path.dirname(config.object_path)
    object_path = os.path.join(object_path, tool)

    def gen_command(config, source=None):
        command = [tool]
        command += [config.command_prepend]
        command += [[include, path] for path in config.include_paths]
        command += [[define, d] for d in config.defines]
        command += [debug] if config.debug_info else []
        command += [standard+config.standard] if config.standard else []
        command += [warnings+w for w in config.warnings]
        command += [no_warnings] if config.no_warnings else []
        command += [optimisation+str(config.optimisation)] if config.optimisation else []
        command += [fPIC] if config.position_independent else []

        if source is None:
            command += [src for src in config.source_files]
            command += [output_exe+config.output_file] if config.output_file else [output_exe+"app.bin"]
            command += [pass_to_linker] if pass_to_linker else []
            command += [[library, path] for path in config.library_paths]
            command += [[link, lib] for lib in config.link_libraries]
        else:
            command += [build_object]
            command += [source]
            command += [output_obj+os.path.join(object_path, os.path.basename(source)+object_ext)]
            command += [exception_handling] if exception_handling else []
            if config.track_dependencies:
                command += [dependencies, dependencies_output, os.path.join(object_path, os.path.basename(source)+".d")]
        command += [config.command_append]
        # flatten / sanitise command
        flat = []
        for arg in command:
            if isinstance(arg, list):
                flat += arg
            else:
                flat += [arg]
        command = flat
        command = [c for c in command if c]
        return command

    if config.build_objects:
        os.makedirs(object_path, exist_ok=True)
        commands = []
        sources = config.source_files
        objects = []
        output_time = config.output_file if config.output_file else "app.bin"
        output_time = os.path.getmtime(output_time).real if os.path.exists(output_time) else 0
        should_link = False
        tracking_md5 = config.track_checksums
        tracking_depends = config.track_dependencies
        config_name = config.confply.config_name if os.path.exists(config.confply.config_name) else None

        # generate checksums
        def md5(fname):
            hash_md5 = hashlib.md5()
            with open(fname, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()

        tracking = {}
        tracking_path = os.path.join(object_path, "tracking.py")

        if tracking_md5 or tracking_depends:
            if os.path.exists(tracking_path):
                with open(tracking_path) as tracking_file:
                    tracking = ast.literal_eval(tracking_file.read())

        def update_tracking(file_path):
            nonlocal tracking
            if os.path.exists(file_path):
                file_time = os.path.getmtime(file_path).real
                if file_path in tracking:
                    if file_time > tracking[file_path]["t"]:
                        if tracking_md5:
                            old_md5 = tracking[file_path]["h"] if "h" in tracking[file_path] else None
                            new_md5 = md5(file_path)
                            tracking[file_path].update({"t":file_time, "h":new_md5})
                            return old_md5 != new_md5
                        else:
                            tracking[file_path].update({"t":file_time})
                            return True
                    else:
                        return False
                elif tracking_md5:
                    tracking[file_path] = {"t":file_time, "h":md5(file_path)}
                    return True
                else:
                    tracking[file_path] = {"t":file_time}
                    return True
                pass
            return False

        compile_all = update_tracking(config_name) if config.rebuild_on_change else False

        commands_db = []
        commands_db_path = os.path.join(config.confply.vcs_root, "compile_commands.json")

        if config.compile_commands:
            if os.path.exists(commands_db_path):
                with open(commands_db_path) as commands_db_file:
                    commands_db = ast.literal_eval(commands_db_file.read())

        def update_command_db(file_path, args):
            nonlocal commands_db
            nonlocal object_path
            dir_path = os.path.dirname(commands_db_path)
            out_path = os.path.join(object_path, os.path.basename(file_path+object_ext))
            dir_path = os.path.abspath(dir_path)
            out_path = os.path.abspath(out_path)
            file_path = os.path.abspath(file_path)
            for entry in commands_db:
                if entry["file"] == file_path \
                   and entry["output"] == out_path \
                   and entry["directory"] == dir_path:
                    entry["arguments"] = args
                    return
            commands_db.append(
                {
                    "arguments": args,
                    "directory": dir_path,
                    "file": file_path,
                    "output": out_path
                }
            )
            pass

        for source_path in sources:
            should_compile = compile_all
            if os.path.exists(source_path):
                deps_path = os.path.join(object_path, os.path.basename(source_path+".d"))
                obj_path = os.path.join(object_path, os.path.basename(source_path+object_ext))
                obj_time = os.path.getmtime(obj_path).real if os.path.exists(obj_path) else 0
                objects.append(obj_path)
                # dependency tracking
                if tracking_depends and os.path.exists(deps_path):
                    with open(deps_path, "r") as deps_file:
                        deps_string = deps_file.read()
                        for dep_path in parse_deps(deps_string):
                            should_compile = update_tracking(dep_path) or should_compile
                else:
                    should_compile = update_tracking(source_path) or should_compile

                if should_compile or obj_time == 0:
                    commands.append(gen_command(config, source_path))
                    if config.compile_commands:
                        update_command_db(source_path, commands[-1])
                    should_link = True
                elif obj_time > output_time:
                    should_link = True
            else:
                log.warning(source_path+" could not be found")

        if should_link and config.output_type == options.output_type.exe:
            config.source_files = objects
            commands.append(gen_command(config))
            config.source_files = sources
            num_commands = len(commands)
            log.normal(str(num_commands)+" files to compile")
        elif should_link and config.output_type == options.output_type.dll:
            #todo: add windows dll support.
            #todo: replace strings
            out = config.output_file
            out = out if out.endswith(dll_extension) else out+dll_extension
            commands.append([tool, "-rdynamic", "-shared", *objects, output_exe, out])
            pass
        elif should_link and config.output_type == options.output_type.lib:
            #todo: add windows lib support.
            out = config.output_file
            out = out if out.endswith(lib_extension) else out+lib_extension
            commands.append(["ar", "rcs", out, *objects])
            pass

        if tracking_md5 or tracking_depends:
            with open(tracking_path, "w") as tracking_file:
                tracking_file.write("# do not edit this file.\n")
                tracking_file.write(json.dumps(tracking, indent=4))

        if config.compile_commands:
            with open(commands_db_path, "w") as commands_db_file:
                commands_db_file.write(json.dumps(commands_db, indent=4))
        if not commands:
            log.normal("no files to compile.")
        return commands
    else:
        return gen_command(config)


def get_environ():
    return os.environ


def handle_args():
    if "--cpp_clean" in config.confply.args or config.clean:
        if os.path.exists(config.object_path):
            log.normal("cleaning compiled objects")
            os.system("rm -r "+config.object_path)
        else:
            log.normal("no objects to remove")


def is_found(in_tool=None):
    path = None
    if in_tool is None:
        if config.confply.tool is not None:
            path = shutil.which(config.confply.tool)
    else:
        path = shutil.which(in_tool)
    if path is None:
        # log.error(in_tool+" not found")
        return False
    else:
        # #todo: something like this is needed, just not here
        # log.success(in_tool+" found: "+path)
        return True
