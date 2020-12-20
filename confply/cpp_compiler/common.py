import confply.log as log
import shutil
import os
import shlex

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


def gen_warnings(config):
    command = ""
    conf_warnings = config["warnings"]
    if isinstance(conf_warnings, list):
        for w in config["warnings"]:
            command += warnings+w+" "
    elif isinstance(conf_warnings, bool):
        if(not conf_warnings):
            command += no_warnings+" "
    elif isinstance(conf_warnings, str):
        command += warnings+conf_warnings+" "
    return command

def generate(config):
    object_path = config["object_path"]
    def gen_command(config, source = None):
        
        command = ""
        command += tool+" "+config["command_prepend"]+" "
        command += include+" "+(" "+include+" ").join(config["include_paths"]) + " " if config["include_paths"] else ""
        command += define+" "+(" "+define+" ").join(config["defines"])+" " if config["defines"] else ""
        command += debug+" " if config["debug_info"] else ""
        command += standard+config["standard"]+" " if config["standard"] else ""
        command += gen_warnings(config) if config["warnings"] else ""
        command += optimisation+str(config["optimisation"])+" " if config["optimisation"] else ""
        if source is None:
            command += " ".join(config["source_files"])+" " if config["source_files"] else ""
            command += output_exe+config["output_file"]+" " if config["output_file"] else output_exe+"app.bin"
            command += pass_to_linker+" "
            command += library+(" "+library).join(config["library_paths"])+" " if config["library_paths"] else ""
            command += link+" "+(" "+link+" ").join(config["link_libraries"])+" " if config["link_libraries"] else ""
        else:
            command += build_object+" "+source+" "+output_obj+os.path.join(object_path, os.path.basename(source)+object_ext+" ")
            command += exception_handling+" "
            if config["track_dependencies"]:
                command += dependencies+" "+dependencies_output+ " "+os.path.join(object_path, os.path.basename(source)+".d ")
        return command+" "+config["command_append"]

    if config["build_objects"]:
        os.makedirs(object_path, exist_ok=True)
        commands = []
        sources = config["source_files"]
        objects = [os.path.join(object_path, os.path.basename(x)+object_ext) for x in sources]
        depends = [os.path.join(object_path, os.path.basename(x)+".d") for x in sources]
        deps_times = []
        gen_depends = []
        output_time = config["output_file"] if config["output_file"] else "app.bin"
        output_time = os.path.getmtime(output_time).real if os.path.exists(output_time) else 0
        should_link = False
        
        if config["track_dependencies"]:
            for x in depends:
                if os.path.exists(x):
                    gen_depends.append(False)
                    with open(x, "r") as f:
                        deps_times.append(max([os.path.getmtime(y).real for y in shlex.split(f.read()) if os.path.exists(y)]))
                    if config["rebuild_on_change"]:
                        deps_times[-1] = max(deps_times[-1], config["confply_modified"])
                else:
                    gen_depends.append(True)
                    deps_times.append(0)

        else:
            deps_times = [os.path.getmtime(x).real for x in sources]
            gen_depends = [False for x in sources]

        object_times = [os.path.getmtime(x).real if os.path.exists(x) else 0 for x in objects]
        
        for ot, st, s, g in zip(object_times, deps_times, sources, gen_depends):
            if ot < st or g:
                commands.append(gen_command(config, s))
                should_link = True
            if ot > output_time:
                should_link = True

        if should_link and config["output_executable"]:
            config["source_files"] = objects
            commands.append(gen_command(config))
            config["source_files"] = sources
            num_commands = len(commands)
            log.normal(str(num_commands)+" files to compile")
        else:
            log.normal("no files to compile")
        return commands
    else:
        return gen_command(config)


def get_environ(config):
    return os.environ

def is_found(tool):
    return not shutil.which(tool) is None
