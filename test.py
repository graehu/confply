#!/usr/bin/env python
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
sys.path.append(".")
from confply import launcher

# fill this with your commands
aliases = {
    # 'mycommand':'path/to/command.py'
    "g++": "--config.confply.tool g++ examples/cpp_compiler.cpp.py --cpp_clean",
    "gcc": "--config.confply.tool gcc examples/cpp_compiler.cpp.py --cpp_clean",
    "clang": "--config.confply.tool clang examples/cpp_compiler.cpp.py --cpp_clean",
    "clang++": "--config.confply.tool clang++ examples/cpp_compiler.cpp.py --cpp_clean",
    "emcc": "--config.confply.tool emcc examples/cpp_compiler.cpp.py --cpp_clean",
    "em++": "--config.confply.tool em++ examples/cpp_compiler.cpp.py --cpp_clean",
    "cl": "--config.confply.tool cl examples/cpp_compiler.cpp.py --cpp_clean",
    "echo": "--config.confply.tool echo examples/cpp_compiler.cpp.py --cpp_clean"
}
# "all" will run all of the aliases
aliases["all"] = " -- ".join([val for key, val in aliases.items()])

if __name__ == "__main__":
    dir_name = os.path.dirname(__file__)
    if not dir_name == "":
        os.chdir(dir_name)
    launcher(sys.argv[1:], aliases)
