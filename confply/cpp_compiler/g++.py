import confply.cpp_compiler.common as common

def generate(config):
    common.tool = "g++"
    return common.generate(config)
