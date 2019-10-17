import os
import sys
import json
import time
import git
import zipfile

import os
import sys
import codecs
from shutil import copyfile

try:
    from tools import *
except:
    from yoctools.tools import *


class Component:
    def __init__(self, path=''):
        self.name = ''
        self.path = path
        self.type = 'common'
        self.depends = []
        self.description = ''
        self.versions = ''
        self.license = ''
        self.historyVersion = {}
        self.updated = ''
        self.repo_url = ''
        self.repo = None
        self.yoc_version = ''
        self.includes = []
        self.sources = []
        self.defconfig = []
        self.AFLAGS = ''
        self.CFLAGS = ''
        self.CXXFLAGS = ''
        self.LDFLAGS = ''
        self.ld_script = ''
        self.depends_on = []  # 该组件被哪个组件依赖

        if self.path:
            self.update_aone()
            self.load_package()


    def loader_json(self, js):
        self.js = js
        self.name = js['name']
        self.depends = js['depends']
        self.description = js['description']
        self.versions = js['versions']
        self.license = js['license']
        self.repo_url = js['aboutURL']

        self.updated = js['updated']

        for ver in js['historyVersion']:
            self.historyVersion[ver['version']] = ver['url']

        if self.name == 'yoc_base':
            self.depends = [
                {"name": "minilibc", "version": "master"},
                {"name": "aos", "version": "master"},
                {"name": "csi", "version": "master"},
                {"name": "rhino", "version": "master"},
                {"name": "lwip", "version": "master"},
            ]
            # print(json.dumps(js, indent=4))

        if self.name == "helloworld":
            self.type = "solution"
            self.depends = [
                {"name": "yunvoice_cpu0", "version": "master"},
                {"name": "chip-yunvoice", "version": "master"},
                {"name": "netmgr", "version": "master"},
            ]

        if self.name == 'chip-yunvoice':
            self.depends = [
                {"name": "yoc_base", "version": "master"},
            ]

        if self.name == 'yunvoice_cpu0':
            self.depends =  [
                {"name": "chip-yunvoice", "version": "master"},
            ]
            self.type = 'board'

        if self.type == "common":
            self.path = 'components/' + self.name
        elif self.type == 'chip':
            self.path = 'chip/' + self.name
        elif self.type == 'board':
            self.path = 'boards/' + self.name
        elif self.type == 'solution':
            self.path = 'solutions/' + self.name
        else:
            self.path = 'components/' + self.name


    def download(self):
        if self.repo_url:
            if (not os.path.exists(self.path)) or (not os.path.isdir(os.path.join(self.path, '.git'))):
                print('git clone %s (%s)...' % (self.name, self.versions))
                self.repo = git.Repo.init(self.path)
                origin = self.repo.create_remote(name='origin', url=http2git(self.repo_url))
                origin.fetch()

                self.repo.create_head(self.versions, origin.refs.master)  # create local branch "master" from remote "master"
                self.repo.heads.master.set_tracking_branch(origin.refs.master)  # set local "master" to track remote "master
                self.repo.heads.master.checkout()  # checkout local "master" to working tree
        elif self.versions in self.historyVersion.keys():
            zip_url = self.historyVersion[self.versions]
            filename = http_get(zip_url, '.cache')
            zipf = zipfile.ZipFile(filename)
            if self.path != '.':
                zipf.extractall('components/')
            else:
                zipf.extractall('.')


    def update_aone(self):
        if self.repo == None:
            self.repo = git.Repo.init(self.path)

        try:
            aone = self.repo.remotes['aone']
        except:
            aone_url = 'git@gitlab.alibaba-inc.com:yoc7/' + self.name + '.git'
            aone = self.repo.create_remote(name='aone', url=aone_url)


    def zip(self):
        path = 'components/' + self.name
        zipName = '.cache/' + self.name + "-" + self.versions + ".zip"
        zip_path(path, zipName)

        return zipName


    def show(self):
        if os.path.isdir(self.path):
            status = '*'
        else:
            status = ' '

        s1 = self.name + ' (' + self.versions + ')'
        size = len(s1)

        text1, text2 = string_strip(self.description, 80)
        print("%s %s %s - %s" % (status, s1, ' ' * (40 - size), text1))
        while text2:
            text1, text2 = string_strip(text2, 80)
            print(' ' * 46 + text1)


    def load_package(self):
        filename = os.path.join(self.path, 'package.yaml')
        self.package = load_package(filename)
        if self.package == None:
            return

        def package_get(name, value):
            if name in self.package.keys():
                return self.package[name]
            return value

        self.name = package_get('name', self.name)
        self.type = package_get('type', self.type)
        self.description = package_get('description', self.description)
        self.yoc_version = package_get('yoc_version', '')
        self.versions    = self.repo.active_branch.name
        self.depends     = package_get('depends', [])
        self.includes    = package_get('CPPPATH', '')
        self.sources     = package_get('SOURCES', [])
        self.defconfig   = package_get('DEFCONFIG', [])
        self.board_name  = package_get('board_name', '')
        self.board       = package_get('BOARD', None)
        if self.board:
            self.ld_script = os.path.join(self.path, self.board.ld_script)

        self.AFLAGS   = package_get('AFLAGS', '')
        self.CFLAGS   = package_get('CFLAGS', '')
        self.CCFLAGS  = package_get('CCFLAGS', '')
        self.CXXFLAGS = package_get('CXXFLAGS', '')
        self.LDFLAGS  = package_get('LDFLAGS', '')


class ComponentGroup:
    def __init__(self):
        self.components = {}

    def add(self, component):
        self.components[component.name] = component

    def get(self, name):
        if name in self.components:
            return self.components[name]

    def remove(self, name):
        if name in self.components:
            del self.components[name]

    def show(self):
        for _, component in self.components.items():
            component.show()

    def items(self):
        return self.components.items()

    def download(self, name):
        if name in self.components:
            component = self.components[name]
            if component:
                component.download()


    def calc_depend(self):
        for _, component in self.components.items():
            component.depends_on = []
        for _, component in self.components.items():
            for dep in component.depends:
                p = self.get(dep)
                if p:
                    p.depends_on.append(component)



def string_strip(text, size):
    L = 0
    R = ''
    i = 0
    for c in text:
        if c >= '\u4E00' and c <= '\u9FA5':
            # print(c)
            L += 2
        else:
            # print('  ', c)
            L += 1
        R += c
        i += 1
        if L >= size:
            break
    return R, text[i:]


def test():
    str_test = 'Opus是一个完全开放的、免费的、多功能的音频编解码器'
    while str_test:
        T, str_test = string_strip(str_test, 20)
        print(T, str_test)


if __name__ == "__main__":
    test()