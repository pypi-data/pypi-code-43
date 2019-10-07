import json

class Repos(object):
    """The class contains repos telematics"""

    def __init__(self, data):
        """The method loading data from json to class fields"""

        if 'id' not in data:
            raise ValueError(data)

        self.id = data['id']
        self.name = data['name']
        self.repotype = data['repotype']
        self.apiversion = data['apiVersion']

class Branches(object):
    """The class contains telematics of branches for a repo"""

    def __init__(self, data):
        """The method loading data from json to class fields"""

        if 'id' not in data:
            raise ValueError(data)

        self.id = data['branches']['id']
        self.name = data['branches']['name']
        self.commit_id = data['branches']['commitid']
        self.timestamp = data['branches']['timestamp']
        self.parent = data['branches']['parent']

class Tables(object):
    """The class contains telematics of tables for a repo"""

    def __init__(self, data):
        """The method loading data from json to class fields"""

        if 'id' not in data:
            raise ValueError(data)

        self.id = data['id']
        self.name = data['name']
        self.repotype = data['repotype']
        self.apiversion = data['apiVersion']
        self.tables = data['tables']

class Dataset(object):
    """The class contains telematics of dataset"""

    def __init__(self, data):
        """The method loading data from json to class fields"""

        if 'id' not in data:
            raise ValueError(data)

        # self.schema = data['tschema']
        self.data = data['data']