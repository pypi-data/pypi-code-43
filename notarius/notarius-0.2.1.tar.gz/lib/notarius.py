import json
import os
import platform
import re
import subprocess

from lib.logging import *
from lib.utils import *
from time import sleep

class Notarius(object):
    def __init__(self, options):
        self.bundle_id = options.bundle_id
        self.filename = options.filename
        self.mock = options.mock
        self.password = options.password
        self.username = options.username

    def check_request_status(self):
        info('Checking request status for: %s' % self.request_uuid)
        info('Will retry every minute for an hour')

        # retry every minute for an hour
        status = None
        retry = 0
        if self.mock:
            sleep_time = 1
        else:
            sleep_time = 60

        opts = (self.request_uuid, self.username, self.password)
        while retry is not 60:
            if self.mock:
                if retry == 5:
                    output = open(os.path.join('.', 'tests', 'notarize-status-success.txt'), 'r').read()
                else:
                   output = open(os.path.join('.', 'tests', 'notarize-status-in-progress.txt'), 'r').read()

            else:
                try:
                    output = self.get_cmd_output('xcrun altool --notarization-info %s -u %s -p %s' % opts, verbose=False)
                except subprocess.CalledProcessError as e:
                    # it seems sometimes we're calling Apple to get the status too quickly and
                    # get an improper response. continuing.
                    m = re.search('Apple Services operation failed. Could not find the RequestUUID.', e.output)
                    if m:
                        continue
                    else:
                        # something else happened, re-raising last error
                        raise
            
            m = re.search('Status: (.*)', output)
            if m:
                status = m.group(1)
            else:
                crash('Could not get status')


            if status == 'success':
                break

            retry += 1

            warning("Current status: %s Expected status: success" % status)
            warning('Sleeping for %s seconds before retrying' % sleep_time)
            sleep(sleep_time)

        m = re.search('LogFileURL: (.*)', output)
        if m:
            log_file_url = m.group(1)
        else:
            crash('Could not get logs URL')

        self.inspect_logs(log_file_url)

    def inspect_logs(self, url):
        output = json.loads(get(url))

        if output['status'] == 'Accepted':
            info('Package has been accepted')

            if 'issues' in output and output['issues'] is not None:
                warning('Issues were found!')
                print(output)
        else:
            crash('Expected status: Accepted, detected status: %s' % output['status'])

    def pre_flight_checks(self):
        if not platform.system() == 'Darwin':
            crash('Can only be executed on macOS!')

        # check xcode version
        output = self.get_cmd_output('xcodebuild -version', verbose=False)

        m = re.search('Xcode 1[0-9].[0-9]', output)
        if not m:
            crash('Expected Xcode 10+')

        # are we working with a file?
        if not os.path.isfile(self.filename):
            crash('Expected path to a file')

    def get_cmd_output(self, cmd, cwd=None, verbose=True, shell=False):
        if verbose:
            self.runner_logger(cmd)

        if isinstance(cmd, str):
            cmd = cmd.split()

        return subprocess.check_output(
            cmd,
            universal_newlines=True,
            cwd=cwd,
            stderr=subprocess.STDOUT
        )

    def runner_logger(self, msg):
        if isinstance(msg, list):
            msg = (' ').join(msg)

        msg = 'Running: %s' % msg
        msg_length = len(msg)
        if msg_length > 80:
            msg_length = 80

        print('-' * msg_length)
        print(msg)
        print('-' * msg_length)

    def staple(self):
        info('Stapling package: %s' % self.filename)
        self.get_cmd_output('xcrun stapler staple %s' % self.filename, verbose=False)

    def submit_dmg(self):
        info('Submitting %s to Apple to be notarized' % self.filename)

        if self.mock:
            output = open(os.path.join('.', 'tests', 'notarize.txt'), 'r').read()
        else:
            cmd = 'xcrun altool --notarize-app -f %s --primary-bundle-id %s -u %s -p %s' % (self.filename, self.bundle_id, self.username, self.password)
            output = self.get_cmd_output(cmd, verbose=False)

        request_uuid = None
        m = re.search('RequestUUID = (.*)', output)
        if m:
            request_uuid = m.group(1)

        info('Detected request UUID: %s' % request_uuid)

        if not request_uuid:
            crash('Failed to get RequestUUID after submitting DMG. Aborting.')
        else:
            self.request_uuid = request_uuid

    def validate(self):
        info('Validing package: %s' % self.filename)
        
        output = self.get_cmd_output('xcrun stapler validate %s' % self.filename, verbose=False)
        m = re.search('The validate action worked!', output)
        if m:
            info('Package is valid')
        else:
            crash('Package is invalid')
