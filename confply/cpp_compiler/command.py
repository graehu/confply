import confply.config
import confply.cpp_compiler.clang as clang
import confply.log as log
import subprocess
import sys
import os


# todo: valid tools exist, have a dependency checker in clang.py, cl.py, gcc.py etc.
def run(config):
    command = None
    if config["compiler"] is not None:
        if config["compiler"] == "clang":
            command = clang.generate_command(config)

    if command is not None:
        log.success("final command:")
        log.normal(command)
        log.header("begin build")


        if confply.config.confply_log_file != None:
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, shell=True)

            old_topic = confply.config.confply_log_topic
            confply.config.confply_log_topic = config["compiler"]
            for line in result.stdout.splitlines():
                log.normal(line)
            confply.config.confply_log_topic = old_topic
            
        else:
            result = subprocess.run(command, shell=True)
            
        if result.returncode == 0:
            log.linebreak()
            log.success("build success!")
        else:
            log.linebreak()
            log.error("build failed.")
    else:
        log.error("no valid compiler found.")

