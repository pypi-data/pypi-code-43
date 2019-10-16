import os
import subprocess
import ruamel.yaml as ruayam


class Secrets(object):

    def __init__(self, **kwargs):

        self.__sources = list(kwargs)
        self.__kwargs = kwargs
        self.secrets = {}

        if len(self.__sources) == 0:
            raise ValueError('The secret source is missing')

        for source in self.__sources:
            self.params = self.__kwargs[source]
            getattr(self, source)()

    def __call__(self):
        return self.secrets

    def keybase(self):

        user = self.params.get('user', '')
        file = self.params.get('file', 'secrets_test.yaml')
        project = self.params.get('project', '')
        kb_path = f'/keybase/private/{user}/{file}'

        if not all(len(x) for x in (user, file, project)):
            raise ValueError('Keybase parameters missing')
        blocks = None
        out = subprocess.check_output(['keybase', 'fs', 'read', kb_path], timeout=30)
        if len(out) < 4:
            raise ValueError('Secrets file output too short')
        try:
            blocks = ruayam.round_trip_load_all(out)
        except ruayam.YAMLError as exc:
            print(exc)
            exit(1)
        for block in blocks:
            for proj, records in block.items():
                if proj in (project, 'global'):
                    self.secrets = {**self.secrets, **records}

    def envs(self):
        environs = {}
        for env, default in self.params.items():
            environs = {**environs, env: os.getenv(env, default)}
        self.secrets = {**self.secrets, **environs}
