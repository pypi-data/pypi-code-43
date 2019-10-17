def UIRobot():
    """load UIRobot driver"""
    from .uirobot.uirobot_binding import UIRobot_binding

    return UIRobot_binding


def Fake():
    """load fake driver"""
    from .fake import FakeMotor

    return FakeMotor


def RandomlyFailing():
    """load randomly failing driver"""
    from .randomly_failing import RandomlyFailingMotor

    return RandomlyFailingMotor


drivers = {
    "UIRobot": UIRobot,
    "Fake": Fake,
    "RandomlyFailing": RandomlyFailing,
}


def select_motor(driver):
    return drivers.get(driver, Fake)()
