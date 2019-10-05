class Colors:
    BLUE = '\033[34m'
    CYAN = '\033[36m'
    GREEN = '\033[32m'
    GRAY = '\033[90m'
    ORANGE = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[00m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def neutral(string):
    return colorize(Colors.ENDC, string)

def green(string):
    return colorize(Colors.GREEN, string)

def red(string):
    return colorize(Colors.RED, string)

def orange(string):
    return colorize(Colors.ORANGE, string)

def blue(string):
    return colorize(Colors.BLUE, string)

def cyan(string):
    return colorize(Colors.CYAN, string)

def gray(string):
    return colorize(Colors.GRAY, string)

def colorize(color, string):
    return "{}{}{}".format(color, string, Colors.ENDC)
