import matplotlib.pyplot as plt

from .instance import Instance
from .solution import Solution


class Visualizer:
    def _plot_points(self, instance: Instance):
        plt.title(instance.name)
        x = [p.get_x() for p in instance]
        y = [p.get_y() for p in instance]
        plt.plot(x, y, 'o', color="black")

    def _plot_edges(self, instance: Instance, solution: Solution):
        for edge in solution:
            p0 = instance[edge.get_i()]
            p1 = instance[edge.get_j()]
            plt.plot([p0.get_x(), p1.get_x()], [p0.get_y(), p1.get_y()], color="blue")

    def _show_or_save(self, path):
        if path:
            plt.savefig(path)
        else:
            plt.show()
        plt.close()

    def visualize_instance(self, instance: Instance, path=None):
        self._plot_points(instance)
        self._show_or_save(path)

    def visualize_solution(self, instance: Instance, solution: Solution, path=None):
        self._plot_edges(instance, solution)
        self._plot_points(instance)
        self._show_or_save(path)
