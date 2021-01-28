# Header used at the top of log files and such
# usage: header = "(>'')><('')><(''<)"
header = r"""
                     _____       .__         
  ____  ____   _____/ ____\_____ |  | ___.__.
_/ ___\/  _ \ /    \   __\\____ \|  |<   |  |
\  \__(  <_> )   |  \  |  |  |_> >  |_\___  |
 \___  >____/|___|  /__|  |   __/|____/ ____|
     \/           \/      |__|        \/     
"""

# do not set by hand! Is set in confply type config files
__tool_type = None

# config elements overriden by the commandline
# usage: don't set this from configs see --config in help
__override_dict = {"confply":{}}

# config elements overriden by the commandline
# usage: don't set this from configs see --config in help
__override_list = []

# sets the desired tool to be used for the command.
# usage: tool = "clang"
tool = None

# sets the topic of the log, e.g. [confply] confguring commands.
# usage: log_topic = "my command"
log_topic = "confply"

# if true, confply will log it's config.
# default behaviour is as if true.
# usage: log_config = False
log_config = None

# if set, confply will save it's output to the file
# default behaviour is as if unset, no logs created.
# usage: log_file = "../logs/my_command.log"
log_file = None

# if set, confply will run the function after the command runs.
# usage: post_run = my_function
post_run = None

# if set, confply will run the function after the config loads.
# usage: post_load = my_function
post_load = None

# platform that the command is running on
# usage: if(platform == "linux"): pass
platform = "unknown"

# arguements that were passed to confply
# usage: if "debug" in args: pass
args = []


