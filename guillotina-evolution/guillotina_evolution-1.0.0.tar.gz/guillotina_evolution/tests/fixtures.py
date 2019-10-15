from contextlib import asynccontextmanager
from guillotina import task_vars
from guillotina import testing
from guillotina.component import get_utility
from guillotina.tests import utils
from guillotina.tests.fixtures import ContainerRequesterAsyncContextManager
from guillotina.tests.utils import get_container
from guillotina_evolution.interfaces import IEvolutionUtility

import json
import pytest


def base_settings_configurator(settings):
    if "applications" in settings:
        settings["applications"].append("guillotina_evolution")
    else:
        settings["applications"] = ["guillotina_evolution"]


testing.configure_with(base_settings_configurator)


class guillotina_evolution_Requester(ContainerRequesterAsyncContextManager):  # noqa
    async def __aenter__(self):
        await super().__aenter__()
        await self.requester(
            "POST",
            "/db/guillotina/@addons",
            data=json.dumps({"id": "guillotina_evolution"}),
        )
        utility = get_utility(IEvolutionUtility)
        await get_container(db=self.requester.db)
        await utility.install()
        return self.requester


@pytest.fixture(scope="function")
async def my_requester(guillotina):
    return guillotina_evolution_Requester(guillotina)


@asynccontextmanager
async def ctx(my_requester):
    async with my_requester as requester:
        task_vars.db.set(requester.db)
        container = await get_container(db=requester.db)
        utils.login()
        yield container
