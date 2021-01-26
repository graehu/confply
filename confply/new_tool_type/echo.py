import confply.{tool_type} as {tool_type}

tool_name = {tool_type}.os.path.basename(__file__)[:-3]

def generate():
    {tool_type}.tool = tool_name
    return {tool_type}.generate()


def get_environ():
    return {tool_type}.get_environ()


def is_found():
    return {tool_type}.is_found(tool_name)
