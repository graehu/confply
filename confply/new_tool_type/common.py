# fill this with common implementation details.
import confply.log as log
import confply.{tool_type}.config as config
import os
import shutil

tool = None

# return the final command string or an array of commands
def generate():
    return str(tool)+" no tool specific implementation"

# return a dictionary of environment variables
def get_environ():
    return os.environ

# return if tool is found or not. (i.e. installed and on path)
def is_found(in_tool=None):
    if in_tool == None:
        if config.confply.tool != None:
            return not shutil.which(config.confply.tool) is None
    else:
        return not shutil.which(in_tool) is None
    return False

