# Confply #

Confply lets you write config files that can be shared between multiple commandline tools with similar functionality. The config files are written in python and executed when confply loads them. This allows them to be dynamically populated. Essentially, confply translates config files into tool appropriate shell commands.

For now compilers are the focus, but you can add another tool type like so:
> `./confply.py --new_tool_type my_tool_type`

That will add the following files:

* /confply/my_tool_type/**help.md**
* /confply/my_tool_type/**__init__.py**
* /confply/my_tool_type/**config/__init__.py**
* /confply/my_tool_type/**options/__init__.py**

**help.md** is printed when users invoke config specific help, like so:
> `./confply.py --help.my_tool_type`

**__init__.py** is where all of the shared code goes. <br>
**config/__init__.py** is where you store all of the tool settings. <br>
**options/__init__.py** is where config options go, store valid values here.

Now you add a file to that folder for every tool you want to configure. (e.g. g++.py, clang++.py, cl.py) <br>
Look at /confply/cpp_compiler/ as an example you can copy.

For further information on confply commandline options, take a look at [help.md](https://github.com/graehu/confply/blob/master/help.md)

## Examples
![Linux Examples](https://github.com/graehu/confply/workflows/Linux%20Examples/badge.svg)
![Windows Examples](https://github.com/graehu/confply/workflows/Windows%20Examples/badge.svg)

You can view the above tests in the [actions](https://github.com/graehu/confply/actions) tab of github. The .yml responsible for running the tests is here: 

> https://github.com/graehu/confply/tree/master/.github/workflows

Below are the config files that are run and their outputs.

### Cpp_compiler

#### Main Config
##### examples/compile_cpp.cpp.py
``` python
#!../confply.py
# generated using:
# python ../confply.py --config cpp_compiler cpp_compiler.cpp.py
import sys
sys.path.append('..')
import confply.cpp_compiler.config as config
import confply.cpp_compiler.options as options
import confply.log as log
############# modify_below ################

config.confply.log_topic = "cpp_compiler"
log.normal("loading cpp_compiler with confply_args: "+str(config.confply.args))

config.source_files = ["main.cpp"]
config.output_file = "hello_confply"
config.link_libraries = ["stdc++"]
config.standard = options.standards.cpp17
config.warnings = options.warnings.all_warnings
config.confply.log_config = True
```
#### Group Config
##### confply.cpp.py
``` python
#!./confply.py
# generated using:
# python confply.py --config cpp_compiler confply.cpp.py
import sys
sys.path.append('.')
import confply.cpp_compiler.config as config
import confply.cpp_compiler.options as options
import confply.log as log
############# modify_below ################
# set the default compiler
config.confply.tool = options.tools.clangpp

# set debug_info from commandline args
debug = False
if "debug" in config.confply.args:
    debug = True
    config.object_path = "objects/debug"
    log.normal("set to debug config")

config.debug_info = debug
```
#### Output

``` log
                     _____       .__         
  ____  ____   _____/ ____\_____ |  | ___.__.
_/ ___\/  _ \ /    \   __\\____ \|  |<   |  |
\  \__(  <_> )   |  \  |  |  |_> >  |_\___  |
 \___  >____/|___|  /__|  |   __/|____/ ____|
     \/           \/      |__|        \/     

[confply] ================================================================
[confply] python(3, 8, 6)
[confply] called with args: ['./cpp_compiler.cpp.py']
[confply] ================================================================
[confply] =========================  run config  =========================
[confply] ================================================================
[confply] ================================================================
[confply] loaded: /home/graehu/Projects/C++/framework/tools/confply/confply.cpp.py
[cpp_compiler] loading cpp_compiler with confply_args: []
[cpp_compiler] ================================================================
[cpp_compiler] loaded: ./cpp_compiler.cpp.py
[cpp_compiler] running post load script: __cpp_post_load
[cpp_compiler] cpp_compiler.cpp.py configuration:
[cpp_compiler] {
[cpp_compiler] 	confply.tool: clang++
[cpp_compiler] 	confply.log_topic: cpp_compiler
[cpp_compiler] 	confply.log_config: True
[cpp_compiler] 	confply.post_load: __cpp_post_load
[cpp_compiler] 	confply.platform: linux
[cpp_compiler] 	confply.git_root: /home/graehu/Projects/C++/framework/tools/confply
[cpp_compiler] 	source_files: 
[cpp_compiler] 		main.cpp
[cpp_compiler] 	link_libraries: 
[cpp_compiler] 		stdc++
[cpp_compiler] 	debug_info: False
[cpp_compiler] 	standard: c++17
[cpp_compiler] 	warnings: 
[cpp_compiler] 		all
[cpp_compiler] 		pedantic
[cpp_compiler] 		extra
[cpp_compiler] 	output_file: hello_confply
[cpp_compiler] }
[cpp_compiler] 
[cpp_compiler] 2 files to compile
[cpp_compiler] final commands:

clang++  -std=c++17 -Wall -Wpedantic -Wextra -c main.cpp -o objects/main.cpp.o  -MMD -MF objects/main.cpp.d  
clang++  -std=c++17 -Wall -Wpedantic -Wextra objects/main.cpp.o -o hello_confply  -l stdc++  

[cpp_compiler] =======================  begin clang++  ========================
[cpp_compiler] ================================================================
[cpp_compiler] clang++  -std=c++17 -Wall -Wpedantic -Wextra -c main.cpp -o objects/main.cpp.o  -MMD -MF objects/main.cpp.d  
[cpp_compiler] 
[cpp_compiler] ================================================================
[cpp_compiler] clang++ succeeded!
[cpp_compiler] time elapsed: 00:00:00.46
[cpp_compiler] ================================================================
[cpp_compiler] clang++  -std=c++17 -Wall -Wpedantic -Wextra objects/main.cpp.o -o hello_confply  -l stdc++  
[cpp_compiler] 
[cpp_compiler] ================================================================
[cpp_compiler] clang++ succeeded!
[cpp_compiler] time elapsed: 00:00:00.08
[cpp_compiler] total time elapsed: 00:00:00.55
[confply] ================================================================

```
### Supported Compilers

* cl.py
* clang++.py
* clang.py
* em++.py
* emcc.py
* g++.py
* gcc.py

**Not fit for human consumption**
