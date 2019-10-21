import pytest
from decaptcha.notarobot import *


@pytest.fixture()
def bot():
    return DispersiveGround()


@pytest.fixture()
def grid(bot):
    try:
        grid = bot.findgrid()
        assert grid is not None
    except:
        button = bot.findbutton()
        grid = bot.findgrid(button)
    return grid


def test_findgrid(bot, grid):
    print(grid)
    assert grid is not None


def test_extractpuzzle(bot, grid):
    wordpuzzle_img, puzzle_img = bot.extractpuzzle(grid)
    word = bot.extractword(wordpuzzle_img)
    print(word)
    assert isinstance(word, str)
    artifacts = bot.extractartifacts(word, puzzle_img)
    assert isinstance(artifacts, dict)
    print(artifacts)
    bot.selectartifacts(artifacts, grid)
