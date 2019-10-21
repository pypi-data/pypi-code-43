import pytest
from pyautogui import locateOnScreen


def test_greencheck():
    greencheck = locateOnScreen("decaptcha/greencheck.png", confidence=0.7)
    print(greencheck)
