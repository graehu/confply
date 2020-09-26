from confply.config import *
confply_command = "cpp_compiler"

# used to add things to system environment variables.
# usage: environment = { "PATH" : "c:/bin/dir/", "etc" : "c:/etc/" }
environment_vars = None

# source files to compile
# usage: source_files = ["main.cpp", "etc.cpp"]
source_files = None

# include directorie paths, searched by compilers
# usage: include_paths = ["c:/path/to/include/files/", "etc."]
include_paths = None

# library directory paths, searched by compilers (linkers)
# usage: library_paths = ["c:/path/to/library/dir/", "etc."]
library_paths = None

# link flags passed to the linker by the compiler e.g. -lopengl for opengl
# usage: ["opengl", "etc."]
link_libraries = None

# causes debug info to be generated, like -g in clang
# usage: debug_info = True
debug_info = None

# sets the optimisation level of the generated binary
# usage: optimisation = 0
optimisation = None

# sets c++ standard
# usage: cpp_standard=17
standard = None

# enables warnings
# usage: warnings=["all", "etc"]
warnings = None

# enables building object files used for building incrementally
# usage: build_objects = True
build_objects = None

# the final result of the build. Builds executables by default.
# usage: output_file = "my_app.bin"
output_file = None
