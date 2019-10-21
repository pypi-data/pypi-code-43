"""
@author Martin Franckie Oct. 2018

Data base of quantum cascade lasers (mainly for simulations using aftershoq.
To add a new QCL, copy an already completed class and change/add layers to the
structure. Give it a unique and obvious name and give a short description and
reference if the structure is, or is based on, published work. Add name of 
creator and date of creation.

Only works if aftershoq is in your PYTHONPATH
"""

from aftershoq.structure import Structure
from aftershoq.materials import *

class EV2624(Structure):
    """Optimized 2-well structure (new record temperature 2018-11-24)
    Based on EV2416, optimized with aftershoq
    """
    
    def __init__(self):
        Structure.__init__(self)
        
        self.setIFR(0.1, 10)
        well = GaAs()
        barr = AlGaAs(name="barrier1", x = 0.25)
        
        self.addLayerWM(8.28, well)
        self.addLayerWM(1.97, barr)
        self.addLayerWM(8.7, well)
        self.addLayerWM(3.0, well)
        self.addLayerWM(5.35, well)
        self.addLayerWM(3.38, barr)
        
        idop= 3
        vdop = 1.5e17 # cm^-3
        1.5
        self.addDoping(0, self.layers[idop].width, vdop, idop)

class ASQW_Opt(Structure):
    """ASQW optimized for DFG at 8 meV with uniform doping
    Based on aftershoq.qcls.Dupont_DFG_ASQW, varying well+barrier+x.
    Sewself predics chi(2) ≈ 1-3.6e6 pm/V (gamma=10 - 5 meV)

    Added by Martin Franckie 2018-10-20.
    """
    
    def __init__(self):
        Structure.__init__(self)
        
        self.setIFR(0.1, 10)
        well = GaAs()
        barrier1 = AlGaAs(name="barrier1", x = 0.29)
        barrier2 = AlGaAs(name="Barrier2", x = 0.43)
        
        self.addLayerWM(7.4, barrier2)
        self.addLayerWM(4.44, well)
        self.addLayerWM(22.25, barrier1)
        self.addLayerWM(7.4, barrier2)
        
        idop= 1
        vdop = 5e18 # cm^-3
        
        self.addDoping(0, self.layers[idop].width, vdop, idop)

class DQW_DFG_AlGaAs(Structure):
    """
    Double quantum well structure for difference frequency generation
    based on AlGaAs (instead of InGaAs/AlInAs as Tymchenko J. Opt. 2017)
    """
        
    def __init__(self):
        Structure.__init__(self)
        self.setIFR(0.1, 10)
        well = GaAs()
        barrier = AlGaAs(x = 0.25)
        
        self.addLayerWM(4, barrier)
        self.addLayerWM(3.4, well)
        self.addLayerWM(2.7, barrier)
        self.addLayerWM(9.1, well) # <----- # 3 uniformly doped to 1*10^18 cm^-3
        self.addLayerWM(4, barrier)
        
        idop= 3
        vdop = 1e18 # cm^-3
        
        self.addDoping(0, self.layers[idop].width, vdop, idop)
        
class EV1429(Structure):
    """Genetically optimized strained InGaAs/AlInAs 4.3 micron QCL 
    Based on N655.

    Added by Martin Franckie 2018-10-22.
    """
    
    def __init__(self):
        Structure.__init__(self)
        
        self.setIFR(0.1, 10)
        well = InGaAs(x=0.635)
        well.params[mp.Ec] = 0
        well.params[mp.Eg] = 0.82

        barrier = AlInAs(x=0.665)
        barrier.params[mp.Ec] = 0.82
        barrier.params[mp.Eg] = 1.68

        self.addLayerWM(2.7, well)
        self.addLayerWM(1.9, barrier)
        self.addLayerWM(2.6, well)
        self.addLayerWM(1.5, barrier)
        self.addLayerWM(2.3, well)
        self.addLayerWM(1.4, barrier)
        self.addLayerWM(2.1, well)
        self.addLayerWM(2.2, barrier)
        self.addLayerWM(1.9, well)
        self.addLayerWM(2.0, barrier)
        self.addLayerWM(1.9, well)
        self.addLayerWM(1.9, barrier)
        self.addLayerWM(1.7, well)
        self.addLayerWM(2.4, barrier)
        self.addLayerWM(1.7, well)
        self.addLayerWM(3.5, barrier)
        self.addLayerWM(1.1, well)
        self.addLayerWM(1.3, barrier)
        self.addLayerWM(3.8, well)
        self.addLayerWM(1.0, barrier)
        self.addLayerWM(3.5, well)
        self.addLayerWM(1.8, barrier)
        
        idop = [6, 7, 8, 9, 10]
        vdop = [1.81e17, 1.0e17, 1.81e17, 1.0e17, 1.81e17] # cm^-3

        for i in range(len(idop)):
            self.addDoping(0, self.layers[idop[i]].width, vdop[i], idop[i])


class EV1429_4p6(Structure):
    """Genetically optimized strained InGaAs/AlInAs 4.6 micron QCL.
    Based on EV1429 (4.3 micron), part of EV2138 (with different composition)
    gaLab identifier: Gen4MeritNo4Seq30607

    Added by Martin Franckie 2018-10-22.
    """
    
    def __init__(self):
        Structure.__init__(self)
        
        self.setIFR(0.1, 10)
        well = InGaAs(x=0.635)
        well.params[mp.Ec] = 0
        well.params[mp.Eg] = 0.82

        barrier = AlInAs(x=0.665)
        barrier.params[mp.Ec] = 0.82
        barrier.params[mp.Eg] = 1.68

        self.addLayerWM(2.76, well)
        self.addLayerWM(1.4, barrier)
        self.addLayerWM(2.41, well)
        self.addLayerWM(1.48, barrier)
        self.addLayerWM(2.46, well)
        self.addLayerWM(1.33, barrier)
        self.addLayerWM(2.19, well)
        self.addLayerWM(1.58, barrier)
        self.addLayerWM(1.85, well)
        self.addLayerWM(1.97, barrier)
        self.addLayerWM(1.74, well)
        self.addLayerWM(2.06, barrier)
        self.addLayerWM(1.47, well)
        self.addLayerWM(2.17, barrier)
        self.addLayerWM(1.56, well)
        self.addLayerWM(3.5, barrier)
        self.addLayerWM(1.31, well)
        self.addLayerWM(1.48, barrier)
        self.addLayerWM(3.76, well)
        self.addLayerWM(1.03, barrier)
        self.addLayerWM(3.29, well)
        self.addLayerWM(1.99, barrier)
        
        idop = [6, 7, 8, 9, 10]
        vdop = [1.29e17, 0.685e17, 1.29e17, 0.685e17, 1.29e17] # cm^-3

        for i in range(len(idop)):
            self.addDoping(0, self.layers[idop[i]].width, vdop[i], idop[i])

class N1022(Structure):
    """
    Quantum cascade detector at 4.7 micron.
    Hofstetter, Daniel, et al. “Mid-Infrared Quantum Cascade Detectors for Applications in
    Spectroscopy and Pyrometry.” In Quantum Sensing and Nanophotonic Devices VII, 7608:76081N.
    International Society for Optics and Photonics, 2010. https://doi.org/10.1117/12.853351.
    """

    def __init__(self):
        Structure.__init__(self)
        self.setIFR(0.1, 10)
        well = InGaAs()
        barrier = AlInAs()

        self.addLayerWM(5.1, well) # <----- # 0 uniformly doped to 4*10^17 cm^-3
        self.addLayerWM(7.5, barrier)
        self.addLayerWM(1.25, well)
        self.addLayerWM(6.5, barrier)
        self.addLayerWM(1.45, well)
        self.addLayerWM(6.4, barrier)
        self.addLayerWM(1.7, well)
        self.addLayerWM(7.9, barrier)
        self.addLayerWM(2.0, well)
        self.addLayerWM(7.7, barrier)
        self.addLayerWM(2.4, well)
        self.addLayerWM(7.5, barrier)
        self.addLayerWM(2.9, well)
        self.addLayerWM(7.1, barrier)
        self.addLayerWM(3.5, well)
        self.addLayerWM(6.8, barrier)

        idop= 0
        vdop = 4e17 # cm^-3

        self.addDoping(0, self.layers[idop].width, vdop, idop)

class HarrerOE2016_QCD(Structure):
    """
    Quantum cascade detector at 4.3 micron.
    A. Harrer, et al., "4.3 μm quantum cascade detector in pixel 
    configuration," Opt. Express 24, 17041-17049 (2016)
    https://doi.org/10.1364/OE.24.017041
    4.3 /6.5/0.85/6.5/0.9/6.5/1.0/5.5/1.2/4.5/1.45/4.5/1.7/4.5/2.05/4.0/2.4/4.0/2.85/3.0nm starting with the active well A, InGaAs in bold, InAlAs normal and the 8e17cm−3     doped well underlined.
    """

    def __init__(self):
        Structure.__init__(self)
        self.setIFR(0.1, 10)
        well = InGaAs()
        barrier = AlInAs()

        self.addLayerWM(4.3, well) # <----- # 0 uniformly doped to 8*10^17 cm^-3
        self.addLayerWM(6.5, barrier)
        self.addLayerWM(0.85, well)
        self.addLayerWM(6.5, barrier)
        self.addLayerWM(0.9, well)
        self.addLayerWM(6.5, barrier)
        self.addLayerWM(1.0, well)
        self.addLayerWM(5.5, barrier)
        self.addLayerWM(1.2, well)
        self.addLayerWM(4.5, barrier)
        self.addLayerWM(1.45, well)
        self.addLayerWM(4.5, barrier)
        self.addLayerWM(2.05, well)
        self.addLayerWM(4.0, barrier)
        self.addLayerWM(2.4, well)
        self.addLayerWM(4.0, barrier)
        self.addLayerWM(2.85, well)
        self.addLayerWM(3.0, barrier)

        idop= 0
        vdop = 8e17 # cm^-3

        self.addDoping(0, self.layers[idop].width, vdop, idop)

class EV1116(Structure):
    """
    THz QCL. Design: Giacomo Scalari
    """

    def __init__(self):
        Structure.__init__(self)
        self.setIFR(0.1, 10)
        barr = AlGaAs(x = 0.15)
        well = GaAs()
        
        self.addLayerWM(11.0,well)
        self.addLayerWM(1.8,barr)
        self.addLayerWM(11.5,well)
        self.addLayerWM(3.8,barr)
        self.addLayerWM(9.4,well)
        self.addLayerWM(4.2,barr)
        self.addLayerWM(18.4,well) # layer 6 doped 2.3E16 cm-3
        self.addLayerWM(5.5,barr)
        
        idop= 6
        vdop = 2.0e16 # cm^-3

        self.addDoping(0, self.layers[idop].width, vdop, idop)    


        
class EV2242(Structure):
    """
    EV1116 but more diagonal THz QCL.
    Based on N907.
    """

    def __init__(self):
        Structure.__init__(self)
        self.setIFR(0.1, 10)
        barr = AlGaAs(x = 0.15)
        well = GaAs()
        
        self.addLayerWM(10.8,well)
        self.addLayerWM(2.4,barr)
        self.addLayerWM(11.5,well)
        self.addLayerWM(3.9,barr)
        self.addLayerWM(9.4,well)
        self.addLayerWM(4.1,barr)
        self.addLayerWM(18.2,well) # layer 6 doped 2.3E16 cm-3
        self.addLayerWM(5.7,barr)
        
        idop= 6
        vdop = 2.3e16 # cm^-3

        self.addDoping(0, self.layers[idop].width, vdop, idop)    

class EV2244(Structure):
    """
    Extremely diagonal THz QCL with braodband lasing in the NDR.
    Based on EV1116 -> EV2242
    """

    def __init__(self):
        Structure.__init__(self)
        self.setIFR(0.1, 10)
        barr = AlGaAs(x = 0.15)
        well = GaAs()
        
        self.addLayerWM(10.6,well)
        self.addLayerWM(2.9,barr)
        self.addLayerWM(11.5,well)
        self.addLayerWM(3.9,barr)
        self.addLayerWM(9.2,well)
        self.addLayerWM(4.1,barr)
        self.addLayerWM(18.3,well) # layer 6 doped 2.3E16 cm-3
        self.addLayerWM(5.8,barr)
        
        idop= 6
        vdop = 2.3e16 # cm^-3

        self.addDoping(0, self.layers[idop].width, vdop, idop)

        
"""
Phonon-polariton strucures (all barriers AlInAs lattice matched to InP)
"""
        
        
class EV2036(Structure):
    """
    Phonon polariton structure with lambda = 23.6 um.
    Added by Martin Franckie 2018-12-18.
    """
    
    def __init__(self):
        Structure.__init__(self)
        
        self.setIFR(0.1, 10)
        well = InGaAs()
        barrier = AlInAs()

        self.addLayerWM(3.0, barrier)
        self.addLayerWM(5.4, well)
        self.addLayerWM(0.4, barrier)
        self.addLayerWM(8.6, well)
        self.addLayerWM(0.5, barrier)
        self.addLayerWM(8.2, well)
        self.addLayerWM(0.5, barrier)
        self.addLayerWM(8.1, well)
        self.addLayerWM(0.6, barrier)
        self.addLayerWM(7.1, well)
        self.addLayerWM(0.7, barrier)
        self.addLayerWM(6.1, well)
        self.addLayerWM(1.1, barrier)
        self.addLayerWM(6.4, well)     # <---- #13 doped 4.1e17 cm-3 
        self.addLayerWM(2.0, barrier)
        self.addLayerWM(7.2, well)
        
        idop = [13]
        vdop = [4.1e17] # cm^-3

        for i in range(len(idop)):
            self.addDoping(0, self.layers[idop[i]].width, vdop[i], idop[i])


        
        
class EV2039(Structure):
    """
    Phonon polariton structure with lambda = 24.4 um.
    Added by Martin Franckie 2018-12-18.
    """
    
    def __init__(self):
        Structure.__init__(self)
        
        self.setIFR(0.1, 10)
        well = InGaAs()
        barrier = AlInAs()

        self.addLayerWM(3.0, barrier)
        self.addLayerWM(5.5, well)
        self.addLayerWM(0.4, barrier)
        self.addLayerWM(8.8, well)
        self.addLayerWM(0.5, barrier)
        self.addLayerWM(8.4, well)
        self.addLayerWM(0.5, barrier)
        self.addLayerWM(8.3, well)
        self.addLayerWM(0.6, barrier)
        self.addLayerWM(7.2, well)
        self.addLayerWM(0.7, barrier)
        self.addLayerWM(6.2, well)
        self.addLayerWM(1.1, barrier)
        self.addLayerWM(6.5, well)     # <---- #13 doped 4.1e17 cm-3 
        self.addLayerWM(2.0, barrier)
        self.addLayerWM(7.3, well)
        
        idop = [13]
        vdop = [4.1e17] # cm^-3

        for i in range(len(idop)):
            self.addDoping(0, self.layers[idop[i]].width, vdop[i], idop[i])


        
        
class EV2091(Structure):
    """
    Phonon polariton structure with lambda = 25.1 um.
    Added by Martin Franckie 2018-12-18.
    """
    
    def __init__(self):
        Structure.__init__(self)
        
        self.setIFR(0.1, 10)
        well = InGaAs()
        barrier = AlInAs()

        self.addLayerWM(3.0, barrier)
        self.addLayerWM(5.7, well)
        self.addLayerWM(0.4, barrier)
        self.addLayerWM(9.1, well)
        self.addLayerWM(0.5, barrier)
        self.addLayerWM(8.7, well)
        self.addLayerWM(0.5, barrier)
        self.addLayerWM(8.6, well)
        self.addLayerWM(0.6, barrier)
        self.addLayerWM(7.5, well)
        self.addLayerWM(0.7, barrier)
        self.addLayerWM(6.5, well)
        self.addLayerWM(1.1, barrier)
        self.addLayerWM(6.8, well)     # <---- #13 doped 4.1e17 cm-3 
        self.addLayerWM(2.0, barrier)
        self.addLayerWM(7.6, well)
        
        idop = [13]
        vdop = [4.1e17] # cm^-3

        for i in range(len(idop)):
            self.addDoping(0, self.layers[idop[i]].width, vdop[i], idop[i])


        
class EV2092(Structure):
    """
    Phonon polariton structure with lambda = 25.3 um.
    Added by Martin Franckie 2018-12-18.
    """
    
    def __init__(self):
        Structure.__init__(self)
        
        self.setIFR(0.1, 10)
        well = InGaAs()
        barrier = AlInAs()

        self.addLayerWM(3.0, barrier)
        self.addLayerWM(5.8, well)
        self.addLayerWM(0.4, barrier)
        self.addLayerWM(9.3, well)
        self.addLayerWM(0.5, barrier)
        self.addLayerWM(8.9, well)
        self.addLayerWM(0.5, barrier)
        self.addLayerWM(8.7, well)
        self.addLayerWM(0.6, barrier)
        self.addLayerWM(7.7, well)
        self.addLayerWM(0.7, barrier)
        self.addLayerWM(6.6, well)
        self.addLayerWM(1.1, barrier)
        self.addLayerWM(6.9, well)     # <---- #13 doped 4.1e17 cm-3 
        self.addLayerWM(2.0, barrier)
        self.addLayerWM(7.8, well)
        
        idop = [13]
        vdop = [4.1e17] # cm^-3

        for i in range(len(idop)):
            self.addDoping(0, self.layers[idop[i]].width, vdop[i], idop[i])



        
class EV2106(Structure):
    """
    Phonon polariton structure with lambda = 26.0 um.
    Added by Martin Franckie 2018-12-18.
    """
    
    def __init__(self):
        Structure.__init__(self)
        
        self.setIFR(0.1, 10)
        well = InGaAs()
        barrier = AlInAs()

        self.addLayerWM(3.0, barrier)
        self.addLayerWM(5.5, well)
        self.addLayerWM(0.3, barrier)
        self.addLayerWM(8.7, well)
        self.addLayerWM(0.4, barrier)
        self.addLayerWM(8.3, well)
        self.addLayerWM(0.4, barrier)
        self.addLayerWM(8.2, well)
        self.addLayerWM(0.5, barrier)
        self.addLayerWM(7.1, well)
        self.addLayerWM(0.6, barrier)
        self.addLayerWM(6.1, well)
        self.addLayerWM(1.1, barrier)
        self.addLayerWM(6.6, well)     # <---- #13 doped 4.1e17 cm-3 
        self.addLayerWM(2.0, barrier)
        self.addLayerWM(7.0, well)
        
        idop = [13]
        vdop = [4.1e17] # cm^-3

        for i in range(len(idop)):
            self.addDoping(0, self.layers[idop[i]].width, vdop[i], idop[i])


class EV1858(Structure):
    """
    4-quantum-well design aimed at 4.7 THz for astronomy applications.
    Published in...
    """
    def __init__(self):
        Structure.__init__(self)
        
        self.setIFR(0.1, 10)
        well = GaAs()
        barrier = AlGaAs(x = 0.15)

        self.addLayerWM(16.5, well)
        self.addLayerWM(5.1, barrier)
        self.addLayerWM(9.3, well)
        self.addLayerWM(1.0, barrier)
        self.addLayerWM(10.5, well)
        self.addLayerWM(3.3, barrier)
        self.addLayerWM(8.7, well)
        self.addLayerWM(4.2, barrier)
        
        idop = [0]
        vdop = [2e16] # cm^-3

        for i in range(len(idop)):
            self.addDoping(0, self.layers[idop[i]].width, vdop[i], idop[i])
    
class EV2556(Structure):
    """
    Optimized 4-quantum-well design aimed at 4.7 THz for astronomy applications.
    Based on EV1858, optimized with aftershoq NEGF.
    """
    def __init__(self):
        Structure.__init__(self)
        
        self.setIFR(0.1, 10)
        well = GaAs()
        barrier = AlGaAs(x = 0.15)

        self.addLayerWM(16.5, well)
        self.addLayerWM(5.1, barrier)
        self.addLayerWM(9.3, well)
        self.addLayerWM(1.0, barrier)
        self.addLayerWM(10.5, well)
        self.addLayerWM(4.317, barrier)
        self.addLayerWM(8.7, well)
        self.addLayerWM(5.007, barrier)
        
        idop = [0]
        vdop = [2e16] # cm^-3

        for i in range(len(idop)):
            self.addDoping(0, self.layers[idop[i]].width, vdop[i], idop[i])
        
class EV2107(Structure):
    """
    Phonon polariton structure with lambda = 25.6 um.
    Added by Martin Franckie 2018-12-18.
    """
    
    def __init__(self):
        Structure.__init__(self)
        
        self.setIFR(0.1, 10)
        well = InGaAs()
        barrier = AlInAs()

        self.addLayerWM(3.0, barrier)
        self.addLayerWM(5.9, well)
        self.addLayerWM(0.3, barrier)
        self.addLayerWM(9.3, well)
        self.addLayerWM(0.4, barrier)
        self.addLayerWM(8.9, well)
        self.addLayerWM(0.4, barrier)
        self.addLayerWM(8.8, well)
        self.addLayerWM(0.5, barrier)
        self.addLayerWM(7.7, well)
        self.addLayerWM(0.6, barrier)
        self.addLayerWM(6.3, well)
        self.addLayerWM(1.1, barrier)
        self.addLayerWM(7.0, well)     # <---- #13 doped 4.1e17 cm-3 
        self.addLayerWM(1.6, barrier)
        self.addLayerWM(8.0, well)
        
        idop = [13]
        vdop = [4.1e17] # cm^-3

        for i in range(len(idop)):
            self.addDoping(0, self.layers[idop[i]].width, vdop[i], idop[i])

 
        
class EV2128(Structure):
    """
    Phonon polariton structure with lambda = 26.3 um.
    Added by Martin Franckie 2018-12-18.
    """
    
    def __init__(self):
        Structure.__init__(self)
        
        self.setIFR(0.1, 10)
        well = InGaAs()
        barrier = AlInAs()

        self.addLayerWM(3.0, barrier)
        self.addLayerWM(6.0, well)
        self.addLayerWM(0.3, barrier)
        self.addLayerWM(9.3, well)
        self.addLayerWM(0.4, barrier)
        self.addLayerWM(8.9, well)
        self.addLayerWM(0.4, barrier)
        self.addLayerWM(8.8, well)
        self.addLayerWM(0.4, barrier)
        self.addLayerWM(7.7, well)
        self.addLayerWM(0.5, barrier)
        self.addLayerWM(6.3, well)
        self.addLayerWM(0.8, barrier)
        self.addLayerWM(6.6, well)     # <---- #13 doped 4.1e17 cm-3 
        self.addLayerWM(1.4, barrier)
        self.addLayerWM(7.5, well)
        
        idop = [13]
        vdop = [4.1e17] # cm^-3

        for i in range(len(idop)):
            self.addDoping(0, self.layers[idop[i]].width, vdop[i], idop[i])

class SWDP_CONFIDENTIAL(Structure):
    """
    Split-well direct phonon design by A. Albo et al. (unpublished, 2019)
    Do not spread design!!!
    
    Widths given as # monolayers
    """
    
    def __init__(self):
        Structure.__init__(self)
        
        self.setIFR(0.1, 10)
        well = GaAs()
        barrier1 = AlGaAs(x=0.15)
        barrier2 = AlAs()
        
        #s.layers[i].material.params[mp.lattconst]/10*s.layers[i].width
        
        self.addLayerWM(24.8*well.params[mp.lattconst]/20, well)     # Doped 
        self.addLayerWM(3.5*barrier1.params[mp.lattconst]/20, barrier1)
        self.addLayerWM(24.8*well.params[mp.lattconst]/20, well)     # Doped
        self.addLayerWM(17.3*barrier1.params[mp.lattconst]/20, barrier1)
        self.addLayerWM(24.8*well.params[mp.lattconst]/20, well)
        self.addLayerWM(5*barrier2.params[mp.lattconst]/20, barrier2)
        
        idop = [0,1]
        vdop = [1.21e16, 1.21e16] # cm^-3

        for i in range(len(idop)):
            self.addDoping(0, self.layers[idop[i]].width, vdop[i], idop[i])
            
            
class ZnO_Meng_2019(Structure):
    """
    4-well ZnO design by Bo Meng, optimized version of previous best 4-well simulated by NEGF.
    """
    
    def __init__(self):
        Structure.__init__(self)
        
        self.setIFR(0.1, 10)
        well = ZnO()
        barrier = ZnMgO(x=0.8815)
        #barrier.calcStrain()
        
        #s.layers[i].material.params[mp.lattconst]/10*s.layers[i].width
        
        self.addLayerWM(3.6, well)
        self.addLayerWM(1.7, barrier)
        self.addLayerWM(3.4, well)
        self.addLayerWM(2.4, barrier)
        self.addLayerWM(2.75, well)
        self.addLayerWM(2.7, barrier)
        self.addLayerWM(2.0, well)
        self.addLayerWM(2.0, well) # <-- #7 Doped 3e18 cm-3
        self.addLayerWM(2.15, well)
        self.addLayerWM(2.5, barrier)
        
        idop = [7]
        vdop = [3e18] # cm^-3

        for i in range(len(idop)):
            self.addDoping(0, self.layers[idop[i]].width, vdop[i], idop[i])
    