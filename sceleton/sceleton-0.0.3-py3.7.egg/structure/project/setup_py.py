import json
import os
import re
import itertools

from . import sceleton
from sceleton.decorators.missing_file import missing

from . import ENCODING


def init(project_name=None, project_path=None,
         version='0.0.1', description=None, author_name=None, license_type=None,
         keywords=None, author_email=None, packages=None, project_url=None, classifiers=None):
        
    project_name = "'{}'".format(project_name)
    version = "'{}'".format(version)
    description = "'{}'".format(description) if description else "''"
    author_name = "'{}'".format(author_name) if author_name else "''"
    author_email = "'{}'".format(author_email) if author_email else "''"
    license = "'{}'".format(license_type) if license_type else "'MIT License'"

    classifiers = "{}".format(''.join(classifiers)) if classifiers else ""
    project_url = "'{}'".format(project_url) if project_url else "''"

    keywords = "'{}'".format(keywords) if keywords else "{}".format(project_name)
    packages = "{}".format(','.join(["'{}'".format(package) \
                                for package in packages.split(' ')])) \
                                if packages else ""

    content = sceleton('setup.txt')
    content = ''.join(content)
    content = content.replace('[projectname]', project_name) \
                     .replace('[version]', version) \
                     .replace('[description]', description) \
                     .replace('[url]', project_url) \
                     .replace('[packages]', packages) \
                     .replace('[author_name]', author_name) \
                     .replace('[author_email]', author_email) \
                     .replace('[license]', license) \
                     .replace('[keywords]', keywords) \
                     .replace('[classifiers]', classifiers)
    return content

@missing(file='setup.py')
def content(project_path):
    setup_py = os.path.join(project_path, 'setup.py')
    with open(setup_py, 'r') as file:
        content = file.readlines()
    return content, setup_py


def edit(field, new_value, project_path, index):
    file_content, setup_py = content(project_path)

    left_spaces = ' ' * (len(file_content[index[0] - 1]) - len(file_content[index[0] - 1].strip()) - 1)
    file_content[index[0]] = "{}{}='{}',\n".format(left_spaces, field, new_value)

    if len(index) > 1:
        file_content[index[0] + 1:index[-1] + 1] = '' * (len(index) - 1)

    with open(setup_py, 'wb') as file:
         file.write(''.join(file_content).encode(ENCODING))

def packages(option, package_names, project_path):
    file_content, setup_py = content(project_path)

    index = []
    in_package_field = False
    for i, line in enumerate(file_content):
        if 'install_requires' in line.strip() or in_package_field:
            in_package_field = True
            index.append(i)
        if in_package_field and ']' in line.strip():
            break

    current_packages = ''.join(file_content[index[0]:index[-1] + 1])\
                        .split('=')[-1]\
                        .strip()\
                        .replace("'", '*')\
                        .replace("\"", "'")\
                        .replace("*", "\"")\
                        .replace('\',\'', '')\
                        .split('\\')

    regex = re.compile("[a-zA-Z]+")
    current_packages = list(itertools.chain.from_iterable([regex.findall(package) 
                                                        for package in current_packages]))

    if 'add' == option:
        current_packages.extend(package_names)
        current_packages = list(set(current_packages))
    elif 'remove' == option:
        current_packages = list(set(current_packages) - set(package_names))

    left_space_size = len(file_content[index[0] - 1]) - len(file_content[index[0] - 1].strip()) - 1
    file_content[index[0]] = "{}install_requires={},\n".format(' ' * left_space_size, 
                                                                current_packages)
    if len(index) > 0:
        file_content[index[0] + 1:index[-1] + 1] = '' * (len(index) - 1)

    with open(setup_py, 'wb') as file:
        file.write("".join(file_content).encode(ENCODING))


def get(type_field, project_path):
    file_content, _ = content(project_path)

    index = []
    in_field = False
    in_setup = False
    for i, line in enumerate(file_content):

        if 'setup(' in line:
            in_setup = True

        if in_setup and (type_field in line or in_field):
            in_field = True
            index.append(i)

        if in_field and (']' in line.strip() or len(file_content[i+1].split("=")) >= 2):
            break

    result = [file_content[i].strip() for i in index]

    return '\n'.join(result), index

def classifiers(project_path, new_classifiers, index):

    file_content, setup_py = content(project_path)

    next_fields = file_content[index[-1] + 1:]
    left_spaces = ' ' * (len(file_content[index[0] - 1]) - len(file_content[index[0] - 1].strip()) - 1)
    if len(new_classifiers) > len(index):
        file_content[index[0] + 1:] = new_classifiers
        file_content.append("{}{}".format(left_spaces, '],\n'))
        file_content.extend(next_fields)
    else:
        file_content[index[0] + 1:] = new_classifiers
        file_content[index[0] + len(new_classifiers) + 1:] = '' * len(file_content[index[0]:])
        file_content.append("{}{}".format(left_spaces, '],\n'))
        file_content.extend(next_fields)

    with open(setup_py, 'wb') as file:
        file.write(''.join(file_content).encode(ENCODING))

def edit_classifier_license(project_path, old_license, new_license):
    file_content, setup_py = content(project_path)

    in_classifiers = False
    index = -1
    for i, line in enumerate(file_content):
        if 'classifiers' in line:
            in_classifiers = True

        if in_classifiers and old_license in line:
            index = i
            break

    if index > 0:
        left_spaces = ' ' * (len(file_content[index - 1]) - len(file_content[index - 1].strip()) - 1)
        file_content[index] = "{}'{}',\n".format(left_spaces, new_license.strip())

        with open(setup_py, 'wb') as file:
            file.write(''.join(file_content).encode(ENCODING))