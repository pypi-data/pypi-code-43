import warnings
from abc import ABC, abstractmethod
from operator import mul
from functools import reduce

warnings.warn("Experimental class, API might change.", FutureWarning)

# Base abstract classes
class BaseRateLaw(ABC):
    def __init__(self, pars=None, substrates=None, modifiers=None):
        self.pars = pars if pars is not None else {}
        self.substrates = substrates if substrates is not None else []
        self.modifiers = modifiers if modifiers is not None else []

    def __str__(self):
        return self.rate_func_str()

    @abstractmethod
    def rate_func_str(self):
        pass

    @abstractmethod
    def rate_func(self):
        pass


class BaseAlgebraicModule(ABC):
    def __init__(self, pars=None, variables=None, derived_variables=None):
        self.pars = pars if pars is not None else {}
        self.variables = variables if variables is not None else []
        self.derived_variables = (
            derived_variables if derived_variables is not None else []
        )

    def __str__(self):
        return "\n".join(f"{var}={func}" for var, func in self.mod_func_strgs().items())

    @abstractmethod
    def mod_func_strgs(self):
        pass

    @abstractmethod
    def mod_func(self):
        pass


# Rate Law Templates


class Constant(BaseRateLaw):
    def __init__(self, k, substrates, modifiers):
        pars = {"k": k}
        super().__init__(pars=pars)

    def rate_func_str(self):
        return f"{self.pars['k']}"

    def rate_func(self, p):
        k = getattr(p, self.pars["k"])
        return k


class MassAction(BaseRateLaw):
    def __init__(self, k, substrates=None, modifiers=None):
        pars = {"k": k}
        super().__init__(pars=pars, substrates=substrates, modifiers=modifiers)

    def rate_func_str(self):
        return f"{self.pars['k']}*" + "*".join(self.substrates + self.modifiers)

    def rate_func(self, p, *args):
        k = getattr(p, self.pars["k"])
        return reduce(mul, args, k)


class ReversibleMassAction(BaseRateLaw):
    def __init__(self, k_fwd, k_eq, substrates, product):
        pars = {"k_fwd": k_fwd, "k_eq": k_eq}
        substrates = substrates
        modifiers = [product] if isinstance(product, str) else product
        super().__init__(pars=pars, substrates=substrates, modifiers=modifiers)

    def rate_func_str(self):
        return (
            f"{self.pars['k_fwd']}/{self.pars['k_eq']}"
            f"*({'*'.join(self.substrates)}-{'*'.join(self.modifiers)})"
        )

    def rate_func(self, p, *args):
        kf = getattr(p, self.pars["k_fwd"])
        eq = getattr(p, self.pars["k_eq"])
        return (
            kf
            * (
                reduce(mul, args[: len(self.substrates)], 1)
                - reduce(mul, args[len(self.substrates) :], 1)
            )
            / eq
        )


class MichaelisMenten(BaseRateLaw):
    def __init__(self, km, vmax, substrate):
        pars = {"km": km, "vmax": vmax}
        substrates = [substrate] if isinstance(substrate, str) else substrate
        super().__init__(pars=pars, substrates=substrates)

    def rate_func_str(self):
        return (
            f"{self.pars['vmax']}*{self.substrates[0]}"
            f"/({self.pars['km']}+{self.substrates[0]})"
        )

    def rate_func(self, p, compound):
        km = getattr(p, self.pars["km"])
        vmax = getattr(p, self.pars["vmax"])
        return vmax * compound / (km + compound)


class ReversibleMichaelisMenten(BaseRateLaw):
    def __init__(self, km_fwd, vmax_fwd, km_rev, vmax_rev, substrate, product):
        pars = {
            "km_fwd": km_fwd,
            "km_rev": km_rev,
            "vmax_fwd": vmax_fwd,
            "vmax_rev": vmax_rev,
        }
        substrates = [substrate] if isinstance(substrate, str) else substrate
        modifiers = [product] if isinstance(product, str) else product
        super().__init__(pars=pars, substrates=substrates, modifiers=modifiers)

    def rate_func_str(self):
        return (
            f"({self.pars['vmax_fwd']}*{self.substrates[0]}/{self.pars['km_fwd']}"
            f"-{self.pars['vmax_rev']}*{self.modifiers[0]}/{self.pars['km_fwd']})"
            f"/(1+{self.substrates[0]}/{self.pars['km_fwd']}+{self.modifiers[0]}/{self.pars['km_rev']})"
        )

    def rate_func(self, p, S, P):
        vmaxf = getattr(p, self.pars["vmax_fwd"])
        vmaxr = getattr(p, self.pars["vmax_rev"])
        kmf = getattr(p, self.pars["km_fwd"])
        kmr = getattr(p, self.pars["km_rev"])
        return (vmaxf * S / kmf - vmaxr * P / kmr) / (1 + S / kmf + P / kmr)


# Algebraic module templates


class Moiety(BaseAlgebraicModule):
    def __init__(self, total, variables, derived_variable):
        pars = {"total": total}
        variables = [variables] if isinstance(variables, str) else variables
        derived_variables = (
            [derived_variable]
            if isinstance(derived_variable, str)
            else derived_variable
        )
        super().__init__(
            pars=pars, variables=variables, derived_variables=derived_variables
        )

    def mod_func_strgs(self):
        return {
            self.derived_variables[
                0
            ]: f"{self.pars['total']}-{'+'.join(self.variables)}"
        }

    def mod_func(self, p, *args):
        total = getattr(p, self.pars["total"])
        return [total - sum(args)]


class MoietyUniMulti(BaseAlgebraicModule):
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


class MoietyMultiMulti(BaseAlgebraicModule):
    def __init__(self, K, variables, derived_variables):
        super().__init__(variables=variables, derived_variables=derived_variables)

    def mod_func_strgs(self):
        return {var: f"{'+'.join(self.variables)}" for var in self.derived_variables}

    def mod_func(self, p, *args):
        pass
