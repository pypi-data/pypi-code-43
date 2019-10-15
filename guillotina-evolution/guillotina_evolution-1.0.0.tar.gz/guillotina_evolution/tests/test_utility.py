from guillotina.component import get_utility
from guillotina.content import create_content_in_container
from guillotina.transactions import transaction
from guillotina.utils import get_registry
from guillotina_evolution.tests.fixtures import ctx
from guillotina_evolution.utility import GENERATION_KEY
from guillotina_evolution.utility import IEvolutionUtility
from guillotina_evolution.utils import register_evolution


async def test_multiple_evolutions_at_once(loop, my_requester):
    async with ctx(my_requester) as container:
        # Create content in the container
        async with transaction():
            await create_content_in_container(container, "Item", id_="foobar")
            ob = await container.async_get("foobar")
            assert hasattr(ob, "title") is False

        # Register a new evolution
        async def ensure_all_items_have_attribute_title(container):
            async for item in container.async_values():
                item.title = ""
                item.register()

        async def ensure_all_items_have_attribute_description(container):
            async for item in container.async_values():
                item.description = "patata"
                item.register()

        utility = get_utility(IEvolutionUtility)

        async with transaction():
            await utility._update_curr_gen(0)

        utility.register(1, ensure_all_items_have_attribute_title)
        utility.register(2, ensure_all_items_have_attribute_description)

        # Evolve
        await utility.evolve(container)

        # Assert generation was updated on container registry
        async with transaction():
            registry = await get_registry()
            assert registry[GENERATION_KEY] == 2

        # Check objects after evolution
        async with transaction():
            ob = await container.async_get("foobar")
            assert ob is not None
            assert hasattr(ob, "title") is True
            assert hasattr(ob, "description") is True
            assert ob.title == ""
            assert ob.description == "patata"


async def test_registry(my_requester):
    async with ctx(my_requester):
        utility = get_utility(IEvolutionUtility)

        async with transaction():
            assert await utility._get_curr_gen() == 0

        async with transaction():
            await utility._update_curr_gen(5)

        registry = await get_registry()
        assert registry[GENERATION_KEY] == 5


def test_register_decorator():
    @register_evolution(1)
    async def migration_step(container):
        pass

    utility = get_utility(IEvolutionUtility)
    assert utility._evolvers == {1: migration_step}
