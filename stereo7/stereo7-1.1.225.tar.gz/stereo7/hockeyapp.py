import os
import json
import fileutils
import subprocess
from management import Slack

android_task = '''curl \
    -F "status=2" \
    -F "notify=1" \
    -F "notes=None." \
    -F "notes_type=0" \
    -F "ipa=@{ipa}" \
    -H "X-HockeyAppToken: 520439d79df6430fb66b45937510cbad" \
    https://rink.hockeyapp.net/api/2/apps/{hockey_app_id}/app_versions/upload
'''

# ios_task = '''curl \
#     -F "status=2" \
#     -F "notify=1" \
#     -F "notes=None." \
#     -F "notes_type=0" \
#     -F "ipa=@ipa/{app}.ipa" \
#     -F "dsym=marines-mobile.app.dsym.zip" \
#     -H "X-HockeyAppToken: 520439d79df6430fb66b45937510cbad" \
#     https://rink.hockeyapp.net/api/2/apps/{hockey_app_id}/app_versions/upload
# '''


def hockey_app_upload(project, parser):
    if parser.platform == 'ios':
        print 'not supported hockey app upload for ios builds'
        exit(1)
    if not project.services[parser.platform].hockeyapp_id:
        exit(0)

    if not parser.ipa:
        parser.ipa = 'c:\\Build\\{project}\\outputs\\apk\\release\\{project}-release.apk'.format(
            root=fileutils.root_dir,
            project=project.project_name,
        )

    command = android_task
    command = command.replace('{ipa}', parser.ipa)
    command = command.replace('{hockey_app_id}', project.services[parser.platform].hockeyapp_id)
    print command

    result = False
    for i in xrange(5):
        result = 0 == os.system(command)
        if result:
            break

    if not result:
        print 'Cannot upload apk to hockey app'
        exit(2)


class SubprocessWrapper(object):

    def __init__(self, arguments):
        assert isinstance(arguments, list) or isinstance(arguments, str)
        if isinstance(arguments, str):
            arguments = arguments.split(' ')
        assert len(arguments) > 0
        self.arguments = arguments
        self.process = subprocess.Popen(arguments, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.out = ''
        self.err = ''
        self.code = 0

    def call(self):
        try:
            self.out, self.err = self.process.communicate()
            self.out = self.out.decode('utf-8') if self.out else ''
            self.err = self.err.decode('utf-8') if self.err else ''
            self.code = self.process.returncode
        except Exception as e:
            print e
            self.out, self.err = ('Timeout', 'Timeout')
            self.code = -1

        return self.code


def request(request_name, request_args, return_json):
    print 'Request: ' + request_name
    process = SubprocessWrapper(request_args)
    process.call()
    print 'Out:'
    print process.out
    print 'Err:'
    print process.err
    print '-----------------------------------------------------------------'
    if return_json:
        return json.loads(process.out)
    return None


def upload(APK_PATH, app_name, app_token):
    try:
        APP_NAME = app_name
        APP_TOKEN = app_token
        REQUEST_UPLOAD_ID = [
            "curl",
            "-X",
            "POST",
            "--header",
            "Content-Type: application/json",
            "--header",
            "Accept: application/json",
            "--header",
            "X-API-Token: " + APP_TOKEN,
            "https://api.appcenter.ms/v0.1/apps/gushchin-dmitry-sih2/%s/release_uploads" % APP_NAME,
        ]

        js = request('Get Upload ID', REQUEST_UPLOAD_ID, True)
        UPLOAD_ID = js['upload_id']
        UPLOAD_URL = js['upload_url']
        REQUEST_UPLOAD_APK = [
            "curl",
            "-F",
            "notify=1",
            "-F",
            "ipa=@" + APK_PATH,
            UPLOAD_URL,
        ]
        request('Upload APK', REQUEST_UPLOAD_APK, False)

        REQUEST_COMMIT = [
            "curl",
            "-X",
            "PATCH",
            "--header",
            "Content-Type: application/json",
            "--header",
            "Accept: application/json",
            "--header",
            "X-API-Token: " + APP_TOKEN,
            '-d { "status": "committed" }',
            "https://api.appcenter.ms/v0.1/apps/gushchin-dmitry-sih2/{APP_NAME}/release_uploads/{UPLOAD_ID}".format(APP_NAME=APP_NAME, UPLOAD_ID=UPLOAD_ID),
        ]
        js = request('Commit changes', REQUEST_COMMIT, True)
        RELEASE_URL = js['release_url']
        RELEASE_ID = js['release_id']

        REQUEST_PUBLISH = [
            "curl",
            "-X",
            "PATCH",
            "--header",
            "Content-Type: application/json",
            "--header",
            "Accept: application/json",
            "--header",
            "X-API-Token: " + APP_TOKEN,
            '-d { "destination_name": "Distribution-Group", "release_notes": "None release notes" }',
            "https://api.appcenter.ms/" + RELEASE_URL,
        ]
        js = request('Publish changes', REQUEST_PUBLISH, True)
        if not js:
            print 'not valid response from AppCenter'
            exit(1)
        return 'https://install.appcenter.ms/users/gushchin-dmitry-sih2/apps/{}/releases/{}'.format(APP_NAME, RELEASE_ID)
    except Exception as e:
        print '-----------------'
        print 'Exception: '
        print e
        print '-----------------'
        exit(2)


def appcenter_upload(project, parser):
    if parser.platform == 'ios':
        print 'not supported appcenter upload for ios builds'
        exit(1)
    if not project.services[parser.platform].appcenter_app_name:
        print 'Please define appcenter_app_name in project.json'
        exit(1)
    if not project.services[parser.platform].appcenter_token:
        print 'Please define appcenter_token in project.json'
        exit(1)

    apk = 'c:\\Build\\{project}\\outputs\\apk\\release\\{project}-release.apk'.format(
        root=fileutils.root_dir,
        project=project.project_name,
    )
    upload(apk,
           project.services[parser.platform].appcenter_app_name,
           project.services[parser.platform].appcenter_token)


if __name__ == '__main__':
    app_name = 'Syndicate-4'
    app_token = '4920850305a640b6becc75f9c2d02b666dc67577'
    upload('syndicate4-release.apk', app_name, app_token)
