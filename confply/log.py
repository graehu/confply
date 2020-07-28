import os
import confply.config

# Logging module to keep logs consistent in confply.
# todo: add formatted() for a formatted log function

class format:
    HEADER = lambda: '\033[95m' if confply.config.confply_log_file == None else ""
    OKBLUE = lambda: '\033[94m' if confply.config.confply_log_file == None else ""
    OKGREEN = lambda: '\033[92m' if confply.config.confply_log_file == None else ""
    WARNING = lambda: '\033[93m' if confply.config.confply_log_file == None else ""
    FAIL = lambda: '\033[91m' if confply.config.confply_log_file == None else ""
    ENDC = lambda: '\033[0m' if confply.config.confply_log_file == None else ""
    BOLD = lambda: '\033[1m' if confply.config.confply_log_file == None else ""
    UNDERLINE = lambda: '\033[4m' if confply.config.confply_log_file == None else ""

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
    print(topic+format.BOLD()+in_string+format.ENDC())

def underline(in_string):
    topic = get_log_topic()
    print(topic+format.UNDERLINE()+in_string+format.ENDC())

def header(in_string):
    topic = get_log_topic()
    half_size = int(((os.get_terminal_size().columns)/2))
    in_string = " "+in_string+" "
    # magic number -2 makes logs look better in terminal editors
    # todo: break this line down
    print(topic+break_str[int(len(in_string)/2+len(topic)):half_size]+format.HEADER()+in_string+format.ENDC()+break_str[:half_size-2-int(len(in_string)/2)])
    
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
    print(topic+format.FAIL()+in_string+format.ENDC())

def warning(in_string):
    topic = get_log_topic()
    print(topic+format.WARNING()+in_string+format.ENDC())

def success(in_string):
    topic = get_log_topic()
    print(topic+format.OKGREEN()+in_string+format.ENDC())
