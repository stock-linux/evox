import colorama

COLOR_CYAN = colorama.Fore.CYAN
COLOR_YELLOW = colorama.Fore.YELLOW
COLOR_RED = colorama.Fore.RED
COLOR_GREEN = colorama.Fore.GREEN
COLOR_RESET = colorama.Fore.RESET
COLOR_MAGENTA = colorama.Fore.MAGENTA
STYLE_BRIGHT = colorama.Style.BRIGHT
STYLE_NORMAL = colorama.Style.NORMAL

def log_info(msg):
    print(f"{COLOR_CYAN}{STYLE_BRIGHT}[I]{STYLE_NORMAL} {msg}{COLOR_RESET}")

def log_warn(msg):
    print(f"{COLOR_YELLOW}{STYLE_BRIGHT}[W]{STYLE_NORMAL} {msg}{COLOR_RESET}")

def log_error(msg):
    print(f"{COLOR_RED}{STYLE_BRIGHT}[E]{STYLE_NORMAL} {msg}{COLOR_RESET}")

def log_success(msg):
    print(f"{COLOR_GREEN}{STYLE_BRIGHT}[S]{STYLE_NORMAL} {msg}{COLOR_RESET}")

def log_ask(msg):
    # We need a simple Y/N input
    # We need to check if the input is valid
    answer = input(f"{COLOR_MAGENTA}{STYLE_BRIGHT}[?]{STYLE_NORMAL} {msg}{COLOR_RESET} [Y/n] ")
    # We check if the answer is valid or not
    # The user can also press enter to accept the default value
    if answer.lower() == "y" or answer == "":
        return True
    elif answer.lower() == "n":
        return False
    else:
        log_error("Invalid input!")
        return log_ask(msg)
