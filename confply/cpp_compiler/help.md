# cpp_compiler config

all the configs and their usage.
#todo: add the relevant information about specific tools etc.

## environment_vars
used to add things to system environment variables.
usage: environment = { "PATH" : "c:/bin/dir/", "etc" : "c:/etc/" }

## defines
used to set preprocessor defines
usage: defines = ["MY_DEFINE=1", "MY_OTHER_DEF"]

## source_files
source files to compile
usage: source_files = ["main.cpp", "etc.cpp"]

## include_paths
include directorie paths, searched by compilers
usage: include_paths = ["c:/path/to/include/files/", "etc."]

## library_paths
library directory paths, searched by compilers (linkers)
usage: library_paths = ["c:/path/to/library/dir/", "etc."]

## link_libraries
link flags passed to the linker by the compiler e.g. -lopengl for opengl
usage: ["opengl", "etc."]

## debug_info
causes debug info to be generated, like -g in clang
usage: debug_info = True

## optimisation
sets the optimisation level of the generated binary
usage: optimisation = 0

## standard
sets c++ standard
usage: cpp_standard=17

## warnings
enables warnings
usage: warnings=["all", "etc"]

## build_objects
enables building object files used for building incrementally
usage: build_objects = True

## object_path
objects will be built to the provided path
usage: object_path = "objects/debug/"

## track_dependencies
enables dependency tracking
usage: track_dependencies = True

## track_checksums
enables checksums generation and tracking
usage: track_checksums = True

## rebuild_on_change
if set, all objects will be reblt when configs change
usage: rebuild_on_change = True

## output_executable
if true, an executable will be nerated.
usage: output_executable = True

## output_file
the final result of the build. Buds executables by default.
usage: output_file = "my_app.bin"

## command_append
appends to the end of the command
usage: command_append = "-something-unsupported"

## command_prepend

prepend to the start of the command
usage: command_prepend_with = "-something-unsupported"
