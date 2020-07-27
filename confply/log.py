import os

# Logging module to keep logs consistent in confply.
# todo: add formatted() for a formatted log function

class format:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

name = "[confply] "
break_char = '='
break_str = ""
for x in range(0, 256): break_str += break_char

def linebreak():
    terminal_size = os.get_terminal_size().columns
    print(name+break_str[len(name):terminal_size])


def bold(in_string):
    print(name+format.BOLD+in_string+format.ENDC)
    pass

def underline(in_string):
    print(name+format.UNDERLINE+in_string+format.ENDC)
    pass

def header(in_string):
    half_size = int(os.get_terminal_size().columns/2)
    in_string = " "+in_string+" "
    linebreak()
    print(name+break_str[len(in_string+name):half_size]+format.HEADER+in_string+format.ENDC+break_str[:half_size])
    linebreak()
    pass

def normal(in_string):
    print(name+in_string)

def error(in_string):
    print(name+format.FAIL+in_string+format.ENDC)

def warning(in_string):
    print(name+format.WARNING+in_string+format.ENDC)

def success(in_string):
    print(name+format.OKGREEN+in_string+format.ENDC)
