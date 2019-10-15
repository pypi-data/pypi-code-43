# coding=utf-8
import os
import re
import sys
import zipfile
import shutil
import time
import subprocess
import tempfile
import getopt
import sys
import platform
import datetime
from .Utils import *
from .Shell import Shell


class GIT:
    def __init__(self):
        self.is_queue = True
        self.queues = []
        self.finals = []
        self.current = None
        self.index = 0
        self.count = 0
        self.follow_queues()

    def follow_queues(self):
        self.current = self.queues
        return self

    def follow_finals(self):
        self.current = self.finals
        return self

    def clean(self, handler=None, *args):
        bins = ['git']
        bins.append('clean')
        if len(args) > 0:
            bins = bins + list(args)
        self.current.append({'handler': handler, 'bins': bins})
        return self

    def clone(self, remote_url, local_url='.', handler=None):
        bins = ['git']
        bins.append('clone')
        bins.append(remote_url)
        bins.append(local_url)
        self.current.append({'handler': handler, 'bins': bins})
        return self

    def checkout(self, branch='.', handler=None):
        bins = ['git']
        bins.append('checkout')
        bins.append(branch)
        self.current.append({'handler': handler, 'bins': bins})
        return self

    def add(self, path='.', handler=None):
        bins = ['git']
        bins.append('add')
        bins.append(path)
        self.current.append({'handler': handler, 'bins': bins})
        return self

    def merge(self, branch=None, handler=None):
        bins = ['git']
        bins.append('merge')
        if branch != None:
            bins.append(branch)
        self.current.append({'handler': handler, 'bins': bins})
        return self

    def reset(self, path='HEAD', hard=False, cached=False, handler=None):
        bins = ['git']
        bins.append('reset')
        bins.append(path)
        if hard:
            bins.append('--hard')
        if cached:
            bins.append('--cached')
        self.current.append({'handler': handler, 'bins': bins})
        return self

    def commit(self, msg='', handler=None):
        bins = ['git']
        bins.append('commit')
        bins.append('-m')
        bins.append('"' + msg + '"')
        self.current.append({'handler': handler, 'bins': bins})
        return self

    def pull(self, branch=None, handler=None):
        bins = ['git']
        bins.append('pull')
        if branch != None:
            bins.append('origin')
            bins.append(branch)
        self.current.append({'handler': handler, 'bins': bins})
        return self

    def push(self, branch=None, u=False, handler=None):
        bins = ['git']
        bins.append('push')
        if u:
            bins.append('-u')
        if branch != None:
            bins.append('origin')
            bins.append(branch)
        self.current.append({'handler': handler, 'bins': bins})
        return self

    def rev(self, handler=None, *args):
        bins = ['git']
        bins.append('rev-parse')
        if len(args) > 0:
            bins = bins + list(args)
        self.current.append({'handler': handler, 'bins': bins})
        return self

    def diff(self, branch=None, staged=False, cached=False, nameonly=True, handler=None):
        bins = ['git']
        bins.append('diff')
        if branch != None:
            bins.append(branch)
        if staged:
            bins.append('--staged')
        if cached:
            bins.append('--cached')
        if nameonly:
            bins.append('--name-only')
        self.current.append({'handler': handler, 'bins': bins})
        return self

    def run_queues(self):
        print_tag('run_queues')
        self.is_queue = True
        self.current = self.queues
        self.index = 0
        self.count = len(self.current)
        if self.count > 0:
            self.step()
        else:
            self.run_finals()

    def run_finals(self):
        print_tag('run_finals')
        self.is_queue = False
        self.current = self.finals
        self.index = 0
        self.count = len(self.current)
        if self.count > 0:
            self.step()
        else:
            self.complete_callback([])

    def run(self, complete_callback, error_callback):
        self.complete_callback = complete_callback
        self.error_callback = error_callback
        self.run_queues()

    def step(self, lines=None):
        item = self.current[self.index]
        bins = item['bins']
        handler = item['handler']
        print_tag(" ".join(bins))
        sh = Shell(bins)
        ret, lines = sh.call()
        if ret == 0:
            if handler != None:
                if handler(lines):
                    self.next(lines)
                else:
                    if self.is_queue:
                        self.run_finals()
                    else:
                        self.error_callback(item, lines)
            else:
                self.next(lines)
        else:
            self.error_callback(item, lines)

    def next(self, lines=None):
        if self.index < self.count - 1:
            self.index = self.index + 1
            self.step(lines)
        else:
            if self.is_queue:
                self.run_finals()
            else:
                self.complete_callback(lines)
