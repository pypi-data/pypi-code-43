# flake8: noqa
import unittest
import numpy as np

from modelbase.ode import Model
from modelbase.ode import ratelaws as rl
from modelbase.io import sbml


class RapidEq(rl.BaseAlgebraicModule):
    def __init__(self, K, variable, derived_variables):
        pars = {"K": K}
        variables = [variable] if isinstance(variable, str) else variable
        super().__init__(
            pars=pars, variables=variables, derived_variables=derived_variables
        )

    def mod_func_strgs(self):
        return {
            self.derived_variables[0]: f"{self.variables[0]}/(1+{self.pars['K']})",
            self.derived_variables[
                1
            ]: f"{self.variables[0]}*{self.pars['K']}/(1+{self.pars['K']})",
        }

    def mod_func(self, p, A):
        K = getattr(p, self.pars["K"])
        return A / (1 + K), A * K / (1 + K)


class ConstantTimeDependent(rl.BaseRateLaw):
    def __init__(self, k, substrates, modifiers):
        super().__init__()
        self.pars["k"] = k
        self.modifiers = modifiers

    def rate_func_str(self):
        return f"exp(-{self.pars['k']} * {self.modifiers[0]})"

    def rate_func(self, p, t):
        k = getattr(p, self.pars["k"])
        return np.exp(-k * t)


class Stimulus(rl.BaseRateLaw):
    def __init__(self, k, substrates, modifiers):
        super().__init__()
        self.pars["k"] = k
        self.substrates = substrates
        self.modifiers = modifiers

    def rate_func_str(self):
        return f"{self.modifiers[1]}  * exp(-{self.pars['k']} * {self.modifiers[0]})"

    def rate_func(self, p, t, x):
        k = getattr(p, self.pars["k"])
        return x * np.exp(-k * t)


class TestOdeModels(unittest.TestCase):
    def test_parameter(self):
        m1 = Model({"k0": 1.0})
        m2 = sbml.create_model_from_sbml(m1.write_to_sbml())
        self.assertEqual(m1._parameters.k0, m2._parameters.k0)

    def test_compounds(self):
        m1 = Model()
        m1.add_compounds(["A"])
        m2 = sbml.create_model_from_sbml(m1.write_to_sbml())
        self.assertEqual(m1.get_compounds()["A"], m2.get_compounds()["A"])

    def test_derived_compounds(self):
        m1 = Model({"tot": 1})
        m1.add_compounds(["A"])
        m1.add_algebraic_module_from_template(
            "Moiety", rl.Moiety, ["tot"], ["A"], ["B"]
        )
        m2 = sbml.create_model_from_sbml(m1.write_to_sbml())
        self.assertEqual(m1.get_all_compounds()["B"], m2.get_all_compounds()["B"])

    def test_all_derived_compounds(self):
        m1 = Model({"tot": 1})
        m1.add_compounds(["A"])
        m1.add_algebraic_module_from_template(
            "Moiety", rl.Moiety, ["tot"], ["A"], ["B"]
        )
        m2 = sbml.create_model_from_sbml(m1.write_to_sbml())
        self.assertEqual(m1.get_all_compounds(), m2.get_all_compounds())

    def test_rate_law_string(self):
        m1 = Model({"k0": 1})
        m1.add_compounds(["A"])
        m1.add_reaction_from_ratelaw("v0", rl.Constant, {"A": 1}, ["k0"])

        m2 = sbml.create_model_from_sbml(m1.write_to_sbml())
        self.assertEqual(
            m1._ratelaws["v0"].rate_func_str(), m2._ratelaws["v0"].rate_func_str()
        )

    def test_rate_law_func(self):
        m1 = Model({"k0": 1})
        m1.add_compounds(["A"])
        m1.add_reaction_from_ratelaw("v0", rl.Constant, {"A": 1}, ["k0"])

        m2 = sbml.create_model_from_sbml(m1.write_to_sbml())
        self.assertEqual(
            m1._ratelaws["v0"].rate_func(m1._parameters),
            m2._ratelaws["v0"].rate_func(m2._parameters),
        )

    def test_alg_mod_func_strgs(self):
        m1 = Model({"tot": 1})
        m1.add_compounds(["A"])
        m1.add_algebraic_module_from_template(
            "Moiety", rl.Moiety, ["tot"], ["A"], ["B"]
        )

        m2 = sbml.create_model_from_sbml(m1.write_to_sbml())
        self.assertEqual(
            m1._module_templates["Moiety"].mod_func_strgs()["B"],
            m2._module_templates["Moiety_B"].mod_func_strgs()["B"],
        )

    def test_alg_mod_func(self):
        m1 = Model({"tot": 1})
        m1.add_compounds(["A"])
        m1.add_algebraic_module_from_template(
            "Moiety", rl.Moiety, ["tot"], ["A"], ["B"]
        )

        m2 = sbml.create_model_from_sbml(m1.write_to_sbml())
        self.assertEqual(
            m1._module_templates["Moiety"].mod_func(m1._parameters, 0.5),
            m2._module_templates["Moiety_B"].mod_func(m2._parameters, 0.5),
        )

    def test_stoichiometries(self):
        m1 = Model({"k0": 1})
        m1.add_compounds(["A"])
        m1.add_reaction_from_ratelaw("v0", rl.Constant, {"A": 1}, ["k0"])
        m2 = sbml.create_model_from_sbml(m1.write_to_sbml())
        self.assertEqual(m1._stoichiometries, m2._stoichiometries)


class TestOdeModelReimport(unittest.TestCase):
    def test_parameter_reimport(self):
        m1 = Model({"k0": 1.0})
        m2 = sbml.create_model_from_sbml(m1.write_to_sbml())
        m3 = sbml.create_model_from_sbml(m2.write_to_sbml())
        self.assertEqual(m1._parameters.k0, m3._parameters.k0)

    def test_compounds_reimport(self):
        m1 = Model()
        m1.add_compounds(["A"])
        m2 = sbml.create_model_from_sbml(m1.write_to_sbml())
        m3 = sbml.create_model_from_sbml(m2.write_to_sbml())
        self.assertEqual(m1.get_compounds()["A"], m3.get_compounds()["A"])

    def test_derived_compounds_reimport(self):
        m1 = Model({"tot": 1})
        m1.add_compounds(["A"])
        m1.add_algebraic_module_from_template(
            "Moiety", rl.Moiety, ["tot"], ["A"], ["B"]
        )
        m2 = sbml.create_model_from_sbml(m1.write_to_sbml())
        m3 = sbml.create_model_from_sbml(m2.write_to_sbml())
        self.assertEqual(m1.get_all_compounds()["B"], m3.get_all_compounds()["B"])

    def test_all_derived_compounds_reimport(self):
        m1 = Model({"tot": 1})
        m1.add_compounds(["A"])
        m1.add_algebraic_module_from_template(
            "Moiety", rl.Moiety, ["tot"], ["A"], ["B"]
        )
        m2 = sbml.create_model_from_sbml(m1.write_to_sbml())
        m3 = sbml.create_model_from_sbml(m2.write_to_sbml())
        self.assertEqual(m1.get_all_compounds(), m3.get_all_compounds())

    def test_rate_law_string_reimport(self):
        m1 = Model({"k0": 1})
        m1.add_compounds(["A"])
        m1.add_reaction_from_ratelaw("v0", rl.Constant, {"A": 1}, ["k0"])

        m2 = sbml.create_model_from_sbml(m1.write_to_sbml())
        m3 = sbml.create_model_from_sbml(m2.write_to_sbml())
        self.assertEqual(
            m1._ratelaws["v0"].rate_func_str(), m3._ratelaws["v0"].rate_func_str()
        )

    def test_rate_law_func_reimport(self):
        m1 = Model({"k0": 1})
        m1.add_compounds(["A"])
        m1.add_reaction_from_ratelaw("v0", rl.Constant, {"A": 1}, ["k0"])

        m2 = sbml.create_model_from_sbml(m1.write_to_sbml())
        m3 = sbml.create_model_from_sbml(m2.write_to_sbml())
        self.assertEqual(
            m1._ratelaws["v0"].rate_func(m1._parameters),
            m3._ratelaws["v0"].rate_func(m3._parameters),
        )

    def test_alg_mod_func_strgs_reimport(self):
        m1 = Model({"tot": 1})
        m1.add_compounds(["A"])
        m1.add_algebraic_module_from_template(
            "Moiety", rl.Moiety, ["tot"], ["A"], ["B"]
        )

        m2 = sbml.create_model_from_sbml(m1.write_to_sbml())
        m3 = sbml.create_model_from_sbml(m2.write_to_sbml())
        self.assertEqual(
            m1._module_templates["Moiety"].mod_func_strgs()["B"],
            m3._module_templates["Moiety_B"].mod_func_strgs()["B"],
        )

    def test_alg_mod_func_reimport(self):
        m1 = Model({"tot": 1})
        m1.add_compounds(["A"])
        m1.add_algebraic_module_from_template(
            "Moiety", rl.Moiety, ["tot"], ["A"], ["B"]
        )

        m2 = sbml.create_model_from_sbml(m1.write_to_sbml())
        m3 = sbml.create_model_from_sbml(m2.write_to_sbml())
        self.assertEqual(
            m1._module_templates["Moiety"].mod_func(m1._parameters, 0.5),
            m3._module_templates["Moiety_B"].mod_func(m3._parameters, 0.5),
        )

    def test_stoichiometries_reimport(self):
        m1 = Model({"k0": 1})
        m1.add_compounds(["A"])
        m1.add_reaction_from_ratelaw("v0", rl.Constant, {"A": 1}, ["k0"])
        m2 = sbml.create_model_from_sbml(m1.write_to_sbml())
        m3 = sbml.create_model_from_sbml(m2.write_to_sbml())
        self.assertEqual(m1._stoichiometries, m3._stoichiometries)


class TestOdeFullModels(unittest.TestCase):
    def test_linear_chain(self):
        m1 = Model({"k0": 1.0, "k1f": 1.0, "k1eq": 0.5, "k2": 1.0})
        m1.add_compounds(["A", "B"])
        m1.add_reaction_from_ratelaw(
            name="v0", ratelaw=rl.Constant, stoichiometries={"A": 1}, parameters=["k0"]
        )
        m1.add_reaction_from_ratelaw(
            name="v1",
            ratelaw=rl.ReversibleMassAction,
            stoichiometries={"A": -1, "B": 1},
            parameters=["k1f", "k1eq"],
            substrates=["A"],
            modifiers=["B"],
        )
        m1.add_reaction_from_ratelaw(
            name="v2",
            ratelaw=rl.MassAction,
            stoichiometries={"B": -1},
            parameters=["k2"],
            substrates=["B"],
        )

        # Two cycles
        m2 = sbml.create_model_from_sbml(m1.write_to_sbml())
        m3 = sbml.create_model_from_sbml(m2.write_to_sbml())
        fcd1 = m1.get_full_concentration_dict(np.ones(len(m1._compounds)))
        fcd3 = m3.get_full_concentration_dict(np.ones(len(m3._compounds)))

        # m._algebraic_modules.keys() # Expected to be differnt
        # m._module_templates # Expected to be differnt

        self.assertEqual(m1._parameters.__dict__, m3._parameters.__dict__)
        self.assertEqual(m1._compounds, m3._compounds)
        self.assertEqual(m1._all_compounds, m3._all_compounds)
        self.assertEqual(m1._stoichiometries, m3._stoichiometries)
        self.assertEqual(m1._ratelaws.keys(), m3._ratelaws.keys())
        self.assertEqual(m1._rates.keys(), m3._rates.keys())
        self.assertEqual(fcd1, fcd3)
        self.assertEqual(m1.get_fluxes(0, fcd1), m3.get_fluxes(0, fcd3))

    def test_linear_chain_rapid_eq(self):
        m1 = Model({"k0": 1.0, "k2": 0.1, "K": 5.0})
        m1.add_compounds(["A"])
        m1.add_reaction_from_ratelaw(
            name="v0", ratelaw=rl.Constant, stoichiometries={"A": 1}, parameters=["k0"]
        )
        m1.add_algebraic_module_from_template(
            name="fast_eq",
            module_template=RapidEq,
            parameters=["K"],
            variables=["A"],
            derived_variables=["X", "Y"],
        )
        m1.add_reaction_from_ratelaw(
            name="v2",
            ratelaw=rl.MassAction,
            stoichiometries={"A": -1},
            parameters=["k2"],
            modifiers=["Y"],
        )

        # Two cycles
        m2 = sbml.create_model_from_sbml(m1.write_to_sbml())
        m3 = sbml.create_model_from_sbml(m2.write_to_sbml())
        fcd1 = m1.get_full_concentration_dict(np.ones(len(m1._compounds)))
        fcd3 = m3.get_full_concentration_dict(np.ones(len(m3._compounds)))

        # m._algebraic_modules.keys() # Expected to be differnt
        # m._module_templates # Expected to be differnt

        self.assertEqual(m1._parameters.__dict__, m3._parameters.__dict__)
        self.assertEqual(m1._compounds, m3._compounds)
        self.assertEqual(m1._all_compounds, m3._all_compounds)
        self.assertEqual(m1._stoichiometries, m3._stoichiometries)
        self.assertEqual(m1._ratelaws.keys(), m3._ratelaws.keys())
        self.assertEqual(m1._rates.keys(), m3._rates.keys())
        self.assertEqual(fcd1, fcd3)
        self.assertEqual(m1.get_fluxes(0, fcd1), m3.get_fluxes(0, fcd3))

    def test_time_dependent_external_conditions(self):
        m1 = Model({"l": 1.0, "k": 0.1})
        m1.add_compounds(["X"])
        m1.add_reaction_from_ratelaw(
            name="v0",
            ratelaw=ConstantTimeDependent,
            stoichiometries={"X": 1},
            parameters=["l"],
            modifiers=["time"],
        )
        m1.add_reaction_from_ratelaw(
            name="v1",
            ratelaw=rl.MassAction,
            stoichiometries={"X": -1},
            parameters=["k"],
            substrates=["X"],
        )

        # Two cycles
        m2 = sbml.create_model_from_sbml(m1.write_to_sbml())
        m3 = sbml.create_model_from_sbml(m2.write_to_sbml())
        fcd1 = m1.get_full_concentration_dict(np.ones(len(m1._compounds)))
        fcd3 = m3.get_full_concentration_dict(np.ones(len(m3._compounds)))

        # m._algebraic_modules.keys() # Expected to be differnt
        # m._module_templates # Expected to be differnt

        self.assertEqual(m1._parameters.__dict__, m3._parameters.__dict__)
        self.assertEqual(m1._compounds, m3._compounds)
        self.assertEqual(m1._all_compounds, m3._all_compounds)
        self.assertEqual(m1._stoichiometries, m3._stoichiometries)
        self.assertEqual(m1._ratelaws.keys(), m3._ratelaws.keys())
        self.assertEqual(m1._rates.keys(), m3._rates.keys())
        self.assertEqual(fcd1, fcd3)
        self.assertEqual(m1.get_fluxes(0, fcd1), m3.get_fluxes(0, fcd3))

    def test_signal_cascade(self):
        m1 = Model({"l": 0.5, "k1": 1.0, "k2": 1.0, "k3": 1.0, "p": 0.5, "tot": 1})
        m1.add_compounds(["X", "Y", "Z"])
        m1.add_algebraic_module_from_template(
            "rapid_eq_x", rl.Moiety, ["tot"], ["X"], ["Xi"]
        )
        m1.add_algebraic_module_from_template(
            "rapid_eq_y", rl.Moiety, ["tot"], ["Y"], ["Yi"]
        )
        m1.add_algebraic_module_from_template(
            "rapid_eq_z", rl.Moiety, ["tot"], ["Z"], ["Zi"]
        )
        m1.add_reaction_from_ratelaw(
            "stimulus", Stimulus, {"X": 1}, ["l"], [], modifiers=["time", "Xi"]
        )
        m1.add_reaction_from_ratelaw(
            "kinase_1",
            rl.MassAction,
            {"Y": 1},
            parameters=["k1"],
            modifiers=["X", "Yi"],
        )
        m1.add_reaction_from_ratelaw(
            "kinase_2",
            rl.MassAction,
            {"Z": 1},
            parameters=["k2"],
            modifiers=["Y", "Zi"],
        )
        m1.add_reaction_from_ratelaw(
            "phosphatase_1",
            rl.MassAction,
            {"X": -1},
            parameters=["p"],
            substrates=["X"],
        )
        m1.add_reaction_from_ratelaw(
            "phosphatase_2",
            rl.MassAction,
            {"Y": -1},
            parameters=["p"],
            substrates=["Y"],
        )
        m1.add_reaction_from_ratelaw(
            "phosphatase_3",
            rl.MassAction,
            {"Z": -1},
            parameters=["p"],
            substrates=["Z"],
        )

        # Two cycles
        m2 = sbml.create_model_from_sbml(m1.write_to_sbml())
        m3 = sbml.create_model_from_sbml(m2.write_to_sbml())
        fcd1 = m1.get_full_concentration_dict(np.ones(len(m1._compounds)))
        fcd3 = m3.get_full_concentration_dict(np.ones(len(m3._compounds)))

        # m._algebraic_modules.keys() # Expected to be differnt
        # m._module_templates # Expected to be differnt

        self.assertEqual(m1._parameters.__dict__, m3._parameters.__dict__)
        self.assertEqual(m1._compounds, m3._compounds)
        self.assertEqual(m1._all_compounds, m3._all_compounds)
        self.assertEqual(m1._stoichiometries, m3._stoichiometries)
        self.assertEqual(m1._ratelaws.keys(), m3._ratelaws.keys())
        self.assertEqual(m1._rates.keys(), m3._rates.keys())
        self.assertEqual(fcd1, fcd3)
        self.assertEqual(m1.get_fluxes(0, fcd1), m3.get_fluxes(0, fcd3))
