# -*- coding: utf-8 -*-
"""Commands for schedulation import/export.

This module includes all commands related to schedulation import/export.

All these commands subclass RemoteCommand as they are executed remotely by
Drummered service.
"""
import json
from sys import path as sys_path
from .base import BaseCommand
from drummer.database import SqliteSession, Schedule
from drummer.utils.fio import read_yaml, write_yaml

class SchedImport(BaseCommand):
    """Import of schedulation from yaml file."""

    def __init__(self, config):
        super().__init__(config)

    def execute(self, cmd_args):

        filename = cmd_args.get('--filename') or 'schedulation.yaml'
        print(f'Importing schedulation from {filename}')

        config = self.config

        # read from file
        schedulation = read_yaml(filename)

        try:

            # init DB session
            session = SqliteSession.create(config)

            # CLEAN TABLE BEFORE LOADING TASKS!
            session.query(Schedule).delete()

            for sch in schedulation:

                print(f'Importing job {sch["name"]}')

                # create job object
                job = Schedule(name=sch['name'],
                    description=sch['description'],
                    cronexp=sch['cronexp'],
                    parameters=json.dumps(sch['parameters']),
                    enabled=sch['enabled'])

                session.add(job)

            session.commit()

        except Exception as err:
            print(f'Impossible to import schedulation: {str(err)}.')

        else:
            print('Import completed.')

        finally:
            session.close()


class SchedExport(BaseCommand):
    """Export of schedulation to yaml file."""

    def execute(self, cmd_args):

        print('Exporting schedulation to file')

        filename = cmd_args.get('--filename') or 'schedulation.yaml'

        config = self.config

        # get all schedules
        session = SqliteSession.create(config)
        schedules = session.query(Schedule).group_by(Schedule.name).all()
        session.close()

        job_list = []
        for s in schedules:

            d = dict()
            d['id'] = s.id
            d['name'] = s.name
            d['description'] = s.description
            d['cronexp'] = s.cronexp
            d['enabled'] = s.enabled
            d['parameters'] = json.loads(s.parameters)

            job_list.append(d)

        write_yaml(filename, job_list)
        print(f'Export completed, schedulation saved to {filename}.')
