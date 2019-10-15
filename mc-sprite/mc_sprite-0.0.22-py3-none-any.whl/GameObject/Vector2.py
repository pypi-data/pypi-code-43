import math
from Timer.Time import Time
class Vector(object):
    def __init__(self, x = 0, y = 0):
        object.__init__(self)
        self._x=x
        self._y=y
        self.oldV=(x,y)
        self.parent=None
        pass
    def Set(self, x = 0, y =0):
        self._x=x
        self._y=y
        #self.parent.rect.move_ip(x,y)
        self.oldV=(x,y)
    def SetParent(self,parent):
        self.parent=parent
        pass
    def UpadteRectPos(self):
        self.parent.rect.move_ip(self._x,self._y)
    @property
    def x(self):
        return self._x
    @property
    def y(self):
        return self._y
    @x.setter
    def x(self,value):
        self._x=value
        if self.parent!=None:
            #self.parent.rect.move_ip(value,0)
            pass
    @y.setter
    def y(self,value):
        self._y=value
        if self.parent!=None:
            #self.parent.rect.move_ip(0,value)
            pass
    @property
    def smoothX(self):
        return self._x
    @smoothX.setter
    def smoothX(self,value):
        self._x += value*Time.deltaTime
        #self.parent.rect.move_ip(value*Time.deltaTime,0)
    @property
    def smoothY(self):
        return self._x
    @smoothY.setter
    def smoothY(self,value):
        self._y += value*Time.deltaTime
        #self.parent.rect.move_ip(0,value*Time.deltaTime)
    @property
    def value(self):
        return (self._x,self._y)
    @property
    def right():
        return Vector(1,0)
    @property
    def left():
        return Vector(-1,0)
    @property
    def down():
        return Vector(0,-1)
    @property
    def up():
        return Vector(0,1)
    @property
    def zero():
        return Vector(0,0)
    @property
    def one():
        return Vector(1,1)
    @property
    def magnitude(self):
        return math.sqrt(self._x*self._x+self._y*self._y)
    @staticmethod
    def MoveTowards(current, target, maxDistanceDelta):
        if current == target:
            return target
        else:
            return (target-current)*maxDistanceDelta*Time.deltaTime
    @staticmethod
    def Move(current,maxDistanceDelta,direction):
        temp=None
        if direction == Vector.right:
            temp = Vector(current.x+maxDistanceDelta*Time.deltaTime, current.y)
            temp.parent=current.parent
            #temp.parent.rect.move_ip(maxDistanceDelta*Time.deltaTime,0)
        elif direction == Vector.left:
            temp = Vector(current.x-maxDistanceDelta*Time.deltaTime, current.y)
            temp.parent=current.parent
            #temp.parent.rect.move_ip(-maxDistanceDelta*Time.deltaTime,0)
        elif direction == Vector.up:
            temp = Vector(current.x, current.y-maxDistanceDelta*Time.deltaTime)
            temp.parent=current.parent
            #temp.parent.rect.move_ip(0,-maxDistanceDelta*Time.deltaTime)
        elif direction == Vector.down:
            temp = Vector(current.x, current.y+maxDistanceDelta*Time.deltaTime)
            temp.parent=current.parent
            #temp.parent.rect.move_ip(0,maxDistanceDelta*Time.deltaTime)
        temp.oldV=current.value
        return temp
        pass
    def __getitem__(self, key):
        pass
    def __call__(self):
        return self
    def __eq__(self, other):
        if self._x == other[0] and self._y == other[1]:
            return True
        else:
            return False
    def __sub__(self, other):
        return Vector(self._x-other.x,self._y-other.y)
    def __add__(self, other):
        return Vector(self._x+other.x,self._y+other.y)
    def __mul__(self, other: int):
        return Vector(self._x*other,self._y*other)
        