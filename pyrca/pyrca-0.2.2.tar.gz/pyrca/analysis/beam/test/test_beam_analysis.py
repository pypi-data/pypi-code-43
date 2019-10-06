import unittest
from pyrca.properties.beam.node import Node
from pyrca.properties.beam.section import Section
from pyrca.properties.beam.beam_section import BeamSection
from pyrca.properties.beam.steel_tension import SteelTension
from ..beam_analyses import BeamAnalyses
from ..stress_distribution import StressDistribution


class TestBeamAnalysis(unittest.TestCase):
    # Definition of beam section nodes.
    _nodes = [Node(0, 0), Node(0, 500), Node(250, 500), Node(250, 0)]

    def test_beam_capacity(self):
        """
        From the book 'Simplified Reinforced Concrete Design for 2010 NSCP
        Problem 2.16:
        A rectangular beam with b = 250 mm and d = 460 m is reinforced for tension only with 3-25 mm bars.
        The beam is simply supported over a span of 6 m and carries a uniform dead load of 680 N/m including
        its own weight. Calculate the uniform live load that the beam can carry.
        Assume fy = 276.5MPa and f'c = 20.7 MPa.

        From solution on the book, Mu = 151.56 kN-m
        :return:
        """

        # Section object
        _section = Section()
        _section.set_main_section(self._nodes)

        # Beam section object
        _bs = BeamSection()
        _bs.set_fc_prime(20.7)
        _bs.set_fy(276.5)
        _bs.set_effective_depth(460)
        _bs.section = _section

        # Tensile reinforcement object
        _tension_steel = SteelTension()
        _tension_steel.set_total_area(1472.62)

        # Set the beam's tensile reinforcement
        _bs.steel_tension = _tension_steel

        # Define analyses object to be able to use the different analysis (e.g. uncrack, capacity/nominal)
        _analysis = BeamAnalyses()
        _analysis.beam_section = _bs

        # Analysis result
        _result = _analysis.beam_capacity_analysis(StressDistribution.WHITNEY)

        # Converted from nominal to suit the requirement from the problem.
        _mu = round(_result.moment_c * 0.9, 2) / 1000000

        # Checking the calculation against the manual method.
        self.assertAlmostEqual(_mu, 151.56, 0, msg='Wrong calculation!')

    def test_balanced_analysis(self):
        _nodes = [Node(0, 0), Node(0, 540), Node(250, 540), Node(250, 0)]

        # Section object
        _section = Section()
        _section.set_main_section(_nodes)

        # Beam section object
        _bs = BeamSection()
        _bs.set_fc_prime(28)
        _bs.set_fy(415)
        _bs.set_effective_depth(500)
        _bs.section = _section

        _bs.steel_tension = SteelTension()

        # Define analyses object to be able to use the different analysis (e.g. uncrack, capacity/nominal)
        _analysis = BeamAnalyses()
        _analysis.beam_section = _bs
        _result = _analysis.beam_balanced_analysis(StressDistribution.PARABOLIC)
        _Asb = _analysis.balanced_steel_tension

        self.assertAlmostEqual(_Asb, 3602, 0, msg='Wrong calculation!')


if __name__ == '__main__':
    unittest.main()
