import confply.config as confply
confply.__tool_type = "cpp_compiler"
confply.__imported_configs.append("cpp_compiler")
# used to add things to system environment variables.
# usage: environment = { "PATH" : "c:/bin/dir/", "etc" : "c:/etc/" }
environment_vars = {}

# used to set preprocessor defines
# usage: defines = ["MY_DEFINE=1", "MY_OTHER_DEF"]
defines = []

# source files to compile
# usage: source_files = ["main.cpp", "etc.cpp"]
source_files = []

# include directorie paths, searched by compilers
# usage: include_paths = ["c:/path/to/include/files/", "etc."]
include_paths = []

# library directory paths, searched by compilers (linkers)
# usage: library_paths = ["c:/path/to/library/dir/", "etc."]
library_paths = []

# link flags passed to the linker by the compiler e.g. -lopengl for opengl
# usage: ["opengl", "etc."]
link_libraries = []

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
build_objects = True

# objects will be built to the provided path
# usage: object_path = "objects/debug/"
object_path = "objects/"

# enables dependency tracking
# usage: track_dependencies = True
track_dependencies = True

# enables checksums generation and tracking
# track_checksums = True
track_checksums = True

# if set, all objects will be rebuilt when configs change
# usage: rebuild_on_change = True
rebuild_on_change = True

# if true, an executable will be generated.
# usage: output_executable = True
output_executable = True

# the final result of the build. Builds executables by default.
# usage: output_file = "my_app.bin"
output_file = None

# appends to the end of the command
# usage: command_append = "-something-unsupported"
command_append = ""

# prepend to the start of the command
# usage: command_prepend_with = "-something-unsupported"
command_prepend = ""


# delete all object files before run
# usage: clean = True
clean = False
