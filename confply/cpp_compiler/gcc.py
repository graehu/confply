import confply.cpp_compiler.common as common

def generate(config):
    common.tool = "gcc"
    return common.generate(config)


def get_environ(config):
    return common.get_environ(config)


def is_found(config):
    return common.is_found("gcc")
