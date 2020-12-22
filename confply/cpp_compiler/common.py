import confply.log as log
import os
import ast
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
        objects = [] # [os.path.join(object_path, os.path.basename(x)+object_ext) for x in sources]
        depends = [] # [os.path.join(object_path, os.path.basename(x)+".d") for x in sources]
        output_time = config["output_file"] if config["output_file"] else "app.bin"
        output_time = os.path.getmtime(output_time).real if os.path.exists(output_time) else 0
        should_link = False
        tracking_md5 = config["track_checksums"]
        tracking_depends = config["track_dependencies"]

        # generate checksums
        def md5(fname):
            hash_md5 = hashlib.md5()
            with open(fname, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()

        tracking = {}

        tracking_path = os.path.join(config["object_path"], "tracking.py")
        if tracking_md5 or tracking_depends:
            if os.path.exists(tracking_path):
                with open(tracking_path, "r") as tracking_file:
                    tracking = ast.literal_eval(tracking_file.read())
        for source_path in sources:
            should_compile = False
            if os.path.exists(source_path):
                deps_path = os.path.join(object_path,os.path.basename(source_path+".d"))
                obj_path = os.path.join(object_path,os.path.basename(source_path+object_ext))
                obj_time = os.path.getmtime(obj_path).real if os.path.exists(obj_path) else 0
                objects.append(obj_path)
                source_time = os.path.getmtime(source_path).real
                old_source_time = tracking[source_path]["t"] if source_path in tracking else 0
                # dependency tracking
                # #todo: currently a file will consider itself, which causes a double evaluation of it later.
                if os.path.exists(deps_path) and tracking_depends:
                    with open(deps_path, "r") as deps_file:
                        deps_string = deps_file.read()
                        for dep_path in shlex.split(deps_string):
                            if os.path.exists(dep_path):
                                dep_time = os.path.getmtime(dep_path).real
                                if dep_path in tracking:
                                    if tracking[dep_path]["t"] < dep_time:
                                        # md5 dependency tracking
                                        if tracking_md5:
                                            current_md5 = md5(dep_path)
                                            old_md5 = tracking[dep_path]["h"]
                                            if old_md5 != current_md5:
                                                should_compile = True
                                                # print("here7")
                                                tracking[dep_path] = {"t" : dep_time,"h" : current_md5}
                                        else:
                                            should_compile = True
                                            # print("here6")
                                            tracking[dep_path] = {"t" : dep_time, "h" : ''}
                                            
                                elif tracking_md5:
                                    tracking[dep_path] = {"t" : dep_time, "h" : md5(dep_path)}
                                    # print("here5")
                                    should_compile = True
                                else:
                                    tracking[dep_path] = {"t" : dep_time, "h" : ''}
                                    # print("here4")
                                    should_compile = True

                # md5 source tracking
                if tracking_md5:
                    if source_path in tracking:
                        if  source_time > old_source_time:
                            current_md5 = md5(source_path)
                            old_md5 = tracking[source_path]["h"]
                            if old_md5 != current_md5:
                                # print("here3")
                                should_compile = True
                                tracking[source_path].update({"h":md5(source_path)})
                    else:
                        # print("here2")
                        tracking = { "t":source_time, "h" : md5(source_path) }
                        should_compile = True
                        
                # no md5 tracking
                elif source_path in tracking:
                    if source_time > old_source_time:
                        tracking[source_path].update({"h" : ''})
                        # print("here1")
                        should_compile = True
                else:
                    tracking[source_path] = {"t":source_time, "h":''}

                # #todo: generate md5 for the config file here...? confply_md5? needs to go into tracking
                if config["rebuild_on_change"] and config["confply_modified"] > output_time:
                    # print("here8")
                    should_compile = True

                if should_compile:
                    commands.append(gen_command(config, source_path))
                    should_link = True
                elif obj_time > output_time:
                    should_link = True
                    
            else:
                log.error(source+" could not be found")
            
        if should_link and config["output_executable"]:
            config["source_files"] = objects
            commands.append(gen_command(config))
            config["source_files"] = sources
            num_commands = len(commands)
            log.normal(str(num_commands)+" files to compile")
        else:
            log.normal("no files to compile")
            
        if tracking_md5 or tracking_depends:
            with open(tracking_path, "w") as tracking_file:
                tracking_file.write(str(tracking))
        return commands
    else:
        return gen_command(config)


def get_environ(config):
    return os.environ

def is_found(tool):
    return not shutil.which(tool) is None
