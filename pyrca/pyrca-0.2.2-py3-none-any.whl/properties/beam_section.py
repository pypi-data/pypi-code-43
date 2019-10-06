from ..utils.beam_constants import *
from ..utils.conversion import *
from .steel_tension import SteelTension
from .steel_compression import SteelCompression
from .section import Section


class BeamSection:
    # Section that defines the beam.
    section: Section = None

    # Tension steel
    steel_tension: SteelTension = None

    # Compression steel
    steel_compression: SteelCompression = None

    # Distance from centroid of tension steel to compression fiber
    effective_depth: float = None

    # Concrete secant modulus in MPa.
    Ec: float = None

    # Modulus of elasticity of steel MPa.
    Es: float = 200000

    # Modular ratio of steel to concrete
    modular_ratio: float = None

    # Concrete strain index
    concrete_strain_index: float = None

    # Beta 1
    beta_1: float = None

    # Concrete yield strength, MPa
    fc_prime: float = None

    # Modulus of rupture
    fr: float = None

    # Steel yield strength
    fy: float = None

    # Unit
    unit: Unit = None

    def __init__(self):
        self.steel_tension = SteelTension()
        self.steel_compression = SteelCompression()
        self.unit = Unit.METRIC

    def get_Ec(self):
        return pressure_convert(self.Ec, self.unit)

    def get_effective_depth(self):
        return linear_convert(self.effective_depth, self.unit)

    def get_Es(self):
        return pressure_convert(self.Es, self.unit)

    def get_fc_prime(self):
        return pressure_convert(self.fc_prime, self.unit)

    def get_fr(self):
        return pressure_convert(self.fr, self.unit)

    def get_fy(self):
        return pressure_convert(self.fy, self.unit)

    def get_modular_ratio(self):
        return self.modular_ratio

    def get_section(self):
        return self.section

    def set_effective_depth(self, effective_depth: float):
        """
        Set the effective depth.
        :param effective_depth:
        :return:
        """
        if self.unit == Unit.ENGLISH:
            self.effective_depth = in_to_mm(effective_depth)
        else:
            self.effective_depth = effective_depth

    def set_fc_prime(self, fc_prime: float):
        self.fc_prime = fc_prime
        if self.unit == Unit.ENGLISH:
            self.fc_prime = psi_to_mpa(fc_prime)
        self.fr = 0.6 * math.sqrt(self.fc_prime)
        self.Ec = 4700 * math.sqrt(self.fc_prime)
        self.modular_ratio = ES / self.Ec
        self.concrete_strain_index = 2 * 0.85 * self.fc_prime / self.Ec

    def set_fy(self, fy: float):
        self.fy = fy
        if self.unit == Unit.ENGLISH:
            self.fy = psi_to_mpa(fy)

    def set_modular_ratio(self, modular_ratio: float):
        self.modular_ratio = modular_ratio
