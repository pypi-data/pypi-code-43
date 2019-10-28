# -*- coding: utf-8 -*-
from os import path, makedirs
from drummer.database import Base, Schedule
from drummer.utils.fio import write_yaml
import drummer.local.data as appdata
from sqlalchemy.orm import sessionmaker
from sqlite3 import dbapi2 as sqlite
from sqlalchemy import create_engine

class EnvInit():

    def execute(self, command_args):

        print('Setting the environment for Drummer...')

        BASE_FOLDER = path.abspath(command_args['base_folder'])

        # task folder
        TASK_DIR = 'tasks'
        TASK_DIR_PATH = path.join(BASE_FOLDER, TASK_DIR)

        # config folder
        CONFIG_DIR = 'config'
        CONFIG_DIR_PATH = path.join(BASE_FOLDER, CONFIG_DIR)
        CONFIG_FILE = 'drummer-config.yml'
        TASK_FILE = 'drummer-tasks.yml'

        # log folder and filepath
        LOG_DIR = 'logs'
        LOG_DIR_PATH = path.join(BASE_FOLDER, LOG_DIR)

        LOG_FILE = 'drummer.log'
        LOG_FILEPATH = path.join(LOG_DIR_PATH, LOG_FILE)

        # database folder and filepath
        DATABASE_DIR = 'database'
        DATABASE_DIR_PATH = path.join(BASE_FOLDER, DATABASE_DIR)

        DATABASE_FILE = command_args.get('--database')
        DATABASE_FILEPATH = path.join(DATABASE_DIR_PATH, DATABASE_FILE)

        SCRIPT_FILE = 'drummer-cli.py'
        SERVICE_FILE = 'drummered.service'

        # FOLDER CREATION
        # ----------------------------------------------- #

        # create root folder
        if not path.exists(BASE_FOLDER):
            makedirs(BASE_FOLDER)

        # create task folder
        if not path.exists(TASK_DIR_PATH):
            makedirs(TASK_DIR_PATH)

        # create config folder
        if not path.exists(CONFIG_DIR_PATH):
            makedirs(CONFIG_DIR_PATH)

        # create database folder
        if not path.exists(DATABASE_DIR_PATH):
            makedirs(DATABASE_DIR_PATH)

        # create database folder
        if not path.exists(LOG_DIR_PATH):
            makedirs(LOG_DIR_PATH)


        # DATABASE CREATION
        # ----------------------------------------------- #

        # create database
        conn_string = f'sqlite+pysqlite:///{DATABASE_FILEPATH}'

        db_engine = create_engine(conn_string, module=sqlite)
        Base.metadata.create_all(db_engine, checkfirst=True)

        print('Database created.')

        # CONFIG CREATION
        # ----------------------------------------------- #

        config_data = {
            'application-name': 'Drummer',
            'base_dir': BASE_FOLDER,
            'logging': {
                'filename': LOG_FILEPATH,
                'level': 'INFO',
                'max-size': 2048*1024
            },
            'socket': {
                'address': 'localhost',
                'port': 10200,
                'max_connections': 1,
                'message_len': 4096
            },
            'database': DATABASE_FILEPATH,
            'taskdir': TASK_DIR_PATH,
            'max-runners': 4,
            'idle-time': 0.1
        }

        write_yaml(path.join(CONFIG_DIR_PATH, CONFIG_FILE), config_data)

        task_data = [
            {
                'classname': 'YourTaskClass',
                'filepath': 'path/to/filename.py',
                'description': 'Description of task'
            }
        ]

        write_yaml(path.join(CONFIG_DIR_PATH, TASK_FILE), task_data)

        # task readme
        with open(path.join(TASK_DIR_PATH, 'README.txt'), 'w') as f:
            f.write('Insert your task files in this folder')

        print('Configuration files created.')


        # SCRIPT CREATION
        # ----------------------------------------------- #

        with open(path.join(BASE_FOLDER, SCRIPT_FILE), 'w') as f:
            f.write(appdata.SCRIPT_CODE)

        print('Python script created.')


        # SERVICE CREATION
        # ----------------------------------------------- #

        command = f'{path.join(BASE_FOLDER, SCRIPT_FILE)} service:start'

        service_code = appdata.SERVICE_CODE
        service_code = service_code.replace('<command>', command)

        with open(path.join(CONFIG_DIR_PATH, SERVICE_FILE), 'w') as f:
            f.write(service_code)

        print(f'Service file created in {CONFIG_DIR_PATH}')
