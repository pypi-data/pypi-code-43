import json
from PyInquirer import style_from_dict, Token, prompt

class UserInteraction:

    def __init__(self):
        self.colors_json = {
            "red": {
                "normal": "[0;31m",
                "bold": "[1;31m",
            },
            "green": {
                "normal": "[0;32m",
                "bold": "[1;32m",
            },
            "yellow": {
                "normal": "[0;33m",
                "bold": "[1;33m",
            },
            "blue": {
                "normal": "[0;34m",
                "bold": "[1;34m"
            },
            "white": {
                "normal": "[0;37m",
                "bold": "[1;37m",
            }
        }


    def style(self):
        return style_from_dict({
            Token.Separator: '',
            Token.QuestionMark: '#3361FF bold',
            Token.Selected: '#3361FF',  # default
            Token.Pointer: '#3361FF',
            Token.Instruction: '',  # default
            Token.Answer: '#000',
            Token.Question: '#3361FF',
        })

    def colorize(self, text, color, bold=False, underline=False, high_intensity=False):
        bash_color = self.colors_json[color]
        if bold:
            color = bash_color['bold']
        elif underline:
            color = bash_color['underline']
        elif high_intensity:
            color = bash_color['high_intensity']
        else:
            color = bash_color['normal']

        return '\033{}'.format(color) + text + '\033[0m'

    # This function asks the user to choose between the found secrets
    def choose_secret(self, found_secrets):

        if len(found_secrets) > 0:
            text = "Found " + str(len(found_secrets)) + " secrets"
            print(self.colorize(text, 'blue', bold=True))
            questions = [{'type': 'list', 'name': 'title', 'message': 'Which secret do you want?', 'choices': [x['title'] for x in found_secrets]}]
            answer = prompt(questions,style=self.style())
            return answer

        else:
            text = 'No secrets found'
            print(self.colorize(text, 'yellow'))
            return None

    # This inner function asks for the parameters the user want from the secret
    def ask_if_needs_username(self):
        questions = [
            {
                'type': 'confirm',
                'name': 'needs_username',
                'message': 'Do you need the username:'
            }
        ]

        return prompt(questions, style=self.style())['needs_username']

    # This inner function is responsible for handling the proccess of adding the secret to the database

    def ask_secret(self):
        questions = [
            {
                'type': 'secret',
                'name': 'secret',
                'message': 'Secret:'
            }
        ]

        return prompt(questions, style=self.style())['secret']

    def wait_for_confirmation(self):
        questions = [
            {
                'type': 'input',
                'name': 'continue',
                'message': 'Press enter key to continue...'
            }
        ]

        prompt(questions, style=self.style())

    # This function returns the help parameters for this application
    def help():
        pass
