#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import sys
import json
import time
import git
import zipfile
import shutil

try:
    from tools import *
    from component import *
    from builder import *
    from occ import *
except:
    from yoctools.tools import *
    from yoctools.component import *
    from yoctools.builder import *
    from yoctools.occ import *

class YoC:
    def __init__(self):
        self.occ = None
        self.occ_components = None
        self.current_solution = None
        self.current_board = None
        self.path = ''
        self.builder = Builder()

        # scanning .yoc file directory
        v = os.getcwd()
        while v != '/':
            if os.path.exists(os.path.join(v, '.yoc')):
                self.path = v
                break
            v = os.path.dirname(v)

        if self.path == '':
            self.path = os.getcwd()
            v = os.path.join(self.path, '.yoc')
            write_file('yoc project', v)

        self.components = ComponentGroup()
        try:
            # scanning yoc all components
            for path in ['components', 'solutions', 'boards']:
                files = os.listdir(os.path.join(self.path, path))
                for component_name in files:
                    comp_path = os.path.join(self.path, path, component_name)
                    if os.path.isdir(comp_path):
                        pack = Component(comp_path)
                        self.components.add(pack)

            # find current solution & board component
            for _, component in self.components.items():
                if component.path == os.getcwd():
                    self.current_solution = component
                    if self.current_solution.board_name:
                        self.current_board = self.components.get(self.current_solution.board_name)

                    save_yoc_config(self.current_solution.defconfig, 'app/include/yoc_config.h')
                    save_csi_config(self.current_solution.defconfig, 'app/include/csi_config.h')

            # add lost component
            for _, component in self.components.items():
                for dep in component.depends:
                    if not self.components.get(dep):
                        self.add_component(dep)

            self.components.calc_depend()

        except Exception as e:
            # print(str(e))
            pass


    def genBuildEnv(self):
        if not self.current_board:
            print('No define board component, please set a board component')
            exit(-1)

        if not self.current_solution:
            print('No define solution component, please set a solution component')
            exit(-1)

        # print(self.current_board)
        builder = Builder()
        for _, component in self.components.items():
            builder.env.AppendUnique(CPPPATH=[component.path])
            if component.includes:
                for p in component.includes:
                    path = os.path.join(component.path, p)
                    builder.env.AppendUnique(CPPPATH=[path])

        builder.env.Replace(
            ASFLAGS   = self.current_board.AFLAGS   + ' ' + self.current_solution.AFLAGS,
            CCFLAGS   = self.current_board.CCFLAGS  + ' ' + self.current_solution.CCFLAGS,
            CXXFLAGS  = self.current_board.CXXFLAGS + ' ' + self.current_solution.CXXFLAGS,
            LINKFLAGS = self.current_board.LDFLAGS  + ' ' + self.current_solution.LDFLAGS
        )

        builder.set_cpu(self.current_board.board.CPU)
        builder.SetInstallPath(os.path.join(self.current_solution.path, 'yoc_sdk'))

        return builder

    def add_component(self, name):
        self.occ_update()

        if self.components.get(name) == None:
            component = self.occ_components.get(name)
            if component:
                for dep in component.depends:
                    self.add_component(dep['name'])
                self.components.add(component)

            return component


    def remove_component(self, name):
        component = self.components.get(name)

        if component:
            if not component.depends_on:                     # 如果没有组件依赖它
                for dep in component.depends:
                    p = self.components.get(dep)
                    if p:
                        if name in p.depends_on:
                            del p.depends_on[name]
                        self.remove_component(dep)

                shutil.rmtree(component.path)
                self.components.remove(component)
                self.components.calc_depend()
                return True
            else:
                print("remove fail, %s depends on:" % component.name)
                for dep in component.depends_on:
                    print('  ', dep.name)
                return False



    def update(self):
        for _, component in self.components.items():
            component.download()
        for _, component in self.components.items():
            if component.type == 'solution':
                genSConstruct(self.components, component.path)


    def occ_update(self):
        if self.occ == None:
            self.occ = OCC('occ.t-head.cn')
            self.occ_components = self.occ.yocComponentList('614193542956318720')
            for _, component in self.occ_components.items():
                component.path = os.path.join(self.path, component.path)


    def list(self):
        for _, component in self.components.items():
            component.show()
            print(component.name)
            if component.depends:
                print('  ', 'depends:')
                for v in component.depends:
                    print('    -', v)
            if component.includes:
                print('  ', 'include:')
                for p in component.includes:
                    print('    -', p)
            if component.depends_on:
                print('  ', 'depends_on:')
                for p in component.depends_on:
                    print('    -', p.name)

def usage():
    print("Usage:")
    print("  yoc <command> [options]\n")
    print("Commands:")
    print("  install                     Install component.")
    print("  uninstall                   Uninstall component.")
    print("  list                        List all packages")
    print("  update                      update all packages")
    print("")

    print("General Options:")
    print("  -h, --help                  Show help.")

def main():
    argc = len(sys.argv)
    if argc < 2:
        usage()
        exit(0)

    if sys.argv[1] == 'list':
        yoc = YoC()
        yoc.occ_update()
        yoc.occ_components.show()
    elif sys.argv[1] == 'lo':
        yoc = YoC()
        yoc.list()
    elif sys.argv[1] in ['install', 'download']:
        if argc >= 3:
            yoc = YoC()
            yoc.add_component(sys.argv[2])
            yoc.update()
            print("%s download Success!" % sys.argv[2])
    elif sys.argv[1] in ['uninstall', 'remove']:
        if argc >= 3:
            yoc = YoC()
            if yoc.remove_component(sys.argv[2]):
                yoc.update()
                print("%s uninstall Success!" % sys.argv[2])
    elif sys.argv[1] == 'update':
        yoc = YoC()
        yoc.update()


if __name__ == "__main__":
    main()