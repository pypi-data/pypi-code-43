from typing import Callable, Any, Dict, List
import logging



class TruCli:

    def __init__(self):
        self.__commands = {}
        self.prompt = '>'

    def run(self):
        while True:
            self.main_loop()

    def main_loop(self):
        line = input(self.prompt)
        name = line.split(' ')[0]
        tokens = self.__parse(line)
        logging.debug('Tokens: ' + str(tokens))
        if tokens is None:
            print(line + ': Could not parse command.')
            return
        if 'help' in tokens[1].keys():
            ret = self.__generate_help(name)
        else:
            params = self.__commands[name][1] # get all parameters in the specified command
            for param_key in params: # check if a parameter with no default hasn't been specified
                if 'default' not in params[param_key].keys() and params[param_key]['arg_name'] not in tokens[1]:
                    # ask the user for the unspecified parameter and cast it to the proper type TODO: try...except for unconvertable inputs
                    tokens[1][params[param_key]['arg_name']] = params[param_key]['type'](input(params[param_key]['prompt'] + ': '))
                elif params[param_key]['arg_name'] not in tokens[1]: # we have a default, so apply it
                    tokens[1][params[param_key]['arg_name']] = params[param_key]['default']
            del tokens[1]['help']
            ret = tokens[0](**tokens[1])
        if ret is not None:
            print(ret)

    def add_command(self, name: str, func: Callable[[Any], Any], params: Dict[str, Dict[str, str]] = None):
        """Add a command.
            Arguments:
            name -- The name of the command. Represent how it will be called from the command line
            func -- The function that will be executed when the command is called
            params -- A dictionary encapsulating the flags and the names of the arguments to pass to the function,
            defaults to None
                structure: {flag1: {'arg_name': name1, 'type': type, 'default': def, 'help': 'help text', 'prompt': 'prompt_text'}}
                e.g. {'-v': {'arg_name': 'verbose', 'type': bool, 'default': False, 'help': 'More detailed outputs'}}"""

        mandatory_keys = ['arg_name', 'type'] # and either default or prompt
        if params is not None:
            if all(key in mandatory_keys for key in params.keys()): # check if some mandatory keys are not there
                raise Exception('Mandatory keys not found')
            for key in params: # check if we are missing both default and prompt
                if 'default' not in params[key].keys() and 'prompt' not in params[key].keys():
                    raise Exception('Params should include either a default or a prompt. ' + key + ' does not.')
            params.update({'-help': {'arg_name': 'help', 'type': bool, 'default': False, 'help': 'Display this text'}})
        else:
            params = {'-help': {'arg_name': 'help', 'type': bool, 'default': False, 'help': 'Display this text'}}
        self.__commands[name] = [func, params]

    def __parse(self, line: str) -> dict:
        tokens = line.split(' ')
        if not tokens[0] in self.__commands.keys():
            return None
        to_ret = [self.__commands[tokens[0]][0], {}] # [func, {arg_name1: arg1, arg_name2: arg2}]
        for i in range(1, len(tokens), 2):
            arg_name = self.__commands[tokens[0]][1][tokens[i]]['arg_name']
            last_token = i >= len(tokens) - 1
            if not last_token and tokens[i].startswith('-') and not tokens[i+1].startswith('-'): # the token is a flag and the next one is arg
                to_ret[1].update({arg_name: tokens[i + 1]})
            elif tokens[i].startswith('-'): # the token is a boolean
                to_ret[1].update({arg_name: True})
                i += 1
            else:
                return None
            # arg_name = self.__commands[tokens[0]][1][tokens[i]]
            # if arg_name is None:
            #     i += 1
            #     continue
            # to_ret[1].update({arg_name: tokens[i + 1]})
        return to_ret

    def __generate_help(self, name: str):
        """Generates a help page for 'name' functions"""
        func = self.__commands[name][0]
        help_string = func.__doc__ + '\n\nParameters:\n'
        params = self.__commands[name][1]
        for key in params.keys():
            par_type = params[key]['type']
            par_type = par_type.__name__ if par_type != bool else ''
            if 'help' in params[key]:
                help_string += key + ' ' +  par_type + ' -- ' + params[key]['help'] + '\n'
            else:
                help_string += key + ' ' +  par_type + ' -- ' + self.__generate_missing_help_string(params[key]) + '\n'

        return help_string

    def __generate_missing_help_string(self, param: Dict[str, Any]):
        return 'Set ' + param['arg_name']

# Example Code =====================================================


def hi(name):
    """Greets a person."""
    print('Hello ' + name)

def hello():
    """Print hello world"""
    print('Hello World')

if __name__ == '__main__':
    print('Initializing example code. Try the \'hello\' command!')
    cli = TruCli()
    #cli.add_command('hello', hi, {'-n': {'arg_name': 'name', 'type': str, 'default': 'World', 'help': 'Specify the name to be greeted'}})
    cli.add_command('hello', hello)
    cli.run()