from .._swatches import _swatches
from .._colormaps import _linear3color
from . import nav as _nav

def swatches():
    return _swatches(__name__, globals())

swatches.__doc__ = _swatches.__doc__

navRodBla = _linear3color(_nav.navRod, _nav.navLysBla, _nav.navBla)
navBlaRod = _linear3color(_nav.navBla, _nav.navLysBla, _nav.navRod)
navGronnRod = _linear3color(_nav.navGronn, _nav.navLimeGronn, _nav.navRod)
navRodGronn = _linear3color(_nav.navRod, _nav.navLimeGronn, _nav.navGronn)
navLysBlaMorkBla = _linear3color(_nav.navLysBla, _nav.navBla, _nav.navDypBla)






   
