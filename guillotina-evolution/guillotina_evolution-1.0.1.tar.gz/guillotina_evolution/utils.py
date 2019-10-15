from guillotina.component import get_utility
from guillotina_evolution.interfaces import IEvolutionUtility


def register_evolution(gen):
    def decorator(evolver):
        utility = get_utility(IEvolutionUtility)
        utility.register(gen, evolver)
        return evolver

    return decorator
