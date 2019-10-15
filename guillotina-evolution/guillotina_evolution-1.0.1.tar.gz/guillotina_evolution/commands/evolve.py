from guillotina.commands import Command
from guillotina.component import get_utility
from guillotina.tests.utils import login
from guillotina.utils import get_containers
from guillotina_evolution.utility import IEvolutionUtility


class EvolveCommand(Command):
    description = "Run evolution"

    async def run(self, arguments, settings, app):
        login()
        utility = get_utility(IEvolutionUtility)
        async for _, _, container in get_containers():
            await utility.evolve(container)
