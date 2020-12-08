import confply.cpp_compiler.common as common

def generate(config):
    common.tool = "clang"
    return common.generate(config)
