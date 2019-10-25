from ..generic.classes import Base

class Hurricane(Base):
    """
    Intialize a hurricane module instance
     
    Keyword arguments: \n
    name: str = name of the scenario or instance
    """
    def __init__(self, name):
        super().__init__(name)
        # class variables
        self.constant = 2.3
        self.name = name
    # class methods
    def importData(self):
        print('Data has been imported into', self.name)
    def analyze(self, data):
        print(self.constant * data)
    def results(self, output_location):
        print('Results have been stored at', str(output_location))
    def hazard(self):
        print("Get yer rifles boys. We're gunna end this hurricane like they did in Florida")