#!../confply.py
# generated using:
# python ../confply.py --config cpp_compiler compile_cpp.py
from confply.cpp_compiler.config import *
def log(in_str):
    print("[cpp_compiler conf] "+in_str)
log("confply_args: "+str(confply_args))

debug = False
if "debug" in confply_args:
    debug = True
    log("running debug")


confply_tool = "clang"
source_files = ["main.cpp"]
output_file = "hello_confply"
link_libraries = ["stdc++"]
debug_info = debug
standard = "c++17"
warnings = ["all"]
confply_log_config = True
confply_log_topic = output_file
# confply_log_file = "log.txt"
