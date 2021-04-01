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
config.confply.log_file = "confply.log"
mail_login = None
slack_bot = None
if os.path.exists("mail_details.py"):
    with open("mail_details.py") as details_file:
        mail_login = ast.literal_eval(details_file.read())
if os.path.exists("slack_details.py"):
    with open("slack_details.py") as details_file:
        slack_bot = ast.literal_eval(details_file.read())
config.confply.__mail_login = mail_login
config.confply.__slack_bot_token = slack_bot
