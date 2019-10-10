# -*- coding: utf-8 -*-
from .click_spinner import Spinner


def init_spinner(beep=True, disable=False, force=False):
    spinner = Spinner(beep=beep, disable=disable, force=force)
    return spinner


def start_spinner(spinner):
    spinner.start()


def stop_spinner(spinner):
    spinner.stop()
