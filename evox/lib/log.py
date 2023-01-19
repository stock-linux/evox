import colorama

def log_info(msg):
    print(colorama.Fore.CYAN + colorama.Style.BRIGHT + "[I] " + colorama.Style.NORMAL + msg + colorama.Fore.RESET)

def log_warn(msg):
    print(colorama.Fore.YELLOW + colorama.Style.BRIGHT + "[W] " + colorama.Style.NORMAL + msg + colorama.Fore.RESET)

def log_error(msg):
    print(colorama.Fore.RED + colorama.Style.BRIGHT + "[E] " + colorama.Style.NORMAL + msg + colorama.Fore.RESET)

def log_success(msg):
    print(colorama.Fore.GREEN + colorama.Style.BRIGHT + "[S] " + colorama.Style.NORMAL + msg + colorama.Fore.RESET)

def log_ask(msg):
    # We need a simple Y/N input
    # We need to check if the input is valid
    answer = input(colorama.Fore.MAGENTA + colorama.Style.BRIGHT + "[?] " + colorama.Style.NORMAL + msg + colorama.Fore.RESET + " [Y/n] ")
    if answer.lower() == "y":
        return True
    elif answer.lower() == "n":
        return False
    else:
        log_error("Invalid input!")
        return log_ask(msg)
