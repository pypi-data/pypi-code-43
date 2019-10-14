from optimeed.core.tools import get_ND_pareto
from optimeed.optimize.optiAlgorithms.convergence.hypervolume import HyperVolume
import numpy as np
from .interfaceConvergence import InterfaceConvergence
from optimeed.visualize import Graphs, Data


class EvolutionaryConvergence(InterfaceConvergence):
    """convergence class for population-based algorithm"""

    def __init__(self, is_monobj=False):
        self.objectives_per_step = dict()
        self.constraints_per_step = dict()
        self.is_monobj = is_monobj

    def set_points_at_step(self, theStep, theObjectives_list, theConstraints_list):
        self.objectives_per_step[theStep] = theObjectives_list
        self.constraints_per_step[theStep] = theConstraints_list

    def get_pareto_convergence(self):
        paretos = dict()
        previous_pareto = list()
        for step in self.objectives_per_step:
            objectives = previous_pareto

            for i in range(len(self.objectives_per_step[step])):
                respect_constraints = True
                for constraint in self.constraints_per_step[step][i]:
                    if constraint > 0:
                        respect_constraints = False
                        break

                if respect_constraints:
                    objectives.append(self.objectives_per_step[step][i])

            try:
                paretos[step], _ = get_ND_pareto(objectives)
            except IndexError:
                paretos[step] = list()
            previous_pareto = paretos[step][:]
        return paretos

    def get_last_pareto(self):
        return self.get_pareto_convergence()[max(self.objectives_per_step.keys())]

    def get_hypervolume_convergence(self, refPoint=None):
        """Get the hypervolume indicator on each step

        :param refPoint: Reference point needed to compute the hypervolume. If None is specified, uses the nadir point Example: [10, 10] for two objectives.
        :return:
        """
        if not self.is_monobj:
            paretos = self.get_pareto_convergence()
            if refPoint is None:
                refPoint = self.get_nadir_point_all_steps()
            hypervolumes = dict()
            hv = HyperVolume(refPoint)
            for step in paretos:
                hypervolumes[step] = hv.compute(paretos[step])

            return hypervolumes
        else:
            paretos = self.get_pareto_convergence()
            theResult = dict()
            for step in paretos:
                theResult[step] = paretos[step][0][0]
            return theResult

    def get_nb_objectives(self):
        last_step = max(self.objectives_per_step.keys())
        return len(self.objectives_per_step[last_step][0])

    def get_nadir_point(self):

        paretos = self.get_pareto_convergence()
        nb_objectives = self.get_nb_objectives()
        last_step = max(self.objectives_per_step.keys())

        nadir = [None] * nb_objectives
        for i in range(nb_objectives):
            nadir[i] = max([objectives[i] for objectives in paretos[last_step]])
        return nadir

    def get_nadir_point_all_steps(self):

        paretos = self.get_pareto_convergence()
        nb_objectives = self.get_nb_objectives()

        nadir = [-np.inf] * nb_objectives
        for step in self.objectives_per_step:
            for i in range(nb_objectives):
                try:
                    nadir[i] = max([max(nadir[i], objectives[i]) for objectives in paretos[step]])
                except ValueError:
                    pass
        return nadir

    def get_nb_steps(self):
        return len(self.objectives_per_step)

    def get_population_size(self):
        return len(self.objectives_per_step[list(self.objectives_per_step.keys())[0]])

    def get_graphs(self):
        theGraphs = Graphs()
        g1 = theGraphs.add_graph()
        hypervolumes = self.get_hypervolume_convergence()
        paretos = self.get_pareto_convergence()
        theDataHV = Data([], hypervolumes.values(), x_label="Step", y_label="Hypervolume")
        theGraphs.add_trace(g1, theDataHV)

        if self.get_nb_objectives() == 1:
            g2 = theGraphs.add_graph()
            theDataPareto = Data([], [objectives[0][0] for objectives in paretos.values()], x_label="Step", y_label="Objective")
            theGraphs.add_trace(g2, theDataPareto)
        elif self.get_nb_objectives() == 2:
            g2 = theGraphs.add_graph()
            for step in paretos:
                theDataPareto = Data([objectives[0] for objectives in paretos[step]], [objectives[1] for objectives in paretos[step]], sort_output=True, x_label="Objective1", y_label="Objective2")
                theGraphs.add_trace(g2, theDataPareto)
        else:
            pass
        return theGraphs
