import os
import sys
import stat
import shlex
import shutil
import timeit
import select
import inspect
import traceback
import importlib
import subprocess
import confply.config
import confply.log as log


# grab the confply config base settings here.
confply_base_config = {}
with open(os.path.dirname(__file__) + "/config.py", 'r') as config_file:
    exec(config_file.read(), {}, confply_base_config)

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

# fill this with your commands
aliases = {comment}

if __name__ == "__main__":
    # "all" will run all of the aliases
    aliases["all"] = ";".join([val for key, val in aliases.items()])
    launcher(sys.argv[1:], aliases)
"""

new_config_str = """#!{confply_dir}/confply.py
# generated using:
# python {confply_dir}/confply.py --config {command_arg} {config_file}
import sys
sys.path.append('{confply_dir}')
import confply.{command_arg}.config as confply
import confply.log as log
############# modify_below ################

confply.confply_log_topic = "{command_arg}"
log.normal("loading {config_file} with confply_args: "+str(confply.confply_args))
"""

def launcher(in_args, aliases):
    return_code = -999999
    printed_header = False
    def try_print_header():
        nonlocal printed_header
        if not printed_header:
            printed_header = True
            log.confply_header()
            log.linebreak()
    confply_dir = os.path.relpath(__file__)
    confply_dir = os.path.dirname(confply_dir)+"/.."
    confply_dir = os.path.relpath(confply_dir)
    confply_dir = confply_dir.replace("\\", "/")
    # #todo: design flaw here, the spliting should be in confply.py, not this launcher.
    if len(in_args) != 0:
        for arg in in_args:
            if arg in aliases:
                for line in aliases[arg].split(";"):
                    shell = shlex.split(line)
                    if len(shell) == 0:
                        continue
                    if os.path.exists(shell[0]):
                        system_code = 0
                        file_args = line.replace(shell[0], "")
                        if os.name == 'nt':
                            # windows doesn't support os.WEXITSTATUS
                            if not printed_header:
                                system_code = os.system("python "+confply_dir+"/confply.py "+shell[0]+" "+file_args)
                                printed_header = True
                            else:
                                system_code = os.system("python "+confply_dir+"/confply.py "+shell[0]+" "+file_args+" --no_header")
                        else:
                            if not printed_header:
                                system_code = os.WEXITSTATUS(os.system("python "+confply_dir+"/confply.py "+shell[0]+" "+file_args))
                                printed_header = True
                            else:
                                system_code = os.WEXITSTATUS(os.system("python "+confply_dir+"/confply.py "+shell[0]+" "+file_args+" --no_header"))
                            
                        if(system_code > return_code and system_code != 0):
                            return_code = system_code
                        if return_code == -1:
                            break
                    else:
                        try_print_header()
                        log.error("alias '"+arg+"' doesn't point to a valid file:")
                        log.normal("\t"+aliases[arg])
                        return_code = -1
                        break
            else:
                try_print_header()
                log.error(arg+" is not in aliases.")
                return_code = -1
                break
    else:
        if not printed_header:
            try_print_header()
        log.error("no arguements supplied.")
        with open(os.path.join(confply_dir,"help.md"), "r") as help_file:
            print("\n"+help_file.read())
        return_code = -1
    log.linebreak()

    if(return_code != -999999):
        exit(abs(return_code))
    else:
        exit(0)

class command:
    def __init__(self, in_args):
        confply_args = []
        while len(in_args) > 0:
            arg = in_args.pop(0)
            if arg == ";" or arg.endswith(";"):
                break
            confply_args.append(arg)

        confply_args = shlex.split(" ".join(confply_args))
        path = confply_args[0]
        confply_args.pop(0)

        if os.name == "nt":
            confply.config.confply_platform = "windows"
        elif os.name == "posix":
            confply.config.confply_platform = "linux"
        
        self.tools = {}
        self.config = {}
        confply.config.confply_args = confply_args
        self.file_path = path
        # open the file and read the junk out of it.
        # also execs any code that may be there.
        # potentially pass some things in via config.
        if os.path.exists(path) and os.path.isfile(path):
            old_path = os.getcwd()
            self.config["confply_modified"] = os.path.getmtime(path).real
            with open(path, 'r') as config_file:
                new_path = os.path.dirname(path)
                if not new_path == "":
                    os.chdir(new_path)
                try:
                    exec(config_file.read(), {}, self.config)
                    # reset these when command class is cleaned up
                    log.linebreak()
                    log.success("successfully loaded: "+path)
                    self.load_success = True
                except:
                    log.error("failed to exec: "+path)
                    trace = traceback.format_exc().replace("<string>", path)
                    log.normal("traceback:\n\n"+trace)
                    self.load_success = False

            if not old_path == "":
                os.chdir(old_path)
        else:
            self.load_success = False
            log.error("failed to load: "+path)

    # #todo: make this import one tool at a time, like previous import_cache behaviour
    def _validate_config(self):
        command = self.config["confply_command"]
        if command not in self.tools:
            dir = os.path.dirname(__file__) +"/"+command
            if os.path.exists(dir):
                files = os.listdir(dir)
            else:
                log.error(command+" is not a valid confply_command and should not be set by users.")
                log.normal("\tuse: 'from confply.[command].config import *' to import confply_command.")
                return None

            self.tools[command] = {}
            module_root = "confply."+command+"."
            for py in files:
                if py.endswith(".py") and not py == "config.py" and not py == "common.py":
                    tool = py[0:-3]
                    self.tools[command][tool] = importlib.import_module(module_root+tool)

        tool = self.config["confply_tool"]
        def print_tools():
            for k in self.tools[command].keys():
                if not self.tools[command][k].is_found(self.config):
                    log.normal("\t"+k+" (not found)")
                else:
                    log.normal("\t"+k)
                    
        def tool_select():
            if confply.config.confply_platform != "windows":
                finished = False
                while not finished:
                    log.normal("continue with a different tool? (Y/N): ", end="", flush=True)
                    rlist, _, _ = select.select([sys.stdin], [], [], 10)
                    if rlist:
                        answer = sys.stdin.readline().upper().replace("\n", "")
                        if answer == "YES" or answer == "Y":
                            log.normal("which tool? options:")
                            print_tools()
                            log.normal("")
                            log.normal("tool: ", end="", flush=True)
                            tool = input("")
                            if tool in self.tools[command]:
                                self.config["confply_tool"] = tool
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
                print_tools()
                log.normal("")
                return False
        
        if tool in self.tools[command]:
            old_envs = os.environ.copy()
            os.environ = self.tools[command][tool].get_environ(self.config)
            
            if not self.tools[command][tool].is_found(self.config):
                log.error("'"+tool+"' could not be found, is it installed?")
                out = tool_select()
                os.environ = old_envs
                return out
            else:
                os.environ = old_envs
                return True
        else:
            log.error("'"+str(tool)+"' is not a valid "+command+" tool.")
            return tool_select()

        return False
        

    def run(self):
        return_code = 0
        if not self.load_success:
            log.error("failed running " + self.file_path + " command.")
            return -1
        confply_path = os.path.dirname(__file__) + "/"

        if(not "confply" in self.config):
            log.error("confply config incorrectly imported")
            log.normal("\tuse: 'import confply.[command].config as confply'")
            return -1
        for k, v in vars(self.config["confply"]).items():
            self.config[k] = v
        
        
        if(not os.path.exists(confply_path+self.config["confply_command"])):
            log.error(self.config["confply_command"]+" is not a valid confply_command and should not be set directly by users.")
            log.normal("\tuse: 'import confply.[command].config as confply' to import confply_command.")
            return -1

        # setting confply command configuration up
        old_log_topic = confply.config.confply_log_topic
        for key in confply_base_config.keys():
            exec("confply.config.{0} = self.config[key]".format(key), globals(), locals())
        new_log_topic = confply.config.confply_log_topic
        old_stdout = sys.stdout
        
        # #todo: this is probably broken, test it
        if confply.config.confply_log_file != None:
            confply.config.confply_log_topic = old_log_topic
            log.normal("writing to: "+confply.config.confply_log_file+"....")
            confply.config.confply_log_topic = new_log_topic
            try:
                sys.stdout = open(confply.config.confply_log_file, "w")
            except:
                log.error("couldn't open "+confply.config.confply_log_file+" for write.")
                return_code = -1

        if return_code >= 0:
            if confply.config.confply_log_config != False:
                self.print_config()
            old_working_dir = os.getcwd()
            new_working_dir = os.path.dirname(self.file_path)
            if len(new_working_dir) > 0:
                os.chdir(new_working_dir)

            try:
                time_start = timeit.default_timer()
                # #todo: tool selection phase should happen first.
                # #todo: rename generate to gen_command
                valid_tools = self._validate_config()
                command = self.config["confply_command"]
                tool = self.config["confply_tool"]
                shell_cmd = self.tools[command][tool].generate(self.config) if valid_tools else None
                if shell_cmd is not None:
                    cmd_env = self.tools[command][tool].get_environ(self.config)
                    if len(shell_cmd) > 0:
                        log.normal("final command:\n\n"+str(shell_cmd)+"\n")
                        log.header("begin "+tool)
                    sys.stdout.flush()
                    def run_shell_cmd(shell_cmd):
                        nonlocal return_code
                        if confply.config.confply_log_file != None:
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
                            log.linebreak()
                            log.normal(cmd)
                            log.normal("", flush=True)
                            run_shell_cmd(cmd)
                    else:
                        run_shell_cmd(shell_cmd)
                else:
                    log.error("couldn't generate a valid command.")
                    return_code = -1

                time_end = timeit.default_timer()
                s = time_end-time_start
                m = int(s/60)
                h = int(m/60)
                # time formating via format specifiers
                # https://docs.python.org/3.8/library/string.html#formatspec
                time = "{h:0>2.0f}:{m:0>2.0f}:{s:0>5.2f}"
                time = time.format_map({"s":s, "m":m, "h":h})
                log.normal("time elapsed: "+time)
            except:
                log.error("failed to run config: ")
                log.normal(str(sys.exc_info()))
                return_code = -1

            if sys.stdout != old_stdout:
                sys.stdout.close()
                sys.stdout = old_stdout

            if self.config["confply_post_run"] and inspect.isfunction(self.config["confply_post_run"]):
                self.config["confply_post_run"]()
            os.chdir(old_working_dir)
        # This resets any confply.config back to what it was prior to running any user
        # config. Stops state leaks between command runs as confply.config is global.
        for key in confply_base_config.keys():
            exec("confply.config.{0} = confply_base_config[key]".format(key), globals(), locals())
        return return_code

    def print_config(self):
        if not self.load_success:
            log.error("Failed printing " + self.file_path + " config.")
            return
        
        base_config = {}
        confply_path = os.path.dirname(__file__) + "/"
        if(os.path.exists(confply_path+self.config["confply_command"])):
            with open(confply_path+self.config["confply_command"]+"/config.py", 'r') as config_file:
                exec(config_file.read(), {}, base_config)
            file_name = os.path.basename(self.file_path)
            log.normal(file_name+" command configuration:")
            log.normal("{")
            
            for k, v in self.config.items():
                if k in base_config and v is not base_config[k]:
                    if isinstance(v, list):
                        log.normal("\t"+str(k)+": ")
                        for i in v:
                            log.normal("\t\t"+str(i))
                    else:
                        log.normal("\t"+str(k)+": "+str(v))

            log.normal("}")
            log.normal("")
        else:
            log.error(self.config["confply_command"]+" is not a valid confply_command and should not be set by users.")
            log.normal("\tuse: 'import confply.[command].config as confply' to import confply_command.")

def handle_help_arg(in_args):
    confply_dir = os.path.relpath(__file__)
    confply_dir = os.path.dirname(confply_dir)+"/.."
    with open(os.path.join(confply_dir,"help.md"), "r") as help_file:
        print("\n"+help_file.read())
        
def handle_launcher_arg(in_args):
    if len(in_args) < 1:
        log.error("--launcher requires a value.")
        log.normal("\t--launcher [new_launcher_file]")
        return
    # this seems like a bad way to get the parent dir. Consider pathlib
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
                    "comment":"{\n    #'mycommand':'path/to/command.py'\n}"
                })
            launcher_file.write(launcher_str)
        st = os.stat(launcher_path)
        os.chmod(launcher_path, st.st_mode | stat.S_IEXEC)
        log.success("wrote: "+launcher_path)
    else:
        log.error(launcher_path+" already exists!")


def handle_config_arg(in_args):
    if len(in_args) < 2:
        log.error("--config requires two values:")
        log.normal("\t--config [confply_command] [new_config_file]")
        log.normal("")
        log.normal("valid confply_commands:")
        confply_dir = os.path.dirname(__file__)
        files = os.listdir(confply_dir)
        for dir in files:
            if os.path.isdir(os.path.join(confply_dir, dir)) and not dir == "__pycache__":
                log.normal("\t"+dir)
        return
    
    # this seems like a bad way to get the parent dir. Consider pathlib
    confply_dir = os.path.relpath(__file__)
    confply_dir = os.path.dirname(confply_dir)+"/.."
    confply_dir = os.path.relpath(confply_dir)
    confply_dir = confply_dir.replace("\\", "/")
    
    command_arg = in_args.pop(0)
    config_arg = in_args.pop(0)
    config_path = os.path.abspath(os.path.curdir)+"/"+config_arg
    command_dir = os.path.dirname(os.path.relpath(__file__))+"/"+command_arg
    
    if not os.path.exists(command_dir):
        log.error(command_arg+" is not a valid command, consider:")
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
                    "command_arg":command_arg,
                    "config_file":config_arg
                })
            config_file.write(config_str)
        st = os.stat(config_path)
        os.chmod(config_path, st.st_mode | stat.S_IEXEC)
        log.success("wrote: "+config_path)
    else:
        log.error(config_path+" already exists!")
        log.normal("aborted --config.")
