#!../confply.py test.py
from confply.cpp_compiler.config import *

compiler = "clang"
source_files = ["main.cpp"]
output_file = "hello_confply"
link_libraries = ["stdc++"]
debug_info = True
cpp_standard = 17
warnings = ["all"]
confply_log_config = True
confply_log_topic = output_file
# confply_log_file = "log.txt"
