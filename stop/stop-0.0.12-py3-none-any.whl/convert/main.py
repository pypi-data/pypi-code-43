from . import extract_files
from . import convert
from .prefs import prefs
import os
import shutil

def main():
    extract_files.extract_files_and_create_temp_folder()

    json_project_url = '{0}/{1}/project.json'.format(os.path.dirname(prefs['sb3_url']), prefs['temp_folder_name'])
    with open(json_project_url, 'r') as f:
        json_string = f.read()

    code = convert.generate_code(json_string)

    with open(prefs['code_file_url'], 'w') as f:
        f.write(code)

    shutil.rmtree(prefs['temp_folder_name'])





# each sprite code segment must consist of something like this:



# first load costumes

# costumes = [
#   {'file': '', 'name': ''},
#   {'file': '', 'name': ''},
#   {'file': '', 'name': ''}
# ]

# # next initiate sprite

# sprite_sprite1 = stop.Sprite(project, costumes=costumes)

# # finally create scripts

# def sprite1_greenflag1():
#   sprite_sprite1.move_steps(10)

# project.green_flag(sprite1_greenflag1)