#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import sys
import hashlib
import json
import time
import git
import zipfile

try:
    from urlparse import urlparse
    import urllib
    import httplib as http
except:
    from urllib.parse import urlparse
    import urllib.request
    import http.client as http
try:
    from toolchain import load_package
except:
    from yoctools.toolchain import load_package

class YoC:
    def __init__(self, path=''):
        self.path = path
        self.occ = None
        self.occ_components = None

        self.components = ComponentGroup()
        try:
            for path in ['components', 'solutions', 'boards']:
                files = os.listdir(os.path.join(self.path, path))
                for component_name in files:
                    comp_path = os.path.join(self.path, path, component_name)
                    if os.path.isdir(comp_path):
                        pack = Component(comp_path)
                        self.components.add(pack)
        except:
            pass


    def add_component(self, name):
        self.download_list()

        if self.components.get(name) == None:
            pack = self.occ_components.get(name)
            if pack:
                for dep in pack.depends:
                    self.add_component(dep['name'])
                self.components.add(pack)


    def update(self):
        for _, pack in self.components.items():
            pack.download()
        genScons(self.components, os.path.join(self.path, 'components'), 'common')
        # genScons(self.components, os.path.join(self.path, 'solutions'), 'solution')
        genScons(self.components, os.path.join(self.path, 'boards'), 'board')
        # genSConstruct(self.path)
        # genMakefile(self.path)


    def download_list(self):
        if self.occ == None:
            self.occ = OCC('occ.t-head.cn')
            # self.occ = OCC('cid.c-sky.com')
            self.occ_components = self.occ.yocComponentList('614193542956318720')


    def list(self):
        for _, pack in self.components.items():
            pack.show()


class Component:
    def __init__(self, path=''):
        self.name = ''
        self.depends = []
        self.description = ''
        self.versions = ''
        self.license = ''
        self.historyVersion = {}
        self.updated = ''
        self.repo_url = ''
        self.repo = None
        self.path = path
        self.type = 'common'
        self.yoc_version = ''
        self.pack = None

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
                origin = self.repo.create_remote(name='origin', url=self.repo_url)
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
        print("%s %s %s - %s" % (status, s1, ' ' * (40 - size), self.description[:60]))
        size = len(self.description)
        begin = 60
        while True:
            if begin < size:
                print(' ' * 46 + self.description[begin:begin+60])
                begin += 60
            else:
                break


    def load_package(self):
        filename = os.path.join(self.path, 'package.yaml')
        # print(filename)
        self.package = load_package(filename)
        if self.package == None:
            return


        def package_get(name, value):
            if name in self.package.keys():
                return self.package[name]
            return value

        self.name = package_get('name', self.name)
        self.description = package_get('description', self.description)
        self.yoc_version = package_get('yoc_version', '')
        self.versions = self.repo.active_branch.name
        dep = package_get('depends', None)
        # if dep:
        #     print(dep)


class ComponentGroup:
    def __init__(self):
        self.components = {}

    def add(self, pack):
        self.components[pack.name] = pack

    def get(self, name):
        if name in self.components:
            return self.components[name]

    def show(self):
        for _, pack in self.components.items():
            pack.show()

    def items(self):
        return self.components.items()

    def download(self, name):
        if name in self.components:
            pack = self.components[name]
            if pack:
                pack.download()


class OCC:
    def __init__(self, host=None):
        if host:
            self.host = host
        else:
            self.host = 'occ.t-head.cn'

    def yocComponentListUpload(self):
        cmd = '/api/resource/cdk/yocComponent/common/upload'
        body = {
             "model": {
                 "name":"CH2201",
                 "version":"version"
                }
        }
        text = json.dumps(body)

        js = self.request(get_url(cmd, text), text)


    def yocGetInfo(self, name):
        cmd = '/api/resource/component/getInfo'
        body = {}
        js = self.request(get_url(cmd, body), body)


    def yocComponentList(self, chipId):
        cmd = '/api/resource/cdk/yocComponentList'
        body = {}
        text = json.dumps(body)


        js = self.request(get_url(cmd, text), text)

        packs = ComponentGroup()
        for p in js:
            pack = Component()
            pack.loader_json(p)
            packs.add(pack)
        return packs


    def request(self, url, body):
        connection = http.HTTPSConnection(self.host)

        try:
            connection.request('POST', url, body)
            response = connection.getresponse()
            if response.status == 200:
                text = response.read()
                js = json.loads(text)
                # print(js)

                if js['code'] == 0:
                    return js['result']['packages']
        except:
            print("network faild.")
            exit(0)
        return {}


def MD5(str):
    hl = hashlib.md5()
    hl.update(str.encode(encoding='utf-8'))
    return hl.hexdigest()


def get_url(cmd, body):
    timestamp = time.strftime('%Y-%m-%d_%H:%M:%S',time.localtime(time.time()))
    md5 = MD5(cmd + timestamp + body)
    return '%s?timestamp=%s&sign=%s&chipId=614193542956318720' % (cmd, timestamp, md5)


def http_get(url, path):
    conn = urlparse(url)

    if conn.scheme == "https":
        connection = http.HTTPSConnection(conn.netloc)
    else:
        connection = http.HTTPConnection(conn.netloc)

    connection.request('GET', conn.path)
    response = connection.getresponse()

    filename = os.path.join(path, os.path.basename(conn.path))

    try:
        with open(filename, 'wb') as f:
            f.write(response.read())
    except:
        pass

    return filename


def dfs_get_zip_file(input_path,result):
    files = os.listdir(input_path)
    for file in files:
        if os.path.isdir(input_path + '/' + file):
            dfs_get_zip_file(input_path + '/' + file,result)
        else:
            result.append(input_path + '/' + file)


def zip_path(input_path, zipName):
    if os.path.isdir(input_path):
        f = zipfile.ZipFile(zipName, 'w', zipfile.ZIP_DEFLATED)
        filelists = []
        dfs_get_zip_file(input_path, filelists)
        for file in filelists:
            f.write(file)
        f.close()


def write_file(text, filename):
    try:
        with open(filename, "w") as f:
            f.write(text)
    except:
        pass


def genScons(components, path, type):
    text = """#! /bin/env python

import os

components = [
%s
]

for d in components:
    file_name = os.path.join(d, 'SConscript')
    if os.path.isfile(file_name):
        SConscript(file_name, duplicate=0)
"""

    comp_list = ''
    for _, comp in components.items():
        if comp.type == type:
            comp_list += '    "' + comp.name + '",\n'

    text = text % comp_list

    script_file = os.path.join(path, 'SConscript')
    write_file(text, script_file)


def genSConstruct(path):
    text = """#! /bin/env python

import yoctools.toolchain as toolchain

defconfig = toolchain.DefaultConfig()

Export('defconfig')

paths = [
    'boards',
    'components',
    'solutions',
]

defconfig.build_package(paths)
"""

    script_file = os.path.join(path, 'SConstruct')
    write_file(text, script_file)


def genMakefile(path):
    text = """CPRE := @
ifeq ($(V),1)
CPRE :=
endif


.PHONY:startup
startup: all

all:
	$(CPRE) toolchain yoc_sdk
	$(CPRE) scons -j4
	@echo YoC SDK Done


.PHONY:clean
clean:
	$(CPRE) rm yoc_sdk -rf
	$(CPRE) scons -c
	$(CPRE) find . -name "*.[od]" -delete

%:
	$(CPRE) scons --component="$@" -j4
"""

    script_file = os.path.join(path, 'Makefile')
    write_file(text, script_file)


def usage():
    print("Usage:")
    print("  yoc <command> [options]\n")
    print("Commands:")
    print("  install                     Install component.")
    print("  uninstall                   Uninstall component.")
    print("  list                        List all packages")
    print("")

    print("General Options:")
    print("  -h, --help                  Show help.")

def main():
    argc = len(sys.argv)
    if argc < 2:
        usage()
        exit(0)

    if sys.argv[1] == 'list':
        occ = OCC('occ.t-head.cn')
        components = occ.yocComponentList('614193542956318720')
        components.show()
    elif sys.argv[1] == 'lo':
        yoc = YoC()
        yoc.list()
    elif sys.argv[1] in ['install', 'download']:
        if argc >= 3:
            yoc = YoC()
            yoc.add_component(sys.argv[2])
            yoc.update()
            print("%s download Success!" % sys.argv[2])


if __name__ == "__main__":
    main()