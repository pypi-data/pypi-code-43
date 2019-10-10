# -*- coding: utf-8 -*-
from .dvtDecimal import *


version = '1.3.3'

if __name__ == '__main__':
    # f = dvtDecimal(-604, 260)
    # print(f.fraction())
    # f.dispResults()
    # print(f.dotWrite(20))
    # print(f.intPart)
    # print(f.irrPart())
    # print(f.repPart)
    # print(f.repPartC())
    # print(f.periodLen())
    # print(f.gcd)
    # print(f.initValues)
    # print(f.simpValues)
    # print(f.mixedF())
    # print('###')
    # f = dvtDecimal(1, 5)
    # g = dvtDecimal(10, 3)
    # h = f + g
    # print(h.mixedF())
    # print('###')
    # i = f / g
    # print(i.mixedF())
    # print('###')
    # f = dvtDecimal(1, 5)
    # g = dvtDecimal(7, 5)
    # h = f - g
    # print(h.simpValues)
    # print(h.sign)
    # print(h.mixedF())
    # print('###')
    # f = dvtDecimal(1, 5)
    # g = 5
    # h = f * g
    # h.dispResults()
    # print(h.sign)
    # print(h.mixedF())
    # print(h.isDecimal())

    # f = dvtDecimal(3.2587)
    # f.dispResults()

    # f = dvtDecimal('0123456789')
    # print(f.simpValues)

    # f = dvtDecimal(18,5)
    # print(f.mixedF())
    # f.tolerance=1e-10
    # print(f.egyptFractions())
    # f.tolerance = 1e-8
    # print(f.egyptFractions(lim=5))
    # print(f.egyptFractions(eF=4))
    # print(f.intPart)
    # print(f.egyptG2())
    
    # f = dvtDecimal(5, 121)
    # print(f.egyptFractions(eF=3, lim=1))
    # print(f.tolerance)
    # f.tolerance = 1e-30
    # print(f.egyptFractions(eF=3))
    # for i in range(100,110):
    #     f = dvtDecimal(1, i)
    #     a, b =f.egyptG2()
    #     #d, e, g = f.egyptFractions2(lim=1)[0]
    #     h, j, k = f.egyptFractions(lim=1)[0]
    #     print(f.initValues, b, j)

    # h = dvtDecimal(1,200)
    # print(h.egyptG2())
    # print(h.egyptFractions())
    # #print(h.egyptFractions2(lim=1))

    # h = dvtDecimal(18,5)
    # s = h.egyptFractions()
    # print(s)
    # s = h.egyptFractions(lim=5)
    # print(s)
    # s = h.egyptFractions(eF=4, lim=0)
    # print()
    # comp = 0
    # for k in s:
    #     print(k, '  \t', end='')
    #     comp = (comp + 1) % 4
    #     if comp == 0:
    #         print()
    
    # #print(s)
    # print('\n') 
    # print(len(s))
    # print(h.intPart)
    # print(h.egyptG2())
    # # s = set(tuple(i) for i in s)
    # # t = h.egyptFractions2(lim='all')
    # # t = set(tuple(i) for i in t)
    # # print([ p in t for p in t^s])
    #print(f.dotWrite(20))

    
    #f=dvtDecimal(3.14159265)
    #print(f.contFraction())
    
    
    #for r in ratApp([3, 7, 15, 1, 292, 1, 1, 1, 2]):
    #    print(" {:<11}{:<11}".format(*r.simpValues), r.dotWrite(12))

    # import math
    # f = dvtDecimal(round(math.sqrt(2), 10))
    # liste = f.contFraction()
    # for g in ratApp(liste):
    #     print(" {:<11}{:<11}".format(*g.simpValues), g.dotWrite(10))

    
    # f=dvtDecimal(634, 75)
    # c=f.contFraction()
    # print(ratApp(c))
    # for d in ratApp(c):
    #     print("{:<1}+{:>3}/{:<2}  {:<11}".format(*d.mixedF(), d.dotWrite(10)))

    # f=dvtDecimal(3.14159265)
    # c=f.contFraction()
    # print(ratApp(c))
    # for d in ratApp(c):
    #     print("{:<1}+{:>7}/{:<8}  {:<8}".format(*d.mixedF(), d.dotWrite(15)))
    
    
    # f=dvtDecimal(365.2421898)
    # c=f.contFraction()
    # for n in ratApp(c):
    #     print(n.mixedF(), n.dotWrite(10))

    # aS=365.2421898
    # mF=[]
    # for a in range(7):
    #     aaS=round(aS,7-a)
    #     print(aaS)
    #     f=dvtDecimal(aaS)
    #     c=f.contFraction()
    #     for d in ratApp(c):
    #         #print(n.mixedF(), n.dotWrite(10))
    #         mF+=[d.mixedF()]
    
    # mF=[list(x) for x in set(tuple(x) for x in mF)]
    # mF.sort(key=lambda l:l[1])
    # print(mF)

        
    # f = dvtDecimal(365.2425)
    # c = f.contFraction()
    # for d in ratApp(c):
    #     print("{:<1}+{:>3}/{:<3}  {:<4}".format(*d.mixedF(), d.dotWrite(4)))


    #problème avec .57 .58 .59
    # for x in [.55, .56, .57, .58, .59, .6]:
    #     f = dvtDecimal(x)
    #     #print(f.dispResults())
    #     g = f * f * f
    #     print("{:<4} {:<4} {:>10}".format(x, f.dotWrite(2), g.dotWrite(10)))

    # f = dvtDecimal(0)
    # f.dispResults()

    # f=dvtDecimal(0.141592)
    # # print(f.egyptFractions(eF=5, lim=1))

    # import math
    # for e in 2, 3, 5, 7, 8, 11, 13, 17, 19, 31:
    #     print(e, contFractionQ((1+math.sqrt(e))/2))
    print(">>> from dvtDecimal import *")
    import math
    f = dvtDecimal(1, 2019)
    print(">>> f = dvtDecimal(1, 2019)")
    print(">>> f.repPart\n"+str(f.repPart))
    f = dvtDecimal('2019')
    print()
    print(">>> f = dvtDecimal('2019')")
    print(">>> f.dotWrite(20)\n"+str(f.dotWrite(20)))
    print(">>> f.egyptG2()\n"+str(f.egyptG2()))
    print(">>> f.egyptFractions()\n"+str(f.egyptFractions()))
    #print(">>> f.egyptFractions(eF=4, lim=1)\n"+str(f.egyptFractions(eF=4, lim=1)))
    print()
    print(">>> import math")
    print(">>> contFractionQ(math.sqrt(2019))\n"+str(contFractionQ(math.sqrt(2019))))
    #print(contFractionQ(math.sqrt(2020)))
