from colorama import Back, Fore, Style
from colorama import init as initiate_colorama


class CLIText:
    def __init__(self):
        # We initiate colorama
        initiate_colorama(autoreset=True)

        self.background_colors = Back
        self.foreground_colors = Fore
        self.styles = Style
