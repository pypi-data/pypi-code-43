from datetime import datetime

class Base:
    """
    Intialize a common module instance
     
    Keyword arguments: \n
    name: str = name of the scenario or instance
    """
    def __init__(self, name):
        # class variables
        self.name = name
        self.dateCreated = datetime.now()
        self.meta = {
            'name': self.name,
            'dateCreated': self.dateCreated
        }
    # class methods
    def info(self):
        print(self.meta)