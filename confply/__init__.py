import os
import sys
import ast
import json
import stat
import types
import timeit
import select
import inspect
import pathlib
import hashlib
import traceback
import importlib
import importlib.util
import subprocess
import confply.config
import confply.server
import confply.log as log
import confply.mail as mail
import confply.slack as slack
from datetime import datetime
from datetime import timedelta

config_modules = set()


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
        log.debug("push "+self.path)
        return self
        pass

    def __exit__(self, type, value, traceback):
        os.chdir(self.old_path)
        log.debug("pop "+self.old_path)
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


def launcher(in_args, aliases):
    return_code = -999999

    def print_header():
        log.confply_header()
        log.linebreak()

    confply_dir = __get_confply_dir()
    if len(in_args) != 0:
        alias = in_args[0]
        args = " ".join(in_args[1:])

        if alias in aliases:
            system_code = 0
            cmd = ("python3 "+confply_dir+"/confply.py ")
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
def run_commandline(in_args):
    """
    runs the confply config, with supplied arguements.
    confply reservered options will be stripped. e.g. --help
    see help.md

    usage: run_commandline(["path_to_config", "optional", "arguements"])
    """
    log.normal("called with args: "+str(in_args))
    in_args = __strip_confply_args(in_args)
    confply.config.args = in_args
    if confply.config.config_path:
        config_path = confply.config.config_path
        if not os.path.exists(config_path):
            log.error("couldn't find: "+config_path)
            return -1
        if config_path.endswith(".py"):
            log.linebreak()
            log.header("run config")
            log.linebreak()
            # setup config run
            should_run = confply.config.run
            config_locals = load_config(config_path)
            if not config_locals:
                log.error("failed to load: "+config_path)
                return -1

            if("config" not in config_locals):
                log.error("confply config incorrectly imported")
                log.normal("\tuse: 'import confply.[config_type].config as config'")
                clean_modules()
                return -1

            config = config_locals["config"]
            if(not __validate_types(config)):
                log.error("failed to run config")
                return -1
            # ensure we don't run if should_run was EVER false
            if should_run is not True:
                confply.config.run = should_run
            # config
            config_hash = md5_file(config.__file__)
            if (config_hash != getattr(config_locals["config"], "version_hash", "")):
                log.warning("warning: config_hash doesn't match expected hash")
                log.normal("\tconfig file might not function correctly")
                log.normal("\texpected:")
                log.normal("\t\t"+"config.version_hash='"+config_hash+"' # add to silence")
                log.normal("")
            return __run_config(config_locals)

        elif config_path.endswith(".json"):
            if os.path.exists(config_path):
                with open(config_path) as in_json:
                    in_dict = json.loads(in_json.read())
                    in_dict["confply"].update({"config_path": config_path})
                    return run_dict(in_dict)
        elif config_path.endswith(".ini"):
            if os.path.exists(config_path):
                import configparser

                def parse_lit(in_val):
                    try:
                        return ast.literal_eval(in_val)
                    except Exception:
                        return in_val

                conf = configparser.ConfigParser()
                conf.read(config_path)
                in_dict = {"confply": {"config_path": config_path}}
                for (key, val) in conf["config"].items():
                    in_dict[key] = parse_lit(val)
                for (key, val) in conf["confply"].items():
                    in_dict["confply"][key] = parse_lit(val)
                return run_dict(in_dict)
        else:
            log.error("unsupported config type: "+config_path)
            return -1
    else:
        return 0
    return 0


def run_dict(in_dict):
    """
    runs the confply dict for the supplied config_type

    usage: run_dict(in_dict)
    """
    log.linebreak()
    log.header("run config")
    log.linebreak()

    # setup config run
    should_run = confply.config.run
    if("config_path" in in_dict["confply"]):
        path = in_dict["confply"]["config_path"]
    else:
        path = None
    __load_vcs_info(path)
    confply.config.config_path = path
    config_name = os.path.basename(path)
    confply.config.config_name = config_name
    confply.config.modified = os.path.getmtime(path).real
    config_locals = apply_to_config(in_dict)
    if not config_locals:
        log.error("failed to load:  json")
        return -1

    if("config" not in config_locals):
        log.error("confply failed import")
        log.normal("\tuse: '__package__': 'confply.[config_type].config' in json/ini")
        clean_modules()
        return -1

    if(not __validate_types(config_locals["config"])):
        log.error("failed to run config")
        return -1

    # ensure we don't run if should_run was EVER false
    if should_run is not True:
        confply.config.run = should_run
    return __run_config(config_locals)


def config_to_dict(config, has_privates=True, is_json=False):
    def is_serialisable(obj):
        return isinstance(obj, (int, float, str, dict, list, bool, tuple))

    def module_to_dict(module):
        out = {}
        for key in dir(module):
            if key in ["__builtins__", "__cached__"]:
                continue
            if key.startswith("__") and not has_privates:
                continue
            value = getattr(module, key)
            if inspect.ismodule(value):
                out[key] = module_to_dict(value)
                continue
            # elif inspect.isfunction(value):
                # #todo: handle functions in a better way
                # out[key] = value.__name__
                # pass
            elif is_serialisable(value) or not is_json:
                out[key] = value
        return out
    return module_to_dict(config)


def load_config(path):
    global config_modules
    if os.name == "nt":
        confply.config.platform = "windows"
    elif os.name == "posix":
        confply.config.platform = "linux"

    __load_vcs_info(path)
    # find group config in parent directories
    directory_paths = __get_group_configs(path)
    directory_paths.append(path)
    config_locals = {}
    # load and execute the config files
    for dir_path in directory_paths:
        if dir_path is None:
            continue
        dir_path = os.path.abspath(dir_path)
        if os.path.exists(dir_path) and os.path.isfile(dir_path):
            config_name = os.path.basename(dir_path)
            confply.config.config_name = config_name
            confply.config.modified = os.path.getmtime(dir_path).real

            try:
                with pushd(os.path.dirname(dir_path)):
                    config_locals = __import_module(config_name)
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
                            config_modules.add(v)

                    # validate there are less than 2 imported configs
                    if len(config_modules) > 1:
                        log.error("too many confply configs imported:")
                        for c in config_modules:
                            log.normal("\t "+c)
                        log.normal(
                            "confply only supports one config import."
                        )
                        clean_modules()
                        return None, None

                    log.linebreak()
                    log.success("loaded: "+str(dir_path))
            except Exception:
                log.error("failed to exec: "+str(dir_path))
                trace = traceback.format_exc().replace("<string>",
                                                       str(dir_path))
                log.normal("traceback:\n\n"+trace)
                return None, None
            # with open(dir_path) as config_file:
            #     with pushd(os.path.dirname(dir_path)):
            #         try:
            #             exec(config_file.read(), {}, config_locals)
            #             # find imported confply configs for cleanup
            #             for k, v in config_locals.items():
            #                 m_valid = isinstance(v, types.ModuleType)
            #                 if not m_valid:
            #                     continue

            #                 v_name = v.__name__
            #                 m_valid = m_valid and v not in config_modules
            #                 m_valid = m_valid and v_name.startswith("confply.")
            #                 m_valid = m_valid and v_name.endswith(".config")
            #                 if m_valid:
            #                     config_modules.add(v)

            #             # validate there are less than 2 imported configs
            #             if len(config_modules) > 1:
            #                 log.error("too many confply configs imported:")
            #                 for c in config_modules:
            #                     log.normal("\t "+c)
            #                 log.normal(
            #                     "confply only supports one config import."
            #                 )
            #                 clean_modules()
            #                 return None, None

            #             log.linebreak()
            #             log.success("loaded: "+str(dir_path))
            #         except Exception:
            #             log.error("failed to exec: "+str(dir_path))
            #             trace = traceback.format_exc().replace("<string>",
            #                                                    str(dir_path))
            #             log.normal("traceback:\n\n"+trace)
            #             return None, None

        else:
            log.error("failed to find: " + str(dir_path))
            return None, None

    return config_locals


def clean_modules():
    global config_modules
    for m in config_modules:
        importlib.reload(m)
    importlib.reload(confply.config)
    importlib.reload(confply.mail)
    importlib.reload(confply.slack)
    pass


def get_version():
    global __version__
    version = __version__+" #"
    git_cmd = "git rev-parse --short HEAD"
    git_cmd = subprocess.check_output(git_cmd, shell=True)
    git_cmd = git_cmd.decode('utf-8').strip()
    version += git_cmd
    return version


def md5_file(in_file):
    hash_md5 = hashlib.md5()
    with open(in_file, "rb") as read_file:
        for chunk in iter(lambda: read_file.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


# private section


__version__ = "0.0.1"
__doc__ = """
Confply is an abstraction layer for other commandline tools.
It lets you write a consistent config file & commandline interface for tools
that have similar functions.
More to come.
"""


__new_launcher_str = r"""#!/usr/bin/env python
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
sys.path.append(os.path.abspath("{confply_dir}"))
from confply import launcher
from confply import run_commandline

# fill this with your configs
aliases = {comment}

# "all" will run all of the aliases
aliases["all"] = " -- ".join([val for key, val in aliases.items()])

if __name__ == "__main__":
    args = sys.argv[1:]
    file_path = os.path.relpath(__file__)
    dir_name = os.path.dirname(__file__)
    if "--listen" in args:
        run_commandline(["--listen", file_path])
    else:
        if not dir_name == "":
            os.chdir(dir_name)
        if args:
            launcher(args, aliases)
        else:
            launcher(["default"], aliases)
"""

__new_config_str = """#!{confply_dir}/confply.py --in
# generated using:
# python {confply_dir}/confply.py --new_config {config_type_arg} {config_file}
import sys
sys.path.append('{confply_dir}')
import confply.{config_type_arg}.config as config
import confply.{config_type_arg}.options as options
import confply.log as log
config.version_hash = '{config_hash}'
############# modify_below ################

config.confply.log_topic = "{config_type_arg}"
log.normal("loading {config_file} with confply_args: "+str(config.confply.args))
"""
# list of configs that have already been run
__configs_run = set()
__directory_stack = []


def __load_vcs_info(path):
    with pushd(os.path.dirname(path)):
        # find the git root
        # #todo: extend this to other version control?
        # move this to a config_type
        if confply.config.vcs == "git":
            try:
                git_cmd = 'git rev-parse --show-toplevel'
                git_cmd = subprocess.check_output(git_cmd, shell=True)
                confply.config.vcs_root = git_cmd.decode('utf-8').strip()
                git_cmd = 'git branch --show-current'
                git_cmd = subprocess.check_output(git_cmd, shell=True)
                confply.config.vcs_branch = git_cmd.decode('utf-8').strip()
                git_cmd = "git log -1 --pretty=format:'%an'"
                git_cmd = subprocess.check_output(git_cmd, shell=True)
                confply.config.vcs_author = git_cmd.decode("utf-8").strip()
                git_cmd = "git log -1"
                git_cmd = subprocess.check_output(git_cmd, shell=True)
                confply.config.vcs_log = git_cmd.decode("utf-8").strip()
            except subprocess.CalledProcessError:
                log.warning('failed to fill git vcs information')


def __run_config(config_locals):
    in_args = confply.config.args
    config = config_locals["config"]
    return_code = 0
    should_run = confply.config.run
    file_path = confply.config.config_path
    __apply_overrides(config)
    new_working_dir = os.path.dirname(file_path)
    old_stdout = sys.stdout
    # setting confply command configuration up
    with pushd(new_working_dir):
        if confply.config.log_file:
            log.normal("writing to: " +
                       confply.config.log_file +
                       "....")
            try:
                sys.stdout = open(confply.config.log_file, "w")
                version = sys.version_info
                version = (version.major, version.minor, version.micro)
                if "--no_header" not in in_args:
                    log.confply_header()
                    log.linebreak()
                    log.normal("python"+str(version))
                    log.normal("confply "+get_version())
                    log.normal("date: "+str(datetime.now()))
                    log.linebreak()
                log.normal("confply logging to "+confply.config.log_file)
            except Exception:
                log.error("couldn't open " +
                          confply.config.log_file +
                          " for write.")
                return_code = -1
        try:
            if (confply.config.post_load and
                    inspect.isfunction(confply.config.post_load)):
                func_name = confply.config.post_load.__name__
                log.normal("running " + func_name)
                sys.stdout.flush()
                success = confply.config.post_load()
                if success is not None and not success:
                    log.error(func_name + " unsuccessful")
                    return_code = -2
                else:
                    log.normal(func_name + " successful")
                log.linebreak()

        except Exception:
            log.error("failed to run "+func_name)
            trace = traceback.format_exc()
            log.normal("traceback:\n\n"+trace)
            return_code = -2
            pass

        diff_config = __get_diff_config(config)
        should_run = confply.config.run
        report = {
            "config_path": file_path,
            "config_json": json.dumps(diff_config, indent=4),
            "config_type": "unknown",
            "tool": "unknown",
            "status": "failure",
            "vcs_root": confply.config.vcs_root,
            "vcs_log": confply.config.vcs_log,
            "vcs": confply.config.vcs,
            "vcs_branch": confply.config.vcs_branch,
            "vcs_author": confply.config.vcs_author,
            "time_taken": "00:00:00"
        }
        if return_code >= 0:
            if confply.config.log_config is not False:
                __print_config(os.path.basename(file_path), config)
            try:
                time_start = timeit.default_timer()
                # #todo: tool selection phase should happen first.
                tools = __validate_config(config)
                config_type = config.__package__
                tool = confply.config.tool
                report["tool"] = tool
                report["config_type"] = config_type
                if tools:
                    shell_cmd = tools[tool]
                    shell_cmd.handle_args()
                    # #todo: rename generate to gen_config_type.
                    if shell_cmd.validate():
                        shell_cmd = shell_cmd.generate()
                    else:
                        shell_cmd = None
                else:
                    shell_cmd = None

                __run_dependencies(config, should_run)

                def print_cmd(in_cmd, depth=0):
                    if len(in_cmd) > 0:
                        if isinstance(in_cmd[0], list):
                            depth = depth + 1
                            for cmd in in_cmd:
                                print_cmd(cmd, depth)
                        else:
                            cmd = [confply.config.command_prepend]+in_cmd
                            cmd = in_cmd+[confply.config.command_append]
                            cmd = [c for c in cmd if c]
                            print(str(depth)+": "+" ".join(cmd))

                def run_cmd(in_cmd, depth=0):
                    if len(in_cmd) > 0:
                        if isinstance(in_cmd[0], list):
                            depth = depth + 1
                            procs = []
                            cmd_time_start = timeit.default_timer()
                            for cmd in in_cmd:
                                if proc := run_cmd(cmd, depth):
                                    procs.append(proc)
                            return_code = 0
                            for proc in procs:
                                if isinstance(proc, int): return_code += 1 if proc else 0
                                else:
                                    proc.wait()
                                    return_code += 1 if proc.returncode else 0
                                    if proc.returncode:
                                        log.error(proc.args+" failed.")
                                        log.error(f"return code: {proc.returncode}")
                                    else:
                                        log.success(proc.args+" succeeded!")
                            if procs:
                                cmd_time_end  = timeit.default_timer()
                                time = f"{timedelta(seconds=cmd_time_end-cmd_time_start)}"
                                log.normal("time elapsed "+time)
                            return return_code
                        else:
                            sys.stdout.flush()
                            log.linebreak()
                            cmd = [confply.config.command_prepend]+in_cmd
                            cmd = cmd+[confply.config.command_append]
                            cmd = [c for c in cmd if c]
                            log.normal(" ".join(cmd))
                            log.normal("", flush=True)
                            return __run_shell_cmd_parallel(cmd, cmd_env)
                    
                if shell_cmd:
                    cmd_env = tools[tool].get_environ()

                    if len(shell_cmd) > 0:
                        log.normal("final commands:\n")
                        print_cmd(shell_cmd)
                        print("")
                        if should_run:
                            log.header("begin "+tool)
                    sys.stdout.flush()

                    if should_run and isinstance(shell_cmd[0], list):
                        return_code = run_cmd(shell_cmd)
                    elif should_run:
                        return_code = __run_shell_cmd(shell_cmd, cmd_env)
                    else:
                        log.warning("no commands run.")

                elif shell_cmd == []:
                    log.normal("no commands to run.")
                else:
                    log.error("failed to generate a valid command.\n\n"+
                              file_path+":1:1: error: broken config\n")
                    return_code = -1

                time_end = timeit.default_timer()
                time = f"{timedelta(seconds=time_end-time_start)}"
                log.normal("time elapsed "+time)
                log.normal("total time elapsed "+time)
                report["time_taken"] = time
                report["status"] = "success" if return_code == 0 else "failure"

            except Exception:
                log.error("failed to run config: ")
                trace = traceback.format_exc()
                log.normal("traceback:\n\n"+trace)
                return_code = -1
            sys.stdout.flush()
            try:
                if (confply.config.post_run and
                        inspect.isfunction(confply.config.post_run)):
                    func_name = confply.config.post_run.__name__
                    log.normal("running " + func_name)
                    sys.stdout.flush()
                    success = confply.config.post_run()
                    if success is not None and not success:
                        log.error(func_name + " unsuccessful")
                        return_code = -2
                    else:
                        log.normal(func_name + " successful")
                    log.linebreak()

            except Exception:
                log.error("failed to run "+func_name)
                trace = traceback.format_exc()
                log.normal("traceback:\n\n"+trace)
                return_code = -2
                pass
            log.normal("date: "+str(datetime.now()))
            log.linebreak()
            sys.stdout.flush()

            if sys.stdout != old_stdout:
                sys.stdout.close()
                sys.stdout = old_stdout
                if confply.config.log_echo_file:
                    with open(confply.config.log_file) as out_log:
                        log_str = out_log.read()
                        log_str = log_str.split("confply logging to " +
                                                confply.config.log_file)[1]
                        log.normal("wrote:"+log_str)

            if (confply.config.mail_send == report["status"] or
                    confply.config.mail_send == "all"):
                mail.host = confply.config.__mail_host
                mail.sender = confply.config.mail_from
                mail.recipients = confply.config.mail_to
                mail.login = confply.config.__mail_login
                mail.attachments = confply.config.mail_attachments
                if (confply.config.log_file and
                        report["status"] == "failure"):
                    mail.attachments.append(os.path.abspath(
                        confply.config.log_file
                    ))
                    pass
                if mail.login:
                    mail.send_report(report)

            if (confply.config.slack_send == report["status"] or
                    confply.config.slack_send == "all"):
                slack.bot_token = confply.config.__slack_bot_token
                slack.uploads = confply.config.slack_uploads
                if (confply.config.log_file and
                        report["status"] == "failure"):
                    slack.uploads.append(os.path.abspath(
                        confply.config.log_file
                    ))
                if slack.bot_token:
                    slack.send_report(report)
    clean_modules()
    return return_code


def __import_module(file_path):
    spec = importlib.util.spec_from_file_location("confply.imported", file_path)
    imp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(imp)
    return vars(imp)


def __run_shell_cmd_parallel(shell_cmd, cmd_env):
    if confply.config.log_file:
        sys.stdout.flush()
        # #todo: check if this can be ansi-coloured
        proc = subprocess.Popen(" ".join(shell_cmd),
                                stdout=sys.stdout,
                                stderr=subprocess.STDOUT,
                                text=True,
                                shell=True,
                                env=cmd_env)
    else:
        proc = subprocess.Popen(" ".join(shell_cmd),
                                shell=True,
                                env=cmd_env)
    return proc


def __run_shell_cmd(shell_cmd, cmd_env):
    if confply.config.log_file:
        sys.stdout.flush()
        # #todo: check if this can be ansi-coloured
        result = subprocess.run(" ".join(shell_cmd),
                                stdout=sys.stdout,
                                stderr=subprocess.STDOUT,
                                text=True,
                                shell=True,
                                env=cmd_env)
    else:
        result = subprocess.run(" ".join(shell_cmd),
                                shell=True,
                                env=cmd_env)

    if result.returncode == 0:
        log.linebreak()
        log.success(shell_cmd[0]+" succeeded!")
        return 0
    else:
        log.linebreak()
        log.error(shell_cmd[0]+" failed.")
        log.error(shell_cmd[0] +
                  " return code: " +
                  str(result.returncode))
        return -2


def __run_dependencies(config, should_run):
    store = config_to_dict(config)
    importlib.reload(config)
    importlib.reload(config.confply)
    confply.config.run = should_run
    depends_return = 0
    if len(store["confply"]["dependencies"]) > 0:
        for d in store["confply"]["dependencies"]:
            if d not in __configs_run:
                confply.config.log_topic = store["confply"]["log_topic"]
                log.normal("running dependency: "+str(d))
                confply.config.log_topic = "confply"
                log.linebreak()
                __configs_run.add(d)
                depends_return = run_commandline(["--in", d])
                if depends_return < 0:
                    confply.config.log_topic = store["confply"]["log_topic"]
                    confply.config.log_file = store["confply"]["log_file"]
                    log.error("failed to run: "+str(d))
                    log.normal("stopping dependency execution")
                    break
                    # #todo: make this configurable rather than prompting the user, the 10s stall crashes emacs.
                    # or make this work better with emacs at least
                    # if not input_prompt("continue execution?"):
                    #     log.normal("aborting final commands")
                    #     break
                    # else:
                    #     log.normal("continuing execution.")
        pass
    # reset confply.config
    apply_to_config(store)
    # #todo: make this jump to the mail section
    return depends_return


def __apply_overrides(config):
    # update the config and confply.config dictionaries with overrides
    if isinstance(confply.config.__override_dict, dict):
        confply_dict = confply.config.__override_dict
        config.confply.__dict__.update(confply_dict["confply"])
        del confply_dict["confply"]
        config.__dict__.update(confply_dict)
        confply.config.__override_dict = {"confply": {}}

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


def __get_group_configs(path):
    directory_paths = []
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
    return directory_paths


def apply_to_config(in_dict):
    global config_modules
    module = importlib.import_module(in_dict["__package__"])
    config_locals = {"config": module}
    config_modules.add(module)

    def apply_to_module(module, in_dict):
        for key in dir(module):
            if key in in_dict:
                if inspect.ismodule(getattr(module, key)):
                    apply_to_module(getattr(module, key), in_dict[key])
                else:
                    setattr(module, key, in_dict[key])
    apply_to_module(module, in_dict)
    return config_locals


def __validate_types(config):
    d1 = config_to_dict(config)
    importlib.reload(config)
    importlib.reload(config.confply)
    d2 = config_to_dict(config)
    apply_to_config(d1)

    def validate_dict(d1, d2):
        valid = True
        for k, v in d1.items():
            if isinstance(v, dict) and isinstance(d2[k], dict):
                valid = valid and validate_dict(v, d2[k])
            elif not isinstance(v, type(d2[k])):
                # edge case, allow tuples as lists & vice versa
                if isinstance(v, (tuple, list)) and isinstance(d2[k], (tuple, list)):
                    continue
                valid = False
                log.error(k+": expected '"+type(d2[k]).__name__+"' got '"+type(v).__name__+"'")
        return valid
    return validate_dict(d1, d2)


# #todo: this can be simplified
def __validate_config(config):
    tools = {}
    tool_dir = os.path.dirname(config.__file__)
    tool_dir = os.path.join(tool_dir, "..")
    if os.path.exists(tool_dir):
        files = os.listdir(tool_dir)
    else:
        log.error(config.__package__+" is not a valid confply_config_type" +
                  " and should not be set by users.")
        log.normal("\tuse: " +
                   "'import confply.[config_type].config as config'" +
                   " to import confply_config_type.")
        return None

    tools = {}
    module_path = config.__package__.rsplit(".", 1)[0]
    for py in files:
        if py.endswith(".py") and not py == "__init__.py":
            tool = py[0:-3]
            tools[tool] = \
                importlib.import_module(module_path+"."+tool)

    tool = confply.config.tool
    pass

    #######
    if tool in tools:
        if not tools[tool].is_found():
            log.error("'"+tool+"' could not be found, is it installed?")
            if __tool_select(tools):
                return tools
            else:
                return None
        else:
            return tools
    else:
        log.error("'"+str(tool)+"' is not a valid tool.")
        if __tool_select(tools):
            return tools
        else:
            return None

    return tools


def __print_config(config_name, config):
    diff_config = __get_diff_config(config)
    config_type_path = config.__file__

    if(os.path.exists(config_type_path)):
        log.normal(config_name+" configuration:")
        log.normal("")

        def print_dict(d1, depth=0):
            for k, v in d1.items():
                if isinstance(v, list):
                    log.bold("\t"*depth+log.format.bold(str(k))+": ")
                    for i in v:
                        log.normal("\t"*(depth+1)+str(i))
                elif isinstance(v, dict):
                    log.normal("\t"*depth+log.format.bold(k)+":")
                    print_dict(v, depth=depth+1)
                    pass
                elif inspect.isfunction(v):
                    log.normal("\t"*depth+log.format.bold(str(k))+": "+v.__name__)
                else:
                    log.normal("\t"*depth+log.format.bold(str(k))+": "+str(v))
        if "confply" in diff_config:
            del diff_config["confply"]
        print_dict(diff_config)
        log.normal("")
    else:
        log.error(confply.config_config_type +
                  " is not a valid confply_config_type" +
                  " and should not be set by users.")
        log.normal("\tuse: 'import confply.[config_type].config" +
                   " as confply' to import confply_config_type.")


def __get_confply_dir(rel_path=True):
    # make confply.py's directory path
    confply_dir = os.path.relpath(__file__)
    confply_dir = os.path.dirname(confply_dir)+"/.."
    if rel_path:
        confply_dir = os.path.relpath(confply_dir)
        pass
    else:
        confply_dir = os.path.abspath(confply_dir)
        pass
    confply_dir = confply_dir.replace("\\", "/")
    return confply_dir


def __get_diff_config(config, has_privates=False):
    store = config_to_dict(config)
    config_dict = config_to_dict(config, has_privates, True)
    importlib.reload(config)
    importlib.reload(config.confply)
    base_dict = config_to_dict(config, has_privates, True)

    def diff_dict(d1, d2):
        d3 = {}
        for k in d1:
            if k not in d2:
                continue
            if isinstance(d1[k], dict):
                d3[k] = diff_dict(d1[k], d2[k])
                if not d3[k]:
                    del d3[k]
            elif d1[k] != d2[k]:
                d3[k] = d2[k]
        return d3
    apply_to_config(store)
    return diff_dict(base_dict, config_dict)


def __tool_select(in_tools):
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


def __strip_confply_args(in_args):
    commandline = []
    in_len = len(in_args)
    for i in range(0, in_len):
        if not len(in_args) > 0:
            break
        option = in_args.pop(0)
        if option.startswith("--"):
            if option == "--launcher":
                confply.__handle_launcher_arg(in_args)
            elif option == "--listen":
                confply.__handle_listen_arg(in_args)
            elif option == "--new_config":
                confply.__handle_new_config_arg(in_args)
            elif option == "--help":
                confply.__handle_help_arg(in_args)
            elif option.startswith("--help."):
                confply.__handle_help_config_arg(option, in_args)
            elif option == "--version":
                confply.__handle_version_arg(in_args)
            elif option == "--config":
                confply._handle_config_dict_arg(in_args)
            elif option.startswith("--config."):
                confply.__handle_config_arg(option, in_args)
            elif option == "--new_tool":
                confply.__handle_new_tool_arg(in_args)
            elif option == "--no_run":
                confply.config.run = False
            elif option == "--no_header":
                # #todo: need to find a way to take headers out of logs
                pass
            elif option == "--in":
                confply.__handle_in_arg(in_args)
                pass
            elif option == "--":
                break
            else:
                commandline.append(option)
            continue
        else:
            commandline.append(option)
    return commandline


def __handle_help_arg(in_args):
    help_path = os.path.join(__get_confply_dir(), "help.md")
    with open(help_path) as help_file:
        print("\n"+help_file.read())


def __handle_help_config_arg(option, in_args):
    module_dir = os.path.relpath(__file__)
    module_dir = os.path.dirname(module_dir)
    help_path = option.split(".")[1]
    help_path = os.path.join(module_dir, help_path)
    if os.path.exists(help_path):
        help_path = os.path.join(help_path, "help.md")
        if os.path.exists(help_path):
            with open(help_path) as help_file:
                print("\n"+help_file.read())
        else:
            log.error(option+" does not have an associated help file")
    else:
        log.error(option+" is not a valid command type")


def __handle_version_arg(in_args):
    log.linebreak()
    log.normal("Confply "+get_version())
    log.normal("Copyright (C) 2021 Graham Hughes.")
    log.normal("License MIT.")
    log.normal("This is free software; " +
               "you are free to change and redistribute it.")
    log.normal("There is NO WARRANTY, to the extent permitted by law.")


def __handle_in_arg(in_args):
    if len(in_args) < 1:
        log.error("--in requires a value.")
        log.normal("\t--in [config_path]")
        return
    in_path = in_args.pop(0)
    confply.config.config_path = in_path


def __handle_new_tool_arg(in_args):
    if len(in_args) < 1:
        log.error("--new_tool requires a value.")
        log.normal("\t--new_tool [config_type]")
        return
    module_dir = os.path.relpath(__file__)
    module_dir = os.path.dirname(module_dir)
    config_type = in_args.pop(0)
    config_type_dir = os.path.join(module_dir, config_type)
    if not os.path.exists(config_type_dir):
        module_dir = os.path.join(module_dir, "new_tool")
        os.mkdir(config_type_dir)
        files = [
            "__init__.py",
            "help.md",
            "default.py",
            "config/__init__.py",
            "options/__init__.py",
            "options/tool.py"
        ]
        for file_name in files:
            with open(os.path.join(module_dir, file_name)) as in_file:
                file_str = in_file.read()
                file_str = file_str.format_map({"config_type": config_type})
                tool_file = os.path.join(config_type_dir, file_name)
                os.makedirs(os.path.dirname(tool_file), exist_ok=True)
                with open(tool_file, "w") as out_file:
                    out_file.write(file_str)
        log.success("created "+config_type+" config_type!")
        log.normal("generate a config file by calling: " +
                   "'./confply.py --new_config "+config_type+" my_config.py'")
    else:
        log.error(config_type+" already exists. (--new_tool)")
        pass


def __handle_launcher_arg(in_args):
    if len(in_args) < 1:
        log.error("--launcher requires a value.")
        log.normal("\t--launcher [new_launcher_file]")
        return
    confply_dir = __get_confply_dir()
    arguement = in_args.pop(0)
    launcher_path = os.path.abspath(os.path.curdir)+"/"+arguement
    if not os.path.exists(launcher_path):
        with open(launcher_path, "w") as launcher_file:
            launcher_str = __new_launcher_str.format_map(
                {
                    "confply_dir": confply_dir,
                    "launcher": arguement,
                    "comment": "{\n    # 'default': '--in path/to/config.py'\n}"
                })
            launcher_file.write(launcher_str)
        st = os.stat(launcher_path)
        os.chmod(launcher_path, st.st_mode | stat.S_IEXEC)
        log.success("wrote: "+launcher_path)
    else:
        log.error(launcher_path+" already exists!")


def __handle_listen_arg(in_args):
    if len(in_args) < 1:
        log.error("--listen requires a value.")
        log.normal("\t--listen [launcher_file]")
        return

    arguement = in_args.pop(0)
    launcher_path = os.path.abspath(os.path.curdir)+"/"+arguement
    if os.path.exists(launcher_path):
        with pushd(os.path.dirname(__file__)):
            confply.server.start_server(launcher=launcher_path)
    else:
        log.error(launcher_path+" not found!")


def __handle_new_config_arg(in_args):
    if len(in_args) < 2:
        log.error("--config requires two values:")
        log.normal("\t--new_config [config_type] [new_config_file]")
        log.normal("")
        log.normal("valid tool types:")
        module_dir = os.path.dirname(__file__)
        files = os.listdir(module_dir)
        for dir in files:
            if (os.path.isdir(os.path.join(module_dir, dir)) and
                    not dir == "__pycache__" and not dir == "new_tool"):
                log.normal("\t"+dir)
        return

    confply_dir = __get_confply_dir()
    config_type_arg = in_args.pop(0)
    config_arg = in_args.pop(0)
    config_path = os.path.abspath(os.path.curdir)+"/"+config_arg
    config_type_dir = os.path.dirname(os.path.relpath(__file__))
    config_type_dir = os.path.join(config_type_dir, config_type_arg)

    if not os.path.exists(config_type_dir):
        log.error(config_type_arg+" is not a valid config_type, consider:")
        for dir_file in os.listdir(confply_dir+"/confply/"):
            if os.path.isdir(confply_dir+"/confply/"+dir_file):
                if not dir_file == "__pycache__":
                    log.normal("\t"+dir_file)
        return

    hash_file = os.path.join(config_type_dir, "config/__init__.py")
    config_hash = md5_file(hash_file)
    if not os.path.exists(config_path):
        with open(config_path, "w") as config_file:
            config_str = __new_config_str.format_map(
                {
                    "confply_dir": confply_dir,
                    "config_type_arg": config_type_arg,
                    "config_file": config_arg,
                    "config_hash": config_hash
                })
            config_file.write(config_str)
        st = os.stat(config_path)
        os.chmod(config_path, st.st_mode | stat.S_IEXEC)
        log.success("wrote: "+config_path)
    else:
        log.error(config_path+" already exists!")
        log.normal("aborted --new_config.")


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


def __handle_config_arg(option, in_args):
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
