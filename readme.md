# Confply #

The goal: One config file, one job, many tools & platforms.

If you've ever been frustraited by tools that do the same thing but have different interfaces, then you've come to the right place. The goal of confply is to make tools that do the same job, comply to one interface.

Confply is written in python and each of it's config files are just python files that are executed to fillout predefined arguements for a specific type of tool. E.g. a compiler.

For now compilers will be the focus, but scope for other tool types has been considered in the design.

## Examples/Compile_cpp.py Config  ##

``` python
#!../confply.py
# generated using:
# python ../confply.py --config cpp_compiler compile_cpp.py
import sys
sys.path.append('..')
import confply.cpp_compiler.config as confply
import confply.log as log
confply_log_topic = "compile_cpp.py"
log.normal("loading compile_cpp.py with confply_args: "+str(confply.confply_args))

debug = False
if "debug" in confply.confply_args:
    debug = True
    confply.object_path = "objects/debug"
    log.normal("set to debug config")


confply.confply_tool = "clang++"
confply.source_files = ["main.cpp"]
confply.output_file = "hello_confply"
confply.link_libraries = ["stdc++"]
confply.debug_info = debug
confply.standard = "c++17"
confply.warnings = ["all"]
confply.confply_log_config = True
# confply.confply_log_file = "log.txt"

```

The above config file is runnable, it runs with confply as the interpreter. As you can see this sets a lot of standard flags. It can be run `./compile_cpp.py`, which generates this:

`clang++ -std=c++17 -Wall main.cpp -o hello_confply -lstdc++`

or like this, `./compile_cpp.py debug` which generates:

`clang++ -g -std=c++17 -Wall main.cpp -o hello_confply -lstdc++`

But, if you set it's compiler to cl.exe it would update all of it's flags and setup the required MS environment for compliation. (that's the idea at least, not currently implemented)

The file was generated by running `python ../confply.py --config cpp_compiler compile_cpp.py` which'll give you the first 7 lines. The file is automatically runnable.

Confply currently supports:

* c++ compilers. (only clang++ on linux atm)
* nothing else because it's very early days.

## Reason this exists?  ##

I'm just getting tired of complicated build systems when I want to compile some files or add a build event and have it work crossplatform. Or just testing the results with a different compiler, etc.

## Todo  ##

- [ ] Add cl.exe to cpp_compilers
- [x] Add g++ to cpp_compilers
- [ ] Add more cpp_compiler options: optimisation, warnings_as_errors, etc.
- [x] Add cpp.o caching
- [ ] Add cpp checksum cache
- [ ] Add custom confply_custom_command
- [x] Add confply_tool verification (installed, on path, etc)
- [ ] Add ./confply -u "{config}" arg, currently only support .py files.
- [x] Add todo section to readme

**Not fit for human consumption**
