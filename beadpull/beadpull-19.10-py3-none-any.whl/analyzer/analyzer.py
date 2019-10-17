def Agilent8753et():
    """load Agilent8753et driver"""
    from .agilent8753et.agilent8753et_binding import Agilent8753et_binding

    return Agilent8753et_binding


def Fake():
    """load fake driver"""
    from .fake import FakeAnalyzer

    return FakeAnalyzer


def RandomlyFailing():
    """load randomly failing driver"""
    from .randomly_failing import RandomlyFailingAnalyzer

    return RandomlyFailingAnalyzer


drivers = {
    "Agilent8753et": Agilent8753et,
    "Fake": Fake,
    "RandomlyFailing": RandomlyFailing,
}


def select_analyzer(driver):
    return drivers.get(driver, Fake)()
