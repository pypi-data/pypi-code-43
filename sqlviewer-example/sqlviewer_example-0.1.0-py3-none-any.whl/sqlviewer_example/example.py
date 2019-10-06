from sqlviewer.connector import Connector
from sqlviewer.render import table

class ExampleConnector(Connector):

    @classmethod
    def setup(cls):
        print("Method to define input params... returns config (dict)")

        config = {
            'keyword1': 'something',
            'keyword2': 'something else'
        }

        print("Config returned: {}".format(config))
        return config

    def __init__(self, **kwargs):
        print("Keywords recieved: {}".format(kwargs))

    def execute(self, query: str):
        print('Connection asked to execute "{}"'.format(query))
        table(['col1', 'col2'], [['example value', 'another'], ['a2', 'b2']])