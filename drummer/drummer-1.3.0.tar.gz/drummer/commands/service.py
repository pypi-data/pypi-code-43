# -*- coding: utf-8 -*-
"""Service commands.

This module includes all commands related to Drummered service.

Commands subclass BaseCommand as they are executed locally on user side.
"""
from sys import path as sys_path
from .base import BaseCommand
from drummer.drummered import Drummered


class ServiceStart(BaseCommand):
    """Initialization of Drummered service."""

    def __init__(self, config):
        super().__init__(config)

    def execute(self, args):

        config = self.config

        print('Starting Drummer service...')
        try:

            sys_path.append(config['taskdir'])

            drummered = Drummered(config)
            drummered.start()

        except Exception as err:
            print(f'Impossible to start Drummer service: {str(err)}')
