from .interfaceCharacterization import InterfaceCharacterization
from time import sleep


class Characterization(InterfaceCharacterization):
    def compute(self, theMachine):
        sleep(10e-6)
