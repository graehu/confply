#!../confply.py
from confply.cpp_compiler.config import *

compiler = "clang"
source_files = ["main.cpp"]
output_file = "hello_confply"
link_libraries = ["stdc++"]
debug_info = True
cpp_standard = 17
warnings = ["all"]
