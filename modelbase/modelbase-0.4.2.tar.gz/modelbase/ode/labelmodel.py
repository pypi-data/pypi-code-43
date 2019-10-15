# modelbase is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# modelbase is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with modelbase.  If not, see <http://www.gnu.org/licenses/>.

"""Model

Description of the module

"""


import itertools
import numpy as _np
import pandas as _pd

from .model import Model


class LabelModel(Model):
    """Extension of model class able to create models with
    carbon labeling pattern information."""

    def __init__(self, parameters=None):
        super().__init__(parameters)
        self._carbon_compounds = {}

    @staticmethod
    def _generate_compound_labels(compound_name, carbons):
        """Convenience function to create binary label string

        Parameters
        ----------
        compound_name : str
            Base name of the compound
        carbons : int
            Number of carbons in the compound

        Returns
        -------
        list[str]
            Returns a list of all label isotopomers of the compound
        """
        if carbons > 0:
            return [
                compound_name + "_" + "".join(i)
                for i in itertools.product(("0", "1"), repeat=carbons)
            ]
        else:
            return [compound_name]

    @staticmethod
    def _split_label_string(label, carbon_list):
        """Splits the label string according to the lengths given in numc

        Parameters
        ----------
        numc : int
            Number of carbons

        Returns
        -------
        splitLabels : list
            List of label positions
        """
        split_labels = []
        cnt = 0
        for i in range(len(carbon_list)):
            split_labels.append(label[cnt : cnt + carbon_list[i]])
            cnt += carbon_list[i]
        return split_labels

    def _create_carbon_compounds(self, compound_name, carbons):
        """Adds all label isotopomers of a compound to the model and creates an algebraic module
        that tracks the total concentration of that compound

        Parameters
        ----------
        compound_name : str
            Base name of the compound
        carbons : int
            Number of carbons in the compound
        """
        # Write compound and carbon information
        self._carbon_compounds[compound_name] = {"carbons": None, "isotopomers": None}
        self._carbon_compounds[compound_name]["carbons"] = carbons

        # Create all possible labelling patterns
        label_names = self._generate_compound_labels(compound_name, carbons)

        # Write derived labels into carbon compounds as well
        self._carbon_compounds[compound_name]["isotopomers"] = label_names

        # Add all labeled compounds
        self.add_compounds(label_names)

        # Create moiety for total compound concentration
        if carbons > 1:
            self.add_algebraic_module(
                compound_name + "_total",
                lambda p, *args: [_np.sum(args, axis=0)],
                label_names,
                [compound_name + "_total"],
            )

    def add_carbon_compounds(self, compounds, carbons=None):
        """Adds a carbon containing compound to the model.
        Either supply a compound name and the number of carbons
        or a dictionary containing {compound:carbons}.

        Parameters
        ----------
        compounds : dict or str
            Name of the compound
        c : int, optional
            Number of carbon atoms of the compound
        """
        if isinstance(compounds, dict):
            for compound_name, carbons in compounds.items():
                self._create_carbon_compounds(compound_name, carbons)
        elif isinstance(compounds, str):
            self._create_carbon_compounds(compounds, carbons)
        else:
            raise TypeError("Function requires list or string input")

    def remove_carbon_compounds(self, compounds):
        """Removes carbon compounds

        Parameters
        ----------
        compounds : str or list of str
            Carbon compounds to be removed

        Raises
        ------
        TypeError
            If compounds is neither str nor list of str
        """

        def _remove_compound(compound):
            self._carbon_compounds.pop(compound)
            for key in list(self._compounds):
                if key.startswith(compound):
                    self._compounds.pop(key)

        if isinstance(compounds, str):
            _remove_compound(compounds)
        elif isinstance(compounds, list):
            for compound in compounds:
                _remove_compound(compound)
        else:
            raise TypeError("Function requires list or string input")

    def get_carbon_compounds(self, compound=None):
        """Returns a dictionary mapping the compounds with the amount of carbons they have

        Parameters
        ----------
        compound : str, optional:
            Constrain output to a single compound
        """
        if compound:
            return self._carbon_compounds[compound]["carbons"]
        else:
            return {
                i: self._carbon_compounds[i]["carbons"] for i in self._carbon_compounds
            }

    def get_compound_isotopomers(self, compound=None):
        """Returns a dictionary mapping compounds to their isotopomers

        Parameters
        ----------
        compound : str, optional:
            Constrain output to a single compound
        """
        if compound:
            return self._carbon_compounds[compound]["isotopomers"]
        else:
            return {
                i: self._carbon_compounds[i]["isotopomers"]
                for i in self._carbon_compounds
            }

    def add_carbonmap_reaction(
        self,
        base_rate_name,
        rate_function,
        carbon_map,
        substrates,
        products,
        additonal_variables=None,
        external_labels=None,
    ):
        """Add a carbonmap reaction. The carbon map maps the carbons of the substrates to those
        of the products. A reaction in which the first and third carbon of two three carbon sugars
        are switched thus has the carbon map [2, 1, 0]. Note that forward and backward reactions
        have to be separated. In reactions containing more carbons in the products than in the substrates
        the position in which the label is inserted can be given by external_labels.

        Parameters
        ----------
        base_rate_name: str
        rate_function: Callable
        carbon_map : list
        substrates : list of str
        products : list of str
        additional_variables : list of str
        external_labels : list of int

        Examples
        --------
        m.add_carbonmap_reaction('TPI_forward',
                                 lambda p, GAP: p.kf_TPI * GAP,
                                 [2, 1, 0],
                                 ['GAP'],
                                 ['DHAP'])

        External labels:
        m = LabelModel()
        m.add_carbon_compounds({'x': 1, 'y': 2})
        m.add_carbonmap_reaction('v_xy', lambda p, x: x, [0, 1], ['x'], ['y'])

        external_labels = [0] or external_labels=None:
            {'x_0': -1, 'y_01': 1}

        external_labels = []:
            {'x_0': -1, 'y_00': 1}
        """
        if not additonal_variables:
            additonal_variables = []

        # First we need to get the amount of carbons of substrates and products
        carbons_substrates = [self.get_carbon_compounds()[i] for i in substrates]
        carbons_products = [self.get_carbon_compounds()[i] for i in products]

        # Check if we need to add external labels: for reactions in which there are more carbons
        # in the products than in the substrates (e.g. influx)
        n_external_labels = sum(carbons_products) - sum(carbons_substrates)
        if n_external_labels > 0:
            # Check whether label import is specified in kwargs
            if external_labels is not None:
                external_label_string = ["0"] * n_external_labels
                for label in external_labels:
                    external_label_string[label] = "1"
                external_labels = "".join(external_label_string)
            else:
                external_labels = "1" * n_external_labels
        else:
            external_labels = ""

        # Get all possible suffixes of label patterns for rates
        rate_suffixes = [
            "".join(i)
            for i in itertools.product(("0", "1"), repeat=sum(carbons_substrates))
        ]

        # Create all reactions
        for suffix in rate_suffixes:
            # Add external labels to suffix
            product_suffix = suffix + external_labels

            # Redistribute string for the products, according to the carbonmap
            product_suffix = "".join([product_suffix[i] for i in carbon_map])

            # Split the label string according to the lengths given by products and substrates
            substrate_labels = self._split_label_string(suffix, carbons_substrates)
            product_labels = self._split_label_string(product_suffix, carbons_products)

            # Add the corresponding substrate isotopomer as argument
            substrate_args = []
            for i, substrate in enumerate(substrates):
                if substrate_labels[i] != "":
                    substrate_args.append(substrate + "_" + substrate_labels[i])
                else:
                    substrate_args.append(substrate)

            # The same for the products
            product_args = []
            for i, product in enumerate(products):
                if product_labels[i] != "":
                    product_args.append(product + "_" + product_labels[i])
                else:
                    product_args.append(product)

            # Create rate function variables
            rate_variables = substrate_args + additonal_variables
            # Create rate stoichiometries
            stoichiometries = {k: -1 for k in substrate_args}
            for k in product_args:
                if k in stoichiometries:
                    stoichiometries[k] += 1
                else:
                    stoichiometries[k] = 1

            if suffix != "":
                rate_name = base_rate_name + "_" + suffix
            else:
                rate_name = base_rate_name

            self.add_reaction(rate_name, rate_function, stoichiometries, rate_variables)

    def remove_carbonmap_reaction(self, rate_name):
        """Removes all variants of a base reaction
        Args:
            reaction (str): base reaction name
        """
        if isinstance(rate_name, str):
            rate_name = rate_name + "_"
            for rate in self.get_rate_names():
                if rate.startswith(rate_name):
                    self._rates.pop(rate)
        else:
            raise TypeError("Function requires str input")

    def _generate_y0(self, init, label_position=None):
        """Generate a vector containing all label combination from the base name dictionary.
        Args:
            init (dict):
            label_position (dic t): containing information about already labeled carbons
        """
        if not label_position:
            label_position = {}

        if isinstance(init, list) or isinstance(init, _np.ndarray):
            init = dict(zip(self.get_carbon_compounds(), init))

        # Create empty vector
        y0 = _np.zeros(len(self._compounds))

        for compound, carbons in self.get_carbon_compounds().items():
            labels = ["0"] * carbons
            if compound in label_position:
                positions = label_position[compound]
                if isinstance(positions, int):
                    labels[positions] = "1"
                elif isinstance(positions, list):
                    for pos in positions:
                        labels[pos] = "1"
            if carbons > 0:
                base_compound = compound + "_" + "".join(labels)
            else:
                base_compound = compound
            y0[self._compounds[base_compound]] = init[compound]
        return y0

    def get_total_rate(self, t, y0, rate):
        """Get the combined rate of all reactions of a base rate
        Args:
            t (int, float, list, ndarray):
            y0 Dict:
            rate (str):
        """
        rates = self.get_fluxes(0, y0)
        return _np.sum([v for k, v in rates.items() if k.startswith(rate)], axis=0)

    def get_label_scope(self, initial_labels):
        """Returns all label positions that can be reached step by step.
        Parameters
        ----------
        initial_labels : list of str
            List of the already labeled positions, e.g. x_01

        Returns
        -------
        label_scope : dict{step : set of new positions}
        """
        if not isinstance(initial_labels, list):
            raise TypeError("Initial labels must be list")
        # Initialize all compounds with 0 (no label)
        labeled_compounds = {compound: 0 for compound in self.get_compounds().keys()}

        # Set all unlabeled compounds to 1, this also sets all compounds
        # that cannot be labeled (c = 0) to 1
        for compound, carbons in self.get_carbon_compounds().items():
            labels = "0" * carbons
            if carbons == 0:
                labeled_compounds[f"{compound}"] = 1
            else:
                labeled_compounds[f"{compound}_{labels}"] = 1

        # Set initial label
        for i in initial_labels:
            if i in labeled_compounds:
                labeled_compounds[i] = 1
            else:
                raise ValueError(f"Compound {i} is not in the model")

        new_labels = set("non empty entry to not fulfill while condition")

        # Loop until no new labels are inserted
        loop_count = 0
        result = {}

        while new_labels != set():
            new_cpds = labeled_compounds.copy()

            for rec, cpd_dict in self.get_stoichiometries().items():
                # Isolate substrates
                cpds = [i for i, j in cpd_dict.items() if j < 0]

                # Count how many of the substrates are 1
                i = 0
                for j in cpds:
                    i += labeled_compounds[j]

                # If all substrates are 1, set all products to 1
                if i == len(cpds):
                    for cpd in self.get_stoichiometries()[rec]:
                        new_cpds[cpd] = 1

            # Isolate "old" labels
            s1 = _pd.Series(labeled_compounds)
            s1 = s1[s1 == 1]

            # Isolate new labels
            s2 = _pd.Series(new_cpds)
            s2 = s2[s2 == 1]

            # Find new labels
            new_labels = set(s2.index).difference(set(s1.index))

            # Break the loop once no new labels can be found
            if new_labels == set():
                break
            else:
                labeled_compounds = new_cpds
                result[loop_count] = new_labels
                loop_count += 1
        return result
