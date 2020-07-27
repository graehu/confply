import os
import sys
import confply.log as log
import confply.cpp_compiler.compiler as cpp_compiler

print("""
                     _____       .__         
  ____  ____   _____/ ____\_____ |  | ___.__.
_/ ___\/  _ \ /    \   __\\____ \|  |<   |  |
\  \__(  <_> )   |  \  |  |  |_> >  |_\___  |
 \___  >____/|___|  /__|  |   __/|____/ ____|
     \/           \/      |__|        \/     
""")
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
                    log.success("loaded config: "+path)
                except:
                    log.error("failed to exec: "+path)
                    log.normal(sys.exc_info())
        else:
            log.error("couldn't load: "+path)
    
    def run(self):
        old_working_dir = os.getcwd()
        os.chdir(os.path.dirname(self.file_path))
        try:
            exec("%s.run(self.config)" % (self.config["cmd_type"]))
            # if self.config["cmd_type"] == "cpp_compiler":
            #     cpp_compiler.run(self.config)
        except:
            log.error("failed to run config: ")
            log.normal(sys.exc_info())
        os.chdir(old_working_dir)

    def print_config(self):
        base_config = {}
        confply_path = os.path.dirname(__file__) + "/"
        with open(confply_path+self.config["cmd_type"]+"/config.py", 'r') as config_file:
            exec(config_file.read(), {}, base_config)
        file_name = os.path.basename(self.file_path)
        log.normal(file_name+" configuration:")
        for k, v in self.config.items():
            if v is not None and k in base_config:
                if isinstance(v, list):
                    log.normal("\t"+str(k)+": ")
                    for i in v:
                        log.normal("\t\t"+str(i))
                else:
                    log.normal("\t"+str(k)+": "+str(v))
        print("")
