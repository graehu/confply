import sys
sys.path.append(".")
import confply.cpp_compiler.config as config
import confply.cpp_compiler.options as options

# set the default compiler
config.confply.tool = options.tools.clangpp
