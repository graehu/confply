import os
import sys
import ast
import stat
import types
import shlex
import shutil
import timeit
import select
import inspect
import pathlib
import traceback
import importlib
import subprocess
import confply.config
import confply.log as log

__version__ = "0.0.1"
__doc__ = """
Confply is an abstraction layer for other commandline tools.
It lets you write a consistent config file & commandline interface for tools that have similar functions.
More to come.
"""
new_launcher_str = r"""#!/usr/bin/env python
#                      _____       .__         
#   ____  ____   _____/ ____\_____ |  | ___.__.
# _/ ___\/  _ \ /    \   __\\____ \|  |<   |  |
# \  \__(  <_> )   |  \  |  |  |_> >  |_\___  |
#  \___  >____/|___|  /__|  |   __/|____/ ____|
#      \/           \/      |__|        \/
# launcher generated using:
# 
# python {confply_dir}/confply.py --launcher {launcher}

import sys
import os

# set current working directory and add confply to path
# so we can import the launcher function
dir_name = os.path.dirname(__file__)
if not dir_name == "":
    os.chdir(dir_name)
sys.path.append("{confply_dir}")
from confply import launcher

# fill this with your configs
aliases = {comment}

if __name__ == "__main__":
    # "all" will run all of the aliases
    aliases["all"] = " -- ".join([val for key, val in aliases.items()])
    launcher(sys.argv[1:], aliases)
"""

new_config_str = """#!{confply_dir}/confply.py
# generated using:
# python {confply_dir}/confply.py --config {tool_type_arg} {config_file}
import sys
sys.path.append('{confply_dir}')
import confply.{tool_type_arg}.config as config
import confply.{tool_type_arg}.options as options
import confply.log as log
############# modify_below ################

config.confply.log_topic = "{tool_type_arg}"
log.normal("loading {config_file} with confply_args: "+str(config.confply.args))
config.confply.tool = options.defaults.tool
"""

def launcher(in_args, aliases):
    return_code = -999999
    def print_header():
        log.confply_header()
        log.linebreak()
    confply_dir = os.path.relpath(__file__)
    confply_dir = os.path.dirname(confply_dir)+"/.."
    confply_dir = os.path.relpath(confply_dir)
    confply_dir = confply_dir.replace("\\", "/")
    if len(in_args) != 0:
        alias = in_args[0]
        args = " ".join(in_args[1:])
        # for arg in in_args:
        if alias in aliases:
            system_code = 0
            if os.name == 'nt':
                # windows doesn't support os.WEXITSTATUS
                system_code = os.system(("python "+confply_dir+"/confply.py "+aliases[alias]+" "+args).replace(" -- ", " "+args+" -- "))
            else:
                system_code = os.WEXITSTATUS(os.system(("python "+confply_dir+"/confply.py "+aliases[alias]+" "+args).replace(" -- ", " "+args+" -- ")))
                
            if (system_code > return_code) and (system_code != 0):
                return_code = system_code
        else:
            print_header()
            log.error(alias+" is not in aliases.")
            return_code = -1
    else:
        print_header()
        log.error("no arguements supplied.")
        with open(os.path.join(confply_dir,"help.md"), "r") as help_file:
            print("\n"+help_file.read())
        return_code = -1
    log.linebreak()

    if(return_code != -999999):
        exit(abs(return_code))
    else:
        exit(0)


# #todo: make this import one tool at a time, like previous import_cache behaviour
def run_config(in_args):
    log.header("run config")
    log.linebreak()
    # private functions
    def _print_config():
        nonlocal file_path
        base_config = {}
        compare_config = {}
        confply_path = os.path.dirname(__file__) + "/"

        if(os.path.exists(confply_path+confply.config.__tool_type)):
            with open(confply_path+confply.config.__tool_type+"/config/__init__.py", 'r') as config_file:
                exec(config_file.read(), {}, base_config)
            with open(confply_path+"config.py", 'r') as config_file:
                exec(config_file.read(), {}, compare_config)

            file_name = os.path.basename(file_path)
            log.normal(file_name+" configuration:")
            log.normal("{")

            for k, v in compare_config.items():
                base_config["confply."+k] = v

            compare_config = {
                **{"confply."+k : v for k,v in confply.config.__dict__.items()},
                **config.__dict__
            }
            
            for k, v in compare_config.items():
                if k.startswith("__") or k.startswith("confply.__"): continue
                if k in base_config and v != base_config[k]:
                    if isinstance(v, list):
                        log.normal("\t"+str(k)+": ")
                        for i in v:
                            log.normal("\t\t"+str(i))
                    elif inspect.isfunction(v):
                        if base_config[k] == None or v.__name__ != base_config[k].__name__:
                            log.normal("\t"+str(k)+": "+v.__name__)
                        else:
                            pass
                    else:
                        log.normal("\t"+str(k)+": "+str(v))

            log.normal("}")
            log.normal("")
        else:
            log.error(confply.config_tool_type+" is not a valid confply_tool_type and should not be set by users.")
            log.normal("\tuse: 'import confply.[tool_type].config as confply' to import confply_tool_type.")
            
    ##########
    
    def _validate_config():
        nonlocal tools
        nonlocal config_modules
        tool_type = confply.config.__tool_type
        if tool_type not in tools:
            dir = os.path.dirname(__file__) +"/"+tool_type
            if os.path.exists(dir):
                files = os.listdir(dir)
            else:
                log.error(tool_type+" is not a valid confply_tool_type and should not be set by users.")
                log.normal("\tuse: 'from confply.[tool_type].config import *' to import confply_tool_type.")
                return None

            tools[tool_type] = {}
            module_path = "confply."+tool_type+"."
            config_modules.append(importlib.import_module("confply."+tool_type))
            for py in files:
                if py.endswith(".py") and not py == "__init__.py":
                    tool = py[0:-3]
                    tools[tool_type][tool] = importlib.import_module(module_path+tool)

        tool = confply.config.tool
        def _print_tools():
            for k in tools[tool_type].keys():
                if not tools[tool_type][k].is_found():
                    log.normal("\t"+k+" (not found)")
                else:
                    log.normal("\t"+k)
        pass
        ##########
        def _tool_select():
            if confply.config.platform != "windows":
                finished = False
                while not finished:
                    log.normal("continue with a different tool? (Y/N): ", end="", flush=True)
                    rlist, _, _ = select.select([sys.stdin], [], [], 10)
                    if rlist:
                        answer = sys.stdin.readline().upper().replace("\n", "")
                        if answer == "YES" or answer == "Y":
                            log.normal("which tool? options:")
                            _print_tools()
                            log.normal("")
                            log.normal("tool: ", end="", flush=True)
                            tool = input("")
                            if tool in tools[tool_type]:
                                config.confply.tool = tool
                                return True
                            else:
                                log.error("'"+tool+"' could not be found, is it installed?")
                                finished = False
                        elif answer == "NO" or answer == "N":
                            finished = True
                        elif answer == "":
                            finished = False
                    else:
                        print("")
                        log.normal("timed out.")
                        finished = True
            else:
                log.normal("options:")
                _print_tools()
                log.normal("")
                return False
            pass
        #######
        if tool in tools[tool_type]:
            if not tools[tool_type][tool].is_found():
                log.error("'"+tool+"' could not be found, is it installed?")
                return _tool_select()
            else:
                return True
        else:
            log.error("'"+str(tool)+"' is not a valid "+tool_type+" tool.")
            return _tool_select()

        return False
    ########
    # setup config run
    return_code = 0
    confply_args = []
    while len(in_args) > 0:
        arg = in_args.pop(0)
        if arg == "--":
            break
        confply_args.append(arg)

    confply_args = shlex.split(" ".join(confply_args))
    path = confply_args[0]
    confply_args.pop(0)
    

    try:
        git_root = subprocess.check_output(['git', 'rev-parse', '--show-toplevel'])
    except CalledProcessError:
        raise IOError('Current working directory is not a git repository')
    confply.config.git_root = git_root.decode('utf-8').strip()

    if os.name == "nt":
        confply.config.platform = "windows"
    elif os.name == "posix":
        confply.config.platform = "linux"

    tools = {}
    config_locals = {}
    confply.config.args = confply_args
    file_path = path
    directory_paths = []
    config_modules = []



    with pathlib.Path(path).absolute() as temp_path:
        path_split = temp_path.name.split(".")
        if path_split[1] != "py":
            def iter_path(path, paths):
                directory_py = path.joinpath("confply."+path_split[1]+".py")
                if directory_py.exists():
                    paths.insert(0, directory_py)

                if(path.parent != path):
                    iter_path(path.parent, paths)
                pass
            temp_path.resolve()
            iter_path(temp_path.parent, directory_paths)
        pass

    directory_paths.append(file_path)
    
    for path in directory_paths:
        if path == None:
            continue
        
        # open the file and read the junk out of it.
        # also execs any code that may be there.
        # potentially pass some things in via config.
        
        if os.path.exists(path) and os.path.isfile(path):
            config_name = os.path.basename(path)
            confply.config.config_name = config_name
            confply.config.modified = os.path.getmtime(path).real
            old_path = os.getcwd()
            with open(path, 'r') as config_file:
                new_path = os.path.dirname(path)
                if not new_path == "":
                    os.chdir(new_path)
                try:
                    exec(config_file.read(), {}, config_locals)
                    for k, v in config_locals.items():
                        if isinstance(v, types.ModuleType) and v not in config_modules:
                            v_name = v.__name__
                            if v_name.startswith("confply.") \
                            and v_name.endswith(".config"):
                                config_modules.append(v)
                    if len(confply.config.__imported_configs) > 1:
                        log.error("too many confply configs imported:")
                        for c in confply.config.__imported_configs:
                            log.normal("\t "+c)
                        log.normal("confply only supports one config per file.")
                        for m in config_modules: del sys.modules[m.__name__]
                        importlib.reload(confply.config)
                        return -1
                    log.linebreak()
                    log.success("loaded: "+str(path))
                except:
                    log.error("failed to exec: "+path)
                    trace = traceback.format_exc().replace("<string>", path)
                    log.normal("traceback:\n\n"+trace)
                    return -1

            if not old_path == "":
                os.chdir(old_path)
        else:
            log.error("failed to load: "+path)
            return -1

    confply_path = os.path.dirname(__file__) + "/"
    if(not "config" in config_locals):
        log.error("confply config incorrectly imported")
        log.normal("\tuse: 'import confply.[tool_type].config as config'")
        for m in config_modules: del sys.modules[m.__name__]
        importlib.reload(confply.config)
        return -1

    config = config_locals["config"]
    # #note: attempting to stop people calling builtin functions
    if "__builtins__" in config.__dict__:
        del config.__dict__["__builtins__"]
    
    if isinstance(confply.config.__override_dict, dict):
        confply_dict = confply.config.__override_dict
        config.confply.__dict__.update(confply_dict["confply"])
        del confply_dict["confply"]
        config.__dict__.update(confply_dict)

    if isinstance(confply.config.__override_list, list):
        for k, v in confply.config.__override_list:
            try:
                exec("{0} = v".format(k), globals(), locals())
            except:
                log.warning("failed to exec "+"{0} = {1}:".format(k, v))
                log.normal("\t\tcheck calling option  --"+k)
                # trace = traceback.format_exc()
                # log.normal("traceback:\n\n"+trace)
        
    # #todo: this push and pop of the directory isn't great
    # it happens later anyway.
    old_working_dir = os.getcwd()
    new_working_dir = os.path.dirname(file_path)
    if len(new_working_dir) > 0:
        os.chdir(new_working_dir)
    try:
        if confply.config.post_load and inspect.isfunction(confply.config.post_load):
            log.normal("running post load script: "+confply.config.post_load.__name__)
            exec(confply.config.post_load.__code__, config_locals, {})
    except:
        log.error("failed to exec "+confply.config.post_load.__name__)
        trace = traceback.format_exc()
        log.normal("traceback:\n\n"+trace)
    os.chdir(old_working_dir)

    if(not os.path.exists(confply_path+str(confply.config.__tool_type))):
        log.error(str(confply.config.__tool_type)+" is not a valid _tool_type and should not be set directly by users.")
        log.normal("\tuse: 'import confply.[tool_type].config as config' to import _tool_type.")

        for m in config_modules: del sys.modules[m.__name__]
        importlib.reload(confply.config)
        return -1

    # setting confply command configuration up
    old_stdout = sys.stdout

    # #todo: this is probably broken, test it
    # #todo: another awkward directory push pop that doesn't need to exist
    if len(new_working_dir) > 0:
        os.chdir(new_working_dir)
    if confply.config.log_file != None:
        log.normal("writing to: "+confply.config.log_file+"....")
        try:
            sys.stdout = open(confply.config.log_file, "w")
        except:
            log.error("couldn't open "+confply.config.log_file+" for write.")
            return_code = -1
            
    os.chdir(old_working_dir)
    if return_code >= 0:
        if confply.config.log_config != False:
            _print_config()
        old_working_dir = os.getcwd()
        new_working_dir = os.path.dirname(file_path)
        if len(new_working_dir) > 0:
            os.chdir(new_working_dir)

        try:
            time_start = timeit.default_timer()
            # #todo: tool selection phase should happen first.
            # #todo: rename generate to gen_tool_type
            valid_tools = _validate_config()
            tool_type = confply.config.__tool_type
            tool = confply.config.tool
            shell_cmd = tools[tool_type][tool].generate() if valid_tools else None
            if shell_cmd is not None:
                cmd_env = tools[tool_type][tool].get_environ()
                if len(shell_cmd) > 0:
                    if isinstance(shell_cmd, list):
                        log.normal("final commands:\n")
                        for shell_str in shell_cmd:
                            print(shell_str)
                        print("")
                    else:
                        log.normal("final command:\n\n"+str(shell_cmd)+"\n")
                    log.header("begin "+tool)
                sys.stdout.flush()
                def _run_shell_cmd(shell_cmd):
                    nonlocal return_code
                    if confply.config.log_file != None:
                        sys.stdout.flush()
                        result = subprocess.run(shell_cmd, stdout=sys.stdout, stderr=subprocess.STDOUT, text=True, shell=True, env=cmd_env)
                    else:
                        result = subprocess.run(shell_cmd, shell=True, env=cmd_env)

                    if result.returncode == 0:
                        log.linebreak()
                        log.success(tool+" succeeded!")
                    else:
                        log.linebreak()
                        log.error(tool+" failed.")
                        log.error(tool+" return code: "+str(result.returncode))
                        return_code = -2

                if isinstance(shell_cmd, list):
                    for cmd in shell_cmd:
                        cmd_time_start = timeit.default_timer()
                        log.linebreak()
                        log.normal(cmd)
                        log.normal("", flush=True)
                        _run_shell_cmd(cmd)
                        cmd_time_end = timeit.default_timer()
                        s = cmd_time_end-cmd_time_start
                        m = int(s/60)
                        h = int(m/60)
                        # time formating via format specifiers
                        # https://docs.python.org/3.8/library/string.html#formatspec
                        time = f"{h:0>2.0f}:{m:0>2.0f}:{s:0>5.2f}"
                        log.normal("time elapsed: "+time)
                else:
                    _run_shell_cmd(shell_cmd)
            else:
                log.error("couldn't generate a valid command.")
                return_code = -1

            time_end = timeit.default_timer()
            s = time_end-time_start
            m = int(s/60)
            h = int(m/60)
            # time formating via format specifiers
            # https://docs.python.org/3.8/library/string.html#formatspec
            time = f"{h:0>2.0f}:{m:0>2.0f}:{s:0>5.2f}"
            log.normal("total time elapsed: "+time)
        except:
            log.error("failed to run config: ")
            trace = traceback.format_exc()
            log.normal("traceback:\n\n"+trace)

            return_code = -1

        if sys.stdout != old_stdout:
            sys.stdout.close()
            sys.stdout = old_stdout

        if confply.config.post_run and inspect.isfunction(confply.config.post_run):
            try:
                log.normal("running post run script: "+confply.config.post_run.__name__)
                exec(confply.config.post_run.__code__, config_locals, {})
            except:
                log.error("failed to exec "+confply.config.post_run.__name__)
                trace = traceback.format_exc()
                log.normal("traceback:\n\n"+trace)
        os.chdir(old_working_dir)
    # This resets any confply.config back to what it was prior to running any user
    for m in config_modules: del sys.modules[m.__name__]
    importlib.reload(confply.config)
    return return_code

def _handle_help_arg(in_args):
    confply_dir = os.path.relpath(__file__)
    confply_dir = os.path.dirname(confply_dir)+"/.."
    with open(os.path.join(confply_dir,"help.md"), "r") as help_file:
        print("\n"+help_file.read())
        
def _handle_help_config_arg(option, in_args):
    confply_dir = os.path.relpath(__file__)
    confply_dir = os.path.dirname(confply_dir)
    help_path = option.split(".")[1]
    help_path = os.path.join(confply_dir, help_path)
    print(help_path)
    if os.path.exists(help_path):
        help_path = os.path.join(help_path, "help.md")
        if os.path.exists(help_path):
            with open(help_path, "r") as help_file:
                print("\n"+help_file.read())
        else:
            log.error(option+" does not have an associated help file")
    else:
        log.error(option+" is not a valid command type")

def _handle_version_arg(in_args):
    log.linebreak()
    log.normal("Confply "+confply.__version__)
    log.normal("Copyright (C) 2021 Graham Hughes.")
    log.normal("License MIT.")
    log.normal("This is free software; you are free to change and redistribute it.")
    log.normal("There is NO WARRANTY, to the extent permitted by law.")


def _handle_new_tool_type(in_args):
    if len(in_args) < 1:
        log.error("--new_tool_type requires a value.")
        log.normal("\t--new_tool_type [tool_type]")
        return
    confply_dir = os.path.relpath(__file__)
    confply_dir = os.path.dirname(confply_dir)
    tool_type = in_args.pop(0)
    tool_type_dir = os.path.join(confply_dir, tool_type)
    if not os.path.exists(tool_type_dir):
        confply_dir = os.path.join(confply_dir, "new_tool_type")
        os.mkdir(tool_type_dir)
        files = [
            "__init__.py",
            "help.md",
            "echo.py",
            "config/__init__.py",
            "options/__init__.py",
            "options/defaults.py",
            "options/tools.py"
        ]
        for file_name in files:
            with open(os.path.join(confply_dir, file_name), "r") as in_file:
                file_str = in_file.read()
                file_str = file_str.format_map({"tool_type":tool_type})
                tool_file = os.path.join(tool_type_dir, file_name)
                os.makedirs(os.path.dirname(tool_file), exist_ok=True)
                with open(tool_file, "w") as out_file:
                    out_file.write(file_str)
        log.success("created "+tool_type+" tool_type!")
        log.normal("generate a config file by calling './confply.py --gen_config "+tool_type+" my_config.py'")
    else:
        log.error(tool_type+" already exists. (--new_tool_type)")
        pass
        
def _handle_launcher_arg(in_args):
    if len(in_args) < 1:
        log.error("--launcher requires a value.")
        log.normal("\t--launcher [new_launcher_file]")
        return
    # #todo: this seems like a bad way to get the parent dir. Consider pathlib
    confply_dir = os.path.relpath(__file__)
    confply_dir = os.path.dirname(confply_dir)+"/.."
    confply_dir = os.path.relpath(confply_dir)
    confply_dir = confply_dir.replace("\\", "/")
    
    arguement = in_args.pop(0)
    launcher_path = os.path.abspath(os.path.curdir)+"/"+arguement
    if not os.path.exists(launcher_path):
        with open(launcher_path, "w") as launcher_file:
            launcher_str = new_launcher_str.format_map(
                {
                    "confply_dir":confply_dir,
                    "launcher":arguement,
                    "comment":"{\n    #'myconfig':'path/to/config.py'\n}"
                })
            launcher_file.write(launcher_str)
        st = os.stat(launcher_path)
        os.chmod(launcher_path, st.st_mode | stat.S_IEXEC)
        log.success("wrote: "+launcher_path)
    else:
        log.error(launcher_path+" already exists!")


def _handle_gen_config_arg(in_args):
    if len(in_args) < 2:
        log.error("--config requires two values:")
        log.normal("\t--gen_config [tool_type] [new_config_file]")
        log.normal("")
        log.normal("valid tool types:")
        confply_dir = os.path.dirname(__file__)
        files = os.listdir(confply_dir)
        for dir in files:
            if os.path.isdir(os.path.join(confply_dir, dir)) and not dir == "__pycache__" and not dir == "new_tool_type":
                log.normal("\t"+dir)
        return
    
    # this seems like a bad way to get the parent dir. Consider pathlib
    confply_dir = os.path.relpath(__file__)
    confply_dir = os.path.dirname(confply_dir)+"/.."
    confply_dir = os.path.relpath(confply_dir)
    confply_dir = confply_dir.replace("\\", "/")
    
    tool_type_arg = in_args.pop(0)
    config_arg = in_args.pop(0)
    config_path = os.path.abspath(os.path.curdir)+"/"+config_arg
    tool_type_dir = os.path.dirname(os.path.relpath(__file__))+"/"+tool_type_arg
    
    if not os.path.exists(tool_type_dir):
        log.error(tool_type_arg+" is not a valid tool_type, consider:")
        for dir_file in os.listdir(confply_dir+"/confply/"):
            if os.path.isdir(confply_dir+"/confply/"+dir_file):
                if not dir_file == "__pycache__":
                    log.normal("\t"+dir_file)
        return
    
    if not os.path.exists(config_path):
        with open(config_path, "w") as config_file:
            config_str = new_config_str.format_map(
                {
                    "confply_dir":confply_dir,
                    "tool_type_arg":tool_type_arg,
                    "config_file":config_arg
                })
            config_file.write(config_str)
        st = os.stat(config_path)
        os.chmod(config_path, st.st_mode | stat.S_IEXEC)
        log.success("wrote: "+config_path)
    else:
        log.error(config_path+" already exists!")
        log.normal("aborted --gen_config.")

def _handle_config_dict_arg(in_args):
    if len(in_args) < 1:
        log.error("--config requires a value.")
        log.normal("\t--config \"{'confply':{'tool':'cl'}}\"")
        return
    overide_dict = None
    try:
        overide_dict = ast.literal_eval(in_args.pop(0))
        if not isinstance(overide_dict, dict):
            log.error("--config must be a dictionary.")
            log.normal("\t--config \"{'confply':{'tool':'cl'}}\"")
            return
        elif "confply" in overide_dict:
            if not isinstance(overide_dict["confply"], dict):
                log.error("--config.confply must be a dictionary.")
                log.normal("\t--config \"{'confply':{'tool':'cl'}}\"")
                return
        else:
            overide_dict["confply"] = {}
    except:
        log.error("--config failed to parse argument as a dictionary")
        return
    
    confply.config.__override_dict.update(overide_dict)
    
def _handle_config_arg(option, in_args):
    if len(in_args) < 1:
        log.error("--config requires a value.")
        log.normal("\t--config.confply.tool \"cl\"")
        return

    path = option.split(".")[1:]
    if len(path) == 0:
        log.error("--config invalid path.")
        log.normal("\t--config.confply.tool \"cl\"")
        return
    
    if path[0] == "confply" and len(path) == 1:
        log.error("--config invalid path, cannot set confply")
        log.normal("\t--config.confply.tool \"cl\"")
        return
    # #todo: this is pretty shit, it doesn't solve the general case at all, but I'm being lazy
    #        you should be able to set values in a deep dictionary, but you can't.
    arg = in_args.pop(0)
    value = None
    try:
        value = ast.literal_eval(arg)
    except:
        value = arg


    if isinstance(value, str):
        log.normal(""+option[2:]+" = \""+str(value)+"\" <"+type(value).__name__+">")
    else:
        log.normal(""+option[2:]+" = "+str(value)+" <"+type(value).__name__+">")
    confply.config.__override_list.append([option[2:], value ])
