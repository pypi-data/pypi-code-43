import os

from . import sceleton
from sceleton.decorators.missing_file import missing
from . import ENCODING

def init(project_name=None, license_type=None):
    content = sceleton('README.txt')
    content = ''.join(content)
    license = license_type or 'MIT License'
    content = content.replace("[projectname-title]", ' '.join(project_name.split('-')).capitalize()) \
                     .replace("[projectname]", project_name) \
                     .replace("[license]", license)

    return content

@missing(file='README.rst')
def content(project_path):
    path = os.path.join(project_path, 'README.rst')
    with open(path, 'r') as file:
        content = file.readlines()
    return content, path

def edit(project_path, old_value, new_value):
    file_content, readme = content(project_path)

    index = -1
    for i, line in enumerate(file_content):
        if old_value in line:
            index = i
            break

    if index > 0:
        file_content[index] = file_content[index].replace(old_value, new_value)
        with open(readme, 'wb') as file:
            file.write(''.join(file_content).encode(ENCODING))