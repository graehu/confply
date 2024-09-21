#!/usr/bin/env python3
#                      _____       .__
#   ____  ____   _____/ ____\_____ |  | ___.__.
# _/ ___\/  _ \ /    \   __\\____ \|  |<   |  |
# \  \__(  <_> )   |  \  |  |  |_> >  |_\___  |
#  \___  >____/|___|  /__|  |   __/|____/ ____|
#      \/           \/      |__|        \/
# launcher generated using:
# 
# python ./confply.py --launcher build.py

import sys
import os
sys.path.append(os.path.abspath("."))
from confply import launcher
from confply import run_commandline

# fill this with your commands
aliases = {
    # 'default': '--in path/to/command.py'
    "g++": "--config.confply.tool g++ --in examples/cpp_compiler.cpp.py --cpp_clean",
    "gcc": "--config.confply.tool gcc --in examples/cpp_compiler.cpp.py --cpp_clean",
    "clang": "--config.confply.tool clang --in examples/cpp_compiler.cpp.py --cpp_clean",
    "clang++": "--config.confply.tool clang++ --in examples/cpp_compiler.cpp.py --cpp_clean",
    "emcc": "--config.confply.tool emcc --in examples/cpp_compiler.cpp.py --cpp_clean",
    "em++": "--config.confply.tool em++ --in examples/cpp_compiler.cpp.py --cpp_clean",
    "cl": "--config.confply.tool cl --in examples/cpp_compiler.cpp.py --cpp_clean",
    "echo": "--config.confply.tool echo --in examples/cpp_compiler.cpp.py --cpp_clean"
}
# "all" will run all of the aliases
aliases["all"] = " -- ".join([val for key, val in aliases.items()])

if __name__ == "__main__":
    args = sys.argv[1:]
    if "--listen" in args:
        run_commandline(["--listen", __file__])
    else:
        dir_name = os.path.dirname(__file__)
        if not dir_name == "":
            os.chdir(dir_name)
        if args:
            launcher(sys.argv[1:], aliases)
        else:
            launcher(["default"], aliases)
