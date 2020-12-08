import confply.cpp_compiler.common as common

def generate(config):
    common.tool = "gcc"
    return common.generate(config)
