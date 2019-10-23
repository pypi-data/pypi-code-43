from textwrap import dedent


class Utils:

    def welcome(self):
        appname = f'{self.APP_NAME.title()}'
        # Gereted by app: figlet
        msg = f"""
            ➜ Welcome to the {appname} Theme Manager
                             _                      
             ___ _ __   __ _| | ___   _ _ __  _   _ 
            / __| '_ \ / _` | |/ / | | | '_ \| | | |
            \__ \ | | | (_| |   <| |_| | |_) | |_| |
            |___/_| |_|\__,_|_|\_\\__, | .__/ \__, |
                                  |___/|_|    |___/
                                        (c) since 2019 - v{self.APP_VERSION}

                    For more command: $ {self.APP_EXEC} --help

            """
        self.printc('p', dedent(msg), self.b_cyan)
