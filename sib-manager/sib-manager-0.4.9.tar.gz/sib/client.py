

"""Module for Sartin'blox client app"""

import logging
import subprocess
import json
import os

logger = logging.getLogger(__name__)

class Client(object):

    def __init__(self, app_dir, build_dir='www'):

        self.folder = app_dir
        self.build_dir = build_dir
        self.deps = ['npm', 'pug', 'sass', 'babel']

    def check_dependencies(self):

        """Check if all dependencies are present"""

        ret = True
        for dep in self.deps:

            try:
                subprocess.run([dep, '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            except FileNotFoundError:
                logger.error(f'Unmet dependency "{dep}"')
                ret = False

        return ret

    def generate_config(self):

        config = {
          "development": {
            "cdn": "https://cdn.happy-dev.fr",
            "xmpp": "https://jabber.happy-dev.fr/http-bind/",
            "authority": "http://127.0.0.1:8000/openid/",
            "endpoints": {
              "businessproviders": "http://127.0.0.1:8000/businessproviders/",
              "circles": "http://127.0.0.1:8000/circles/",
              "groups": "http://127.0.0.1:8000/groups/",
              "joboffers": "http://127.0.0.1:8000/job-offers/",
              "projects": "http://127.0.0.1:8000/projects/",
              "skills": "http://127.0.0.1:8000/skills/",
              "users": "http://127.0.0.1:8000/users/"
            }
          }
        }

        return json.dumps(config, separators=(',', ':'), indent=None)

    def install(self):

        """Create a new client application"""

        if self.check_dependencies():

            # npm install
            try:
                subprocess.run(['npm', 'install'], cwd=self.folder, check=True)
            except subprocess.CalledProcessError as e:
                logger.error(e.stderr)
                raise

    def compile(self):

        """Compile the client application"""

        if self.check_dependencies():

            abs_build_dir = os.path.join(self.folder, self.build_dir)

            # compile HTML
            try:
                cmd = ['pug', '--pretty', 'src/index.pug', '-O', self.generate_config(), '--out', self.build_dir]
                subprocess.run(cmd, cwd=self.folder, env=dict(os.environ, ENV="development"), check=True)
            except subprocess.CalledProcessError as e:
                logger.error(e.stderr)
                raise

            # compile CSS
            try:
                os.mkdir(os.path.join(abs_build_dir, 'styles'))
                output = os.path.join(self.build_dir, 'styles', 'index.css')
                cmd = ['sass', 'src/styles/_index.scss', output, '--source-map']
                subprocess.run(cmd, cwd=self.folder, check=True)

            except FileExistsError: pass

            except subprocess.CalledProcessError as e:
                logger.error(e.stderr)
                raise

            # compile JS
            try:
                os.mkdir(os.path.join(abs_build_dir, 'scripts'))
                output = os.path.join(self.build_dir, 'scripts', 'index.js')
                cmd = ['sass', 'src/styles/_index.scss', output, '--source-map']
                subprocess.run(cmd, cwd=self.folder, check=True)

            except FileExistsError: pass

            except subprocess.CalledProcessError as e:
                logger.error(e.stderr)
                raise

