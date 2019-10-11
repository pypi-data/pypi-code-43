import json
import os
import shutil
import hashlib
import random
from string import ascii_lowercase

from .pyboard import Pyboard
from . import snippets


########################################################################
class UPython:
    """"""

    ROOT = 'root'
    HASHFILE = '.upython'
    EQUAL = 'equal'
    REMOVED = 'removed'
    ADDED = 'added'
    MODIFIED = 'modified'

    # ----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.connect()

    # ----------------------------------------------------------------------
    def connect(self):
        """"""
        for port in range(15):
            try:
                self.pyb = Pyboard(f'/dev/ttyUSB{port}')
                return
            except:
                pass

    # ----------------------------------------------------------------------
    def pull(self):
        """"""
        response = self.run_snippet(snippets.walk)

        shutil.rmtree(self.ROOT, ignore_errors=True)
        os.makedirs(self.ROOT, exist_ok=True)

        print('[pull]')
        hashfiles = {}
        for _, file, path in response[0]['response']:
            if path:
                p, h = self.touch(path)
                hashfiles[p] = h
                print(f'pulled {path}')

        print('\n')

        json.dump(hashfiles, open(self.HASHFILE, 'w'), indent=2)

    # ----------------------------------------------------------------------
    def touch(self, path):
        """"""
        full_path = os.path.join(self.ROOT, path[1:])
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        content = self.run_snippet(snippets.readfile, path)['response']

        with open(full_path, 'w') as file:
            file.write(content)
            return full_path, self.hash_file(content)

    # ----------------------------------------------------------------------
    def run_snippet(self, snippet, *args, **kwargs):
        """"""
        self.pyb.enter_raw_repl()
        r = self.pyb.exec(snippet.format(*args, **kwargs))
        if r:
            try:
                response = json.loads(r)
            except:
                response = r
        else:
            response = {}
        self.pyb.exit_raw_repl()
        return response

    # ----------------------------------------------------------------------
    def hash_file(self, content):
        """"""
        hasher = hashlib.md5()
        hasher.update(content.encode())
        return hasher.hexdigest()

    # ----------------------------------------------------------------------
    def status(self, silent=False):
        """"""
        remote_hashfiles = json.load(open(self.HASHFILE, 'r'))
        local_hashfiles = {}

        for root, dirs, files in os.walk(self.ROOT, topdown=False):
            for name in files:
                filename = os.path.join(root, name)
                with open(filename, 'r') as file:
                    local_hashfiles[filename] = self.hash_file(file.read())

        modified = {}

        for key in local_hashfiles:

            if not key in remote_hashfiles:
                modified[key] = self.ADDED

            elif remote_hashfiles[key] != local_hashfiles[key]:
                modified[key] = self.MODIFIED

            else:
                modified[key] = self.EQUAL

        for key in remote_hashfiles:

            if not key in modified:
                modified[key] = self.REMOVED

        if not silent:
            print("[status]")
            mod = 0
            add = 0
            eql = 0
            for k in modified:
                if modified[k] != self.EQUAL:
                    print(f'{k}: {modified[k]}')

                    if modified[k] == self.MODIFIED:
                        mod += 1
                    if modified[k] == self.ADDED:
                        add += 1
                else:
                    eql += 1

            print('-' * 70)
            if add:
                print(f'{add} file(s) added')
            if mod:
                print(f'{mod} file(s) modified')
            if eql:
                print(f'{eql} file(s) unchanged')
            print('\n')

        return modified

    # ----------------------------------------------------------------------
    def push(self):
        """"""
        modified = self.status(silent=True)

        print('[push]')
        m = 0
        for k in modified:
            if modified[k] != 'equal':
                m += 1
        if not m:
            print('No modified files')
            print('\n')
            return

        for filename in modified:
            status = modified[filename]

            remote_filename = filename.replace(self.ROOT, "", 1)

            # files in root must no have / in the name
            if remote_filename.count('/') == 1 and remote_filename[0] == '/':
                remote_filename = remote_filename[1:]

            if status in [self.ADDED, self.MODIFIED]:
                with open(filename, 'r') as file:
                    content = file.read()
                    print(f'writting {len(content)} bytes in {remote_filename}')
                    self.run_snippet(snippets.writefile, remote_filename, content)

            elif status == self.REMOVED:
                print(f'removing {remote_filename}')
                self.run_snippet(snippets.removefile, remote_filename)
        print('\n')
        # self.status(silent=True)

    # ----------------------------------------------------------------------
    def run(self, filename):
        """"""
        if filename.startswith(self.ROOT):
            filename = filename.replace(self.ROOT, '')

        path, filename = os.path.split(filename)
        tmp_filename = ''.join([random.choice(ascii_lowercase) for _ in range(8)])

        response = self.run_snippet(snippets.runfile, path, filename.replace('.py', ''), tmp_filename)
        if response:
            try:
                print(response.decode())
            except:
                print(response)
