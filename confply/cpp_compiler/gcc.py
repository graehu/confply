import confply.cpp_compiler.common as common

def generate():
    common.tool = "gcc"
    return common.generate()


def get_environ():
    return common.get_environ()


def is_found():
    return common.is_found()
