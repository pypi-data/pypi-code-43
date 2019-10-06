import os
import sys
import typing
from better import ConfigParser
import contextlib
import readline
import atexit
import pkg_resources

from . import render

class DisplayManager:
    """ Intergrated terminal environment for the connection and execution of sql commands. Basic input looper. """

    DIRECTORY = os.path.join(os.path.expanduser("~"), ".pysql")
    HISTORY_PATH = os.path.join(DIRECTORY, 'history')
    MASTER_PATH = os.path.join(DIRECTORY, "master.ini")
    MASTER_HISTORY = os.path.join(DIRECTORY, 'master.hist')

    _PLUGINS = {
        'example': "*** 'example' connector can be install via 'pip install sqlviewer_example' ***"
    }

    def __init__(self):
        self.config = ConfigParser().read(self.MASTER_PATH)
        self._loaded_connectors = {}

        readline.clear_history()
        readline.read_history_file(self.MASTER_HISTORY)
        readline.set_history_length(100)

        atexit.register(lambda path: self.config.write(path), self.MASTER_PATH)

    def interaction_help(self):
        print(
            "\n"
            "COMMANDS:\n"
            "       add [name]          Add a connection and reference it with the given name\n"
            "       connect [name]      Open a connection to the database named [name]\n"
            "       list                List databases currently setup\n"
            "       remove [name]       Remove connection information for [name]\n"
            "       exit                Close application\n"
        )

    def displayConfig(self):
        render.table(
            columns = ['NAME', 'TYPE', 'SETTINGS'],
            rows = [
                [
                    name,
                    settings['drivername'],
                    ", ".join(['{}: {}'.format(k, v) for k, v in settings.items() if k not in ('drivername', 'password')])
                ] for name, settings in self.config.items()
            ],
            buffer = 8,
            title = 'Databases'
        )

    def interact(self):

        while True:
            try:
                command = input('>>> ').split()
                if not command: continue

                if command[0] == 'add':
                    # User is attempting to add a new connection
                    assert len(command) ==  2, "add requires two arguments"
                    self.add(command[1])

                elif command[0] == 'connect':
                    assert len(command) == 2, "connect requires two arguments"
                    self.connect(command[1])

                elif command[0] == 'remove':
                    assert len(command) == 2, "remove requires two arguments"
                    self.remove(command[1])

                elif command[0] == 'list':
                    self.displayConfig()

                elif command[0] == 'help':
                    self.interaction_help()

                elif command[0] == 'exit':
                    break

                else:
                    print("Unknown command: {}".format(command))

            except Exception as e:
                print("\nERROR: {}".format(e))
                print("enter 'help' for commands\n")

            except KeyboardInterrupt:
                print()
                exit(0)

    def add(self, name: str):
        """ Add a new connection variable - test the connection save the variables """
        print("Adding new connection object '{}'...\n".format(name))

        drivername = input("Drivername: ")

        connector = self._load(drivername)
        try:
            config = connector.setup()
        except KeyboardInterrupt:
            return print("Setup cancelled.")

        # Add the driver name to the config for this viewer to determine its class
        config['drivername'] = drivername
        self.config[name] = config
        print("Successfully added new connection")

    def connect(self, name: str):
        """ Parse a connection string and setup the manager for working with a connection """

        if name in self.config:
            config = self.config[name].copy()
            drivername = config.pop('drivername')
            connector = self._load(drivername)
            connection = connector(**config)

        else:
            raise ValueError("No connection referred to by that name - '{}'".format(name))

        with self._setupHistory(name):
            connection.serve()

    def remove(self, name: str):
        if name in self.config:
            del self.config[name]
            os.remove(os.path.join(self.HISTORY_PATH, name + '.hist'))
        else:
            raise ValueError("Not connection exists with that name")

    def _load(self, drivername: str):

        if drivername in self._loaded_connectors:
            connector = self._loaded_connectors[drivername]

        else:
            for entry_point in pkg_resources.iter_entry_points('sqlviewer_connectors'):
                if entry_point.name == drivername:
                    self._loaded_connectors[entry_point.name] = entry_point.load()
                    connector = self._loaded_connectors[drivername]
                    break

            else:
                message = "Couldn't find a connector for the drivername '{}'".format(drivername)
                if drivername in self._PLUGINS:
                    message += '\n{}'.format(self._PLUGINS[drivername])

                raise ValueError(message)

        return connector

    @contextlib.contextmanager
    def _setupHistory(self, name):

        # Write the history of the toplevel care to file
        readline.write_history_file(self.MASTER_HISTORY)
        readline.clear_history()

        # Identify the connectors history file
        path = os.path.join(self.HISTORY_PATH, name + '.hist')
        try:
            readline.read_history_file(path)
        except:
            pass

        yield

        readline.write_history_file(path)
        readline.clear_history()

        # Read back in main history
        readline.read_history_file(self.MASTER_HISTORY)

def main():

    # Set up the argument parser
    arguments = sys.argv

    # Set up a display manager
    manager = DisplayManager()

    print(
        "Basic SQL viewer - Kieran Bacon - https://github.com/Kieran-Bacon"
    )

    if len(arguments) ==  1:
        manager.displayConfig()
        manager.interact()

    elif len(arguments) ==  2:
        if arguments[1] in manager.config:
            manager.connect(arguments[1])
        else:
            print('Connection name not recognised: {}'.format(arguments[1]))