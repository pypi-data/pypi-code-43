from ..generic.classes import Base

class Tsunami(Base):
    """
    Intialize a tsunami module instance
     
    Keyword arguments: \n
    name: str = name of the scenario or instance
    """
    def __init__(self, name):
        super().__init__(name)
        # class variables
        self.constant = 1.6
        self.name = name
    # class methods
    def importData(self):
        print('Data has been imported into', self.name)
    def analyze(self, data):
        print(self.constant * data)
    def results(self, output_location):
        print('Results have been stored at', str(output_location))
    def hazard(self):
        print('Surfs up dude')