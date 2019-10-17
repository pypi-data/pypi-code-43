#! /bin/env python

import os
import sys
from shutil import copyfile

try:
    from yoc import YoC
    from tools import load_package
except:
    from yoctools.yoc import YoC
    from yoctools.tools import load_package

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


class Build(object):
    def __init__(self, tool):
        self.conf = tool
        self.env = tool.env.Clone()
        self.BUILD = 'release'
        self.INSTALL_PATH = tool.INSTALL_PATH
        self.lib_path = tool.lib_path
        self.yoc_lib_path = tool.lib_path

        self.env.Replace(
            ASFLAGS = self.conf.AFLAGS,
            CCFLAGS = self.conf.CCFLAGS,
            CXXFLAGS = self.conf.CXXFLAGS,
            LINKFLAGS = self.conf.LDFLAGS
        )

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
        self.yoc = YoC()
        self.build = self.yoc.genBuildEnv()

    def build(self):
        return Build(self)

    def library(self, name, src, **parameters):
        build = Build(self.build)
        build.library(name, src, **parameters)

    def library_yaml(self):
        build = Build(self.build)
        pack = load_package('package.yaml')
        if pack:
            name = pack['name']
            component = self.yoc.components.get(name)

            sources = []
            for src in component.sources:
                for f in self.build.env.Glob(src):
                    sources.append(f)


            del pack['name']
            del pack['SOURCES']

            build.library(name, sources, **pack)

    def program(self, **parameters):
        build = Build(self.build)
        pack = load_package('package.yaml')

        if pack:
            name = pack['name']
            component = self.yoc.components.get(name)
            sources = []
            for src in component.sources:
                for f in self.build.env.Glob(src):
                    sources.append(f)

            del pack['name']
            del pack['SOURCES']
            pack['LD_SCRIPT'] = self.yoc.current_board.ld_script

            build.program(name + '.elf', sources, **pack)

    def build_package(self, packages):
        for d in packages:
            file_name = os.path.join(d, 'SConscript')
            if os.path.isfile(file_name):
                scons.SConscript(file_name, exports={"env" : self.build.env.Clone()})
