"""
@author Martin Franckie Jan. 2019

Data base of quantum cascade detectors and QWIPs (mainly for simulations using 
aftershoq.)
To add a new structure, copy an already completed class and change/add layers to the
structure. Give it a unique and obvious name and give a short description and
reference if the structure is, or is based on, published work. Add name of 
creator and date of creation.
"""

from aftershoq.structure import Structure
from aftershoq.materials import *

class QCDL1437(Structure):
    """
    QCD detecting at 8.7 micron (143 meV) for Qombs project. Designed by Carlo Sirtori et al.
    Active region period is repeated 8 times. Al comp. 35% (with CBO = 275 meV according to 
    growth sheet.)
    """
    def __init__(self):
        Structure.__init__(self)
        
        self.setIFR(0.1, 10)
        well = GaAs()
        barrier = AlGaAs(x = 0.35)

        self.addLayerWM(3.2, barrier)
        self.addLayerWM(1.0, well)
        self.addLayerWM(5.0, well) # 2. Doped layer 1e18 cm-3
        self.addLayerWM(1.0, well)
        self.addLayerWM(6.7, barrier)
        self.addLayerWM(2.0, well)
        self.addLayerWM(4.6, barrier)
        self.addLayerWM(2.5, well)
        self.addLayerWM(3.8, barrier)
        self.addLayerWM(3.3, well)
        self.addLayerWM(3.3, barrier)
        self.addLayerWM(4.5, well)
        
        idop = [2]
        vdop = [1.0e18] # cm^-3

        for i in range(len(idop)):
            self.addDoping(0, self.layers[idop[i]].width, vdop[i], idop[i])
    
class QCD_4well_SirtoriA(Structure):
    """
    QCD detecting at 8.8 micron (141 meV) for Qombs project. Designed by Carlo Sirtori et al.
    Active region period is repeated 8 times. Al comp. 35% with CBO = 300 meV.
    """
    def __init__(self):
        Structure.__init__(self)
        
        self.setIFR(0.1, 10)
        well = InGaAs()
        barrier = AlInAs()

        self.addLayerWM(2.5, barrier)
        self.addLayerWM(6.2, well)
        self.addLayerWM(2.0, barrier) 
        self.addLayerWM(4.8, well)
        self.addLayerWM(3.0, barrier)
        self.addLayerWM(3.8, well)
        self.addLayerWM(4.0, barrier)
        self.addLayerWM(9.5, well) # 7. Doped layer 1e18 cm-3
        
        idop = [7]
        vdop = [1.0e18] # cm^-3

        for i in range(len(idop)):
            self.addDoping(0, self.layers[idop[i]].width, vdop[i], idop[i])
            
class QCD_4well_SirtoriB(Structure):
    """
    QCD detecting at 4.5 micron (275 meV) for Qombs project. Designed by Carlo Sirtori et al.
    Active region period is repeated 8 times. Lattice matched material system with CBO=520 meV.
    """
    def __init__(self):
        Structure.__init__(self)
        
        self.setIFR(0.1, 10)
        well = InGaAs()
        barrier = AlInAs()

        self.addLayerWM(2.5, barrier)
        self.addLayerWM(4.4, well)
        self.addLayerWM(2.0, barrier) 
        self.addLayerWM(3.6, well)
        self.addLayerWM(3.0, barrier)
        self.addLayerWM(2.7, well)
        self.addLayerWM(1.7, barrier)
        self.addLayerWM(6.0, well) # 7. Doped layer 1e18 cm-3
        
        idop = [7]
        vdop = [1.5e18] # cm^-3

        for i in range(len(idop)):
            self.addDoping(0, self.layers[idop[i]].width, vdop[i], idop[i])
            
class QCD_Azzurra_1(Structure):
    """
    QCD detecting at 4.5 micron (280 meV) for Qombs project. Designed by Carlo Sirtori et al.
    Active region period is repeated 5 times. Strain compensated with CBO=520 meV
    """
    def __init__(self, on_GaAs = False):
        Structure.__init__(self)
        
        self.setIFR(0.1, 10)
        if on_GaAs:
            well = InGaAs_on_GaAs(x = 0.1)
            well.calcStrain()
            barrier = AlGaAs(x = 0.4)
            barrier.calcStrain()
        else:
            well = InGaAs()
            barrier = AlInAs()

        self.addLayerWM(3.5, barrier)
        self.addLayerWM(0.5, well)
        self.addLayerWM(4.0, well) # 2. Doped layer 1.5e18 cm-3
        self.addLayerWM(0.5, well)
        self.addLayerWM(6.3, barrier) 
        self.addLayerWM(1.2, well)
        self.addLayerWM(5.0, barrier)
        self.addLayerWM(1.6, well)
        self.addLayerWM(4.5, barrier)
        self.addLayerWM(2.1, well)
        self.addLayerWM(4.5, barrier)
        self.addLayerWM(2.6, well)
        self.addLayerWM(4.0, barrier)
        self.addLayerWM(3.4, well)
        
        idop = [2]
        vdop = [1.5e18] # cm^-3

        for i in range(len(idop)):
            self.addDoping(0, self.layers[idop[i]].width, vdop[i], idop[i])
            
class QCD_Azzurra_2(Structure):
    """
    QCD detecting at 4.5 micron (280 meV) for Qombs project. Designed by Carlo Sirtori et al.
    Active region period is repeated 5 times. Strain compensated with CBO=520 meV
    """
    def __init__(self):
        Structure.__init__(self)
        
        self.setIFR(0.1, 10)
        well = InGaAs()
        barrier = AlInAs()

        self.addLayerWM(3.6, barrier)
        self.addLayerWM(0.5, well)
        self.addLayerWM(4.1, well) # 2. Doped layer 1.5e18 cm-3
        self.addLayerWM(0.5, well)
        self.addLayerWM(6.3, barrier) 
        self.addLayerWM(1.2, well)
        self.addLayerWM(5.0, barrier)
        self.addLayerWM(1.5, well)
        self.addLayerWM(5.0, barrier)
        self.addLayerWM(1.8, well)
        self.addLayerWM(4.5, barrier)
        self.addLayerWM(2.2, well)
        self.addLayerWM(4.5, barrier)
        self.addLayerWM(2.7, well)
        self.addLayerWM(3.8, barrier)
        self.addLayerWM(3.5, well)
        
        idop = [2]
        vdop = [1.5e18] # cm^-3

        for i in range(len(idop)):
            self.addDoping(0, self.layers[idop[i]].width, vdop[i], idop[i])
            
class QCD_Azzurra_3(Structure):
    """
    QCD detecting at 4.5 micron (280 meV) for Qombs project. Designed by Carlo Sirtori et al.
    Active region period is repeated 5 times. Strain compensated with CBO=520 meV
    """
    def __init__(self):
        Structure.__init__(self)
        
        self.setIFR(0.1, 10)
        well = InGaAs()
        barrier = AlInAs()

        self.addLayerWM(3.8, barrier)
        self.addLayerWM(0.5, well)
        self.addLayerWM(2.8, well) # 2. Doped layer 1.5e18 cm-3
        self.addLayerWM(0.5, well)
        self.addLayerWM(2.0, barrier) 
        self.addLayerWM(0.9, well)
        self.addLayerWM(6.4, barrier)
        self.addLayerWM(1.2, well)
        self.addLayerWM(5.8, barrier)
        self.addLayerWM(1.5, well)
        self.addLayerWM(5.5,barrier)
        self.addLayerWM(1.8, well)
        self.addLayerWM(5.0, barrier)
        self.addLayerWM(2.2, well)
        self.addLayerWM(4.5, barrier)
        self.addLayerWM(2.8, well)
        
        idop = [2]
        vdop = [1.5e18] # cm^-3

        for i in range(len(idop)):
            self.addDoping(0, self.layers[idop[i]].width, vdop[i], idop[i])