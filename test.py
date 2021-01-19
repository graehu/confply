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

# set current working directory and add confply to path
# so we can import the launcher function
dir_name = os.path.dirname(__file__)
if not dir_name == "":
    os.chdir(dir_name)
sys.path.append(".")
from confply import launcher

# fill this with your commands
aliases = {
    #'mycommand':'path/to/command.py'
    "cl" : "--config.confply.tool cl examples/cpp_compiler.py --cpp_clean",
    "g++" : "--config.confply.tool g++ examples/cpp_compiler.py --cpp_clean",
    "gcc" : "--config.confply.tool gcc  examples/cpp_compiler.py --cpp_clean",
    "clang" : "--config.confply.tool clang  examples/cpp_compiler.py --cpp_clean",
    "clang++" : "--config.confply.tool clang++  examples/cpp_compiler.py --cpp_clean"
}


if __name__ == "__main__":
    # "all" will run all of the aliases
    aliases["all"] = " -- ".join([val for key, val in aliases.items()])
    # aliases["cpp_compiler"] = " -- ".join([val for key, val in aliases.items() if "cpp_compiler" in val])
    launcher(sys.argv[1:], aliases)
