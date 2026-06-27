import os
import sys

#ANSI lambda colo(u)r magic
def supports_ansi() -> bool:
    if os.getenv("NO_COLOR") is not None:
        return False

    if not sys.stdout.isatty():
        return False

    if os.name == "nt":
        return (
            os.getenv("WT_SESSION") is not None or
            os.getenv("TERM_PROGRAM") == "vscode"
        )

    return os.getenv("TERM", "") not in ("", "dumb")

USE_COLOUR = supports_ansi()




def colour(code: str, text: str) -> str:
    if not USE_COLOUR:
        return text
    return f"\033[{code}m{text}\033[0m"

GREEN   = lambda t: colour("1;32", t)
BLUE    = lambda t: colour("1;34", t)
YELLOW  = lambda t: colour("1;33", t)
CYAN    = lambda t: colour("1;36", t)
RED     = lambda t: colour("1;31", t)
MAGENTA = lambda t: colour("1;35", t)
GRAY    = lambda t: colour("0;37", t)
D_GRAY  = lambda t: colour("0;90", t)
