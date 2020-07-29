import os
import confply.config
from confply.config import confply_log_file

# Logging module to keep logs consistent in confply.
# todo: add formatted() for a formatted log function

class format:
    header = lambda x: '\033[95m'+x+'\033[0m' if confply_log_file == None else x
    ok_blue = lambda x: '\033[94m'+x+'\033[0m' if confply_log_file == None else x
    ok_green = lambda x: '\033[92m'+x+'\033[0m' if confply_log_file == None else x
    warning = lambda x: '\033[93m'+x+'\033[0m' if confply_log_file == None else x
    error = lambda x: '\033[91m'+x+'\033[0m' if confply_log_file == None else x
    bold = lambda x: '\033[1m'+x+'\033[0m' if confply_log_file == None else x
    underline = lambda: '\033[4m'+x+'\033[0m' if confply_log_file == None else x

def get_log_topic():
    return "[" + confply.config.confply_log_topic + "] "
break_char = '='
break_str = ""
space_str = ""

for x in range(0, 256): break_str += break_char
for x in range(0, 256): space_str += " "

def linebreak():
    topic = get_log_topic()
    # magic number -2 makes logs look better in terminal editors
    terminal_size = os.get_terminal_size().columns-2
    print(topic+break_str[len(topic):terminal_size])

def bold(in_string):
    topic = get_log_topic()
    print(topic+format.bold(in_string))

def underline(in_string):
    topic = get_log_topic()
    print(topic+format.UNDERLINE(in_string))

def header(in_string):
    topic = get_log_topic()
    half_size = int(((os.get_terminal_size().columns)/2))
    in_string = " "+in_string+" "
    # magic number -2 makes logs look better in terminal editors
    # todo: break this line down
    print(topic+break_str[int(len(in_string)/2+len(topic)):half_size]+format.header(in_string)+break_str[:half_size-2-int(len(in_string)/2)])
    
def centered(in_string):
    topic = get_log_topic()
    half_size = int(((os.get_terminal_size().columns)/2))
    in_string = " "+in_string+" "
    # magic number -2 makes logs look better in terminal editors
    # todo: break this line down
    print(topic+space_str[int(len(in_string)/2+len(topic)):half_size]+in_string+space_str[:half_size-2-int(len(in_string)/2)])

    
def normal(in_string):
    topic = get_log_topic()
    print(topic+in_string)

def error(in_string):
    topic = get_log_topic()
    print(topic+format.error(in_string))

def warning(in_string):
    topic = get_log_topic()
    print(topic+format.warning(in_string))

def success(in_string):
    topic = get_log_topic()
    print(topic+format.ok_green(in_string))
