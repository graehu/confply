#!../confply.py
# generated using:
# python ../confply.py --config cpp_compiler compile_cpp.py
import sys
import os
sys.path.append('..')
import confply.cpp_compiler.config as config
import confply.log as log
config.confply.log_topic = "cpp_compiler"
log.normal("loading cpp_compiler with confply_args: "+str(config.confply.args))

debug = False
if "debug" in config.confply.args:
    debug = True
    config.object_path = "objects/debug"
    log.normal("set to debug config")

# default tool is clang++
config.confply.tool = "clang++"
config.source_files = ["main.cpp"]
config.output_file = "hello_confply"
config.link_libraries = ["stdc++"]
config.debug_info = debug
config.standard = "c++17"
config.warnings = ["all"]
config.confply.log_config = True
# config.confply.log_file = "log.txt"

########### testing
# config.confply.header = "reeeee"
# config.confply.post_load = lambda: log.normal("hello! "+config.confply.tool)
# config.confply.post_run = lambda: print("hello! "+config.confply.tool)
