# Header used at the top of log files and such
# usage: confply_header = "(>'')><('')><(''<)"
confply_header = """
                     _____       .__         
  ____  ____   _____/ ____\_____ |  | ___.__.
_/ ___\/  _ \ /    \   __\\____ \|  |<   |  |
\  \__(  <_> )   |  \  |  |  |_> >  |_\___  |
 \___  >____/|___|  /__|  |   __/|____/ ____|
     \/           \/      |__|        \/     
"""

# do not set by hand! Is set in confply type config files
confply_command = None

# sets the desired tool to be used for the command.
# usage: confply_tool = "clang"
confply_tool = None

# sets the topic of the log, e.g. [confply] confguring commands.
# usage: confply_log_topic = "my command"
confply_log_topic = "confply"

# if true, confply will log it's config.
# default behaviour is as if true.
# usage: confply_log_config = False
confply_log_config = None

# if set, confply will save it's output to the file
# default behaviour is as if unset, no logs created.
# usage: confply_log_file = "../logs/my_command.log"
confply_log_file = None
