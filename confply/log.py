import os
import re
import confply.config

# Logging module to keep logs consistent in confply.
# #todo: add formatted() for a formatted log function
# #todo: fix formating inside of log files

try:
    terminal_test = os.get_terminal_size()
    valid_ioctl = True
except:
    valid_ioctl = False

def can_format():
    return confply.config.log_file == None and valid_ioctl

class format:
    header = lambda x: '\033[95m'+x+'\033[0m' if can_format() else x
    ok_blue = lambda x: '\033[94m'+x+'\033[0m' if can_format() else x
    ok_green = lambda x: '\033[92m'+x+'\033[0m' if can_format() else x
    warning = lambda x: '\033[93m'+x+'\033[0m' if can_format() else x
    error = lambda x: '\033[91m'+x+'\033[0m' if can_format() else x
    bold = lambda x: '\033[1m'+x+'\033[0m' if can_format() else x
    underline = lambda x: '\033[4m'+x+'\033[0m' if can_format() else x
    
def get_log_topic():
    return "[" + confply.config.log_topic + "] "

def confply_header():
    print(confply.config.header)

def linebreak(break_char = "="):
    topic = get_log_topic()
    # magic number -1 makes logs look better in terminal editors
    if can_format():
        terminal_size = os.get_terminal_size().columns - len(topic) -1
    else:
        terminal_size = 96
    print(topic+''.center(terminal_size, break_char ))
    
def bold(in_string):
    topic = get_log_topic()
    print(topic+format.bold(in_string))
    
def underline(in_string):
    topic = get_log_topic()
    print(topic+format.underline(in_string))
    
def header(in_string, break_char = "="):
    in_string = format.underline(" "+in_string+" ")
    centered(in_string, break_char)
    
def escape_ansi(line):
    ansi_escape =re.compile(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]')
    return ansi_escape.sub('', line)
    
def centered(in_string, fill_string = " "):
    topic = get_log_topic()
    ansi_delta = len(in_string) - len(escape_ansi(in_string))
    # magic number -1 makes logs look better in terminal editors
    if can_format():
        terminal_width = os.get_terminal_size().columns - len(topic) - 1 + ansi_delta
    else:
        terminal_width = 96
    in_string = (" "+in_string+" ").center(terminal_width, fill_string)
    print(topic+in_string)
    
def normal(in_string, end = "\n", flush=False):
    topic = get_log_topic()
    print(topic+in_string, end=end, flush=flush)
    
def error(in_string):
    topic = get_log_topic()
    print(topic+format.error(in_string))
    
def warning(in_string):
    topic = get_log_topic()
    print(topic+format.warning(in_string))
    
def success(in_string):
    topic = get_log_topic()
    print(topic+format.ok_green(in_string))
