#!/usr/bin/python3
# coding: utf-8
from imenu_builder import MenuBuilder
import os

def header_builder(environment):
    print("Current PATH: {PATH}".format(**environment))

def main():
    builder = MenuBuilder()

    builder.environment(os.environ.copy()).header(header_builder).title('Menu title')

    builder.item('l', 'List directory').os_command('ls -la').create()

    builder.item('p', 'Show path').os_command('echo {PATH}').create()

    builder.item('i', 'Set i variable').set_variable('i').create()

    submenu = builder.item('s', 'A submenu').sub_menu()

    submenu.item('1', 'First item').os_command('echo First menu item').create()
    submenu.item('2', 'Second item').os_command('echo Second menu item').create()

    submenu.item().defaults().create()

    menu = builder.item().defaults().create()

    menu.run()

if __name__ == '__main__':
    main()
