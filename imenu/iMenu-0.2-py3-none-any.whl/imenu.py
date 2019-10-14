#!/usr/bin/python3
# coding:utf-8

from . import console
import os


class Menu(object):

    def __init__(self, environment={}):
        self.title = None
        self.header_builder = None
        self._itens = []
        self._environment = environment

    def add_item(self, menu_item):
        self._itens.append(menu_item)

    def run(self):
        result = None

        while result not in ('quit', 'back'):
            console.clear_screen()

            self._draw_menu()

            key = console.getch()

            for item in self._itens:
                if key == item._shortcut:
                    result = item.run(self._environment)
                    break

        return result

    def _draw_menu(self):
        if self.header_builder:
            self.header_builder(self._environment)
            print()

        if self.title:
            print('*** {} ***'.format(self.title))
            print()

        for item in self._itens:
            self._print_item(item)

    def _print_item(self, item):
        for i in range(0, item._lines_before):
            print()

        print('{}.  {}'.format(item._shortcut, item._label))


class MenuItem(object):

    def __init__(self, shortcut, label, action=None, lines_before=0):
        self._shortcut = shortcut
        self._label = label
        self._action = None
        self._lines_before = lines_before

    def run(self, environment):
        if self._action and hasattr(self._action, '__call__'):
            result = self._action(environment)

            return result if result else 'ok'
        else:
            return 'ok'


class OSCommandMenuItem(MenuItem):

    def __init__(self, shortcut, label, os_command=None, active_folder=None):
        super().__init__(shortcut, label)

        self._command = os_command
        self._active_folder = active_folder

    def run(self, environment):
        super().run(environment)

        if self._active_folder:
            old_directory = os.path.realpath('.')
            os.chdir(self._active_folder.format(**environment))

        command = self._command.format(**environment)
        # print(command)
        os.system(command)

        if self._active_folder:
            os.chdir(old_directory)

        console.wait()

        return 'ok'


class InternalCommandMenuItem(MenuItem):

    def __init__(self, shortcut, label, command, lines_before=0):
        super().__init__(shortcut, label, lines_before=lines_before)
        self._command = command

    def run(self, environment):
        super().run(environment)

        return self._command


class VariableSetterMenuItem(MenuItem):

    def __init__(self, shortcut, label, variable):
        super().__init__(shortcut, label)

        self.variable = variable

    def run(self, environment):
        super().run(environment)

        return set_variable(environment, self.variable)

    @staticmethod
    def set_variable(environment, variable):
        print()
        print('Possible commands ::cancel ::remove')
        print('Current {}\'s value: "{}"'.format(
            variable, environment.get(variable, '<not defined>')))
        value = input('{} = '.format(self.variable))

        if value == '::remove':
            if variable in environment.keys():
                environment.pop(variable)
        elif value != '::cancel':
            environment[variable] = value
        else:
            return 'cancelled'

        return 'ok'


class SubMenuItem(MenuItem):

    def __init__(self, shortcut, label, submenu):
        super().__init__(shortcut, label)

        self.submenu = submenu

    def run(self, environment):
        super().run(environment)

        command = self.submenu.run()

        if command == 'back':
            return 'ok'
        else:
            return command
