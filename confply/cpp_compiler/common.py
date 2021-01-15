import confply.log as log
import confply.cpp_compiler.config as config
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
link = "-l"
library = "-L "
build_object = "-c"
output_obj = "-o "
output_exe = "-o "
object_ext = ".o"
dependencies = "-MMD"
dependencies_output = "-MF"
exception_handling = ""
pass_to_linker = ""
parse_deps = lambda x: shlex.split(x)



def gen_warnings():
    command = ""
    conf_warnings = config.warnings
    if isinstance(conf_warnings, list):
        for w in config.warnings:
            command += warnings+w+" "
    elif isinstance(conf_warnings, bool):
        if(not conf_warnings):
            command += no_warnings+" "
    elif isinstance(conf_warnings, str):
        command += warnings+conf_warnings+" "
    return command

def generate():
    object_path = config.object_path
    def gen_command(config, source = None):
        
        command = ""
        command += tool+" "+config.command_prepend+" "
        command += include+" "+(" "+include+" ").join(config.include_paths) + " " if config.include_paths else ""
        command += define+" "+(" "+define+" ").join(config.defines)+" " if config.defines else ""
        command += debug+" " if config.debug_info else ""
        command += standard+config.standard+" " if config.standard else ""
        command += gen_warnings() if config.warnings else ""
        command += optimisation+str(config.optimisation)+" " if config.optimisation else ""
        if source is None:
            command += " ".join(config.source_files)+" " if config.source_files else ""
            command += output_exe+config.output_file+" " if config.output_file else output_exe+"app.bin"
            command += pass_to_linker+" "
            command += library+(" "+library).join(config.library_paths)+" " if config.library_paths else ""
            command += link+" "+(" "+link+" ").join(config.link_libraries)+" " if config.link_libraries else ""
        else:
            command += build_object+" "+source+" "+output_obj+os.path.join(object_path, os.path.basename(source)+object_ext+" ")
            command += exception_handling+" "
            if config.track_dependencies:
                command += dependencies+" "+dependencies_output+ " "+os.path.join(object_path, os.path.basename(source)+".d ")
        return command+" "+config.command_append

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
        tracking_path = os.path.join(config.object_path, "tracking.py")
        
        if tracking_md5 or tracking_depends:
            if os.path.exists(tracking_path):
                with open(tracking_path, "r") as tracking_file:
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
        
        for source_path in sources:
            should_compile = compile_all
            if os.path.exists(source_path):
                deps_path = os.path.join(object_path,os.path.basename(source_path+".d"))
                obj_path = os.path.join(object_path,os.path.basename(source_path+object_ext))
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
                    should_link = True
                elif obj_time > output_time:
                    should_link = True
                    
            else:
                log.warning(source_path+" could not be found")
                
        if should_link and config.output_executable:
            config.source_files = objects
            commands.append(gen_command(config))
            config.source_files = sources
            num_commands = len(commands)
            log.normal(str(num_commands)+" files to compile")
        else:
            log.normal("no files to compile")

        if tracking_md5 or tracking_depends:
            with open(tracking_path, "w") as tracking_file:
                tracking_file.write("# do not edit this file.\n")
                tracking_file.write(json.dumps(tracking, indent=4))
        return commands
    else:
        return gen_command(config)


def get_environ():
    return os.environ

def is_found():
    return not shutil.which(config.confply.tool) is None
