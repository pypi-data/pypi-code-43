# import cobra
#
#
# class Simulator:
#     def __init__(self, model):
#         self._model = model
#         self._cobra_model = cobra.Model()
#         self._solution = None
#
#         metabolites = {i: cobra.Metabolite(i) for i in self._model.get_compounds()}
#         self._cobra_model.add_metabolites(list(metabolites.values()))
#
#         reactions = {}
#         for reaction_name, reaction_dict in self._model._reactions.items():
#             reactions[reaction_name] = cobra.Reaction(reaction_name)
#             reaction_metabolites = {
#                 metabolites[i]: j for i, j in reaction_dict["stoichiometry"].items()
#             }
#             reactions[reaction_name].add_metabolites(reaction_metabolites)
#             lb, ub = reaction_dict["bounds"]
#             reactions[reaction_name].lower_bound = lb
#             reactions[reaction_name].upper_bound = ub
#
#         self._cobra_model.add_reactions(list(reactions.values()))
#
#     def set_objective_function(self, function_dict):
#         objective = {
#             getattr(self._cobra_model.reactions, key): value
#             for key, value in function_dict.items()
#         }
#         self._cobra_model.objective = objective
#
#     def simulate(self):
#         self._solution = self._cobra_model.optimize()
#         return self._solution
#
#     def get_objective_value(self):
#         return self._solution.objective_value
#
#     def get_solution_status(self):
#         return self._solution.status
#
#     def get_solution_fluxes(self):
#         return self._solution.fluxes
#
#     def get_solution_shadow_prices(self):
#         return self._solution.shadow_prices
