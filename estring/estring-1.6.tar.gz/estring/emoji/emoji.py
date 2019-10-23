from efdir import fs
import pkg_resources
from elist.elist import mapv
from dlist.dlist import dlist2dict
from edict.edict import d2kvlist

# MANIFEST.in 设置完毕后
# 记住在setup.py 设置
#      include_package_data=True,
#      package_data = {
#          'resources':["estring/emoji/resources/*"]
#      },


dtbfn = pkg_resources.resource_filename("estring","emoji/resources/emoji.dtb.json")
dtb = fs.rjson(dtbfn)
_dl = mapv(dtb,lambda row:{row['desc']:row['ord']})
d = dlist2dict(_dl)
_kl,_vl = d2kvlist(d)

class _Null():
    def __init__(self,*args):
        self.Θ = "null" if(len(args) ==0) else args[0]
    def __repr__(self):
        return(self.Θ)

def _get_emojies():
    obj = _Null("emoji")
    for k in d:
        obj.__setattr__(k,d[k])
    return(obj)


emoji = _get_emojies()

