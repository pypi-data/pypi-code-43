# # modelbase is free software: you can redistribute it and/or modify
# # it under the terms of the GNU General Public License as published by
# # the Free Software Foundation, either version 3 of the License, or
# # (at your option) any later version.
# #
# # modelbase is distributed in the hope that it will be useful,
# # but WITHOUT ANY WARRANTY; without even the implied warranty of
# # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# # GNU General Public License for more details.
# #
# # You should have received a copy of the GNU General Public License
# # along with modelbase.  If not, see <http://www.gnu.org/licenses/>.
#
# """Stoichiometric
#
# Description of the module
#
# """
# from .. import core
# import numpy as np
# import pandas as pd
#
#
# class Model(core.Model):
#     """The main class for modeling. Provides model construction tools."""
#
#     def __init__(self):
#         super().__init__()
#         self._reactions = {}
#
#     def get_compounds(self):
#         return list(self._compounds.keys())
#
#     def add_reaction(self, name, stoichiometry, lower_bound=0, upper_bound=1000):
#         self._reactions[name] = {}
#         self._reactions[name]["stoichiometry"] = stoichiometry
#         self._reactions[name]["bounds"] = (lower_bound, upper_bound)
#
#     def get_reaction_names(self):
#         return list(self._reactions.keys())
#
#     def get_stoichiometries(self, reaction_name=None):
#         if reaction_name:
#             return self._reactions[reaction_name]["stoichiometry"]
#         else:
#             return {
#                 reaction: reaction_dict["stoichiometry"]
#                 for reaction, reaction_dict in self._reactions.items()
#             }
#
#     def get_reaction_bounds(self, reaction_name=None):
#         if reaction_name:
#             return self._reactions[reaction_name]["bounds"]
#         else:
#             return {
#                 reaction: reaction_dict["bounds"]
#                 for reaction, reaction_dict in self._reactions.items()
#             }
#
#     def get_stoichiometry_matrix(self):
#         # type: () -> np.ndarray
#         """Return the stoichiometric matrix
#         Returns
#         -------
#         stoichiometric_matrix : np.array
#         """
#         M = np.array(np.zeros([len(self._compounds), len(self._reactions)]))
#         for i, j in enumerate(self._reactions.values()):
#             for k, v in j["stoichiometry"].items():
#                 M[self._compounds[k], i] = v
#         return M
#
#     def get_stoichiometry_df(self):
#         # type: () -> np.ndarray
#         """Return the stoichiometric matrix as a pandas DataFrame
#         Returns
#         -------
#         stoichiometric_matrix : pd.DataFrame
#         """
#         # type: () -> pd.DataFrame
#         return pd.DataFrame(
#             self.get_stoichiometry_matrix(),
#             self.get_compounds(),
#             self.get_reaction_names(),
#         )
#
#
# def reduce_kinetic_model(model):
#     """Reduce kinetic modelbase.ode model into stoichiometric model"""
#     sm = Model()
#     sm.add_compounds(list(model.get_compounds().keys()))
#     for reaction_name, stoichiometry in model.get_stoichiometries().items():
#         sm.add_reaction(reaction_name, stoichiometry)
#     return sm
