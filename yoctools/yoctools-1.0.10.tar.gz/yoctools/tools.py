

import os
import sys
import hashlib
import json
import time
import git
import zipfile
import codecs

try:
    from urlparse import urlparse
    import urllib
    import httplib as http
except:
    from urllib.parse import urlparse
    import urllib.request
    import http.client as http

try:
    import yaml
except:
    print("\n\nNot found pyyaml, please install: \nsudo pip install pyyaml")
    sys.exit(0)

class Conf(object):
    def __init__(self, conf):
        self.conf = conf

    def get(self, name, default):
        if name in self.conf:
            return self.conf[name]
        return default

class Board(Conf):
    def __init__(self, conf):
        Conf.__init__(self, conf)

        self.VENDOR = self.get('vendor_name', '')
        self.CHIP = self.get('chip_name', '')
        self.BOARD = self.get('board_name', '')
        self.CPU = self.get('cpu_name', '')
        self.ld_script = self.get('ld_script', '')

    def __str__(self):
        return "vendor: %s, chip: %s, cpu: %s" % (self.VENDOR, self.CHIP, self.CPU)


class BuildConfig(Conf):
    def __init__(self, conf):
        Conf.__init__(self, conf)
        self.include = self.get('include', [])
        self.cflag = self.get('cflag', '')
        self.cxxflag = self.get('cxxflag', '')
        self.asmflag = self.get('asmflag', '')
        self.define = self.get('define', [])


class package_yaml(object):
    def __init__(self, filename):
        self.conf = load_package(file)
        if self.conf == None:
            self.conf = {}


    def __getattr__(self, name):
        if name in self.conf:
            return self.conf[name]
        else:
            return None

def load_package(filename):
    # print(filename)
    if not os.path.exists(filename):
        print("not found", filename)
        return None

    with codecs.open(filename, encoding='utf-8') as fh:
        text = fh.read()
        try:
            conf = yaml.safe_load(text)

            package = {}

            def package_set(name, value):
                if value:
                    package[name] = value

            def package_conf(sets, key, name):
                if key in sets:
                    package_set(name, sets[key])

            package_conf(conf, 'name', 'name')
            package_conf(conf, 'type', 'type')
            package_conf(conf, 'description', 'description')
            package_conf(conf, 'source_file', 'SOURCES')
            package_conf(conf, 'defconfig', 'DEFCONFIG')
            package_conf(conf, 'depends', 'depends')
            package_conf(conf, 'board_name', 'board_name')

            if 'build_config' in conf:
                cflags = ''
                cppflags = ''
                asmflags = ''
                defines = ''

                build_conf = conf['build_config']

                if 'cflag' in build_conf:
                    cflags = build_conf['cflag']

                if 'cxxflag' in build_conf:
                    cppflags = build_conf['cxxflag']

                if 'asmflag' in build_conf:
                    asmflags = build_conf['asmflag']

                if 'define' in build_conf:
                    for d in build_conf['define']:
                        defines += ' -D' + d

                cflags += defines
                cppflags += defines

                package_set('CCFLAGS', cflags)
                package_set('CPPFLAGS', cppflags)
                package_conf(build_conf, 'include', 'CPPPATH')

            if 'install' in conf:
                installs = []
                for ins in conf['install']:
                    dest = ins['dest']
                    for src in ins['source']:
                        v = (dest, src)
                        installs.append(v)
                package_set('INSTALL', installs)

            if 'link_config' in conf:
                link_config = conf['link_config']
                package_conf(link_config, 'ld_script', 'LD_SCRIPT')
                package_conf(link_config, 'libs', 'LIBS')
                package_conf(link_config, 'linkflags', 'LINK_FLAGS')


            if 'board' in conf:
                package['BOARD'] = Board(conf['board'])
                package['DEFCONFIG']['CONFIG_CHIP_NAME'] = package['BOARD'].CHIP
                package['DEFCONFIG']['CONFIG_BOARD_NAME'] = package['BOARD'].BOARD
                package['DEFCONFIG']['CONFIG_VENDOR_NAME'] = package['BOARD'].VENDOR
                package['DEFCONFIG']['CONFIG_CPU'] = package['BOARD'].CPU

                package['DEFCONFIG']['CONFIG_CPU_' + package['BOARD'].CPU]='y'
                package['DEFCONFIG']['CONFIG_CHIP_' + package['BOARD'].CHIP.upper()]='y'

            return package
        except Exception as e:
            print(filename, ":", str(e))
    return None


def http2git(url):
    conn = urlparse(url)
    url = 'git@' + conn.netloc + ':' + conn.path[1:]
    return url

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
    contents = None

    try:
        with open(filename, 'r') as f:
            contents = f.read()
    except:
        pass

    if text == contents:
        return
    try:
        p = os.path.dirname(filename)
        try:
            os.makedirs(p)
        except:
            pass

        with open(filename, 'w') as f:
            f.write(text)
    except:
        print("Generate %s file failed." % filename)



def genScons(components, path, type):
    text = """#! /bin/env python

import os

components = [
%s]

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


def genSConstruct(components, path):
    text = """#! /bin/env python

import sys
import yoctools.toolchain as toolchain

defconfig = toolchain.DefaultConfig()

Export('defconfig')

paths = [
%s]

defconfig.build_package(paths)
defconfig.program()
"""

    comp_list = ''
    for _, comp in components.items():
        p = os.path.relpath(comp.path, path)
        if p != '.':
            comp_list += '    "' + p + '",\n'

    text = text % comp_list

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



def save_yoc_config(defines, filename):
    contents = ""

    try:
        with open(filename, 'r') as f:
            contents = f.read()
    except:
        pass


    text = '''/* don't edit, auto generated by tools/toolchain.py */\n
#ifndef __YOC_CONFIG_H__
#define __YOC_CONFIG_H__\n\n'''
    for k, v in defines.items():
        if v in ['y', 'Y']:
            text += '#define %s 1\n' % k
        elif v in ['n', 'N']:
            text += '// #define %s 1\n' % k
        elif type(v) == int:
            text += '#define %s %d\n' % (k, v)
        else:
            text += '#define %s "%s"\n' % (k, v)

    text += '\n#endif\n'

    if text == contents:
        return False

    write_file(text, filename)


def save_csi_config(defines, filename):
    text = '''/* don't edit, auto generated by tools/toolchain.py */

#ifndef __CSI_CONFIG_H__
#define __CSI_CONFIG_H__

#include <yoc_config.h>

#endif

'''

    write_file(text, filename)
