from .._swatches import _swatches
from . import nav as _nav

def swatches():
    return _swatches(__name__, globals())

swatches.__doc__ = _swatches.__doc__

navColors = [_nav.navRod, _nav.navOransje, _nav.navLimeGronn, _nav.navGronn, _nav.navLilla, _nav.navDypBla,
            _nav.navBla, _nav.navLysBla]

navGrays = [_nav.navGra20, _nav.navGra40, _nav.navGra60, _nav.navGra80,
           _nav.navMorkGra]






   
