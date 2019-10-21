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


def test_imnotarobot(bot):
    clicked = bot.imnotarobot()
    print(clicked)
