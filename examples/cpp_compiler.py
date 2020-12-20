#!../confply.py
# generated using:
# python ../confply.py --config cpp_compiler compile_cpp.py
import sys
import os
sys.path.append('..')
import confply.cpp_compiler.config as confply
import confply.log as log
confply.confply_log_topic = "cpp_compiler"
log.normal("loading cpp_compiler with confply_args: "+str(confply.confply_args))

debug = False
if "debug" in confply.confply_args:
    debug = True
    confply.object_path = "objects/debug"
    log.normal("set to debug config")

# default tool is clang++
confply.confply_tool = "clang++"

if "-clean" in confply.confply_args:
    if os.path.exists(confply.object_path):
        log.normal("cleaning compiled objects")
        os.system("rm -r "+confply.object_path)
    else:
        log.normal("no objects to remove")
        
if "-tool" in confply.confply_args:
    tool_index = confply.confply_args.index("-tool") + 1
    if tool_index < len(confply.confply_args):
        confply.confply_tool = confply.confply_args[tool_index]
        log.normal("setting tool to "+confply.confply_tool)


confply.source_files = ["main.cpp"]
confply.output_file = "hello_confply"
if confply.confply_tool != "cl":
    confply.link_libraries = ["stdc++"]
confply.debug_info = debug
confply.standard = "c++17"
confply.warnings = ["all"]
confply.confply_log_config = True
# confply.confply_log_file = "log.txt"
