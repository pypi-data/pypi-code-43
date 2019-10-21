import pytest
from decaptcha import *


@pytest.fixture(scope="session")
def bot():
    bot = NotARobot()
    bot.set_model("yolo.h5")
    return bot


def test_bot(bot):
    bot.run()
    assert bot.state.victory == True or bot.state.killswitch == True
