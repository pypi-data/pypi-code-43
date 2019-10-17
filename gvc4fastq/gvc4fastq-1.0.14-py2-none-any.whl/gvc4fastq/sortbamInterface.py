
class Singleton(object):
    _instance = None
    def __new__(cls,*args,**kw):
        if not cls._instance:
            cls._instance = super(Singleton,cls).__new__(cls,*args,**kw)
        return cls._instance


class SortBamInterface(Singleton):

    _l_sort_bam = list()

    def append_bam(self,bam):
        self._l_sort_bam.append(bam)

    def getbams(self):
        return self._l_sort_bam
