#!../confply.py
# generated using:
# python ../confply.py --config cpp_compiler compile_cpp.py
import sys
sys.path.append('..')
import confply.cpp_compiler.config as confply
import confply.log as log
confply_log_topic = "compile_cpp.py"
log.normal("loading compile_cpp.py with confply_args: "+str(confply_args))

debug = False
if "debug" in confply_args:
    debug = True
    log.normal("set to debug config")


confply.confply_tool = "clang++"
confply.source_files = ["main.cpp"]
confply.output_file = "hello_confply"
confply.link_libraries = ["stdc++"]
confply.debug_info = debug
confply.standard = "c++17"
confply.warnings = ["all"]
confply.confply_log_config = True
# confply.confply_log_file = "log.txt"
