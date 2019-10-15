###############################################################################
# (c) Copyright 2013 CERN                                                     #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
'''
Simple script to extract slot who need to be compile
Create one file for each slot. Each file contains parameters for the next job.
Now we only have the slot name in parameter in files
'''
__author__ = 'Colas Pomies <colas.pomies@cern.ch>'

import os
import sys
from LbNightlyTools.Utils import JobParams, Dashboard
from LbNightlyTools.Configuration import loadConfig
from LbNightlyTools.Scripts.Common import PlainScript


class Script(PlainScript):
    '''
    Script to create one file for all enable slots or for slots in parameters
    This file contain the slot name and the slot build id
    The slot build id is extract with the function get_ids
    '''
    __usage__ = '%prog [options] flavour output_file.txt'
    __version__ = ''

    def defineOpts(self):
        self.parser.add_option(
            '--config-dir',
            help='Directory where to find configurations '
            'files [default: %default]')
        self.parser.add_option(
            '--flavour', help='nightly builds flavour '
            '[default: %default]')
        self.parser.add_option(
            '--output',
            help='template for output file name, it must '
            'contain a "{name}" that will be replaced '
            'by the slot name '
            '[default: %default]')
        self.parser.add_option(
            '--slots',
            help='do not look for active slots, but use the '
            'provided space or comma separated list')
        self.parser.add_option(
            '--resolve-mrs',
            action='store_true',
            help='resolve symbolic merge requests (all, label=X...) to a list '
            'pairs (mr_iid, commit_id)')

        self.parser.set_defaults(
            config_dir=None,
            flavour='nightly',
            output='slot-params-{name}.txt',
            slots=None,
            resolve_mrs=False)

    def write_files(self, slots, flavour, output_file):
        from couchdb import ResourceConflict

        d = Dashboard(flavour=flavour)

        for slot in slots:
            slot.build_id = d.lastBuildId(slot.name) + 1
            output_file_name = output_file.format(name=slot.name)
            while True:
                try:
                    # reserve the build id by creating a place holder in the
                    # dashboard DB
                    d.db['{0}.{1}'.format(slot.name, slot.build_id)] = {
                        'type': 'slot-info',
                        'slot': slot.name,
                        'build_id': slot.build_id,
                        'config': slot.toDict(),
                    }
                    break
                except ResourceConflict:
                    # if the place holder with that name already exists, bump
                    # the build id
                    slot.build_id += 1
            open(output_file_name, 'w') \
                .write(str(JobParams(slot=slot.name,
                                     slot_build_id=slot.build_id
                                     )) + '\n')
            self.log.info('%s written for slot %s with build id %s',
                          output_file_name, slot.name, slot.build_id)

        self.log.info('%s slots to start', len(slots))

    def main(self):
        if self.args:
            self.parser.error('unexpected arguments')

        if self.options.resolve_mrs and not os.environ.get('GITLAB_TOKEN'):
            self.parser.error('environment variable GITLAB_TOKEN must be '
                              'set to use --resolve-mrs')

        self.log.info('Loading slot configurations')
        slots = loadConfig(self.options.config_dir).values()
        if not self.options.slots:
            self.log.info('get only enabled slots')
            slots = [slot for slot in slots if slot.enabled]
        else:
            self.options.slots = set(
                self.options.slots.replace(',', ' ').split())
            self.log.info('get only requested slots')
            slots = [slot for slot in slots if slot.name in self.options.slots]

        if self.options.resolve_mrs:
            self.log.info('resolving merge requests aliases')
            from LbNightlyTools.GitlabUtils import resolveMRs
            slots = resolveMRs(slots)

        # Create a file that contain JobParams for each slot
        self.write_files(slots, self.options.flavour, self.options.output)

        self.log.info('End of extraction of all enable slot')

        return 0
