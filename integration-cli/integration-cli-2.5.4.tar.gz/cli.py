import click
import os
from time import sleep
from smart_cli.helpers import FileManager, find_django_manager, install_dependies
from smart_cli.colors import Base


@click.group()
def cli():
    pass


@cli.command()
@click.option('--name', default='project',
              help='This name of your project')
@click.argument('name', type=click.STRING, default='project', required=True)
@click.option('--type', default='widget',
              help='Choose type of your project(oauth, widget)')
@click.argument('type', type=click.STRING, default='widget', required=True)
@click.argument('structure', type=click.STRING, default='default', required=True)
@click.option('--structure', default='default',
              help='Choose structure type(default, inside)')
def init(name, type, structure):
    print("st: ", structure)
    if type.lower() not in ['widget', 'oauth', 'crm']:
        raise Exception("Invalid type, type must oauth, widget or crm")
    file_manager = FileManager(name)
    print(Base.HEADER, f"-=-=-: STARTING PROJECT: {name} :-=-=-", Base.END)
    if structure.lower() == 'inside':
        os.system(f'django-admin startproject {name} .')
    else:
        os.system(f'django-admin startproject {name}')
    print(Base.OKBLUE, f"-=-=-: init basic application for {name} :-=-=-", Base.END)
    sleep(2)
    folder = '.' if structure.lower() == 'inside' else name
    if type.lower() == 'widget':
        os.popen(f'cp -R {file_manager.integration_dir}/integration_files/widget/* {folder}')
    elif type.lower() == 'oauth':
        os.popen(f'cp -R {file_manager.integration_dir}/integration_files/oauth/* {folder}')
    elif type.lower() == 'crm':
        while True:
            print("================")
            auth_type = input("Chose auth type(basic, oauth): ")
            print("================")
            if auth_type.lower() == 'basic':
                os.popen(f'cp -R {file_manager.integration_dir}/integration_files/widget/* {folder}')
                os.popen(f'cp -R {file_manager.integration_dir}/integration_files/crm/basic/* {folder}')
                break
            if auth_type.lower() == 'oauth':
                os.popen(f'cp -R {file_manager.integration_dir}/integration_files/oauth/* {folder}')
                os.popen(f'cp -R {file_manager.integration_dir}/integration_files/crm/oauth/* {folder}')
                break
            else:
                print(Base.WARNING, "WARNING chose valid auth_type(basic, oauth):", Base.END)
    else:
        raise Exception("Invalid type")
    os.popen(f'cp -R {file_manager.integration_dir}/integration_files/methods/ {folder}')

    print(Base.OKBLUE, f"-=-=-: INSTALL DEPENDENCIES FOR PROJECT: {name} :-=-=-", Base.END)
    install_dependies()

    print(Base.OKGREEN, "-=-=-: FINISH INSTALL DEPENDENCIES :-=-=-", Base.END)
    sleep(4)
    print(Base.HEADER, f"-=-=-: STARTING CREATE django project :-=-=-", Base.END)
    file_manager.rewrite_settings(structure)
    sleep(6)
    print(Base.OKBLUE, f"-=-=-: Created :-=-=-", Base.END)
    sleep(2)
    print(Base.OKGREEN, "-=-=-: DONE :-=-=-", Base.END)


@cli.command()
@click.option('--command', default='runserver',
              help='This name of django command')
@click.argument('command', type=click.STRING, default='runserver', required=True)
def django(command):
    manage = find_django_manager()
    os.system(f"python ./{manage} {command}")


@cli.command()
@click.option('--command', default='runserver',
              help='This name of django command')
@click.argument('command', type=click.STRING, default='tail', required=True)
def zappa(command, *params):
    str_params = " ".join(p for p in params)
    os.system(f"zappa {command} {str_params}")
