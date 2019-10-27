import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
from . import helpers

''' ellipses don't look very nice'''

def all(name, mass=None, sma=None, inc=None):
	try:
		nsma, nmass, ninc= len(sma), len(mass), len(inc)
	except: 
		raise ValueError('sma, mass, inc have to be iterable\n{} {} {}'.format(
							type(sma), type(mass), type(inc)))
	
	assert nsma == nmass == ninc
	
	for k, (a, m, i) in enumerate(zip (sma, mass, inc)):
		fname= '{}/arch{}'.format(name, k)
		individual(fname, np.asarray(a),np.asarray(m),np.asarray(i))
	
def individual(fname, a,m,i, angle=35, ratio= 0.3):
	f, ax = plt.subplots()
	ax.set_title('Architecture')
	ax.set_xlabel('sma')
	ax.set_ylabel('inc[?]')

	ax.set_xlim(-3,1)
	ax.set_ylim(-3,1)
	
	x0, y0= -2, -2
			
	_system(f, ax, a, m, i, x0=x0, y0=y0, angle=angle, ratio=ratio)
	
	helpers.save(plt, 'png/architecture/{}'.format(fname))		

def _system(f, ax, a, m, i, x0=0, y0=0, angle=35, ratio=0.3):
	''' 
	plots an individual system onto a predefined axis 
	NOTE on Ellipse : 
		sma is North-South
		height/width are _diameter_
	'''
	
	amin= np.log10(0.05)-x0
	e= Ellipse((x0, y0), height= 2.*amin, width= 2.*amin*ratio, angle= angle-90, fill=False, ec='b')
	ax.add_artist(e)

	amax= np.log10(1.0)-x0
	e= Ellipse((x0, y0), height= 2.*amax, width= 2.*amax*ratio, angle= angle-90, fill=False, ec='b')
	ax.add_artist(e)


	xx= np.linspace(*ax.get_xlim())
	ax.plot(x0+ (xx-x0)* np.cos(np.pi* (angle)/180.), 
			y0+ (xx-x0)* np.sin(np.pi* (angle)/180.), marker='', ls=':', color='0.5')

	di= i * np.resize([1,-1], i.size) # alternating angles
	sma_x= x0+ (np.log10(a)-x0)* np.cos(np.pi* (angle+0.5*di)/180.)
	sma_y= y0+ (np.log10(a)-x0)* np.sin(np.pi* (angle+0.5*di)/180.)
	
	ax.plot(sma_x, sma_y, ls='', marker='o', color='b')
	
	for _a, _m, _i, _di in zip(a, m, i, di):
		diameter= 2.*(np.log10(_a)-x0)
		e= Ellipse((x0, y0), height=diameter, width=diameter*ratio, 
			angle= angle-90+0.5*_di, 
			fill=False, ec='b',ls=':')
		ax.add_artist(e)
	