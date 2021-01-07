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


confply.source_files = ["main.cpp"]
confply.output_file = "hello_confply"
confply.link_libraries = ["stdc++"]
confply.debug_info = debug
confply.standard = "c++17"
confply.warnings = ["all"]
confply.confply_log_config = True
# confply.confply_log_file = "log.txt"
