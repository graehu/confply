import confply.cpp_compiler.clang as clang


# todo: valid tools exist, have a dependency checker in clang.py, cl.py, gcc.py etc.
def generate(config):
    command = None
    if config["compiler"] is not None:
        if config["compiler"] == "clang":
            return clang.generate_command(config)

    return None

