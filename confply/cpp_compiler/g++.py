import confply.cpp_compiler as cpp_compiler

tool_name = cpp_compiler.os.path.basename(__file__)[:-3]


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
    return cpp_compiler.is_found(tool_name)
