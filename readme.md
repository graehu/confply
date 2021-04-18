Confply
----------

Confply translates config files into shell commands. The config files are written in python and executed when confply loads them. This allows them to be dynamically populated. The config files can be shared between multiple command-line tools with the same functionality. e.g. c++ compilers.

For now compilers are the focus, but confply is extendable.

## Key Features

### Python Configs

Write python to fill your config or branch in specific conditions. The python files are [exec][exec]'d to populate the config_type/config prior to command generation and run.

[exec]: https://docs.python.org/3.8/library/functions.html#exec

### Auto completion

Because it's Python auto-completion works with minimal setup. The `config` and `options` imports make it easy to find your tools available features.

<details>
<summary>screenshot</summary>

![](https://github.com/graehu/hosting/blob/main/screenshots/confply/auto-complete.png)

</details>

### Command-line 

Command-line output is designed to be instructional, making debugging simple. In non-fatal error cases, confply queries the user for input. Information on confply command-line options can be found here: [help.md][help]

<details>
<summary>screenshot</summary>

![](https://github.com/graehu/hosting/blob/main/screenshots/confply/command-line.png)

</details>

[help]: https://github.com/graehu/confply/blob/master/help.md

### Lightweight Install

Confply uses pure python 3.8, there are no additional modules to install. It's designed to sit inside your repository, rather than being installed system wide. This makes it easier to control the version you use for your projects.

### Extendable

Confply allows you to create your own tools, like so:
> `./confply.py --new_tool my_tool`

This adds the following files:

* /confply/my\_tool/**help.md**
* /confply/my\_tool/**\_\_init\_\_.py**
* /confply/my\_tool/**config/\_\_init\_\_.py**
* /confply/my\_tool/**options/\_\_init\_\_.py**

**help.md** is printed when users invoke config specific help, like so:
> `./confply.py --help.my_tool`

**\_\_init\_\_.py** is where all of the shared code goes. <br>
**config/\_\_init\_\_.py** is where you store all of the tool settings. <br>
**options/\_\_init\_\_.py** is where config options go, store valid values here.

Now you add a file to that folder for every tool you want to configure. (e.g. g++.py, clang++.py, cl.py) <br>
Look at `/confply/cpp_compiler/` as an example you can copy.

### Command-line Overrides

You can override any field within a config from the command-line using `--config.{field}`. It's very easy to modify the behaviour of your config externally. Here's an example:

``` bash
python confply.py --config.confply.tool g++ --in examples/cpp_compiler.cpp.py
python confply.py --config.confply.tool cl --in examples/cpp_compiler.cpp.py
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

### Simple Server

With a combination of --launcher files and --listen you can run a simple server. The server will all of the aliases you define in your launcher.

``` shell
graehu@github:~/confply$ ./confply.py --launcher test.py
[confply] called with args: ['--launcher', 'test.py']
[confply] wrote: /home/graehu/confply/test.py
[confply] ===========================================================================================================================================

graehu@github:~/confply$ ./confply.py --listen test.py
[confply] called with args: ['--listen', 'test.py']
Server started http://0.0.0.0:8000

```

<details>
<summary>screenshot</summary>

![](https://github.com/graehu/hosting/blob/main/screenshots/confply/confply_listen.png)

</details>

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
#!../confply.py --in
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
config.standard = options.standard.cpp17
config.warnings = options.warnings.all_warnings
config.confply.log_config = True
def post_run():
    import subprocess
    import sys
    subprocess.run("./hello_confply",
                   stdout=sys.stdout,
                   stderr=subprocess.STDOUT,
                   shell=True)
    pass

config.confply.post_run = post_run

```
#### Group Config
##### confply.cpp.py
``` python
#!./confply.py --in
# generated using:
# python confply.py --config cpp_compiler confply.cpp.py
import sys
import ast
import os
sys.path.append('.')
import confply.cpp_compiler.config as config
import confply.cpp_compiler.options as options
import confply.log as log
############# modify_below ################
# set the default compiler
config.confply.tool = options.tool.clangpp

# set debug_info from commandline args
debug = False
if "debug" in config.confply.args:
    debug = True
    config.object_path = "objects/debug"
    log.normal("set to debug config")

config.debug_info = debug
config.confply.mail_to = "graehu@gmail.com"
config.confply.mail_from = "confply.dev@gmail.com"
config.confply.log_file = "confply.log"
mail_login = None
slack_bot = None
if os.path.exists("mail_details.py"):
    with open("mail_details.py") as details_file:
        mail_login = ast.literal_eval(details_file.read())
if os.path.exists("slack_details.py"):
    with open("slack_details.py") as details_file:
        slack_bot = ast.literal_eval(details_file.read())
config.confply.__mail_login = mail_login
config.confply.__slack_bot_token = slack_bot
config.confply.log_echo_file = True

```
#### Output

``` log
                     _____       .__
  ____  ____   _____/ ____\_____ |  | ___.__.
_/ ___\/  _ \ /    \   __\\____ \|  |<   |  |
\  \__(  <_> )   |  \  |  |  |_> >  |_\___  |
 \___  >____/|___|  /__|  |   __/|____/ ____|
     \/           \/      |__|        \/

[cpp_compiler] ================================================================================================
[cpp_compiler] python(3, 8, 6)
[cpp_compiler] ================================================================================================
[cpp_compiler] cpp_compiler.cpp.py configuration:
[cpp_compiler] {
[cpp_compiler] 	confply.tool: clang++
[cpp_compiler] 	confply.log_topic: cpp_compiler
[cpp_compiler] 	confply.log_config: True
[cpp_compiler] 	confply.log_file: confply.log
[cpp_compiler] 	confply.post_run: post_run
[cpp_compiler] 	confply.platform: linux
[cpp_compiler] 	confply.args: 
[cpp_compiler] 		--cpp_clean
[cpp_compiler] 	confply.vcs_root: /home/graehu/Projects/C++/framework/tools/confply
[cpp_compiler] 	confply.vcs_author: Graham Hughes
[cpp_compiler] 	confply.vcs_branch: master
[cpp_compiler] 	confply.mail_from: confply.dev@gmail.com
[cpp_compiler] 	confply.mail_to: graehu@gmail.com
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
[cpp_compiler] cleaning compiled objects
[cpp_compiler] 2 files to compile
[cpp_compiler] final commands:

clang++  -std=c++17 -Wall -Wpedantic -Wextra -c main.cpp -o objects/main.cpp.o  -MMD -MF objects/main.cpp.d  
clang++  -std=c++17 -Wall -Wpedantic -Wextra objects/main.cpp.o -o hello_confply  -l stdc++  

[cpp_compiler] =======================================  begin clang++  ========================================
[cpp_compiler] ================================================================================================
[cpp_compiler] clang++  -std=c++17 -Wall -Wpedantic -Wextra -c main.cpp -o objects/main.cpp.o  -MMD -MF objects/main.cpp.d  
[cpp_compiler] 
[cpp_compiler] ================================================================================================
[cpp_compiler] clang++ succeeded!
[cpp_compiler] time elapsed: 00:00:00.45
[cpp_compiler] ================================================================================================
[cpp_compiler] clang++  -std=c++17 -Wall -Wpedantic -Wextra objects/main.cpp.o -o hello_confply  -l stdc++  
[cpp_compiler] 
[cpp_compiler] ================================================================================================
[cpp_compiler] clang++ succeeded!
[cpp_compiler] time elapsed: 00:00:00.08
[cpp_compiler] total time elapsed: 00:00:00.54
[cpp_compiler] ================================================================================================
[cpp_compiler] running post run script: post_run

hello confply!
time wasting calculation result: 102334155
time wasted: 823844u(823.844ms)

[cpp_compiler] ================================================================================================
[cpp_compiler] ================================================================================================

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
