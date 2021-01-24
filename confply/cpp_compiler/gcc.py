import confply.cpp_compiler.common as common

tool_name = common.os.path.basename(__file__)[:-3]

def generate():
    common.tool = tool_name
    return common.generate()


def get_environ():
    return common.get_environ()


def is_found():
    return common.is_found(tool_name)
