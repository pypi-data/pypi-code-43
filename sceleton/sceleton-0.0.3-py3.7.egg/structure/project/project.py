import os
import sys
import subprocess
import time

from . import package, setup_py, readme, git, venv, license
from sceleton.decorators.missing_file import missing

def init(project_path=None, project_name=None, version=None,
        description=None, author_name=None, license_type=None, classifiers=None, 
        keywords=None, author_email=None, project_url=None, packages=None,
        create_django_project=False, set_virtual_env=True):

    license_type = 'MIT License' if license_type == '' or license_type is None else license_type

    if create_django_project:
        django(project_path=project_path, project_name=project_name)
        project_path = os.path.join(project_path, project_name)
    else:
        setup_py_file_content = setup_py.init(project_name=project_name,
                                              project_path=project_path,
                                              version=version,
                                              description=description,
                                              author_name=author_name,
                                              license_type=license_type,
                                              keywords=keywords,
                                              author_email=author_email,
                                              packages=packages,
                                              project_url=project_url,
                                              classifiers=classifiers)

        project_path = os.path.join(project_path, project_name)
        os.makedirs(project_path)
        make_file(folder_path=project_path, filename='setup.py', content=setup_py_file_content)
        make_file(folder_path=project_path, filename='setup.cfg', content="")
        pkg_dir(folder_path=project_path, project_name=project_name)

        if packages:
            sys.stdout.write("Adding packages {} to setup.py.\n\n".format(packages))
            sys.stdout.write("After initializing the project activate `venv`\n" +
                             "if you chose `--venv` option, and run `sceleton install`,\n" +
                             "to install all packages to the current virtual environment.\n\n")
            setup_py.packages(option='add', package_names=packages, project_path=project_path)

    license_type_file_content = license.init(license_type=license_type)
    readme_file_content = readme.init(project_name=project_name, license_type=license_type)
    gitignore_file_content = git.ignore(project_name=project_name)

    make_file(folder_path=project_path, filename='README.rst', content=readme_file_content)
    make_file(folder_path=project_path, filename='.gitignore', content=gitignore_file_content)
    make_file(folder_path=project_path, filename='LICENSE', content=license_type_file_content)

    git.init(project_path=project_path)

    if set_virtual_env:
        sys.stdout.write("\nAdding virtualenv...\n")
        venv.init(project_path=project_path)

def new_setup_py(project_path=None, version=None, description=None, 
                 author_name=None, author_email=None, packages=None, 
                 license_type=None, keywords=None, project_url=None, 
                 classifiers=None):
    
    project_name = project_path.split(os.sep)[-1]

    setup_py = setup_py.init(project_name=project_name, project_path=project_path, 
                            version=version, description=description, author_name=author_name, 
                            license_type=license_type,
                            keywords=keywords, author_email=author_email, packages=packages,
                            project_url=project_url, classifiers=classifiers)

    make_file(folder_path=project_path, filename='setup.py', content=setup_py)


def make_file(folder_path, filename, content):
    fullpath = os.path.join(folder_path,  filename)
    with open(fullpath, 'wb') as file:
        file.write(content.encode('utf-8'))

def pkg_dir(folder_path, project_name):
    pkg_folder = os.path.join(folder_path, project_name)
    os.makedirs(pkg_folder)
    init = os.path.join(pkg_folder, '__init__.py')
    with open(init, 'wb') as file:
        pass

@missing(file='setup.py')
def build(project_path):
    subprocess.run(['python3', 'setup.py', 'sdist'])

@missing(file='dist')
def upload(project_path):
    subprocess.run(['twine', 'upload', 'dist/*'])

@missing(file='setup.py')
def local(project_path):
    subprocess.run(['python3', 'setup.py', 'install'])

def django(project_name, project_path):
    directory = os.path.join(project_path, project_name)
    os.makedirs(directory)
    subprocess.run(['django-admin', 'startproject', project_name, directory])

@missing(file='setup.py')
def module(project_path, module_name, parent_module=None, files=None):

    fullpath = parent_module
    sep = '\\' if sys.platform == 'win32' else '/'
    exist = False
    if not module_name in os.listdir(fullpath):
        fullpath = os.path.join(fullpath, module_name)
        os.makedirs(fullpath)
        init = os.path.join(fullpath, '__init__.py')
        with open(init, 'wb') as file:
            pass
    else:
        fullpath = os.path.join(fullpath, module_name)
        exist = True

    if files:
        for file in files:

            path = os.path.join(fullpath, file)

            if file in os.listdir(fullpath):
                raise FileExistsError('File with name {} already exist.'.format(file))
            
            with open(path, 'wb') as file:
                pass
    elif exist:
        raise FileExistsError('File with name {} already exist.'.format(module_name))