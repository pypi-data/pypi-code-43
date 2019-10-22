import sys, numpy,  scipy.constants as codata

from orangewidget import gui
from orangewidget.settings import Setting
from oasys.widgets import gui as oasysgui
from oasys.widgets import congruence

from syned.storage_ring.magnetic_structures.undulator import Undulator

from orangecontrib.syned.widgets.gui import ow_insertion_device

m2ev = codata.c * codata.h / codata.e

VERTICAL = 1
HORIZONTAL = 2
BOTH = 3

class OWUndulatorLightSource(ow_insertion_device.OWInsertionDevice):

    name = "Undulator Light Source"
    description = "Syned: Undulator Light Source"
    icon = "icons/undulator.png"
    priority = 2

    auto_energy = Setting(0.0)
    auto_harmonic_number = Setting(1)

    def __init__(self):
        super().__init__()

        tab_util = oasysgui.createTabPage(self.tabs_setting, "Utility")

        left_box_1 = oasysgui.widgetBox(tab_util, "Auto Setting of Undulator", addSpace=False, orientation="vertical")

        oasysgui.lineEdit(left_box_1, self, "auto_energy", "Set Undulator at Energy [eV]", labelWidth=250, valueType=float, orientation="horizontal")
        oasysgui.lineEdit(left_box_1, self, "auto_harmonic_number", "As Harmonic #",  labelWidth=250, valueType=int, orientation="horizontal")

        button_box = oasysgui.widgetBox(left_box_1, "", addSpace=False, orientation="horizontal")

        gui.button(button_box, self, "Set Kv value", callback=self.auto_set_undulator_V)
        gui.button(button_box, self, "Set Kh value", callback=self.auto_set_undulator_H)
        gui.button(button_box, self, "Set Both K values", callback=self.auto_set_undulator_B)

    def get_magnetic_structure(self):
        return Undulator(K_horizontal=self.K_horizontal,
                         K_vertical=self.K_vertical,
                         period_length=self.period_length,
                         number_of_periods=self.number_of_periods)


    def check_magnetic_structure_instance(self, magnetic_structure):
        if not isinstance(magnetic_structure, Undulator):
            raise ValueError("Magnetic Structure is not a Undulator")

    def populate_magnetic_structure(self, magnetic_structure):
        self.K_horizontal = magnetic_structure._K_horizontal
        self.K_vertical = magnetic_structure._K_vertical
        self.period_length = magnetic_structure._period_length
        self.number_of_periods = magnetic_structure._number_of_periods

    def auto_set_undulator_V(self):
        self.auto_set_undulator(VERTICAL)

    def auto_set_undulator_H(self):
        self.auto_set_undulator(HORIZONTAL)

    def auto_set_undulator_B(self):
        self.auto_set_undulator(BOTH)

    def auto_set_undulator(self, which=VERTICAL):
        congruence.checkStrictlyPositiveNumber(self.auto_energy, "Set Undulator at Energy")
        congruence.checkStrictlyPositiveNumber(self.auto_harmonic_number, "As Harmonic #")
        congruence.checkStrictlyPositiveNumber(self.electron_energy_in_GeV, "Energy")
        congruence.checkStrictlyPositiveNumber(self.period_length, "Period Length")

        wavelength = self.auto_harmonic_number*m2ev/self.auto_energy
        K = round(numpy.sqrt(2*(((wavelength*2*self.gamma()**2)/self.period_length)-1)), 6)

        if which == VERTICAL   or which==BOTH: self.K_vertical = K
        if which == HORIZONTAL or which==BOTH: self.K_horizontal = K

    def gamma(self):
        return 1e9*self.electron_energy_in_GeV / (codata.m_e *  codata.c**2 / codata.e)

    def resonance_energy(self, theta_x=0.0, theta_z=0.0, harmonic=1):
        gamma = self.gamma()

        wavelength = (self.period_length / (2.0*gamma **2)) * \
                     (1 + self.K_vertical**2 / 2.0 + self.K_horizontal**2 / 2.0 + \
                      gamma**2 * (theta_x**2 + theta_z ** 2))

        wavelength /= harmonic

        return m2ev/wavelength

from PyQt5.QtWidgets import QApplication

if __name__ == "__main__":
    a = QApplication(sys.argv)
    ow = OWUndulatorLightSource()
    ow.show()
    a.exec_()
