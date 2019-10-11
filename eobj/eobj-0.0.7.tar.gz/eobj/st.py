import ltdict.ltdict as ltlt
import edict.edict as eded

def st2ivltd(st):
    ltd = {}
    index = 0
    for each in st:
        ltd[index] = each
        index = index + 1
    return(ltd)

def st2viltd(st):
    ltd = st2ivltd(st)
    ltd = eded.dict_mirror(ltd)
    return(ltd)

def st2md(st):
    ltd = {}
    index = 0
    for each in st:
        ltd[index] = each
        ldt[each] = index
        index = index + 1
    return(ltd)

class nset(set):
    def ivltd(self):
        return(st2ivltd(self))
    def viltd(self):
        return(st2viltd(self))
    def mdltd(self):
        return(st2md(self))
