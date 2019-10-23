# >>> obj.__setattr__(html.entities.html5['theta;'],None)
# >>> obj.__setattr__(html.entities.html5['varepsilon;'],None)
# >>>
# >>> obj.
# obj.θ  obj.ϵ
# >>> obj.


import html

class _Null():
    def __init__(self,*args):
        self.Θ = "null" if(len(args) ==0) else args[0]
    def __repr__(self):
        return(self.Θ)

#isinstance 属于继承链 就行

def _get_html5_entities():
    entities = html.entities.html5
    obj = _Null("html.entities.html5")
    for k in entities:
        nk = k.strip(";")
        obj.__setattr__(nk,entities[k])
    return(obj)

h5 = _get_html5_entities()

_kl = list(html.entities.html5.keys())
_dkl = [k.strip(";") for k in _kl]
_vl = list(html.entities.html5.values())


#from estring.h5entity import h5
