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

import json
import os
from LbNightlyTools.Utils import JobParams, Dashboard
from LbNightlyTools.Configuration import loadConfig
from LbNightlyTools.MergeRequestBuilds import (make_mr_slots,
                                               post_gitlab_feedback)
from LbNightlyTools.Scripts.Common import PlainScript, addDashboardOptions


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
        addDashboardOptions(self.parser)

        self.parser.set_defaults(
            config_dir=None,
            flavour='nightly',
            output='slot-params-{name}.txt',
            slots=None,
            resolve_mrs=False)

    def write_files(self, slots):
        from couchdb import ResourceConflict

        d = Dashboard(
            flavour=self.options.flavour,
            server=self.options.db_url,
            dbname=self.options.db_name)

        for slot in slots:
            slot.build_id = d.lastBuildId(slot.name) + 1
            output_file_name = self.options.output.format(name=slot.name)
            while True:
                key = '{0}.{1}'.format(slot.name, slot.build_id)
                value = {
                    'type': 'slot-info',
                    'slot': slot.name,
                    'build_id': slot.build_id,
                    'config': slot.toDict(),
                }
                if not self.options.submit:
                    self.log.info('Configuration for slot {}:\n{}'.format(
                        key, json.dumps(value, indent=2)))
                    break
                try:
                    # reserve the build id by creating a place holder in the
                    # dashboard DB
                    d.db[key] = value
                    self.log.info('updated %s', d.urlForKey(key))
                    break
                except ResourceConflict:
                    # if the place holder with that name already exists, bump
                    # the build id
                    slot.build_id += 1
            if self.options.submit:
                with open(output_file_name, 'w') as f:
                    f.write(
                        str(
                            JobParams(
                                slot=slot.name, slot_build_id=slot.build_id)) +
                        '\n')
                self.log.info('%s written for slot %s with build id %s',
                              output_file_name, slot.name, slot.build_id)

        self.log.info('%s slots to start', len(slots))

    def main(self):
        if self.args:
            self.parser.error('unexpected arguments')

        self.log.info('Loading slot configurations')
        slots = list(loadConfig(self.options.config_dir).values())

        mr_slots_config = os.environ.get('MR_TOKEN')
        if mr_slots_config:
            mr_slots_config = json.loads(mr_slots_config)
            slots = make_mr_slots(mr_slots_config, slots)

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
        self.write_files(slots)

        # Use the assigned build_id to give feedback for MR slots
        if mr_slots_config:
            assert len(slots) == 2
            post_gitlab_feedback(slots[0], slots[1], self.options.flavour,
                                 mr_slots_config)

        self.log.info('End of extraction of all enable slot')

        return 0
