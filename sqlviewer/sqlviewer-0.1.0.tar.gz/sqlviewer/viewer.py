import os
import sys
import sqlalchemy
import typing
from better import ConfigParser
import contextlib
import readline
import atexit
import time

def table(
    columns: typing.Iterable[str],
    rows: typing.Iterable[typing.Iterable[object]],
    *,
    title: str = None,
    buffer: int = 2
):
    """ Render a basic table

    Params:
        columns (Iterable[str]): The columns of the table
        rows (Iterable[Iterable[object]]): An iterable providing rows with arbitrary typed
        *,
        title (str): --
        buffer (int): The white space to be added to a column's width after setting width to the largest column entry
    """

    # Determine the width of the window
    _, terminalWidth = os.popen('stty size', 'r').read().split()
    terminalWidth = int(terminalWidth)
    tprint = lambda x: print(x) if len(x) < terminalWidth else print(x[:terminalWidth - 4] + '...')

    # Determine the columns widths
    columnWidths = [0]*len(columns)
    for row in [columns] + rows:
        for i in range(len(columns)):
            columnWidths[i] = max(columnWidths[i], len(str(row[i])))
    columnWidths = [x + buffer for x in columnWidths]

    # define the row formats
    rowTemplate = '|'.join(['{'+str(i)+':^{'+str(i + len(columns))+'}}' for i in range(len(columns))])

    header = rowTemplate.format(*columns, *columnWidths)
    print()

    if title is not None:
        width = min(terminalWidth, len(header))
        print("{0:^{1}}".format(title, width))
        print('='*width)

    tprint(header)
    tprint('='*len(header))
    for row in rows:
        tprint(rowTemplate.format(*[str(x) for x in row], *columnWidths))
    print()

class SQLAlchemyConnector:
    """ Basic connector to connections supported by the sqlalchemy url method """

    def __init__(self, **kwargs):
        self.engine = sqlalchemy.engine.create_engine(sqlalchemy.engine.url.URL(**kwargs))

    def execute(self, command: str):
        """ Execute command against the underlying engine and render any table response

        Params:
            command (str): the sql query to be executed
        """

        start = time.time()
        resultProxy = self.engine.execute(command)
        columns = resultProxy.keys()
        if columns:
            rows = resultProxy.fetchmany(size=80)
            table(columns, rows)

        print("Command executed in {}".format(time.time() - start))

class DisplayManager:
    """ Intergrated terminal environment for the connection and execution of sql commands. Basic input looper. """

    DIRECTORY = os.path.join(os.path.expanduser("~"), ".pysql")
    HISTORY_PATH = os.path.join(DIRECTORY, 'history')
    MASTER_PATH = os.path.join(DIRECTORY, "master.ini")
    MASTER_HISTORY = os.path.join(DIRECTORY, 'master.hist')

    def __init__(self):
        readline.clear_history()
        readline.read_history_file(self.MASTER_HISTORY)
        readline.set_history_length(100)

        self.config = ConfigParser().read(self.MASTER_PATH)

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
        table(
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
                    if len(command) == 2:
                        self.add(command[1])
                    else:
                        raise ValueError('some shit')

                elif command[0] == 'connect':
                    assert len(command) == 2
                    self.connect(command[1])

                elif command[0] == 'remove':
                    if command[1] in self.config:
                        del self.config[command[1]]
                        os.remove(os.path.join(self.HISTORY_PATH, command[1] + '.hist'))
                    else:
                        raise ValueError("Not connection exists with that name")

                elif command[0] == 'list':
                    self.displayConfig()

                elif command[0] == 'help':
                    self.interaction_help()

                elif command[0] == 'exit':
                    break

                else:
                    print("Unknown command: {}".format(command))

            except Exception as e:
                print("Error on command: {}".format(e))
                self.interaction_help()

            except KeyboardInterrupt:
                print()
                exit(0)

    def add(self, name: str):
        """ Add a new connection variable - test the connection save the variables """
        print("Adding new connection object named {}...".format(name))

        conn = {}
        for question in ['drivername', 'host', 'port', 'database', 'username', 'password']:
            answer = input('{}: '.format(question))
            if answer: conn[question] = answer

        if conn['drivername'] == 'sqlite':
            conn['database'] = os.path.abspath(conn['database'])

        try:
            SQLAlchemyConnector(**conn)
            self.config[name] = conn
            print("Successfully added new connection")

        except Exception as e:
            print('Error on attempted connection to new database: {}'.format(e))


    def connect(self, name: str):
        """ Parse a connection string and setup the manager for working with a connection """

        try:
            if name in self.config:
                connection = SQLAlchemyConnector(**self.config[name])

            else:
                print("Couldn't find connection target: {}".format(name))
                return

        except Exception as e:
            print("Error on connection: {}".format(e))
            return

        with self._setupHistory(name):

            query = [] # Store various lines of sql query to be executed
            while True:
                # Hold connection open until the user indicates that they would like to break

                try:
                    # Extract a line of the query
                    sql = input('$ ')
                    if not sql: continue # Empty - do nothing

                    while ';' in sql:
                        query.append(sql[:sql.index(';')])

                        connection.execute(' '.join(query))
                        query.clear()

                        sql = sql[sql.index(';') + 1:]

                    query.append(sql)

                except Exception as e:
                    print("Execution Error: {}".format(e))

                except KeyboardInterrupt:
                    print()
                    break

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