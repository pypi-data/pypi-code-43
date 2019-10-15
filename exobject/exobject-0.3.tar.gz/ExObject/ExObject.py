import json
import re
class ExObject():
    """CodeStyle Like DotNet By Chenyi"""
    def __init__(self, default=None):
        if (type(default) is list 
        or type(default) is dict 
        or type(default) is tuple 
        or type(default) is str  
        or type(default) is set):
            self.defaultIter=iter(default)

        if (type(default) is ExObject):
            self.default=default.default
            self.defaultIter=default.defaultIter
        else:
            self.default = default
    def __getitem__(self, key):
        if not self.default:
            return ExObject()
        if len(key)>5 and key[0:5]=="null_":
            key="?"+key[5:]
        if type(self.default) is list or type(self.default) is tuple:
            if key[:1]=="?":
                try:
                    key=key[1:]
                    if(int(key)<=len(self.default)-1):
                        return ExObject(self.default[int(key)])
                    else:
                        return ExObject()
                except KeyError:
                    return ExObject()
            else:
                return ExObject(self.default[int(key)])
        if type(key) is slice:
            #如果是分片索引
            return self.default[key]
        if key[:1]=="?":
            try:
                key=key[1:]
                if hasattr(self.default,key):
                    return ExObject(self.default.__getitem__(key))
                elif key in self.default.keys():
                    return ExObject(self.default[key])
                else:
                    return ExObject()
            except:
                return ExObject()
        else:
            return ExObject(self.default.__getitem__(key))

    def __getattr__(self, name):
        return self.__getitem__(name)
    def __str__(self):
        return str(self.default)
    def __repr__(self):
        return str(self.default)
    def __add__(self,value):
        if self.ToString():
            return self.ToString()+value
        else:
            return value
    def __bool__(self):
        if self.default:
            return True
        else:
            return False

    def __iter__(self):
        return self

    def __next__(self):
        try:
            if self.defaultIter:
                return ExObject(self.defaultIter.__next__())
            else:
                raise StopIteration()
        except:
            if (type(self.default) is list 
            or type(self.default) is dict 
            or type(self.default) is tuple 
            or type(self.default) is str  
            or type(self.default) is set):
                self.defaultIter=iter(self.default)
            raise StopIteration()

    def __len__(self):
        return len(self.default)

    def ToString(self,defaultValue="")->str:
        if self.default:
            return str(self.default)
        return defaultValue

    def __lt__(self,value):
        return self.default<value
    def __gt__(self,value):
        return self.default>value
    def __le__(self,value):
        return self.default<=value
    def __ge__(self,value):
        return self.default>=value
    def __eq__(self,value):
        return self.default==value
    def __ne__(self,value):
        return self.default!=value

    def ToCleanString(self)->str:
        return self.ToString().strip()

    def ToOriginal(self):
        return self.default

    def FirstOrDefault(self):
        if self.ToOriginal():
            return self["?0"].ToOriginal()
        return None

    def FirstOrDefaultObject(self):
        if self.ToOriginal():
            return self["?0"]
        return ExObject()

    def FirstOrDefaultString(self)->str:
        if self.ToOriginal():
            return self["?0"].ToString().strip()
        return ""

    def LastOrDefaultString(self)->str:
        if self.ToOriginal():
            return self["?"+str(len(self)-1)].ToString().strip()
        return ""

    def Where(self,func):
        if type(self.default) is list or type(self.default) is tuple or type(self.default) is dict or type(self.default) is set:
            r=[]
            for item in self:
                if func(item):
                    r.append(item)
            return ExObject(r)
        return ExObject()
    
    def Select(self,func):
        if type(self.default) is list or type(self.default) is tuple or type(self.default) is dict or type(self.default) is set:
            r=[]
            for item in self:
                r.append(func(item))
            return ExObject(r)
        return ExObject()

    def SortBy(self,func,asc=True):
        """
        func:sort Method \r\n
        asc:defalt=True
        """
        def quick_sort(b):
            if len(b) < 2:
                return b
            omid=b[len(b) // 2]
            mid = func(omid)
            left, right = [], []
            b.remove(omid)
            for item in b:
                if func(item) >= mid:
                    right.append(item)
                else:
                    left.append(item)
            return quick_sort(left) + [omid] + quick_sort(right)
        if type(self.default) is list or type(self.default) is tuple or type(self.default) is dict or type(self.default) is set:
            newList=list(self.default)
            r=quick_sort(newList)
            if not asc:
                r.reverse()
            return ExObject(r)
        return self

    @staticmethod
    def loadJson(jsonStr):
        try:
            jitem=json.loads(jsonStr)
            return ExObject(jitem)
        except:
            return ExObject()
            
    @staticmethod
    def regex(pattern,string,flags=0):
        """正则匹配并转换为ExObject类型"""
        try:
            return ExObject(re.findall(pattern,string,flags))
        except Exception as e:
            return ExObject()

    @staticmethod
    def regexOne(pattern,string):
        """获得默认第一个匹配字符串,没有匹配则返回空字符串"""
        _r=ExObject.regex(pattern,string)["?0"]
        while type(_r.default) is list or type(_r.default) is tuple:
            _r=_r["?0"]
        return _r.ToString()