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

# the tool type to run with after loading the config
# usage: don't set this, it's set on config import
__tool_type = None

# the number of configs imported so far
# usage: don't set this, it's set on config import
__imported_configs = []

# config elements overriden by the commandline
# usage: don't set this from configs see --config in help
__override_dict = {"confply": {}}

# config elements overriden by the commandline
# usage: don't set this from configs see --config in help
__override_list = []

# sets the desired tool to be used for the command.
# usage: tool = "clang"
tool = None

# sets whether to run the resulting commands or not
# usage: run = True
run = True

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

# list of configs the current config depends on
# usage: dependencies = ["config.py"]
dependencies = []

# version control system
# usage: vcs = "git"
vcs = "git"

# path to the root of the vcs repository
# usage: log_file = vcs_root+"/logs/my_log.log"
vcs_root = "."

# author of latest submission/commit
# usage: log.normal(vcs_author)
vcs_author = "unknown"

# current branch
# usage: log.normal(vcs_branch)
vcs_branch = "unknown"

# latest submission/commit log
# usage: log.normal(vcs_log)
vcs_log = "unknown"

# mail server login details
# usage: mail_from = "confply@github.com"
mail_from = None

# send messages to email address
# usage: mail_to = "graehu@github.com"
mail_to = None

# mail server login details
# usage: mail_login = ("username", "password")
mail_login = None

# mail hosting server
# usage: mail_host = ""
mail_host = "smtp.gmail.com"

# file attachments for the mail
# usage: mail_attachments = ["path/to/attachment.txt"]
mail_attachments = []
