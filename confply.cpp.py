#!./confply.py
# generated using:
# python confply.py --config cpp_compiler confply.cpp.py
import sys
sys.path.append('.')
import confply.cpp_compiler.config as config
import confply.cpp_compiler.options as options
import confply.log as log
############# modify_below ################
# set the default compiler
config.confply.tool = options.tools.clangpp

# set debug_info from commandline args
debug = False
if "debug" in config.confply.args:
    debug = True
    config.object_path = "objects/debug"
    log.normal("set to debug config")

config.debug_info = debug
