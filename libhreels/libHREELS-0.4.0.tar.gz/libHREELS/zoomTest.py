import matplotlib.pyplot as plt
import numpy as np


def omega(q):
    '''Returns the two solutions for the lattice vibration of a one-dimensional chain with 2 atoms for a wavevector q in units of pi/a'''
    m1 = 1.3      # mass of atom 1
    m2 = 1.7      # mass of atom 2
    D = 1.       # spring constant
    a = D*(1./m1 + 1./m2)
    b = D*np.sqrt((1/m1+1/m2)**2 - 4./m1/m2*(np.sin(q/2.))**2)
    return np.sqrt(a+b), np.sqrt(a-b)

fig = plt.figure()
ax = fig.add_subplot(111)
 
q = np.arange(0,np.pi*1.15,0.05)
ax.plot(q, omega(q)[0])
ax.plot(q, omega(q)[1])
plt.ylim(0,2.2)
 
xmin, xmax = ax.get_xlim() 
ymin, ymax = ax.get_ylim()
print(xmin, xmax, ymin, ymax )
 

plt.show()

xmin, xmax = ax.get_xlim() 
ymin, ymax = ax.get_ylim()
print(xmin, xmax, ymin, ymax )
