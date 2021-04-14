import confply.{tool_type} as {tool_type}

tool_name = "echo"


def generate():
    {tool_type}.tool = tool_name
    return {tool_type}.generate()


def get_environ():
    return {tool_type}.get_environ()


def handle_args():
    {tool_type}.handle_args()
    pass


def is_found():
    return {tool_type}.is_found(tool_name)
