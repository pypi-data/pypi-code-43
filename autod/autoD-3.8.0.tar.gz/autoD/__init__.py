'''
##########################################
The MIT License (MIT)

Copyright (c) 2016 w.x.chan1986@gmail.com

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
#############################################

File: autoD.py
Description: Forward automatic differentiation
History:
    Date    Programmer SAR# - Description
    ---------- ---------- ----------------------------
  Author: w.x.chan1986@gmail.com 24Feb2016           - Created
  Author: w.x.chan1986@gmail.com 25Feb2016           - v2
                                        -include multi-variable entry
  Author: w.x.chan1986@gmail.com 03May2016           - v2.1
                                        -change x and dOrder inputs to type dict
                                        -corrected Multiply, Power etc. on value of new differntiation order
                                        -corrected change multiplication to numpy.dots
  Author: w.x.chan1986@gmail.com 18May2016           - v3
                                        -corrected bug in Power where power goes to -1 from 0
                                        -add dependent scalars to reduce runtime
  Author: w.x.chan1986@gmail.com 19May2016           - v3.1
                                        -remove class creation inside class function to reduce runtime
                                        -Multiply and Addition now accepts floats as one of the object in list
  Author: w.x.chan1986@gmail.com 03Jun2016           - v3.2
                                        -added complex conjugate, real and imaginary
                                        -added shortcut method __add__ etc
  Author: w.x.chan1986@gmail.com 13Dec2016           - v3.3
                                        -added absolute
  Author: w.x.chan1986@gmail.com 02Jan2017           - v3.4
                                        -added hyperbolic trigo functions
  Author: w.x.chan1986@gmail.com 03Jan2017           - v3.5
                                        -added debug print out
  Author: w.x.chan1986@gmail.com 04Jan2017           - v3.5.1
                                        -overwrite __new__ to return number when input is not AD object
                                        -move debug control to the main module functions
  Author: w.x.chan1986@gmail.com 17Jan2017           - v3.6.0
                                        -change all object to callable __call__ instead of using .cal()
  Author: w.x.chan1986@gmail.com 16Jul2017           - v3.6.1
                                        -debug Power class with power=0 (error in differentiating x^0 wrt x)
                                        -added self print to indicate dependent variables
  Author: w.x.chan1986@gmail.com 16Jul2017           - v3.7.0
                                        -clean up __new__ for pickle
                                        -swap is instance(float,int,...) to not(isinstance(AD))
  Author: w.x.chan1986@gmail.com 14Oct2019           - v3.8.0
                                        -change dOrder to kwarg

'''

'''
Standardized class def: 
func            class object      class object must contain the following function
                                    def __call__(self,x,dOrder):
                                        x        dict[identifier]=float
                                        dOrder   dict[identifier]=int
                                        return float results or call to other class object __call__ function

Note:
I divided the Class into three types; basic functions, base-end functions and flexible functions.
Basic functions contain class objects that deals with differentiating operations.
Base end functions returns the result for any order of differentiation without call to other functions (seed).
Flexible functions accepts user-defined function and turn them into callable objects "func" in this module.


'''
_version='3.8.0'
print('autoD version',_version)

import numpy as np
'''
--------------------Main Class-----------------
'''
class AD:
    def defaultDebugSwitch(self,x,dOrder,result):
        return True
    debugPrintout=False
    debugName=''
    debugSwitchFunc=defaultDebugSwitch
    def __pow__(self, val):
        return Power(self,val)
    def __rpow__(self, val):
        return Power(val,self)
    def __add__(self, val):
        return Addition([self,val])
    def __radd__(self, val):
        if val == 0:
            return self
        else:
            return Addition([self,val])
    def __sub__(self, val):
        return Addition([self,Multiply([-1.,val])])
    def __rsub__(self,val):
        return Addition([val,Multiply([-1.,self])])
    def __mul__(self, val):
        return Multiply([self,val]) 
    def __rmul__(self, val):
        if val == 1:
            return self
        else:
            return Multiply([self,val])
    def __truediv__(self, val):
        return Multiply([self,Power(val,-1)])
    def __rtruediv__(self, val):
        return Multiply([val,Power(self,-1)])
    def __neg__(self):
        return Multiply([-1.,self])
    def __str__(self):
        try:
            if 'ALL' in self.dependent:
                return 'autoD function'
        except NameError:
            return 'autoD function'
        strOut=','.join(self.dependent)
        return 'autoD function('+strOut+')'
    def debugPrint(self,x,dOrder,result):
        if self.debugPrintout and self.debugSwitchFunc(x,dOrder,result):
            print(self.debugName,'@',x)
            print('    differential=',dOrder)
            print('    value=',result)
        return;
    
        
'''
#---------------Basic Functions-------------------------------#
'''

class Differentiate(AD):
    def __new__(cls, *args, **kwargs):
        if args:
            if not(isinstance(args[0], AD)):
                if bool(kwargs):
                    for order in kwargs.values:
                        if order>0:
                            return 0.
                return args[0]
        return super().__new__(cls)
    def __init__(self,func,order):
        self.inputFunc=func
        self.inputorder=order
        try:
            self.dependent=func.dependent[:]
        except AttributeError:
            self.dependent=['ALL']
    def __call__(self,x,dOrder={}):
        new_dOrder=dOrder.copy()
        for var in self.inputorder:
            if var in dOrder:
                new_dOrder[var]=self.inputorder[var]+dOrder[var]
            else:
                new_dOrder[var]=self.inputorder[var]+0
        if 'ALL' not in self.dependent:
            for var in new_dOrder:
                if new_dOrder[var]>0 and (var not in self.dependent):
                    self.debugPrint(x,dOrder,0.)
                    return 0.
        result=self.inputFunc(x,new_dOrder)
        self.debugPrint(x,dOrder,result)
        return result
        
class Addition(AD):
    def __new__(cls, *args, **kwargs):
        if args:
            for func in args[0]:
                if isinstance(func, AD):
                    return super().__new__(cls)
        else:
            return super().__new__(cls)
        return sum(args[0])
    def __init__(self,funcList):
        self.funcList=funcList
        for n in range(len(self.funcList)):
            if not(isinstance(self.funcList[n], AD)):
                self.funcList[n]=Constant(self.funcList[n])
        self.dependent=[]
        for func in self.funcList:
            try:
                for dependent in func.dependent:
                    if dependent not in self.dependent:
                        self.dependent.append(dependent)
            except AttributeError:
                self.dependent=['ALL']
            
    def __call__(self,x,dOrder={}):
        if 'ALL' not in self.dependent:
            for var in dOrder:
                if dOrder[var]>0 and (var not in self.dependent):
                    self.debugPrint(x,dOrder,0.)
                    return 0.
        temp=[]
        for n in range(len(self.funcList)):
            temp.append(self.funcList[n](x,dOrder))
        result=sum(temp)
        self.debugPrint(x,dOrder,result)
        return result
              
class Multiply(AD):
    def __new__(cls, *args, **kwargs):
        if args:
            for func in args[0]:
                if isinstance(func, AD):
                    return super().__new__(cls)
            mul=1.
            for func in args[0]:
                mul*=func
        else:
            return super().__new__(cls)
        return mul
    def __init__(self,funcList):
        self.funcList=[]
        self.coef=1.
        self.dependent=[]
        for func in funcList:
            if isinstance(func, AD):
                self.funcList.append(func)
            else:
                self.coef=self.coef*func
        for func in self.funcList:
            try:
                for dependent in func.dependent:
                    if dependent not in self.dependent:
                        self.dependent.append(dependent)
            except AttributeError:
                self.dependent=['ALL']
        self.rdOL=rotatingdOrderList(len(self.funcList))
    def __call__(self,x,dOrder={}):
        if 'ALL' not in self.dependent:
            for var in dOrder:
                if dOrder[var]>0 and (var not in self.dependent):
                    self.debugPrint(x,dOrder,0.)
                    return 0.
        dOrderList,keyList=splitdOrder(dOrder)
        addList=[]
        pastCalculation={}
        if len(dOrderList)==0:
            mul=self.coef
            for n in range(len(self.funcList)):
                mul=mul*self.funcList[n](x,{})
            self.debugPrint(x,dOrder,mul)
            return mul
        self.rdOL.reset(dOrderList)
        while not(self.rdOL.end):
            mul=self.coef
            temp_dOrderList=self.rdOL.get()
            for n in range(len(self.funcList)):
                pastCalculationKey=str(n)+' '+''.join(map(str,temp_dOrderList[n]))
                if pastCalculationKey in pastCalculation:
                    mul=mul*pastCalculation[pastCalculationKey]
                else:
                    temp_dOrder=mergedOrder(temp_dOrderList[n],keyList)
                    temp_value=self.funcList[n](x,temp_dOrder)
                    pastCalculation[pastCalculationKey]=temp_value
                    mul=mul*temp_value
            addList.append(mul)
            self.rdOL.incr()
        result=sum(addList)
        self.debugPrint(x,dOrder,result)
        return result

class Power(AD):
    def __new__(cls, *args, **kwargs):
        if args:
            if not(isinstance(args[0], AD)) and not(isinstance(args[1], AD)):
                    return args[0]**args[1]
        return super().__new__(cls)
    def __init__(self,func,pow):
        if isinstance(func, AD):
            self.func=func
        else:
            self.func=Constant(func)
        self.pow=pow 
        try:
            self.dependent=func.dependent[:]
        except AttributeError:
            self.dependent=['ALL']
        if isinstance(self.pow, AD):
            self.new_exp=Exp(Multiply([Ln(self.func),self.pow]))
            try:
                for dependent in pow.dependent:
                    if dependent not in self.dependent:
                        self.dependent.append(dependent)
            except AttributeError:
                self.dependent=['ALL']
        else:
            self.new_exp=None
        self.rdOL=rotatingdOrderListPower()
    def __call__(self,x,dOrder={}):
        if 'ALL' not in self.dependent:
            for var in dOrder:
                if dOrder[var]>0 and (var not in self.dependent):
                    self.debugPrint(x,dOrder,0.)
                    return 0.
        if self.pow==1:
            result=self.func(x,dOrder)
            self.debugPrint(x,dOrder,result)
            return result
        elif self.pow==0:
            result=Constant(1.)(x,dOrder)
            self.debugPrint(x,dOrder,result)
            return result
        elif not(self.new_exp==None):
            result=self.new_exp(x,dOrder)
            self.debugPrint(x,dOrder,result)
            return result
        dOrderList,keyList=splitdOrder(dOrder)
        if len(dOrderList)==0:
            result=self.func(x,dOrder)**self.pow
            self.debugPrint(x,dOrder,result)
            return result
        self.rdOL.reset(dOrderList)
        addList=[]
        pastCalculation={}
        while not(self.rdOL.end):
            mul=1.
            temp_dOrderList=self.rdOL.get()
            count=0
            for n in range(len(temp_dOrderList)):
                if len(temp_dOrderList[n])!=0:
                    mul=mul*(self.pow-count)
                    count+=1
            if mul!=0:
                if (self.pow-count)!=0:
                    mul=mul*self.func(x,{})**(self.pow-count)
                for n in range(len(temp_dOrderList)):
                    if len(temp_dOrderList[n])!=0:
                        pastCalculationKey=''.join(map(str, temp_dOrderList[n]))
                        if pastCalculationKey in pastCalculation:
                            mul=mul*pastCalculation[pastCalculationKey]
                        else:
                            temp_dOrder=mergedOrder(temp_dOrderList[n],keyList)
                            temp_value=self.func(x,temp_dOrder)
                            pastCalculation[pastCalculationKey]=temp_value
                            mul=mul*temp_value
                addList.append(mul)
            self.rdOL.incr()
        result=sum(addList)
        self.debugPrint(x,dOrder,result)
        return result
    
class Exp(AD):
    def __new__(cls, *args, **kwargs):
        if args:
            if not(isinstance(args[0], AD)):
                    return np.exp(args[0])
        return super().__new__(cls)
    def __init__(self,func):
        self.func=func
        if isinstance(func, AD):
            self.func=func
        else:
            self.func=Constant(func)
        try:
            self.dependent=func.dependent[:]
        except AttributeError:
            self.dependent=['ALL']
        self.rdOL=rotatingdOrderListPower()
    def __call__(self,x,dOrder={}):
        if 'ALL' not in self.dependent:
            for var in dOrder:
                if dOrder[var]>0 and (var not in self.dependent):
                    self.debugPrint(x,dOrder,0.)
                    return 0.
        dOrderList,keyList=splitdOrder(dOrder)
        exp_value=np.exp(self.func(x,{}))
        if len(dOrderList)==0:
            self.debugPrint(x,dOrder,exp_value)
            return exp_value
        self.rdOL.reset(dOrderList)
        addList=[]
        pastCalculation={}
        while not(self.rdOL.end):
            mul=1.
            temp_dOrderList=self.rdOL.get()
            for n in range(len(temp_dOrderList)):
                if len(temp_dOrderList[n])!=0:
                    pastCalculationKey=''.join(map(str,temp_dOrderList[n]))
                    if pastCalculationKey in pastCalculation:
                        mul=mul*pastCalculation[pastCalculationKey]
                    else:
                        temp_dOrder=mergedOrder(temp_dOrderList[n],keyList)
                        temp_value=self.func(x,temp_dOrder)
                        pastCalculation[pastCalculationKey]=temp_value
                        mul=mul*temp_value
            addList.append(mul)
            self.rdOL.incr()
        result=sum(addList)*exp_value
        self.debugPrint(x,dOrder,result)
        return result
        
class Ln(AD):
    def __new__(cls, *args, **kwargs):
        if args:
            if not(isinstance(args[0], AD)):
                    return np.log(args[0])
        return super().__new__(cls)
    def __init__(self,func):
        self.func=func
        if isinstance(func, AD):
            self.func=func
        else:
            self.func=Constant(func)
        try:
            self.dependent=func.dependent[:]
        except AttributeError:
            self.dependent=['ALL']
        self.rdOL=rotatingdOrderListPower()
    def __call__(self,x,dOrder={}):
        if 'ALL' not in self.dependent:
            for var in dOrder:
                if dOrder[var]>0 and (var not in self.dependent):
                    self.debugPrint(x,dOrder,0.)
                    return 0.
        dOrderList,keyList=splitdOrder(dOrder)
        if len(dOrderList)==0:
            result=np.log(self.func(x,{}))
            self.debugPrint(x,dOrder,result)
            return result
        self.rdOL.reset(dOrderList)
        addList=[]
        pastCalculation={}
        while not(self.rdOL.end):
            mul=1.
            temp_dOrderList=self.rdOL.get()
            count=0
            for n in range(len(temp_dOrderList)):
                if len(temp_dOrderList[n])!=0:
                    if count!=0:
                        mul=mul*count
                    count-=1
            mul=mul*self.func(x,{})**count
            for n in range(len(temp_dOrderList)):
                if len(temp_dOrderList[n])!=0:
                    pastCalculationKey=''.join(map(str,temp_dOrderList[n]))
                    if pastCalculationKey in pastCalculation:
                        mul=mul*pastCalculation[pastCalculationKey]
                    else:
                        temp_dOrder=mergedOrder(temp_dOrderList[n],keyList)
                        temp_value=self.func(x,temp_dOrder)
                        pastCalculation[pastCalculationKey]=temp_value
                        mul=mul*temp_value
            addList.append(mul)
            self.rdOL.incr()
        result=sum(addList)
        self.debugPrint(x,dOrder,result)
        return result
        
class Log(AD):
    def __new__(cls, *args, **kwargs):
        if args:
            if not(isinstance(args[0], AD)) and not(isinstance(args[1], AD)):
                    return np.log(args[0])/np.log(args[1])
        return super().__new__(cls)
    def __init__(self,func,base):
        self.func=func
        if isinstance(func, AD):
            self.func=func
        else:
            self.func=Constant(func)
        self.base=base
        try:
            self.dependent=func.dependent[:]
        except AttributeError:
            self.dependent=['ALL']
        if not(isinstance(self.base, (int, float,complex))):
            self.new_ln=Multiply([Ln(self.func),Power(Ln(self.base),-1.)])
            self.coef=1.
            for dependent in self.base.dependent:
                if dependent not in self.dependent:
                    self.dependent.append(dependent)
        else:
            self.new_ln=Ln(self.func)
            self.coef=-1./np.log(self.base)
    def __call__(self,x,dOrder={}):
        if 'ALL' not in self.dependent:
            for var in dOrder:
                if dOrder[var]>0 and (var not in self.dependent):
                    self.debugPrint(x,dOrder,0.)
                    return 0.
        result=self.coef*self.new_ln(x,dOrder)
        self.debugPrint(x,dOrder,result)
        return result
            
class Cos(AD):
    def __new__(cls, *args, **kwargs):
        if args:
            if isinstance(args[0], (int, float,complex)):
                    return np.cos(args[0])
        return super().__new__(cls)
    def __init__(self,func):
        self.func=func
        if isinstance(func, AD):
            self.func=func
        else:
            self.func=Constant(func)
        try:
            self.dependent=func.dependent[:]
        except AttributeError:
            self.dependent=['ALL']
        self.rdOL=rotatingdOrderListPower()
    def __call__(self,x,dOrder={}):
        if 'ALL' not in self.dependent:
            for var in dOrder:
                if dOrder[var]>0 and (var not in self.dependent):
                    self.debugPrint(x,dOrder,0.)
                    return 0.
        dOrderList,keyList=splitdOrder(dOrder)
        cosValue=np.cos(self.func(x,{}))
        if len(dOrderList)==0:
            self.debugPrint(x,dOrder,cosValue)
            return cosValue
        self.rdOL.reset(dOrderList)
        addList=[]
        pastCalculation={}
        sinValue=np.sin(self.func(x,{}))
        while not(self.rdOL.end):
            mul=1.
            temp_dOrderList=self.rdOL.get()
            count=0
            for n in range(len(temp_dOrderList)):
                if len(temp_dOrderList[n])!=0:
                    count+=1
            for n in range(len(temp_dOrderList)):
                if len(temp_dOrderList[n])!=0:
                    pastCalculationKey=''.join(map(str,temp_dOrderList[n]))
                    if pastCalculationKey in pastCalculation:
                        mul=mul*pastCalculation[pastCalculationKey]
                    else:
                        temp_dOrder=mergedOrder(temp_dOrderList[n],keyList)
                        temp_value=self.func(x,temp_dOrder)
                        pastCalculation[pastCalculationKey]=temp_value
                        mul=mul*temp_value
            temp=count%4
            if temp==0:
                mul=mul*cosValue
            elif temp==1:
                mul=-mul*sinValue
            elif temp==2:
                mul=-mul*cosValue
            elif temp==3:
                mul=mul*sinValue
            addList.append(mul)
            self.rdOL.incr()
        result=sum(addList)
        self.debugPrint(x,dOrder,result)
        return result
class Cosh(AD):
    def __new__(cls, *args, **kwargs):
        if args:
            if not(isinstance(args[0], AD)):
                    return np.cosh(args[0])
        return super().__new__(cls)
    def __init__(self,func):
        self.func=func
        if isinstance(func, AD):
            self.func=func
        else:
            self.func=Constant(func)
        try:
            self.dependent=func.dependent[:]
        except AttributeError:
            self.dependent=['ALL']
        self.cosh=Cos(func*1j)
    def __call__(self,x,dOrder={}):
        result=self.cosh(x,dOrder)
        self.debugPrint(x,dOrder,result)
        return result
class Sin(AD):
    def __new__(cls, *args, **kwargs):
        if args:
            if not(isinstance(args[0], AD)):
                    return np.sin(args[0])
        return super().__new__(cls)
    def __init__(self,func):
        self.func=func
        if isinstance(func, AD):
            self.func=func
        else:
            self.func=Constant(func)
        try:
            self.dependent=func.dependent[:]
        except AttributeError:
            self.dependent=['ALL']
        self.rdOL=rotatingdOrderListPower()
    def __call__(self,x,dOrder={}):
        if 'ALL' not in self.dependent:
            for var in dOrder:
                if dOrder[var]>0 and (var not in self.dependent):
                    self.debugPrint(x,dOrder,0.)
                    return 0.
        dOrderList,keyList=splitdOrder(dOrder)
        sinValue=np.sin(self.func(x,{}))
        if len(dOrderList)==0:
            self.debugPrint(x,dOrder,sinValue)
            return sinValue
        self.rdOL.reset(dOrderList)
        addList=[]
        pastCalculation={}
        cosValue=np.cos(self.func(x,{}))
        while not(self.rdOL.end):
            mul=1.
            temp_dOrderList=self.rdOL.get()
            count=0
            for n in range(len(temp_dOrderList)):
                if len(temp_dOrderList[n])!=0:
                    count+=1
            for n in range(len(temp_dOrderList)):
                if len(temp_dOrderList[n])!=0:
                    pastCalculationKey=''.join(map(str,temp_dOrderList[n]))
                    if pastCalculationKey in pastCalculation:
                        mul=mul*pastCalculation[pastCalculationKey]
                    else:
                        temp_dOrder=mergedOrder(temp_dOrderList[n],keyList)
                        temp_value=self.func(x,temp_dOrder)
                        pastCalculation[pastCalculationKey]=temp_value
                        mul=mul*temp_value
            temp=count%4
            if temp==0:
                mul=mul*sinValue
            elif temp==1:
                mul=mul*cosValue
            elif temp==2:
                mul=-mul*sinValue
            elif temp==3:
                mul=-mul*cosValue
            addList.append(mul)
            self.rdOL.incr()
        result=sum(addList)
        self.debugPrint(x,dOrder,result)
        return result
class Sinh(AD):
    def __new__(cls, *args, **kwargs):
        if args:
            if not(isinstance(args[0], AD)):
                    return np.sinh(args[0])
        return super().__new__(cls)
    def __init__(self,func):
        self.func=func
        if isinstance(func, AD):
            self.func=func
        else:
            self.func=Constant(func)
        try:
            self.dependent=func.dependent[:]
        except AttributeError:
            self.dependent=['ALL']
        self.sinh=-1j*Sin(func*1j)
    def __call__(self,x,dOrder={}):
        result=self.sinh(x,dOrder)
        self.debugPrint(x,dOrder,result)
        return result
class Tan(AD):
    def __new__(cls, *args, **kwargs):
        if args:
            if not(isinstance(args[0], AD)):
                    return np.tan(args[0])
        return super().__new__(cls)
    def __init__(self,func):
        self.func=func
        if isinstance(func, AD):
            self.func=func
        else:
            self.func=Constant(func)
        try:
            self.dependent=func.dependent[:]
        except AttributeError:
            self.dependent=['ALL']
        self.tan=Sin(func)/Cos(func)
    def __call__(self,x,dOrder={}):
        result=self.tan(x,dOrder)
        self.debugPrint(x,dOrder,result)
        return result
class Tanh(AD):
    def __new__(cls, *args, **kwargs):
        if args:
            if not(isinstance(args[0], AD)):
                    return np.tanh(args[0])
        return super().__new__(cls)
    def __init__(self,func):
        self.func=func
        if isinstance(func, AD):
            self.func=func
        else:
            self.func=Constant(func)
        try:
            self.dependent=func.dependent[:]
        except AttributeError:
            self.dependent=['ALL']
        self.tanh_negative=(1-Exp(-2.*func))/(1+Exp(-2.*func))
        self.tanh_positive=(Exp(2.*func)-1)/(Exp(2.*func)+1)
    def __call__(self,x,dOrder={}):
        result=self.tanh_negative(x,dOrder)
        if not(float('-inf')<np.abs(result)<float('inf')):
            result=self.tanh_positive(x,dOrder)
        self.debugPrint(x,dOrder,result)
        return result
'''
#---------------Complex Functions-------------------------------#
'''
class Conjugate(AD):
    def __new__(cls, *args, **kwargs):
        if args:
            if not(isinstance(args[0], AD)):
                    return np.conjugate(args[0])
        return super().__new__(cls)
    def __init__(self,func):
        self.func=func
        if isinstance(func, AD):
            self.func=func
        else:
            self.func=Constant(func)
        try:
            self.dependent=func.dependent[:]
        except AttributeError:
            self.dependent=['ALL']
    def __call__(self,x,dOrder={}):
        result=np.conjugate(self.func(x,dOrder))
        self.debugPrint(x,dOrder,result)
        return result
class Real(AD):
    def __new__(cls, *args, **kwargs):
        if args:
            if not(isinstance(args[0], AD)):
                    return args[0].real
        return super().__new__(cls)
    def __init__(self,func):
        self.func=func
        if isinstance(func, AD):
            self.func=func
        else:
            self.func=Constant(func)
        try:
            self.dependent=func.dependent[:]
        except AttributeError:
            self.dependent=['ALL']
    def __call__(self,x,dOrder={}):
        result=self.func(x,dOrder).real
        self.debugPrint(x,dOrder,result)
        return result
class Imaginary(AD):
    def __new__(cls, *args, **kwargs):
        if args:
            if not(isinstance(args[0], AD)):
                    return args[0].imag
        return super().__new__(cls)
    def __init__(self,func):
        self.func=func
        if isinstance(func, AD):
            self.func=func
        else:
            self.func=Constant(func)
        try:
            self.dependent=func.dependent[:]
        except AttributeError:
            self.dependent=['ALL']
    def __call__(self,x,dOrder={}):
        result=self.func(x,dOrder).imag
        self.debugPrint(x,dOrder,result)
        return result
class Absolute(AD):
    def __new__(cls, *args, **kwargs):
        if args:
            if not(isinstance(args[0], AD)):
                    return np.absolute(args[0])
        return super().__new__(cls)
    def __init__(self,func):
        self.func=func
        if isinstance(func, AD):
            self.func=func
        else:
            self.func=Constant(func)
        self.abs=(Real(self.func)**2.+Imaginary(self.func)**2.)**0.5
        try:
            self.dependent=func.dependent[:]
        except AttributeError:
            self.dependent=['ALL']
    def __call__(self,x,dOrder={}):
        result=self.abs(x,dOrder)
        self.debugPrint(x,dOrder,result)
        return result
'''
#---------------Base End Functions-------------------------------#
'''
            
class Constant(AD):
    def __init__(self,const):
        self.const=const
        self.dependent=[]
    def __call__(self,x,dOrder={}):
        for var in dOrder:
            if dOrder[var]>0:
                self.debugPrint(x,dOrder,0.)
                return 0.
                break
        else:
            self.debugPrint(x,dOrder,self.const)
            return self.const
         
class Scalar(AD):
    def __init__(self,name):
        self.name=name
        self.dependent=[name]
    def __call__(self,x,dOrder={}):
        returnX=True
        for var in dOrder:
            if dOrder[var]>0:
                if var==self.name:
                    if dOrder[var]>1:
                        self.debugPrint(x,dOrder,0.)
                        return 0.
                    else:
                        returnX=False
                else:
                    self.debugPrint(x,dOrder,0.)
                    return 0.
        if returnX:
            self.debugPrint(x,dOrder,x[self.name])
            return x[self.name]
        else:
            self.debugPrint(x,dOrder,1.)
            return 1. 
'''
#---------------Flexible Functions-----------------#
'''
class Function(AD):
    def __init__(self,func,*args,dependent=['ALL']):
        self.func=func
        self.args=args
        self.dependent=dependent
    def __call__(self,x,dOrder={}):
        args=self.args
        result=self.func(x,dOrder,*args)
        self.debugPrint(x,dOrder,result)
        return result
    def changeArgs(self,*new_args):
        self.args=new_args
        return;
    def checkArgs(self):
        return self.args

'''
--------------------Functions used-----------------
'''
def mergedOrder(dOrderList,keyList):
    newdOrder={}
    for ind in dOrderList:
        if keyList[ind] in newdOrder:
            newdOrder[keyList[ind]]+=1
        else:
            newdOrder[keyList[ind]]=1
    return newdOrder
def splitdOrder(dOrder):
    dOrderList=[]
    keyList=[]
    temp_dOrder=dOrder.copy()
    count=0
    for key in temp_dOrder:
        keyList.append(key)
        while temp_dOrder[key]>0:
            dOrderList.append(count)
            temp_dOrder[key]-=1
        count+=1
    return (dOrderList,keyList)
class rotatingdOrderList:
    def __init__(self,numOfFunc):
        self.rotatingList=[]
        self.dOrderList=[]
        self.dOrderListNum=0
        self.numOfFunc=numOfFunc
        self.end=False
    def reset(self,dOrderList):
        self.rotatingList=[]
        self.dOrderList=dOrderList
        self.dOrderListNum=len(dOrderList)
        for n in range(self.dOrderListNum):
            self.rotatingList.append(0)
        self.end=False
    def incr(self):
        ind=0
        count=True
        while not(self.end) and count:
            if self.rotatingList[ind]>=(self.numOfFunc-1):
                self.rotatingList[ind]=0
                if ind==(self.dOrderListNum-1):
                    self.end=True
                else:
                    ind+=1
            else:
                self.rotatingList[ind]+=1
                count=False
    def get(self):
        arrangeList=[]
        for n in range(self.numOfFunc):
            arrangeList.append([])
        for n in range(self.dOrderListNum):
            arrangeList[self.rotatingList[n]].append(self.dOrderList[n])
        return arrangeList
class rotatingdOrderListPower:
    def __init__(self):
        self.rotatingList=[]
        self.dOrderList=[]
        self.dOrderListNum=0
        self.numOfFunc=-1
        self.end=False
    def reset(self,dOrderList):
        self.rotatingList=[]
        self.dOrderList=dOrderList
        self.dOrderListNum=len(dOrderList)
        for n in range(self.dOrderListNum):
            self.rotatingList.append(0)
        self.end=False
        self.numOfFunc=self.dOrderListNum
    def incr(self):
        ind=0
        count=True
        while not(self.end) and count:
            if ind==(self.dOrderListNum-1):
                self.end=True
            elif self.rotatingList[ind]>max(self.rotatingList[(ind+1):]):
                self.rotatingList[ind]=0
                ind+=1
            else:
                self.rotatingList[ind]+=1
                count=False
    def get(self):
        arrangeList=[]
        for n in range(self.numOfFunc):
            arrangeList.append([])
        for n in range(self.dOrderListNum):
            arrangeList[self.rotatingList[n]].append(self.dOrderList[n])
        return arrangeList
                
'''
-------------------- Debug functions -----------------
'''
def debugSwitch(adObject,func):
    if isinstance(adObject, AD):
        adObject.debugSwitchFunc=func
    return;    
def debugOn(adObject,name=''):
    if isinstance(adObject, AD):
        adObject.debugPrintout=True
        if name!='':
            adObject.debugName=name
    return;
def debugOff(adObject):
    if isinstance(adObject, AD):
        adObject.debugPrintout=False
    return;
