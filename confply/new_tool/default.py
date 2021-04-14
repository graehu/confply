import confply.{config_type} as {config_type}

tool_name = "echo"


def generate():
    {config_type}.tool = tool_name
    return {config_type}.generate()


def get_environ():
    return {config_type}.get_environ()


def handle_args():
    {config_type}.handle_args()
    pass


def is_found():
    return {config_type}.is_found(tool_name)
