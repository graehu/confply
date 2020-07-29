# Confply #

The goal: One config file, many commandline tools.

If you've ever been frustraited by tools that do the same thing but have different interfaces, then you've come to the right place. The goal of confply is to make tools that do the same job, comply to one interface.

Confply is written in python and each of it's config files are just python files that are executed to fillout predefined arguements for a specific type of tool. E.g. a compiler.

For now compilers will be the focus, but scope for other tool types has been considered in the design.

## Example Cpp Compiler Config  ##

``` python

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

```

The above config file is runnable, it will first try to run test.py with confply, then it will run itself with confply. As you can see this sets a lot of standard flags. It's final output would be:

`clang -g -std=c++17 -Wall main.cpp -lstdc++ -o hello_confply`

But, if you set it's compiler to cl.exe it would update all of it's flags and setup the required MS environment for compliation. (that's the idea at least, not currently implemented)

Confply currently supports:

* c++ compilers. (only clang on linux atm)
* nothing else because it's very early days.

## Reason this exists?  ##

I'm just getting tired of complicated build systems when I want to compile some files or add a build event and have it work crossplatform. Or just testing the results with a different compiler, etc.

**Not fit for human consumption**
