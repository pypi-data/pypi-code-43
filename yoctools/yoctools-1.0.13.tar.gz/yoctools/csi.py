#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import sys
import hashlib
import json
import time
import git
import zipfile
import codecs
import yaml
import shutil
import re

try:
    from tools import write_file
except:
    from yoctools.tools import write_file


class Driver:
    def __init__(self, tag=''):
        self.name       = ''
        self.tag        = tag
        self.vendor     = ''
        self.ip_id      = ''
        self.ip_version = ''
        self.model      = ''
        self.files      = []
        self.tests      = []

    def install(self, src_path, dest_path):
        for f in self.files:
            src = os.path.join(src_path, f.file)
            dest = os.path.join(dest_path, f.dest_file)

            file_copy3(src, dest)


    def show(self):
        print(self.tag, self.name, self.model)
        # print('    ', 'src')
        for f in self.files:
            print('    ', f.file)
        print("")


'''
driver file:    tag != '' and model != '' and chip == ''
interface file: tag == '' and model != '' and chip == ''
chip file:      tag == '' and chip != ''
'''
class File:
    def __init__(self, filename):
        self.file = filename
        self.dest_file = filename
        self.brief = ''
        self.version = ''
        self.date = ''
        self.vendor = ''
        self.name = ''
        self.ip_id = ''
        self.model = ''
        self.tag = ''
        self.chip = ''
        self.scan_file()

    def set_value(self, key, text):
        idx = text.find(key)
        if idx > 0:
            key = key[1:]
            if key in self.__dict__:
                self.__dict__[key] = text[idx + len(key) + 1:].strip()
            return True


    def get_type(self):
        if self.tag == 'HAL':
            return 'HAL_FILE'
        if self.tag == 'CHIP':
            return 'CHIP_FILE'
        if self.tag != '':
            return 'DRV_FILE'


    def scan_file(self):
        contents = ''
        try:
            with open(self.file, 'r') as f:
                contents = f.read()
        except Exception as e:
            # print(filename, str(e))
            pass

        m = re.compile("/\*([^\*]|(\*)*[^\*/])*(\*)*\*/", re.M | re.I)

        for v in m.finditer( contents ):
            for x in v.group(0).split('\n'):
                self.set_value('@brief', x) or \
                self.set_value('@version', x) or \
                self.set_value('@date', x) or \
                self.set_value('@vendor', x) or \
                self.set_value('@name', x) or \
                self.set_value('@ip_id', x) or \
                self.set_value('@tag', x) or \
                self.set_value('@model', x) or \
                self.set_value('@chip', x)

            if self.tag == '' and self.model != '':
                self.tag = 'HAL'
            if self.tag == '' and self.chip != '':
                self.tag = 'CHIP'


            if self.tag:
                break

    def show(self):
        print("tag: %s, model: %s, vendor: %s, chip: %s, file: %s" %(self.tag, self.model, self.vendor, self.chip, self.file))


class Device:
    def __init__(self, conf):
        self.conf = conf
        self.TAG = self.get('TAG', '')
        self.VERSION = self.get('VERSION', '')
        self.REGISTER_ADDRESS = self.get('REGISTER_ADDRESS', 0)
        self.IRQ_NO = self.get('IRQ_NO', -1)
        self.DEVICE_INDEX = self.get('DEVICE_INDEX', 0)

    def get(self, name, default):
        if name in self.conf:
            return self.conf[name]
        return default


class Chip:
    def __init__(self, base_path, chip_conf):
        self.chip_name = ''
        self.devices = []           # 设备列表
        self.drivers_need = {}
        self.models = {}
        self.csi_path = base_path

        self.load(chip_conf)
        self.drivers = csi_scan(base_path, self) # 驱动列表
        for d in self.devices:
            if d.TAG in self.drivers:
                d.driver = self.drivers[d.TAG]


    def load(self, filename):
        with codecs.open(filename) as fh:
            text = fh.read()
            try:
                conf = yaml.safe_load(text)
                self.chip_name = conf['chip']
                for drv in conf['devices']:
                    d = Device(drv)
                    self.devices.append(d)
                    self.drivers_need[d.TAG] = d
            except Exception as e:
                print(filename, str(e))


    def have(self, f):
        if f.chip == self.chip_name:
            return True
        if f.tag and f.tag in self.drivers_need:
            return True


    def install(self, dest_path):
        for _, v in self.drivers.items():
            v.install(self.csi_path, dest_path)
        self.genChip(dest_path)
        save_package(self, os.path.join(dest_path, 'package.yaml'))


    def show(self):
        for _, v in self.drivers.items():
            v.show()


    def genChip(self, dest_path):
        max_irq = 0
        for d in self.devices:
            if d.IRQ_NO > max_irq:
                max_irq = d.IRQ_NO

        devices = []
        for i in range(0, max_irq + 1):
            devices.append('')

        for d in self.devices:
            s = '    {%s, 0x%x, %d}' % (d.TAG, d.REGISTER_ADDRESS, d.DEVICE_INDEX)
            devices[d.IRQ_NO] = s

        fmt = '''
const device_map_t chip_device_config[] = {\n%s};
'''
        text = ''
        for i, s in enumerate(devices):
            if s:
                text += s + ',\n'
            else:
                text += '    {-1, -1, -1},\n'

        text = fmt % text

        write_file(text, os.path.join(dest_path, 'include/soc.h'))


def csi_scan(path, chip):
    driver_list = {}
    nodes = []

    # 生成所有 File
    for dirpath, _, filenames in os.walk(path):
        for name in filenames:
            filename = os.path.join(dirpath, name)
            if filename[-2:] in ['.c', '.h', '.s', '.S']:
                node = File(filename)
                if node.get_type():
                    node.file = os.path.relpath(node.file, path)
                    if  node.tag == 'CHIP':
                        filename = node.file.replace(node.vendor, '').replace(node.chip, '')
                        filename = os.path.relpath(filename, '/')
                        node.dest_file = filename
                    elif node.tag == 'HAL':
                        filename = os.path.basename(node.file)
                        node.dest_file = os.path.join('include', filename)
                    elif node.tag:
                        filename = os.path.basename(node.file)
                        node.dest_file = os.path.join('drivers', filename)

                    nodes.append(node)

    # 合并文件到 Driver
    models = {}
    for f in nodes:
        if chip.have(f):
            if f.model and f.tag != 'HAL':
                models[f.model] = True

            if f.tag not in driver_list:
                drv = Driver(f.tag)
                drv.name = f.name
                drv.model = f.model
                drv.vendor = f.vendor
                drv.ip_id = f.ip_id
                driver_list[f.tag] = drv
            else:
                drv = driver_list[f.tag]

            drv.files.append(f)

    for f in nodes:
        if f.tag == 'HAL' and f.model in models:
            if f.tag not in driver_list:
                drv = Driver(f.tag)
                drv.name = f.name
                drv.model = f.model
                drv.vendor = f.vendor
                drv.ip_id = f.ip_id
                driver_list[f.tag] = drv
            else:
                drv = driver_list[f.tag]

            drv.files.append(f)
    return driver_list


def file_copy3(src, dest):
    try:
        path = os.path.dirname(dest)
        if not os.path.exists(path):
            os.makedirs(path)
        print('install', src)
        shutil.copy2(src, dest)
        return True
    except Exception as e:
        print(str(e))


def save_package(chip, filename):
    fmt = '''
name: chip-%s
description: ''
keywords:
  - base
license: Apache license v2.0

hidden: true

depends:
  - yoc_base

build_config:
  include:
    - include
    - %s/include
  cflag: ''
  cxxflag: ''
  asmflag: ''

source_file:
%s
'''
    fs = ''
    for _, v in chip.drivers.items():
        for f in v.files:
            if f.dest_file[-2:] in ['.c', '.S']:
                fs += '  - ' + f.dest_file + '\n'
    text = fmt % (chip.chip_name, chip.chip_name, fs)
    write_file(text, filename)


def test_chip():
    chip = Chip('../../csi/csi_driver', 'chip.yaml')
    chip.show()
    chip.install('sdk')


def gen_chip_sdk():
    if len(sys.argv) > 3:
        chip = Chip(sys.argv[1], sys.argv[2])
        chip.install(sys.argv[3])

if __name__ == "__main__":
    if len(sys.argv) > 2:
        gen_chip_sdk()
    else:
        test_chip()

