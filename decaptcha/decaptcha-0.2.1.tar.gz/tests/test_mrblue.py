import pytest
from decaptcha.base import GroundState


@pytest.fixture()
def DispersiveGround():
    class DispersiveGround(GroundState):
        def run(self):
            pass

        def next(self):
            pass

    return DispersiveGround


@pytest.fixture()
def bot(DispersiveGround):
    return DispersiveGround()


@pytest.fixture()
def mrblue(bot):
    mrblue = bot.findmrblue()
    print(mrblue)
    return mrblue


def test_redundantclick(bot, mrblue):
    clicked = bot.redundantclick(mrblue)
    print(clicked)
