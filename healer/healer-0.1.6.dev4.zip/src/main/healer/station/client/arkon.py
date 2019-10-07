"""
Station web client module
"""

from .assist import *
from .unit import ArkonUnit
from .unit import ArkonView

console_log('%c HEALER CLIENT ', 'background: #222; color: #bada55')

window.view = ArkonView().arkon
window.unit = ArkonUnit().arkon
