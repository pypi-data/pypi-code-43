#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import argparse
from string import Template
from pbxproj import XcodeProject

def code_generation(temp_file_path, out_file_path, replace):
    out_file = open(out_file_path, 'w')
    template_file = open(temp_file_path, 'r')
    tmpl = Template(template_file.read())
    code = []

    code.append(tmpl.substitute(replace))

    out_file.writelines(code)
    out_file.close()

def all_tmpl_generation(tmpl_path,dest_path,name):
    g = os.walk(tmpl_path)
    replace = dict(name=name)
    all_file = []
    for path,dir_list,file_list in g:
        for file_name in file_list:
            file_path = os.path.join(path, file_name)
            out_path = '{}/{}{}.swift'.format(dest_path, name, file_name)
            out_path = out_path.replace('.tmpl', '')
            code_generation(file_path, out_path, replace)
            all_file.append(out_path)
    return all_file


def auto_genneration(tmpl_path, pbxproj_path, name):
    '''
    1.创建solomon目录,已经存的话，不会创建
    2.生成模版代码
    '''
    pbxproj = XcodeProject.load(pbxproj_path)
    source_group = pbxproj.get_or_create_group('Source')
    mvp_group = pbxproj.get_or_create_group('MVP',parent=source_group)
    contract_group = pbxproj.get_or_create_group('Contract',parent=mvp_group)
    model_group = pbxproj.get_or_create_group('Model',parent=mvp_group)
    presenter_group = pbxproj.get_or_create_group('Precenter',parent=mvp_group)
    view_group = pbxproj.get_or_create_group('View',parent=mvp_group)

    tmpl_files = all_tmpl_generation(tmpl_path,'./Source', name)
    for f in tmpl_files:
        parent = source_group
        if 'Contract' in f:
            parent = contract_group
        elif 'Model' in f:
            parent = model_group
        elif 'Presenter' in f:
            parent = presenter_group
        elif 'View' in f:
            parent = view_group
        pbxproj.add_file(f, parent=parent)



    pbxproj.backup()
    pbxproj.save()

def main():
    this_dir, this_filename = os.path.split(__file__)
    tmpl_path = "{}/tmpl".format(this_dir)
    parser = argparse.ArgumentParser()
    parser.add_argument('path', help="Path to project.pbxproj",
                        nargs='?')
    parser.add_argument('-n', '--name', help="Name of solomon tmpl")

    args = parser.parse_args()
    auto_genneration(tmpl_path, args.path, args.name)
    print("generate success")


if __name__ == '__main__':
    main()
