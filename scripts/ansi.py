# ANSI lambda colo(u)r magic
def color(code, text):
    return f"\033[{code}m{text}\033[0m"

GREEN   = lambda t: color("1;32", t)
BLUE    = lambda t: color("1;34", t)
YELLOW  = lambda t: color("1;33", t)
CYAN    = lambda t: color("1;36", t)
RED     = lambda t: color("1;31", t)
MAGENTA = lambda t: color("1;35", t)
GRAY    = lambda t: color("0;37", t)
D_GRAY   = lambda t: color("0;90", t)

# colo(u)r inhibitors, you can keep those commented out or actually use them if you care about consistency.

# primary
#def T1(text):
#    return YELLOW(text)

# secondary
#def T2(text):
#    return BLUE(text)

