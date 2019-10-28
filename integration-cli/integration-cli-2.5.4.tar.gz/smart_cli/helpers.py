import os
import sys
import shutil
import glob
from pathlib import Path
from .utils import generate_secret_key


def install_dependies():
    dependies = [
        'zappa==0.47.1',
        'requests>=2.18.1',
        'validators',
        'zappa-sentry==0.3.1',
        'pytz==2018.4',
        'six==1.11.0',
        'boto',
        'boto3',
        'django-storages',
        'django-cors-headers',
        'cfn-flip==1.0.2',
        'eventmonitoring-client',
        'smart-integration-utils',
    ]
    with open('.req.txt', 'a') as f:
        for d in dependies:
            f.write(d + '\n')

    os.system('pip install -r .req.txt')
    os.remove('.req.txt')


class FileManager(object):
    def __init__(self, project_name):
        self.project_name = project_name
        self.integration_dir = self.create_integration_dir()
        self.move_dist_files()

    def get_lib_path(self):
        for path in sys.path:
            if 'site-packages' in path:
                return path

    def create_integration_dir(self):
        home_dir = os.getenv("HOME")
        if '.integration' not in os.listdir(home_dir):
            os.mkdir(f'{os.getenv("HOME")}/.integration')
        return f'{home_dir}/.integration'

    def move_dist_files(self):

        lib = self.get_lib_path()
        source = f"{lib}/smart_cli/integration_files"
        if 'integration_files' not in os.listdir(self.integration_dir):
            for file_path in glob.glob(source + '/*'):
                # Move each file to destination Directory
                print(file_path)
                try:
                    shutil.move(file_path, f"{self.integration_dir}/integration_files")
                except shutil.Error:
                    pass

    def rewrite_settings(self, type='default'):
        with open(self.get_lib_path() + '/smart_cli/_default_settings.py', 'r') as r:
            with open('settings.py', 'a') as w:
                for i in r:
                    if '__base_project_name__' in i:
                        i = i.replace('__base_project_name__', self.project_name)
                    elif 'SECRET_KEY' in i:
                        i = f'SECRET_KEY = "{generate_secret_key()}"\n'
                    w.write(i)

        with open(self.get_lib_path() + '/smart_cli/_default_wsgi.py', 'r') as r:
            with open('wsgi.py', 'a') as w:
                for i in r:
                    if '__base_project_name__' in i:
                        i = i.replace('__base_project_name__', self.project_name)
                    w.write(i)

        with open(self.get_lib_path() + '/smart_cli/_default_urls.py', 'r') as r:
            with open('urls.py', 'a') as w:
                for i in r:
                    w.write(i)
        if type == 'default':
            os.system(f'cp settings.py {self.project_name}/{self.project_name}/')
            os.system(f'cp wsgi.py {self.project_name}/{self.project_name}/')
            os.system(f'cp urls.py {self.project_name}/{self.project_name}/')
            os.remove('settings.py')
            os.remove('wsgi.py')
            os.remove('urls.py')
            os.chdir(self.project_name)
        else:
            os.system(f'cp settings.py {self.project_name}/')
            os.system(f'cp wsgi.py {self.project_name}/')
            os.system(f'cp urls.py {self.project_name}/')
            os.remove('settings.py')
            os.remove('wsgi.py')
            os.remove('urls.py')
        os.system('pip freeze > requirements.txt')

        return True


def find_django_manager():
    for file_path in Path('.').glob('**/*manage.py'):
        if 'boto' not in str(file_path):
            return str(file_path)
