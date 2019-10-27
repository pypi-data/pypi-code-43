'''
Jenkins handler

A dynamically configurable handler to start Jenkins jobs.

Configuration is available via environment variables, YAS_JENKINS_URL, YAS_JENKINS_USERNAME,
YAS_JENKINS_PASSWORD, and the json encoded YAS_JENKINS_JOBS. For instance, with:

    YAS_JENKINS_URL=https://jenkins.example.com
    YAS_JENKINS_USERNAME=yas
    YAS_JENKINS_PASSWORD=secret
    YAS_JENKINS_JOBS='{"MyTestJob": "deploy (?P<branch>\w+) to (?P<site>\w+)"}'

The job 'MyTestJob' on jenkins.example.com would be triggered by the message "@yas deploy master to uat". The named
groups in the command regex will be passed as parameters to the job..
'''
import json
import os
import time
import re

import jenkins

from yas import YasHandler

class JenkinsHandlerError(Exception):
    pass

class JenkinsHandler(YasHandler):
    def __init__(self, bot):
        super().__init__(bot)

        raw_jobs = json.loads(os.environ.get('YAS_JENKINS_JOBS', '{}'))
        self.jobs = {name: re.compile(regex) for name, regex in raw_jobs.items()}

        url = os.environ.get('YAS_JENKINS_URL')
        username = os.environ.get('YAS_JENKINS_USERNAME')
        password = os.environ.get('YAS_JENKINS_PASSWORD')
        self.timeout = int(os.environ.get('YAS_JENKINS_BUILD_TIMEOUT', 30))
        self.server = jenkins.Jenkins(url, username=username, password=password)
        self.server.get_whoami()
        self.current_job = None
        self.current_match = None
        self.verbose_reply = False

    def test(self, data):
        text = data.get('text', '').strip()
        if text.endswith('verbose'):
            self.verbose_reply = True
        for job, regex in self.jobs.items():
            current_match = regex.search(text)
            if bool(current_match):
                self.current_job = job
                self.current_match = current_match
                return True
        return False

    def handle(self, _, reply):
        job_info = self.server.get_job_info(self.current_job)
        next_build_number = job_info['nextBuildNumber']
        self.server.build_job(self.current_job, parameters=self.current_match.groupdict())
        pretty_params = ', '.join([f'`{name}: {value}`' for name, value in self.current_match.groupdict().items()])
        reply(f'Starting build {next_build_number} of {self.current_job} with {pretty_params}')
        for _ in range(self.timeout):
            time.sleep(1)
            job_info = self.server.get_job_info(self.current_job)
            if job_info['lastBuild']['number'] == next_build_number:
                break
        else:
            reply(f'Build {next_build_number} of {self.current_job} did not start in {self.timeout} seconds. '
                  f' It may have failed, please check <{job_info["url"]}|the job> before notifying your ops team.')
            return

        build_info = self.server.get_build_info(self.current_job, job_info['lastBuild']['number'])
        if self.verbose_reply:
            reply(f'Build started: <{build_info["url"]}|{build_info["displayName"]}>'
                  f' with an estimated duration of {build_info["estimatedDuration"]} milliseconds.')
        else:
            reply(f'Build started: <{build_info["url"]}|{build_info["displayName"]}>')
