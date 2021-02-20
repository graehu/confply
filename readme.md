Confply
----------

Essentially, confply translates config files into shell commands. The config files are written in python and executed when confply loads them. This allows them to be dynamically populated. The config files can be shared between multiple command-line tools with the same functionality. e.g. c++ compilers.

For now compilers are the focus, but confply is extendable.

## Key Features

### Python Configs

Write python to fill your config or branch in specific conditions. The python files are [exec][exec]'d to populate the tool_type/config prior to command generation and run.

[exec]: https://docs.python.org/3.8/library/functions.html#exec

### Auto completion

Because it's Python auto-completion works with minimal setup. The `config` and `options` imports make it easy to find your tools available features.

![](https://github.com/graehu/hosting/blob/main/screenshots/confply/auto-complete.png)

### Command-line 

Command-line output is designed to be instructional, making debugging simple. In non-fatal error cases, confply queries the user for input. Information on confply command-line options can be found here: [help.md][help]

![](https://github.com/graehu/hosting/blob/main/screenshots/confply/command-line.png)

[help]: https://github.com/graehu/confply/blob/master/help.md

### Lightweight Install

Confply uses pure python 3.8, there are no additional modules to install. It's designed to sit inside your repository, rather than being installed system wide. This makes it easier to control the version you use for your projects.

### Extendable

Confply allows you to create your own tool types, like so:
> `./confply.py --new_tool_type my_tool_type`

This adds the following files:

* /confply/my\_tool\_type/**help.md**
* /confply/my\_tool\_type/**\_\_init\_\_.py**
* /confply/my\_tool\_type/**config/\_\_init\_\_.py**
* /confply/my\_tool\_type/**options/\_\_init\_\_.py**

**help.md** is printed when users invoke config specific help, like so:
> `./confply.py --help.my_tool_type`

**\_\_init\_\_.py** is where all of the shared code goes. <br>
**config/\_\_init\_\_.py** is where you store all of the tool settings. <br>
**options/\_\_init\_\_.py** is where config options go, store valid values here.

Now you add a file to that folder for every tool you want to configure. (e.g. g++.py, clang++.py, cl.py) <br>
Look at `/confply/cpp_compiler/` as an example you can copy.

### Command-line Overrides

You can override any field within a config from the command-line using `--config.{field}`. It's very easy to modify the behaviour of your config externally. Here's an example:

``` bash
python confply.py --config.confply.tool g++ examples/cpp_compiler.cpp.py
python confply.py --config.confply.tool cl examples/cpp_compiler.cpp.py
```

Which generates:

``` bash
g++  -std=c++17 -Wall -Wpedantic -Wextra -c main.cpp -o objects/main.cpp.o  -MMD -MF objects/main.cpp.d
g++  -std=c++17 -Wall -Wpedantic -Wextra objects/main.cpp.o -o hello_confply  -l stdc++
```
``` bash
cl  -std:c++17 -Wall -c main.cpp -Foobjects/main.cpp.obj -EHsc  -sourceDependencies objects/main.cpp.d
cl  -std:c++17 -Wall objects/main.cpp.obj -Fehello_confply -link
```

### Config Dependencies

Setting `config.confply.dependencies` allows you to list configs that must be run prior to the current config's final commands.

### Config Groups

If you name your config `my_config.my_group.py` confply will search for `confply.my_group.py` in your parent directories. `confply.my_group.py` will be run first, allowing you to write a base configuration file that can be shared among any files in the same group. see `confply.cpp.py` and `examples/cpp_compiler.cpp.py` for an example of how you might use it.

### Config Arguments

Any arguments passed to confply after a config file will be added to `confply.config.args` allowing you to branch certain behaviours. Here's an example:

``` python
# set debug_info from command-line args
debug = False
if "debug" in config.confply.args:
    debug = True
    config.object_path = "objects/debug"
    log.normal("set to debug config")

config.debug_info = debug
```


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
