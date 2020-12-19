import confply.cpp_compiler.common as common

def generate(config):
    common.tool = "g++"
    return common.generate(config)


def get_environ(config):
    return common.get_environ(config)
