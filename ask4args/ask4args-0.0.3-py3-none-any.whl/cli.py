# import sys
# from abc import ABC, abstractmethod
# from pathlib import Path
# from PyInquirer import Token, style_from_dict

# class BaseClass(ABC):
#     home_path = Path.home()

#     @abstractmethod
#     def run(self):
#         pass
# def choose_class():
#     argv = sys.argv
#     if len(argv) < 2:
#         raise IOError('please input the class name')
#     name = argv[1]
#     for cls in BaseClass.__subclasses__():
#         if cls.name.lower() == name:
#             return cls
#     else:
#         print(f'not found class {name}')

# class ExampleClass(BaseClass):

#     def run(self):
#         questions = [
#             {
#                 'type': 'input',
#                 'name': 'first_name',
#                 'message': 'What\'s your first name',
#             },
#         ]
#         answers = prompt(questions)
#         print(answers)
#         # {'first_name': ''}

# class TempVenv(BaseClass):

#     def run(self):
#         import venv
#         questions = [
#             {
#                 'type': 'confirm',
#                 'message': 'a Boolean value indicating that the system Python site-packages should be available to the environment.',
#                 'name': 'system_site_packages',
#                 'default': False,
#             },
#             {
#                 'type': 'confirm',
#                 'message': 'a Boolean value which, if true, will delete the contents of any existing target directory, before creating the environment.',
#                 'name': 'clear',
#                 'default': False,
#             },
#             {
#                 'type': 'confirm',
#                 'message': 'a Boolean value indicating whether to attempt to symlink the Python binary rather than copying.',
#                 'name': 'symlinks',
#                 'default': False,
#             },
#             {
#                 'type': 'confirm',
#                 'message': 'a Boolean value which, if true, will upgrade an existing environment with the running Python - for use when that Python has been upgraded in-place.',
#                 'name': 'upgrade',
#                 'default': False,
#             },
#             {
#                 'type': 'confirm',
#                 'message': 'a Boolean value which, if true, ensures pip is installed in the virtual environment.',
#                 'name': 'with_pip',
#                 'default': False,
#             },
#             {
#                 'type': 'confirm',
#                 'message': 'a String to be used after virtual environment is activated (defaults to None which means directory name of the environment would be used).',
#                 'name': 'prompt',
#                 'default': False,
#             },
#         ]
#         answers = prompt(questions, style=custom_style_1)
#         print(answers)
#         # {'first_name': ''}

# if __name__ == "__main__":
#     t = TempVenv()
#     t.run()
