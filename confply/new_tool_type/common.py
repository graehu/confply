# fill this with common implementation details.
import confply.log as log
import confply.{tool_type}.config as config
import shutil

# return the final command string or an array of commands
def generate():
    return "echo no tool specific implementation"

# return a dictionary of environment variables
def get_environ():
    return os.environ
    pass

# return if tool is found or not. (i.e. installed and on path)
def is_found():
    return not shutil.which(config.confply.tool) is None
    pass
