# fill this with common implementation details.
import confply.log as log
import confply.{config_type}.config as config
import confply.{config_type}.options as options
import os
import shutil

tool = None

# return if the current config is valid
def validate():
    return True;


# return the final command string or an array of commands
def generate():
    return [tool, "no tool specific implementation"]


# return a dictionary of environment variables
def get_environ():
    return os.environ


# performs any actions invoked by specific commandline args
def handle_args():
    pass


# return if tool is found or not. (i.e. installed and on path)
def is_found(in_tool=None):
    if in_tool is None:
        if config.confply.tool is not None:
            return not shutil.which(config.confply.tool) is None
    else:
        return not shutil.which(in_tool) is None
    return False
