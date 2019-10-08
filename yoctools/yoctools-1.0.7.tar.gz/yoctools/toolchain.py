#! /bin/env python

import os
import sys
import codecs
from shutil import copyfile

try:
    import SCons.Script as scons

    scons.AddOption('--verbose', dest='verbose', default=True,
        action='store_false',
        help='verbose command line output')

    scons.AddOption('--component',
            dest='component',
            type='string',
            nargs=1,
            action='store',
            help='compile component list.')
except:
    pass
try:
    import yaml
except:
    print("\n\nNot found pyyaml, please install: \nsudo pip install pyyaml")
    sys.exit(0)

# toolchains options
CROSS_TOOL_PATH   = '/opt/gcc-csky-abiv2/bin'


class Build(object):
    def __init__(self, tool):
        self.conf = tool
        self.env = tool.env.Clone()
        self.YOC_SDK = tool.YOC_SDK
        self.BUILD = 'release'
        self.INSTALL_PATH = tool.INSTALL_PATH
        self.lib_path = tool.lib_path
        # self.yoc_lib_path = os.path.join(tool.YOC_SDK, "lib/" + self.conf.CHIP + '/' + self.conf.CPU)
        self.yoc_lib_path = os.path.join(tool.YOC_SDK, "lib/")

        self.env.Replace(
            AS   = self.conf.AS, ASFLAGS = self.conf.AFLAGS,
            CC   = self.conf.CC, CCFLAGS = self.conf.CFLAGS,
            CXX  = self.conf.CXX, CXXFLAGS = self.conf.CXXFLAGS,
            AR   = self.conf.AR, ARFLAGS = '-rc',
            LINK = self.conf.LINK, LINKFLAGS = self.conf.LDFLAGS
        )

        self.env.PrependENVPath('TERM', "xterm-256color")
        self.env.PrependENVPath('PATH', os.getenv('PATH'))

        self.def_includes = [
            'boards/' + self.conf.BOARD + '/include',
            'include/csi/chip/' + self.conf.CHIP,
            'include',
            'include/csi',
            'include/rhino',
        ]
        for p in self.def_includes:
            path_name = os.path.join(self.YOC_SDK, p)
            self.env.Append(CPPPATH=[path_name])

    def SetInstallPath(self, path):
        if not path:
            path = self.YOC_SDK
        self.INSTALL_PATH = path
        # self.lib_path = os.path.join(path, "lib/" + self.conf.CHIP + '/' + self.conf.CPU)
        self.lib_path = os.path.join(path, "lib")

    def library(self, name, src, **parameters):
        group = parameters

        objs = None

        if name and src:
            if 'CCFLAGS' in group:
                self.env.AppendUnique(CCFLAGS = ' ' + group['CCFLAGS'])
            if 'CPPPATH' in group:
                if type(group['CPPPATH']) == type('str'):
                    self.env.AppendUnique(CPPPATH=group['CPPPATH'])
                else:
                    for path in group['CPPPATH']:
                        self.env.AppendUnique(CPPPATH=path)

            if 'CPPFLAGS' in group:
                self.env.AppendUnique(CPPFLAGS=' ' + group['CPPFLAGS'])
            objs = self.env.StaticLibrary(os.path.join(self.lib_path, name), src)

        jobs = []
        if objs:
            jobs += objs

        if 'INSTALL' in group:
            for ins in group['INSTALL']:
                inc_path = os.path.join(self.INSTALL_PATH, ins[0])
                file_list = []
                if type(ins[1]) == str:
                    file_list = self.env.Glob(ins[1])
                else:
                    file_list = ins[1]
                jobs += self.env.Install(inc_path, file_list)


        self.env.Default(jobs)

        return objs


    def program(self, name, source, **parameters):
        if 'CPPPATH' in parameters:
            for path in parameters['CPPPATH']:
                self.env.AppendUnique(CPPPATH=path)
            del parameters['CPPPATH']

        parameters['LIBPATH'] = self.yoc_lib_path + ':' + self.lib_path

        linkflags =  ' -Wl,--whole-archive -l' + ' -l'.join(parameters['LIBS'])
        linkflags += ' -Wl,--no-whole-archive -nostartfiles -Wl,--gc-sections -lm '

        if 'LD_SCRIPT' in parameters:
            linkflags += ' -T ' + parameters['LD_SCRIPT']
            del parameters['LD_SCRIPT']

        linkflags += ' -Wl,-ckmap="yoc.map" -Wl,-zmax-page-size=1024'

        self.env.AppendUnique(LINKFLAGS=linkflags)

        del parameters['LIBS']

        v = self.env.Program(target=name, source=source, **parameters)

        self.env.Default(v)

class DefaultConfig(object):
    def __init__(self):
        if os.getenv('YOC_SDK'):
            self.YOC_SDK = os.getenv('YOC_SDK')
        else:
            self.YOC_SDK = os.path.abspath("yoc_sdk")

        self.env = scons.Environment(tools = ['default'])

        if scons.GetOption('verbose'):
            self.env.Replace(
                ARCOMSTR = 'AR $TARGET',
                ASCOMSTR = 'AS $TARGET',
                ASPPCOMSTR = 'AS $TARGET',
                CCCOMSTR = 'CC $TARGET',
                CXXCOMSTR = 'CXX $TARGET',
                # LINKCOMSTR = 'LINK $TARGET',
                # INSTALLSTR = 'INSTALL $TARGET'
            )

        self.INSTALL_PATH = self.YOC_SDK

        self.CROSS_TOOL_PATH = CROSS_TOOL_PATH
        self.PREFIX  = 'csky-elfabiv2-'
        self.CC      = self.PREFIX + 'gcc'
        self.CXX     = self.PREFIX + 'g++'
        self.AS      = self.PREFIX + 'gcc'
        self.AR      = self.PREFIX + 'ar'
        self.LINK    = self.PREFIX + 'g++'
        self.SIZE    = self.PREFIX + 'size'
        self.OBJDUMP = self.PREFIX + 'objdump'
        self.OBJCPY  = self.PREFIX + 'objcopy'
        self.STRIP   = self.PREFIX + 'strip'
        self.CFLAGS  = ''
        self.DEBUG   = 'release'

        self.yoc_compile_flags = \
            ' -ffunction-sections -fdata-sections' + \
            ' -g -Wpointer-arith -Wundef -Wall -Wl,-EL' + \
            ' -fno-inline-functions -nostdlib -fno-builtin -mistack' + \
            ' -fno-strict-aliasing -fno-strength-reduce'

        self.conf = {}

        self.load_config('')
        self.SetInstallPath(self.YOC_SDK)

    def GenConfig(self):
        config_file = os.path.join(self.YOC_SDK, 'include/yoc_config.h')
        if self.save_yoc_config(config_file):
            config_file = os.path.join(self.YOC_SDK, 'include/csi_config.h')
            self.save_csi_config(config_file)

    def SetInstallPath(self, path):
        if not path:
            path = self.YOC_SDK
        self.INSTALL_PATH = path
        # self.lib_path = os.path.join(path, "lib/" + self.CHIP + '/' + self.CPU)
        self.lib_path = os.path.join(path, "lib/")

    def yoc_path(self, path):
        return os.path.join(self.YOC_SDK, path)

    def load_config(self, conf_file):
        try:
            pack = load_package('package.yaml')

            self.CHIP = pack['BOARD'].CHIP
            self.BOARD = pack['BOARD'].BOARD
            self.VENDOR = pack['BOARD'].VENDOR
            self.CPU = pack['BOARD'].CPU.lower()

            for line in pack['DEFCONFIG']:
                line = line.strip()
                if len(line) > 0 and line[0] != "#":
                    kv = line.split('=')
                    if len(kv) >= 2:
                        self.conf[kv[0]] = kv[1]
                        if kv[0] == 'CONFIG_CHIP_NAME':
                            self.CHIP = eval(kv[1])
                        elif kv[0] == 'CONFIG_BOARD_NAME':
                            self.BOARD = eval(kv[1])
                        elif kv[0] == 'CONFIG_VENDOR_NAME':
                            self.VENDOR = eval(kv[1])
                        elif kv[0][:10] == 'CONFIG_CPU':
                            self.CPU = kv[0][11:].lower()

            self.set_cpu()

            # print(self.CHIP, self.BOARD, self.VENDOR, self.CPU)
        except :
            print("Open defconfig file failed.")

        if not self.CHIP:
            print("no defind `CONFIG_CHIP_NAME` in defconfig")
            exit(-1)

        if not self.BOARD:
            print("no defind `CONFIG_BOARD_NAME` in defconfig")
            exit(-1)

        if not self.VENDOR:
            print("no defind `CONFIG_VENDOR_NAME` in defconfig")
            exit(-1)

    def __getattr__(self, name):
        if name in self.conf:
            return self.conf[name]
        else:
            return None


    def set_cpu(self):
        if self.CPU in ['ck801', 'ck802', 'ck803', 'ck805', 'ck803f', 'ck803ef', 'ck803efr1', 'ck803efr2', 'ck803efr3', 'ck804ef', 'ck805f']:
            DEVICE = '-mcpu=' + self.CPU
            if 'f' in self.CPU:
                DEVICE += ' -mhard-float'

            if self.CPU == 'ck803ef':
                DEVICE += ' -mhigh-registers -mdsp'
        else:
            print ('Please make sure your cpu mode')
            exit(0)


        self.CFLAGS  = ' -MP -MMD ' + DEVICE
        self.AFLAGS  = ' -c ' + DEVICE
        self.LDFLAGS  = DEVICE

        if self.BUILD == 'debug':
            self.CFLAGS += ' -O0 -g'
        else:
            self.CFLAGS += ' -Os'

        self.CFLAGS  += self.yoc_compile_flags
        self.CXXFLAGS = self.CFLAGS

    def build(self):
        return Build(self)

    def library(self, name, src, **parameters):
        build = Build(self)
        build.library(name, src, **parameters)

    def library_yaml(self):
        build = Build(self)
        pack = load_package('package.yaml')
        if pack:
            name = pack['name']

            sources = []
            for src in pack['SOURCES']:
                for f in self.env.Glob(src):
                    sources.append(f)


            del pack['name']
            del pack['SOURCES']

            build.library(name, sources, **pack)

    def program(self, **parameters):
        build = Build(self)
        pack = load_package('package.yaml')

        if pack:
            name = pack['name']
            source = pack['SOURCES']
            del pack['name']
            del pack['SOURCES']

            build.program(name, source, **pack)

    def build_package(self, packages):
        for d in packages:
            file_name = os.path.join(d, 'SConscript')
            if os.path.isfile(file_name):
                scons.SConscript(file_name, exports={"env" : self.env.Clone()})

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

            package_conf(conf, 'name', 'name')
            package_conf(conf, 'source_file', 'SOURCES')
            package_conf(conf, 'defconfig', 'DEFCONFIG')
            package_conf(conf, 'description', 'description')
            package_conf(conf, 'depends', 'depends')

            # if 'depends' in package:
            #     if 'LIBS' not in package:
            #         package['LIBS'] = []
            #     for dep in conf['depends']:
            #         package['LIBS'].append(dep)

            if 'board' in conf:
                package['BOARD'] = Board(conf['board'])
                package['DEFCONFIG']['CONFIG_CHIP_NAME'] = package['BOARD'].CHIP
                package['DEFCONFIG']['CONFIG_BOARD_NAME'] = package['BOARD'].BOARD
                package['DEFCONFIG']['CONFIG_VENDOR_NAME'] = package['BOARD'].VENDOR
                package['DEFCONFIG']['CONFIG_CPU'] = package['BOARD'].CPU

                package['DEFCONFIG']['CONFIG_CPU_' + package['BOARD'].CPU]='y'
                package['DEFCONFIG']['CONFIG_CHIP_' + package['BOARD'].CHIP.upper()]='y'

                if 'board_name' in conf['board']:
                    board_name = conf['board']['board_name']
                    if package['name'] != conf['board']['board_name']:
                        board_pack_file = conf['board']['board_name']
                        board_pack_file = os.path.join('../../boards', board_pack_file, 'package.yaml')

                        pack = load_package(board_pack_file)
                        if pack:
                            board = pack['BOARD']
                            if board:
                                package['BOARD'].ld_script  = os.path.join('../../boards', board_name, board.ld_script)
                                package['LD_SCRIPT'] = package['BOARD'].ld_script


            return package
        except Exception as e:
            print(str(e))
    return None

def save_csi_config(defines, filename):
    text = '''/* don't edit, auto generated by tools/toolchain.py */

#ifndef __CSI_CONFIG_H__
#define __CSI_CONFIG_H__

#include <yoc_config.h>

#endif

'''
    try:
        p = os.path.dirname(filename)
        try:
            os.makedirs(p)
        except:
            pass

        with open(filename, 'w') as f:
            f.write(text)
            print("Generate %s done!" % filename)
    except:
        print("Generate %s file failed." % filename)


def save_defconfig(pack, filename):
    defines = pack['DEFCONFIG']
    try:
        p = os.path.dirname(filename)
        try:
            os.makedirs(p)
        except:
            pass

        with open(filename, 'w') as f:
            for k, v in defines.items():
                text = ''
                if v in ['y', 'n', 'Y', 'N']:
                    text = k + '=' + v
                elif type(v) == int:
                    text = k + '=' + str(v)
                else:
                    text = k + '="' + str(v) + '"'

                f.write(text + '\n')
            print("Generate %s done!" % filename)
        return True
    except:
        print("Generate %s file failed." % filename)


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

    try:
        p = os.path.dirname(filename)
        try:
            os.makedirs(p)
        except:
            pass

        with open(filename, 'w') as f:
            f.write(text)
            print("Generate %s done!" % filename)
        return True
    except:
        print("Generate %s file failed." % filename)


class Board(object):
    def __init__(self, conf):
        self.VENDOR = ''
        self.CHIP = ''
        self.BOARD = ''
        self.CPU = ''
        self.ld_script = ''
        self.load_conf(conf)

    def load_conf(self, conf):
        if 'vendor_name' in conf:
            self.VENDOR = conf['vendor_name']

        if 'chip_name' in conf:
            self.CHIP = conf['chip_name']

        if 'board_name' in conf:
            self.BOARD = conf['board_name']

        if 'cpu_name' in conf:
            self.CPU = conf['cpu_name']

        if 'ld_script' in conf:
            self.ld_script = conf['ld_script']


def main():
    package_file = 'package.yaml'
    yoc_sdk = 'yoc_sdk'
    if len(sys.argv) >= 2:
        yoc_sdk = sys.argv[1]
    if len(sys.argv) >= 3:
        package_file = sys.argv[2]
    pack = load_package(package_file)

    if pack:
        config_file = os.path.join(yoc_sdk, 'include/yoc_config.h')

        # save_defconfig(pack, 'defconfig')
        if save_yoc_config(pack['DEFCONFIG'], config_file):
            config_file = os.path.join(yoc_sdk, 'include/csi_config.h')
            save_csi_config(pack['DEFCONFIG'], config_file)
        try:
            for fn in ['package.yaml', 'README.md', 'LICENSE']:
                copyfile(fn, os.path.join(yoc_sdk, fn))
        except:
            pass

if __name__ == "__main__":
    main()
