# Confply #

Confply lets you write config files that can be shared between multiple commandline tools with similar functionality. The config files are written in python and executed when confply loads them. This allows them to be dynamically populated. Essentially, confply translates config files into tool appropriate shell commands.

For now compilers are the focus, but you can add another tool type like so:
> `./confply.py --new_tool_type my_tool_type`

That will add the following files:

* /confply/my_tool_type/**help.md**
* /confply/my_tool_type/**common.py**
* /confply/my_tool_type/**config.py**

**help.md** is printed when users invoke config specific help, like so:
> `./confply.py --help.my_tool_type`

**config.py** is where you store all of the tool settings. <br>
**common.py** is where all of the shared code goes.

Now you add a file to that folder for every tool you want to configure. (e.g. g++.py, clang++.py, cl.py) <br>
Look at /confply/cpp_compiler/ as an example you can copy.

For further information on confply commandline options, take a look at [help.md](https://github.com/graehu/confply/blob/master/help.md)

## Examples
![Linux Examples](https://github.com/graehu/confply/workflows/Linux%20Examples/badge.svg)
![Windows Examples](https://github.com/graehu/confply/workflows/Windows%20Examples/badge.svg)

You can view the above tests in the [actions](https://github.com/graehu/confply/actions) tab of github. The .yml responsible for running the tests is here: 

> https://github.com/graehu/confply/tree/master/.github/workflows

Below are the config files that are run and their outputs.

### Compile_cpp.py

#### Config
``` python
#!../confply.py
# generated using:
# python ../confply.py --config cpp_compiler compile_cpp.py
import sys
import os
sys.path.append('..')
import confply.cpp_compiler.config as config
import confply.log as log
config.confply.log_topic = "cpp_compiler"
log.normal("loading cpp_compiler with confply_args: "+str(config.confply.args))

debug = False
if "debug" in config.confply.args:
    debug = True
    config.object_path = "objects/debug"
    log.normal("set to debug config")

# default tool is clang++
config.confply.tool = "clang++"
config.source_files = ["main.cpp"]
config.output_file = "hello_confply"
config.link_libraries = ["stdc++"]
config.debug_info = debug
config.standard = "c++17"
config.warnings = ["all"]
config.confply.log_config = True
# config.confply.log_file = "log.txt"

```
#### Output

```log
                     _____       .__         
  ____  ____   _____/ ____\_____ |  | ___.__.
_/ ___\/  _ \ /    \   __\\____ \|  |<   |  |
\  \__(  <_> )   |  \  |  |  |_> >  |_\___  |
 \___  >____/|___|  /__|  |   __/|____/ ____|
     \/           \/      |__|        \/     

[confply] ================================================================
[confply] python(3, 8, 6)
[confply] called with args: ['--config.confply.tool', 'clang++', 'examples/cpp_compiler.py', '--cpp_clean']
[confply] config.confply.tool = "clang++" <str>
[confply] ================================================================
[confply] =========================  run config  =========================
[confply] ================================================================
[cpp_compiler] loading cpp_compiler with confply_args: ['--cpp_clean']
[cpp_compiler] ================================================================
[cpp_compiler] successfully loaded: examples/cpp_compiler.py
[cpp_compiler] running post load script: _cpp_post_load
[cpp_compiler] no objects to remove
[cpp_compiler] cpp_compiler.py configuration:
[cpp_compiler] {
[cpp_compiler] 	source_files: 
[cpp_compiler] 		main.cpp
[cpp_compiler] 	link_libraries: 
[cpp_compiler] 		stdc++
[cpp_compiler] 	-debug_info: False
[cpp_compiler] 	-standard: c++17
[cpp_compiler] 	warnings: 
[cpp_compiler] 		all
[cpp_compiler] 	-output_file: hello_confply
[cpp_compiler] }
[cpp_compiler] 
[cpp_compiler] 2 files to compile
[cpp_compiler] final commands:

clang++  -std=c++17 -Wall -c main.cpp -o objects/main.cpp.o  -MMD -MF objects/main.cpp.d  
clang++  -std=c++17 -Wall objects/main.cpp.o -o hello_confply  -l stdc++  

[cpp_compiler] =======================  begin clang++  ========================
[cpp_compiler] ================================================================
[cpp_compiler] clang++  -std=c++17 -Wall -c main.cpp -o objects/main.cpp.o  -MMD -MF objects/main.cpp.d  
[cpp_compiler] 
[cpp_compiler] ================================================================
[cpp_compiler] clang++ succeeded!
[cpp_compiler] time elapsed: 00:00:00.45
[cpp_compiler] ================================================================
[cpp_compiler] clang++  -std=c++17 -Wall objects/main.cpp.o -o hello_confply  -l stdc++  
[cpp_compiler] 
[cpp_compiler] ================================================================
[cpp_compiler] clang++ succeeded!
[cpp_compiler] time elapsed: 00:00:00.08
[cpp_compiler] total time elapsed: 00:00:00.54
[confply] ================================================================
[confply] ================================================================

```

**Not fit for human consumption**
