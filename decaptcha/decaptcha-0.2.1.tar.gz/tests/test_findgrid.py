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
def grid(bot):
    try:
        grid = bot.findgrid()
    except:
        try:
            button = bot.findbutton()
            grid = bot.findgrid(button)
        except:
            grid = None

    return grid


def test_findgrid(bot, grid):
    print(grid)
    assert grid is not None


def test_savepuzzle(bot, grid):
    bot.savepuzzle(grid, "testpuzzle.png")
