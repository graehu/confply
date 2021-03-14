import os
import sys
import ast
import json
import stat
import types
import timeit
import select
import inspect
import smtplib
import pathlib
import traceback
import importlib
import subprocess
import confply.config
import confply.server
import email.mime.text
import confply.log as log
import email.mime.multipart
import email.mime.application

__version__ = "0.0.1"
__doc__ = """
Confply is an abstraction layer for other commandline tools.
It lets you write a consistent config file & commandline interface for tools
that have similar functions.
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
sys.path.append("{confply_dir}")
from confply import launcher

# fill this with your configs
aliases = {comment}

# "all" will run all of the aliases
aliases["all"] = " -- ".join([val for key, val in aliases.items()])

if __name__ == "__main__":
    dir_name = os.path.dirname(__file__)
    if not dir_name == "":
        os.chdir(dir_name)
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
# list of configs that have already been run
__configs_run = []
__directory_stack = []


class SafeDict(dict):
    def __missing__(self, key):
        return '{' + key + '}'


class pushd:
    """
    push a directory, use it like so:

    with pushd("my_dir"):
        do_stuff()
    """
    path = ""
    old_path = ""

    def __init__(self, path):
        self.path = os.path.abspath(path)
        self.old_path = os.getcwd()
        pass

    def __enter__(self):
        os.chdir(self.path)
        return self
        pass

    def __exit__(self, type, value, traceback):
        os.chdir(self.old_path)
        pass


def input_prompt(message):
    """
    prompt the user for a Y/N answer on a 10 second timeout
    """
    if os.name != "nt":
        while True:
            log.normal(message+" (Y/N): ",
                       end="", flush=True)
            select_args = ([sys.stdin], [], [], 10)
            rlist, _, _ = select.select(*select_args)
            if rlist:
                answer = sys.stdin.readline()
                answer = answer.upper()
                answer = answer.replace("\n", "")
                if answer == "YES" or answer == "Y":
                    return True

                elif answer == "NO" or answer == "N":
                    return False
            else:
                print("")
                log.normal("timed out after 10 seconds")
                return False
    else:
        return False


def print_config(config_name, config):
    base_config = {}
    compare_config = {}
    confply_path = os.path.dirname(__file__) + "/"
    tool_type_path = confply_path+confply.config.__tool_type

    if(os.path.exists(tool_type_path)):
        tool_type_path += "/config/__init__.py"
        with open(tool_type_path) as config_file:
            exec(config_file.read(), {}, base_config)
        with open(confply_path+"config.py") as config_file:
            exec(config_file.read(), {}, compare_config)

        log.normal(config_name+" configuration:")
        log.normal("{")

        for k, v in compare_config.items():
            base_config["confply."+k] = v

        compare_config = {
            **{"confply." +
                k: v for k, v in confply.config.__dict__.items()},
            **config.__dict__
        }
        out_config = {}
        for k, v in compare_config.items():
            if (k.startswith("__") or k.startswith("confply.__") or
                    k == "confply.mail_login"):
                continue
            if k in base_config and v != base_config[k]:
                out_config[k] = v
                if isinstance(v, list):
                    log.normal("\t"+str(k)+": ")
                    for i in v:
                        log.normal("\t\t"+str(i))
                elif inspect.isfunction(v):
                    if base_config[k] is None or \
                       v.__name__ != base_config[k].__name__:
                        log.normal("\t"+str(k)+": "+v.__name__)
                    else:
                        pass
                else:
                    log.normal("\t"+str(k)+": "+str(v))

        log.normal("}")
        log.normal("")
    else:
        log.error(confply.config_tool_type +
                  " is not a valid confply_tool_type" +
                  " and should not be set by users.")
        log.normal("\tuse: 'import confply.[tool_type].config" +
                   " as confply' to import confply_tool_type.")


def get_diff_config(config):
    base_config = {}
    compare_config = {}
    diff_config = {}
    confply_path = os.path.dirname(__file__) + "/"
    tool_type_path = confply_path+confply.config.__tool_type

    if(os.path.exists(tool_type_path)):
        tool_type_path += "/config/__init__.py"
        with open(tool_type_path) as config_file:
            exec(config_file.read(), {}, base_config)
        with open(confply_path+"config.py") as config_file:
            exec(config_file.read(), {}, compare_config)

        for k, v in compare_config.items():
            base_config["confply."+k] = v

        compare_config = {
            **{"confply." +
                k: v for k, v in confply.config.__dict__.items()},
            **config.__dict__
        }
        for k, v in compare_config.items():
            if (k.startswith("__") or k.startswith("confply.__") or
                    k == "confply.mail_login"):
                continue
            if k in base_config and v != base_config[k] and not inspect.isfunction(v):
                diff_config[k] = v
    return diff_config


def tool_select(in_tools):
    def _print_tools():
        num = -1
        for k in in_tools.keys():
            num += 1
            if not in_tools[k].is_found():
                log.warning("\t"+str(num)+") "+k+" (not found)")
            else:
                log.normal("\t"+str(num)+") "+k)
    shown_options = False
    while True:
        if input_prompt("continue with a different tool?"):
            if not shown_options:
                log.normal("which tool? options:")
                _print_tools()
                log.normal("")
                shown_options = True
            log.normal("tool: ", end="", flush=True)
            in_tool = input("")
            if(in_tool.isdigit()):
                tool_num = int(in_tool)
                if tool_num < len(in_tools):
                    tool_keys = list(in_tools.keys())
                    confply.config.tool = tool_keys[tool_num]
                    return True
                else:
                    log.error("'" + in_tool +
                              "' is out of range.")
                pass
            else:
                if in_tool in in_tools:
                    confply.config.tool = in_tool
                    return True
                else:
                    log.error("'" + in_tool +
                              "' could not be found," +
                              " is it installed?")
        else:
            if not shown_options:
                log.normal("options:")
                _print_tools()
                log.normal("")
            return False


def launcher(in_args, aliases):
    # #todo: remove the launcher at some point
    return_code = -999999

    def print_header():
        log.confply_header()
        log.linebreak()
    # make confply.py's directory path
    confply_dir = os.path.relpath(__file__)
    confply_dir = os.path.dirname(confply_dir)+"/.."
    confply_dir = os.path.relpath(confply_dir)
    confply_dir = confply_dir.replace("\\", "/")
    if len(in_args) != 0:
        alias = in_args[0]
        args = " ".join(in_args[1:])

        if alias in aliases:
            system_code = 0
            cmd = ("python "+confply_dir+"/confply.py ")
            cmd += (aliases[alias]+" "+args)
            cmd = cmd.replace(" -- ", " "+args+" -- ")
            # windows doesn't support os.WEXITSTATUS
            if os.name == 'nt':
                system_code = os.system(cmd)
            else:
                system_code = os.WEXITSTATUS(os.system(cmd))

            if (system_code > return_code) and (system_code != 0):
                return_code = system_code
        else:
            print_header()
            log.error(alias+" is not in aliases.")
            return_code = -1
    else:
        print_header()
        log.error("no arguements supplied.")
        with open(os.path.join(confply_dir, "help.md")) as help_file:
            print("\n"+help_file.read())
        return_code = -1
    log.linebreak()

    if(return_code != -999999):
        exit(abs(return_code))
    else:
        exit(0)


# #todo: make this import one tool at a time,
# like previous import_cache behaviour
def run_config(in_args):
    """
    runs the confply config, with supplied arguements.
    confply reservered options will be stripped. e.g. --help
    see help.md

    usage: run_config(["path_to_config", "optional", "arguements"])
    """
    in_args = _strip_confply_args(in_args)
    if len(in_args) == 0:
        return 0
    log.linebreak()
    log.header("run config")
    log.linebreak()
    ##########

    def _validate_config():
        nonlocal tools
        nonlocal config_modules
        tool_type = confply.config.__tool_type
        if tool_type not in tools:
            dir = os.path.dirname(__file__) + "/" + tool_type
            if os.path.exists(dir):
                files = os.listdir(dir)
            else:
                log.error(tool_type+" is not a valid confply_tool_type" +
                          " and should not be set by users.")
                log.normal("\tuse: " +
                           "'import confply.[tool_type].config as config'" +
                           " to import confply_tool_type.")
                return None

            tools[tool_type] = {}
            module_path = "confply."+tool_type+"."
            config_modules.append(
                importlib.import_module("confply."+tool_type)
            )
            for py in files:
                if py.endswith(".py") and not py == "__init__.py":
                    tool = py[0:-3]
                    tools[tool_type][tool] = \
                        importlib.import_module(module_path + tool)

        tool = confply.config.tool
        pass

        #######
        if tool in tools[tool_type]:
            if not tools[tool_type][tool].is_found():
                log.error("'"+tool+"' could not be found, is it installed?")
                return tool_select(tools[tool_type])
            else:
                return True
        else:
            log.error("'"+str(tool)+"' is not a valid "+tool_type+" tool.")
            return tool_select(tools[tool_type])

        return False
    ########

    # setup config run
    return_code = 0
    path = in_args.pop(0)

    # find the git root
    # #todo: extend this to other version control?
    try:
        git_cmd = ['git', 'rev-parse', '--show-toplevel']
        git_root = subprocess.check_output(git_cmd)
        confply.config.git_root = git_root.decode('utf-8').strip()

    except subprocess.CalledProcessError:
        log.warning('git_root not found')

    if os.name == "nt":
        confply.config.platform = "windows"
    elif os.name == "posix":
        confply.config.platform = "linux"

    tools = {}
    config_locals = {}
    confply.config.args = in_args
    file_path = path
    directory_paths = []
    config_modules = []

    def clean_modules():
        nonlocal config_modules
        for m in config_modules:
            del sys.modules[m.__name__]
        importlib.reload(confply.config)
        pass

    # find group config in parent directories
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
    should_run = confply.config.run
    # load and execute the config files
    for path in directory_paths:
        if path is None:
            continue

        if os.path.exists(path) and os.path.isfile(path):
            config_name = os.path.basename(path)
            confply.config.config_name = config_name
            confply.config.modified = os.path.getmtime(path).real

            with open(path) as config_file:
                with pushd(os.path.dirname(path)):
                    try:
                        exec(config_file.read(), {}, config_locals)
                        # find imported confply configs for cleanup
                        for k, v in config_locals.items():
                            m_valid = isinstance(v, types.ModuleType)
                            if not m_valid:
                                continue

                            v_name = v.__name__
                            m_valid = m_valid and v not in config_modules
                            m_valid = m_valid and v_name.startswith("confply.")
                            m_valid = m_valid and v_name.endswith(".config")
                            if m_valid:
                                config_modules.append(v)

                        # validate there are less than 2 imported configs
                        if len(confply.config.__imported_configs) > 1:
                            log.error("too many confply configs imported:")
                            for c in confply.config.__imported_configs:
                                log.normal("\t "+c)
                            log.normal(
                                "confply only supports one config import."
                            )
                            clean_modules()
                            return -1

                        log.linebreak()
                        log.success("loaded: "+str(path))
                    except Exception:
                        log.error("failed to exec: "+path)
                        trace = traceback.format_exc().replace("<string>",
                                                               path)
                        log.normal("traceback:\n\n"+trace)
                        return -1

        else:
            log.error("failed to load: "+path)
            return -1

    # ensure we don't run if should_run was EVER false
    if should_run is not True:
        confply.config.run = should_run

    confply_path = os.path.dirname(__file__) + "/"
    if("config" not in config_locals):
        log.error("confply config incorrectly imported")
        log.normal("\tuse: 'import confply.[tool_type].config as config'")
        clean_modules()
        return -1

    config = config_locals["config"]
    # attempting to stop people calling builtin functions
    if "__builtins__" in config.__dict__:
        del config.__dict__["__builtins__"]

    # update the config and confply.config dictionaries with overrides
    if isinstance(confply.config.__override_dict, dict):
        confply_dict = confply.config.__override_dict
        config.confply.__dict__.update(confply_dict["confply"])
        del confply_dict["confply"]
        config.__dict__.update(confply_dict)

    # update the configs with further overrides
    if isinstance(confply.config.__override_list, list):
        for k, v in confply.config.__override_list:
            try:
                exec("{0} = v".format(k), globals(), locals())
            except Exception:
                log.warning("failed to exec "+"{0} = {1}:".format(k, v))
                log.normal("\t\tcheck calling option  --"+k)
                # trace = traceback.format_exc()
                # log.normal("traceback:\n\n"+trace)

    # #todo: this push and pop of the directory isn't great
    # it happens later anyway.
    new_working_dir = os.path.dirname(file_path)
    with pushd(new_working_dir):
        try:
            if (confply.config.post_load and
                    inspect.isfunction(confply.config.post_load)):
                log.normal("running post load script: " +
                           confply.config.post_load.__name__)
                exec(confply.config.post_load.__code__, config_locals, {})

        except Exception:
            log.error("failed to exec "+confply.config.post_load.__name__)
            trace = traceback.format_exc()
            log.normal("traceback:\n\n"+trace)

    if(not os.path.exists(confply_path+str(confply.config.__tool_type))):
        log.error(str(confply.config.__tool_type) +
                  " is not a valid _tool_type and should not be set directly.")
        log.normal("\tuse: 'import confply.[tool_type].config as config'" +
                   " to import _tool_type.")

        clean_modules()
        return -1

    # setup mail
    mail_message = email.mime.multipart.MIMEMultipart('html')
    mail_message["Subject"] = (pathlib.Path(confply.config.git_root).name +
                               ": " + file_path)
    mail_message["From"] = confply.config.mail_from
    mail_message["To"] = confply.config.mail_to

    # setting confply command configuration up
    old_stdout = sys.stdout

    # #todo: this is probably broken, test it
    # #todo: another awkward directory push pop that doesn't need to exist
    with pushd(new_working_dir):
        log_file = confply.config.log_file
        if log_file is not None:
            log.normal("writing to: "+log_file+"....")
            try:
                sys.stdout = open(log_file, "w")
                version = sys.version_info
                version = (version.major, version.minor, version.micro)
                if "--no_header" not in in_args:
                    log.confply_header()
                    log.linebreak()
                    log.normal("python"+str(version))
                    log.linebreak()
            except Exception:
                log.error("couldn't open " +
                          log_file +
                          " for write.")
                return_code = -1

        if return_code >= 0:
            if confply.config.log_config is not False:
                print_config(os.path.basename(file_path), config)

            try:
                time_start = timeit.default_timer()
                # #todo: tool selection phase should happen first.
                # #todo: rename generate to gen_tool_type.
                valid_tools = _validate_config()
                tool_type = confply.config.__tool_type
                tool = confply.config.tool
                should_run = confply.config.run
                if valid_tools:
                    shell_cmd = tools[tool_type][tool]
                    shell_cmd.handle_args()
                    shell_cmd = shell_cmd.generate() if valid_tools else None
                else:
                    shell_cmd = None

                old_topic = confply.config.log_topic
                mail_login = confply.config.mail_login
                mail_host = confply.config.mail_host
                mail_attachments = confply.config.mail_attachments
                if log_file is not None:
                    mail_attachments.append(log_file)
                diff_config = get_diff_config(config)
                clean_modules()
                confply.config.run = should_run
                dependencies = confply.config.dependencies
                if len(dependencies) > 0:
                    for d in dependencies:
                        if d not in __configs_run:
                            confply.config.log_topic = old_topic
                            log.normal("running dependency: "+str(d))
                            confply.config.log_topic = "confply"
                            log.linebreak()
                            __configs_run.append(d)
                            depends_return = run_config([d])
                            if depends_return < 0:
                                confply.config.log_topic = old_topic
                                confply.config.log_file = log_file
                                log.error("failed to run: "+str(d))
                                if not input_prompt("continue execution?"):
                                    log.normal("aborting final commands")
                                    return depends_return
                                else:
                                    log.normal("continuing execution.")
                    pass
                confply.config.log_topic = old_topic
                confply.config.log_file = log_file

                if shell_cmd is not None:
                    cmd_env = tools[tool_type][tool].get_environ()
                    if len(shell_cmd) > 0:
                        if isinstance(shell_cmd, list):
                            log.normal("final commands:\n")
                            for shell_str in shell_cmd:
                                print(shell_str)
                            print("")
                        else:
                            log.normal("final command:\n\n" +
                                       str(shell_cmd) +
                                       "\n")
                        if should_run:
                            log.header("begin "+tool)
                    sys.stdout.flush()

                    def _run_shell_cmd(shell_cmd):
                        nonlocal return_code
                        if log_file is not None:
                            sys.stdout.flush()
                            # #todo: check if this can be ansi-coloured
                            result = subprocess.run(shell_cmd,
                                                    stdout=sys.stdout,
                                                    stderr=subprocess.STDOUT,
                                                    text=True,
                                                    shell=True,
                                                    env=cmd_env)
                        else:
                            result = subprocess.run(shell_cmd,
                                                    shell=True,
                                                    env=cmd_env)

                        if result.returncode == 0:
                            log.linebreak()
                            log.success(tool+" succeeded!")
                        else:
                            log.linebreak()
                            log.error(tool+" failed.")
                            log.error(tool +
                                      " return code: " +
                                      str(result.returncode))
                            return_code = -2

                    if should_run and isinstance(shell_cmd, list):
                        for cmd in shell_cmd:
                            cmd_time_start = timeit.default_timer()
                            log.linebreak()
                            log.normal(cmd)
                            log.normal("", flush=True)
                            _run_shell_cmd(cmd)
                            cmd_time_end = timeit.default_timer()
                            # #todo: this can be tidied with format var capture
                            s = cmd_time_end-cmd_time_start
                            m = int(s/60)
                            h = int(m/60)
                            # time formating via format specifiers
                            # https://docs.python.org/3.8/library/string.html#formatspec
                            time = f"{h:0>2.0f}:{m:0>2.0f}:{s:0>5.2f}"
                            log.normal("time elapsed: "+time)
                    elif should_run:
                        _run_shell_cmd(shell_cmd)
                    else:
                        log.warning("no commands run")
                else:
                    log.error("failed to generate a valid command.")
                    return_code = -1

                time_end = timeit.default_timer()
                s = time_end-time_start
                m = int(s/60)
                h = int(m/60)
                # time formating via format specifiers
                # https://docs.python.org/3.8/library/string.html#formatspec
                time = f"{h:0>2.0f}:{m:0>2.0f}:{s:0>5.2f}"
                log.normal("total time elapsed: "+time)
                html_file = os.path.dirname(__file__)
                html_file = os.path.join(html_file, "mail.html")

                with open(html_file) as mail_file:
                    message_str = mail_file.read()
                    html_replace = {
                        "config": file_path,
                        "success": ("successfully" if
                                    return_code == 0 else "unsuccessfully"),
                        "config_json": json.dumps(diff_config, indent=4),
                        "time": time
                    }
                    for key, val in html_replace.items():
                        message_str = message_str.replace("{"+key+"}", str(val))

                    message_mime = email.mime.text.MIMEText(message_str, 'html')
                    mail_message.attach(message_mime)
                    for f in mail_attachments:
                        if f is None or (not os.path.exists(f)):
                            log.error("failed to send attachment: "+str(f))
                            continue
                        with open(f, "rb") as fil:
                            part = email.mime.application.MIMEApplication(
                                fil.read(),
                                Name=os.path.basename(f)
                            )
                        # After the file is closed
                        part['Content-Disposition'] = (
                            'attachment; filename="%s"'
                            % os.path.basename(f)
                        )
                        mail_message.attach(part)

            except Exception:
                log.error("failed to run config: ")
                trace = traceback.format_exc()
                log.normal("traceback:\n\n"+trace)
                # mail_message.set_content("failed to run "+file_path)
                return_code = -1

            if sys.stdout != old_stdout:
                sys.stdout.close()
                sys.stdout = old_stdout

            if (confply.config.post_run and
                    inspect.isfunction(confply.config.post_run)):
                try:
                    log.normal("running post run script: " +
                               confply.config.post_run.__name__)
                    exec(confply.config.post_run.__code__, config_locals, {})

                except Exception:
                    log.error("failed to exec " +
                              confply.config.post_run.__name__)
                    trace = traceback.format_exc()
                    log.normal("traceback:\n\n"+trace)

    if mail_login and should_run:
        server = smtplib.SMTP_SSL(mail_host)
        server.ehlo()
        server.login(*mail_login)
        server.send_message(mail_message)
        server.quit()
    return return_code


def _strip_confply_args(in_args):
    commandline = []
    in_len = len(in_args)
    for i in range(0, in_len):
        if not len(in_args) > 0:
            break
        option = in_args.pop(0)
        if option.startswith("--"):
            if option == "--launcher":
                confply._handle_launcher_arg(in_args)
            elif option == "--listen":
                confply._handle_listen_arg(in_args)
            elif option == "--gen_config":
                confply._handle_gen_config_arg(in_args)
            elif option == "--help":
                confply._handle_help_arg(in_args)
            elif option.startswith("--help."):
                confply._handle_help_config_arg(option, in_args)
            elif option == "--version":
                confply._handle_version_arg(in_args)
            elif option == "--config":
                confply._handle_config_dict_arg(in_args)
            elif option.startswith("--config."):
                confply._handle_config_arg(option, in_args)
            elif option == "--new_tool_type":
                confply._handle_new_tool_type(in_args)
            elif option == "--no_run":
                confply.config.run = False
            elif option == "--no_header":
                # #todo: need to find a way to take headers out of logs
                pass
            elif option == "--":
                break
            else:
                commandline.append(option)
            continue
        else:
            commandline.append(option)
    return commandline


def _handle_help_arg(in_args):
    confply_dir = os.path.relpath(__file__)
    confply_dir = os.path.dirname(confply_dir)+"/.."
    with open(os.path.join(confply_dir, "help.md")) as help_file:
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
            with open(help_path) as help_file:
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
    log.normal("This is free software; " +
               "you are free to change and redistribute it.")
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
            with open(os.path.join(confply_dir, file_name)) as in_file:
                file_str = in_file.read()
                file_str = file_str.format_map({"tool_type": tool_type})
                tool_file = os.path.join(tool_type_dir, file_name)
                os.makedirs(os.path.dirname(tool_file), exist_ok=True)
                with open(tool_file, "w") as out_file:
                    out_file.write(file_str)
        log.success("created "+tool_type+" tool_type!")
        log.normal("generate a config file by calling: " +
                   "'./confply.py --gen_config "+tool_type+" my_config.py'")
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
                    "confply_dir": confply_dir,
                    "launcher": arguement,
                    "comment": "{\n    # 'myconfig':'path/to/config.py'\n}"
                })
            launcher_file.write(launcher_str)
        st = os.stat(launcher_path)
        os.chmod(launcher_path, st.st_mode | stat.S_IEXEC)
        log.success("wrote: "+launcher_path)
    else:
        log.error(launcher_path+" already exists!")


def _handle_listen_arg(in_args):
    if len(in_args) < 1:
        log.error("--listen requires a value.")
        log.normal("\t--listen [launcher_file]")
        return
    # #todo: this seems like a bad way to get the parent dir. Consider pathlib
    confply_dir = os.path.relpath(__file__)
    confply_dir = os.path.dirname(confply_dir)+"/.."
    confply_dir = os.path.relpath(confply_dir)
    confply_dir = confply_dir.replace("\\", "/")

    arguement = in_args.pop(0)
    launcher_path = os.path.abspath(os.path.curdir)+"/"+arguement
    if os.path.exists(launcher_path):
        with pushd(os.path.dirname(__file__)):
            confply.server.start_server(launcher=launcher_path)
    else:
        log.error(launcher_path+" not found!")


def _handle_gen_config_arg(in_args):
    if len(in_args) < 2:
        log.error("--config requires two values:")
        log.normal("\t--gen_config [tool_type] [new_config_file]")
        log.normal("")
        log.normal("valid tool types:")
        confply_dir = os.path.dirname(__file__)
        files = os.listdir(confply_dir)
        for dir in files:
            if (os.path.isdir(os.path.join(confply_dir, dir)) and
                    not dir == "__pycache__" and not dir == "new_tool_type"):
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
    tool_type_dir = os.path.dirname(os.path.relpath(__file__))
    tool_type_dir = os.path.join(tool_type_dir, tool_type_arg)

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
                    "confply_dir": confply_dir,
                    "tool_type_arg": tool_type_arg,
                    "config_file": config_arg
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
    except Exception:
        log.error("--config failed to parse argument as a dictionary")
        return

    confply.config.__override_dict.update(overide_dict)


logged_overrides = False


def _handle_config_arg(option, in_args):
    global logged_overrides
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
    # #todo: this is pretty shit, it doesn't solve the general case at all
    #  but I'm being lazy you should be able to set values in a deep dictionary
    #  but you can't.
    arg = in_args.pop(0)
    value = None
    try:
        value = ast.literal_eval(arg)
    except Exception:
        value = arg

    # #todo: this should be done prior to running the config. not now.
    # this logging section is lazy af.
    if not logged_overrides:
        logged_overrides = True
        log.normal("overrides:")

    if isinstance(value, str):
        log.normal("\t"+option[2:]+" = \"" +
                   str(value)+"\" <"+type(value).__name__+">")
    else:
        log.normal("\t"+option[2:]+" = " +
                   str(value)+" <"+type(value).__name__+">")
    confply.config.__override_list.append([option[2:], value])
