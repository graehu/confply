import confply.cpp_compiler as cpp_compiler

fallbacks = ["cl", "clang++",  "g++", "gcc", "clang"]
tool_name = None

for tool in fallbacks:
    if cpp_compiler.is_found(tool):
        tool_name = tool
        break


def validate():
    return cpp_compiler.validate()


def generate():
    cpp_compiler.tool = tool_name
    return cpp_compiler.generate()


def get_environ():
    return cpp_compiler.get_environ()


def handle_args():
    cpp_compiler.handle_args()


def is_found():
    return bool(tool_name)
