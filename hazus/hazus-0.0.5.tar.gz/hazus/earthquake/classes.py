from ..generic.classes import Base

class Earthquake(Base):
    """Intialize an earthquake module instance.
     
    Keyword arguments:
    name: str -- name of the scenario or instance;
    magnitude: float -- magnitude of the earthquake
    """
    def __init__(self, name):
        super().__init__(name)
        # class variables
        self.constant = 1.9
        self.name = name
    # class methods
    def importData(self):
        """import data into the earthquake module instance"""
        print('Data has been imported into', self.name)
    def analyze(self, data):
        """analyze earthquake data
             
        Keyword arguments: \n
        data: float = value multipled against the earthquake constant
        """
        print(self.constant * data)
    def results(self, output_location):
        """export earthquake module results
             
        Keyword arguments: \n
        output_location: str = directory to export results
        """
        print('Results have been stored at', str(output_location))
    def hazard(self):
        """method simulating the hazard
        """
        print('Whoooaaaa! That rumblin aint my tummy')