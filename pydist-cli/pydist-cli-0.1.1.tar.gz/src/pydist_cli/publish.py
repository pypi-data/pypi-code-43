import os
import subprocess
import sys
import shutil

from pydist_cli.settings import pypi


def build():
    try:
        subprocess.run([sys.executable, 'setup.py', 'sdist', 'bdist_wheel'])
    finally:
        shutil.rmtree('build')


def check(dists):
    subprocess.run([sys.executable, '-m', 'twine', 'check', *dists], check=True)


def upload(settings, dists):
    subprocess.run([
        sys.executable, '-m', 'twine', 'upload',
        # PyPI uses a different upload URL from its base URL, so if we use PyPI don't override the default URL.
        # TODO: handle other indices with this distinction.
        *([] if settings['index'] == pypi else ['--repository-url', settings['index']]),
        '--username', settings['username'] or 'null',
        '--password', settings['api_key'],
        *dists,
    ], check=True)


def publish(settings):
    dist_exists = os.path.exists('dist')
    if not dist_exists:
        build()

    dists = [os.path.join('dist', f) for f in os.listdir('dist')]
    try:
        check(dists)
        upload(settings, dists)
    finally:
        # only clean up dist/ if we built it.
        if not dist_exists:
            shutil.rmtree('dist')
