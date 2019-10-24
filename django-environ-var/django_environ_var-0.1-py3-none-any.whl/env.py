
import os, inspect


class Env:

    def __init__(self):

        self.set_imported_directory()

        if os.path.isfile(self.currenct_working_directory+"/settings.py"):
            pass
        else:
            raise Exception("Sorry! this is not settings.py")

    def set_imported_directory(self):

        # self.this_file_name = os.path.abspath(inspect.stack()[1].filename)
        # self.currenct_working_directory = os.path.dirname(self.this_file_name)
        self.currenct_working_directory = os.getcwd()

    def find_dot_env(self):

        try:
            self.file_handler = open(self.currenct_working_directory + '/../.env.prod', 'r')
        except:
            try:
                self.file_handler = open(self.currenct_working_directory + '/../.env.dev', 'r')
            except:
                raise Exception(".env.dev or .env.prod couldn't find your project directory")


    def parse_line_and_validate(self, line, error_line_number=None, file=None):

        if not "=" in line:
            raise Exception("Invalid")
        elif line.count("==") > 0:
            raise Exception("Invalid")
        else:
            parts = line.split("=", 1)
            if not parts[0].isidentifier():
                raise Exception("Invalid Identifier")
            else:
                return parts

    def init(self):
        self.set_imported_directory()
        self.find_dot_env()
        for line in [self.file_handler.readline()]:
            if not line:
                continue
            key, value = self.parse_line_and_validate(line)
            os.environ[key.strip()] = value.strip()






