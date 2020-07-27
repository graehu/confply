import confply.cpp_compiler.clang as clang
import confply.log as log
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
        if os.system(command) == 0:
            log.linebreak()
            log.success("build success!")
        else:
            log.linebreak()
            log.error("build failed.")
    else:
        log.error("no valid compiler found.")

