from colored import fore, back, style


def format_dict(xdict):
    fmt = ", ".join(f"{fore.MAGENTA_3A}{k}{style.RESET}: {v}" for k, v in xdict.items())
    return "{" + fmt + "}"


def format_caller(*names):
    fmt_name = ":".join([name for name in names])
    fmt = f"{fore.MAGENTA_3A}{fmt_name}{style.RESET}"
    return fmt


def format_idn(idn):
    fmt = f"{fore.LIGHT_BLUE}{style.BOLD}{idn}{style.RESET}"
    return fmt
