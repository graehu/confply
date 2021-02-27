#!./confply.py
# generated using:
# python confply.py --config cpp_compiler confply.cpp.py
import sys
import ast
import os
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
config.confply.mail_to = "graehu@gmail.com"
config.confply.mail_from = "confply.dev@gmail.com"
mail_login = None
if os.path.exists("details.py"):
    with open("details.py") as details_file:
        mail_login = ast.literal_eval(details_file.read())
config.confply.mail_login = mail_login
