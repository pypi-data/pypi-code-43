from typing import TypeVar

from pyfiglet import Figlet
from pyfiglet import print_figlet

f = Figlet(font='starwars', width=20)
Mascot = TypeVar('Mascot')


def make_fun(app_name: str, ascii_picture: str, upper: bool = False) -> str:
    app_name = app_name.upper() if upper else app_name
    print("\033[033m", ascii_picture, "\033[0m")
    print_figlet(app_name, colors='YELLOW:RESET')
    return ascii_picture


def funny() -> None:
    mascot: str = """                                     
___________   ___________________________________________
 ___   ___ |||  ___   ___   ___   |   |   |        ,---, \\
|   | |   |||| |   | |   | |   |  |   |   |        |___|  \\
|___| |___|||| |___| |___| |___|  | O | O |                \\
           |||                    |   |   |                 )
___________|||____________________|___|___|________________/
                                 /    |    \\             /-------
---------------------------------------------------------"""

    make_fun('', mascot)
    print("\033[033m", 'power by pysubway', "\033[0m")


if __name__ == '__main__':
    funny()
