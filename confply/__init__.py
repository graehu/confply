import os
import sys
import timeit
import traceback
import importlib
import subprocess
import confply.config
import confply.log as log

import_cache = {}
# grab the confply config base settings here.
confply_base_config = {}
with open(os.path.dirname(__file__) + "/config.py", 'r') as config_file:
    exec(config_file.read(), {}, confply_base_config)

print(confply.config.confply_header)
log.linebreak()

class command:
    def __init__(self, path):
        self.config = {}
        self.file_path = path
        # open the file and read the junk out of it.
        # also execs any code that may be there.
        # potentially pass some things in via config.
        if os.path.exists(path):
            with open(path, 'r') as config_file:
                try:
                    exec(config_file.read(), {}, self.config)
                    # reset these when command class is cleaned up
                    log.success("successfully loaded: "+path)
                    self.load_success = True
                except:
                    log.error("failed to exec: "+path)
                    trace = traceback.format_exc().replace("<string>", path)
                    log.normal("traceback:\n\n"+trace)
                    self.load_success = False
        else:
            self.load_success = False
            log.error("failed to load: "+path)
            
    def run(self):
        if not self.load_success:
            log.error("failed running " + self.file_path + " command.")
            return
        # setting confply command configuration up
        old_log_topic = confply.config.confply_log_topic
        for key in confply_base_config.keys():
            exec("confply.config.{0} = self.config[key]".format(key), globals(), locals())
        new_log_topic = confply.config.confply_log_topic
        old_stdout = sys.stdout
        if confply.config.confply_log_file != None:
            confply.config.confply_log_topic = old_log_topic
            log.normal("writing to: "+confply.config.confply_log_file+"....")
            confply.config.confply_log_topic = new_log_topic
            sys.stdout = open(confply.config.confply_log_file, "w")
            print(confply.config.confply_header)
        if confply.config.confply_log_config != False:
            self.print_config()
        old_working_dir = os.getcwd()
        os.chdir(os.path.dirname(self.file_path))
        try:
            log.centered("[ running "+(self.config["confply_command"])+" command. ]")
            time_start = timeit.default_timer()
            module_name = "confply."+self.config["confply_command"]+".command"
            if module_name not in import_cache:
                import_cache[module_name] = importlib.import_module(module_name)
            command = import_cache[module_name]
            shell_cmd = command.generate(self.config)

            if shell_cmd is not None:
                log.normal("final command:\n\n"+shell_cmd+"\n")
                log.header("begin build")
                
                if confply.config.confply_log_file != None:
                    sys.stdout.flush()
                    result = subprocess.run(shell_cmd, stdout=sys.stdout, stderr=subprocess.STDOUT, text=True, shell=True)
                else:
                    result = subprocess.run(shell_cmd, shell=True)
                
                if result.returncode == 0:
                    log.linebreak()
                    log.success("command success!")
                else:
                    log.linebreak()
                    log.error("command failed.")
            else:
                log.error("couldn't generate valid command.")
            
            time_end = timeit.default_timer()
            log.centered("[ "+(self.config["confply_command"])+" command complete. ]")
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
            log.normal(sys.exc_info())
        if sys.stdout != old_stdout:
            sys.stdout.close()
            sys.stdout = old_stdout
        for key in confply_base_config.keys():
            exec("confply.config.{0} = confply_base_config[key]".format(key), globals(), locals())
        os.chdir(old_working_dir)

    def print_config(self):
        if not self.load_success:
            log.error("Failed printing " + self.file_path + " config.")
            return
        base_config = {}
        confply_path = os.path.dirname(__file__) + "/"
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
