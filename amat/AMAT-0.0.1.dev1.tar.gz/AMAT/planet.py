'''
FILENAME : planet.py
AUTHOR   : Athul Pradeepkumar Girija
E-MAIL   : apradee@purdue.edu / athulpg007@gmail.com
PURPOSE  : Define planetary constants and load atmosphere models

CREATED  : Oct 17, 2019
MODIFIED : Oct 17, 2019

REQUIRES : numpy, scipy
'''

import numpy as np
from scipy.interpolate import interp1d

class Planet:

	def __init__(self, planetID):

		'''
		Initializes planet object with physical properties such as radius, rotation rate etc...
		'''
		
		if planetID == 'VENUS':

			self.ID     = 'VENUS'      # planet identifier string, string
			self.RP     = 6051.8000E3  # mean radius of the target planet in meters, float
			self.OMEGA  = -2.99237E-7  # mean angular velocity of rotation of the planet about its axis of rotation in rad/s, float
			self.GM     = 3.248599E14  # gravitational parameter of the planet in M3/S2, include as many significant digits available, float
			self.rho0   = 64.790       # reference atmospheric density at the surface of the target planet in kg/m3, float
			self.CPCV   = 1.289        # reference specific heat ratio CP/CV at the surface of the planet, float
			self.J2     = 4.458E-6     # gravitational harmonic J2, float
			self.J3     = 0.000000     # gravitational harmonic J3, float
			self.h_thres= 180000.0     # atmospheric model cutoff / threshold altitude in meters, density = 0, if h>h_thres, float
			self.h_skip = 180000.0     # define skip out altitude in METERS: if vehicle altitude exceeds this value, trajectory is cut off, float
			self.h_trap = 10000.0      # define trap in altitude  in meters: if vehicle altitude falls below this value, trajectory is cut off, float

		elif planetID == 'EARTH':

			self.ID     = 'EARTH'      # planet identifier string, string
			self.RP     = 6371.0000E3  # mean radius of the target planet in meters, float
			self.OMEGA  = 7.272205E-5  # mean angular velocity of rotation of the planet about its axis of rotation in rad/s, float
			self.GM     = 3.986004E14  # gravitational parameter of the planet in M3/S2, include as many significant digits available, float 
			self.rho0   = 1.2250       # reference atmospheric density at the surface of the target planet in kg/m3, float
			self.CPCV   = 1.4          # reference specific heat ratio CP/CV at the surface of the planet, float
			self.J2     = 1082.6E-6    # gravitational harmonic J2, float
			self.J3     = -2.532E-6    # gravitational harmonic J3, float
			self.h_thres= 120.0E3      # atmospheric model cutoff / threshold altitude in meters, density = 0, if h>h_thres, float
			self.h_skip = 120.0E3      # define skip out altitude in METERS: if vehicle altitude exceeds this value, trajectory is cut off, float
			self.h_trap = 10.0E3       # define trap in altitude  in meters: if vehicle altitude falls below this value, trajectory is cut off, float

		elif planetID == 'MARS':

			self.ID     = 'MARS'       # planet identifier string, string
			self.RP     = 3389.5000E3  # mean radius of the target planet in meters, float
			self.OMEGA  = 7.088253E-5  # mean angular velocity of rotation of the planet about its axis of rotation in rad/s, float
			self.GM     = 4.282837E13  # gravitational parameter of the planet in M3/S2, include as many significant digits available, float 
			self.rho0   = 0.0200       # reference atmospheric density at the surface of the target planet in KG/M3, float
			self.CPCV   = 1.289        # reference specific heat ratio CP/CV at the surface of the planet, float
			self.J2     = 1960.45E-6   # gravitational harmonic J2, float
			self.J3     = 31.5E-6      # gravitational harmonic J3, float
			self.h_thres= 120.0E3      # atmospheric model cutoff / threshold altitude in METERS, density = 0, if h>h_thres, float
			self.h_skip = 120.0E3      # define skip out altitude in METERS: if vehicle altitude exceeds this value, trajectory is cut off, float
			self.h_trap = 10.0E3       # define trap in altitude  in meters: if vehicle altitude falls below this value, trajectory is cut off, float

		elif planetID == 'TITAN':

			self.ID     = 'TITAN'       # planet identifier string, string
			self.RP     = 2575.0000E3   # mean radius of the target planet in meters, float
			self.OMEGA  = 4.5451280E-6  # mean angular velocity of rotation of the planet about its Z-axis in rad/s, float
			self.GM     = 8.9780000E12  # gravitational parameter of the planet in M3/S2, include as many significant digits available, float
			self.rho0   = 5.43500       # reference atmospheric density at the surface of the target planet in kg/m3, float
			self.CPCV   = 1.400         # reference specific heat ratio CP/CV at the surface of the planet, float
			self.J2     = 31.808E-6     # gravitational harmonic J2, float
			self.J3     = -1.880E-6     # gravitational harmonic J3, float
			self.h_thres= 1000.0E3      # atmospheric model cutoff / threshold altitude in METERS, density = 0, if h>h_thres,float
			self.h_skip = 1000.0E3      # define skip out altitude in METERS: if vehicle altitude exceeds this value, trajectory is cut off, float
			self.h_trap = 30.0E3        # define trap in altitude  in METERS: if vehicle altitude falls below this value, trajectory is cut off, float

		elif planetID == 'URANUS':

			self.ID     = 'URANUS'      # PLANET IDENTIFIER STRING
			self.RP     = 25559.0E3     # mean radius of the target planet in METERS
			self.OMEGA  = -1.01237E-4   # mean angular velocity of rotation of the planet about its Z-axis in RAD/S
			self.GM     = 5.793939E15   # gravitational parameter of the planet in M3/S2, include as many significant digits available 
			self.rho0   = 0.3788        # reference atmospheric density at the surface of the target planet in KG/M3
			self.CPCV   = 1.450         # reference specific heat ratio CP/CV at the surface of the planet
			self.J2     = 3343.3E-6     # gravitational harmonic J2, numeric value
			self.J3     = 0.000000      # gravitational harmonic J3, numeric value
			self.h_thres= 1500.0E3      # atmospheric model cutoff / threshold altitude in METERS, density = 0, if h>h_thres
			self.h_skip = 1500.0E3      # define skip out altitude in METERS: if vehicle altitude exceeds this value, trajectory is cut off.
			self.h_trap = 50.0E3        # define trap in altitude  in METERS: if vehicle altitude falls below this value, trajectory is cut off.

		elif planetID == 'NEPTUNE':

			self.ID     = 'NEPTUNE'     # PLANET IDENTIFIER STRING
			self.RP     = 24622.000E3   # mean radius of the target planet in METERS
			self.OMEGA  = 1.083385E-4   # mean angular velocity of rotation of the planet about its Z-axis in RAD/S
			self.GM     = 6.8365299E15  # gravitational parameter of the planet in M3/S2, include as many significant digits available 
			self.rho0   = 0.44021       # reference atmospheric density at the surface of the target planet in KG/M3
			self.CPCV   = 1.450         # reference specific heat ratio CP/CV at the surface of the planet
			self.J2     = 3411.0E-6     # gravitational harmonic J2, numeric value
			self.J3     = 0.000000      # gravitational harmonic J3, numeric value
			self.h_thres= 1000.0E3      # atmospheric model cutoff / threshold altitude in METERS, density = 0, if h>h_thres
			self.h_skip = 1000.0E3      # define skip out altitude in METERS: if vehicle altitude exceeds this value, trajectory is cut off.
			self.h_trap = 10.0E3        # define trap in altitude  in METERS: if vehicle altitude falls below this value, trajectory is cut off.

		else:
			print(" >>> ERR : Invalid planet identifier provided.")

		# create reference values (Reference: 1998 - Modeling, Simulation and Visualization of Aerocapture - Leszczynski - MS Thesis)

		self.Vref      = np.sqrt(self.GM/self.RP)     # reference velocity for non-dimensionalization
		self.tau       = self.RP / self.Vref          # reference timescale tau is used to non-dimensionalize time, angular rates
		self.OMEGAbar  = self.OMEGA*self.tau          # non-dimensional angular rate of planet's rotation

		self.EARTHG    = 9.80665                      # ref. surface gravity on Earth, CONST


	def loadAtmosphereModel(self, datfile, heightCol, tempCol, presCol, densCol, intType, heightInKmFlag=False):
		'''
		Load atmospheric model from a look up table with height, temperature, pressure and density
		
		INPUT(s): 
		datfile   - string, file containing atmospheric lookup table
		heightCol - int, column number of height array, assumes unit = m (first column = 0, second column = 1,etc.)
		tempCol   - int, column number of temperature array, assumes unit = K (first column = 0, second column = 1 etc.)
		presCol   - int, column number of pressure array, assumes unit = Pa (first column = 0, second column = 1, etc.)
		densCol   - int, column number of density array, assumes unit = kgm3 (first column = 0, second column = 1, etc.)
		intType   - string, interpolation type: 'linear', 'quadratic' or 'cubic'
		heightInKmFlag - optional, set to True if heightCol has units of km, False by default
		
		OUTPUT(s): 
		
		'''
		self.ATM          = np.loadtxt(datfile) # load data from textfile using np.loadtxt()

		if heightInKmFlag == True:
			self.ATM_height   = self.ATM[:,heightCol]*1E3    # convert heightCol from km to meters
		else:
			self.ATM_height   = self.ATM[:,heightCol]        # extract first column into 1D array ATM_height, height above surface in METERS

		self.ATM_temp     = self.ATM[:,tempCol]          # extract second column into 1D array ATM_temp,  temperature in KELVIN
		self.ATM_pressure = self.ATM[:,presCol]          # extract third column into 1D array ATM_pressure, pressure in NEWTON/M2
		self.ATM_density  = self.ATM[:,densCol]          # extract fourth column into 1D array ATM_density, density in KG/M3

		# derive speed of sound profile from pressure, density and specific heat ratio
		self.ATM_sonic    = np.sqrt(self.CPCV*self.ATM_pressure/self.ATM_density)
		
		# create interpolating functions using scipy.interpolate.interp1d

		
		# fill_value is the value returned by the interpolating function if input arguments fall outside available data range.
		# fill_value = 0.0 for temp_int, pressure_int, density_int

		# bounds_error=False indicates the function will not return an error if input arguments fall outside available data range.

		# The fill_value and bounds_error arguments are used due to the fact that while propogating trajectories, the vehicle
		# might go above the altitude for which atmospheric data is available, or go below the surface where at atmpospheric data is available.

		self.temp_int      = interp1d(self.ATM_height, self.ATM_temp    , kind=intType, fill_value=0.0, bounds_error=False)
		self.pressure_int  = interp1d(self.ATM_height, self.ATM_pressure, kind=intType, fill_value=0.0, bounds_error=False)
		self.density_int   = interp1d(self.ATM_height, self.ATM_density , kind=intType, fill_value=0.0, bounds_error=False)
		self.sonic_int     = interp1d(self.ATM_height, self.ATM_sonic   , kind=intType, fill_value=1E20, bounds_error=False)


	def density(self, h):
		'''
		Returns atmospheric density, scalar value, at altitude h(METERS)

		INPUT(s): 
		h - float, altitude h(METERS) at which atmospheric density is desired

		OUTPUT(s): 1
		density - scalar : returns the atmospheric density at input altitude h(METERS)
		'''
		if h>=0 and h<=self.h_thres:
		# if altitude is within available data range, return density data from interpolating function density_int()
			return np.float(self.density_int(h))

		elif h>self.h_thres:
			# if altitude is above atmospheric cut off altitude, return density=0
			return 0

		elif h<0:
			# if altitude is below 0, return the reference density at the surface
			# the trajectory will be cut off at the surface / trap in altitude during post-processing 
			# rho0 is provided so that the solver has some numerical density value to work with even if the
			# trajectory goes below the surface during propogation
			return self.rho0


	def tempvectorized(self, h):
		'''
		Returns atmospheric temperature, vector , at altitudes array h[:], (METERS)

		INPUT(s): 
		h, FLOAT, ARRAY: altitude h[:](METERS) at which atmospheric temperature is desired

		OUTPUT(s): 1
		density, FLOAT, ARRAY: returns the atmospheric temperature at altitudes h[:], KELVIN
		'''
		
		ans    = np.zeros(len(h))
		ans[:] = self.temp_int(h[:])
		
		return ans

	def presvectorized(self, h):
		'''
		Returns atmospheric pressure, vector , at altitudes array h[:], (METERS)

		INPUT(s): 
		h, FLOAT, ARRAY: altitude h[:](METERS) at which atmospheric pressure is desired

		OUTPUT(s): 1
		density, FLOAT, ARRAY: returns the atmospheric pressure at altitudes h[:], Pa
		'''
		
		ans    = np.zeros(len(h))
		ans[:] = self.pressure_int(h[:])
		
		return ans

	def densityvectorized(self, h):
		'''
		Returns atmospheric density, vector , at altitudes array h[:], (METERS)

		INPUT(s): 
		h, FLOAT, ARRAY: altitude h[:](METERS) at which atmospheric density is desired

		OUTPUT(s): 1
		density, FLOAT, ARRAY: returns the atmospheric density at altitudes h[:], kgm3
		'''
		
		ans    = np.zeros(len(h))
		ans[:] = self.density_int(h[:])
		
		return ans

	def avectorized(self, h):
		'''
		Returns atmospheric sonic speed, vector , at altitudes array h[:], (METERS)

		INPUT(s): 
		h, FLOAT, ARRAY: altitude h[:](METERS) at which atmospheric density is desired

		OUTPUT(s): 1
		density, FLOAT, ARRAY: returns the atmospheric sonic speed at altitudes h[:], kgm3
		'''
		
		ans    = np.zeros(len(h))
		ans[:] = self.sonic_int(h[:])
		
		return ans

	def rho(self, r, theta, phi):
		'''
		Returns atmospheric density rho, scalar, as a function of radial distance from the target planet center r
		as well as longitude theta and latitude phi
		
		INPUT(s): 3
		h, FLOAT, SCALAR: altitude h(METERS)
		theta, FLOAT, SCALAR: longitude theta(RADIANS), theta e [-PI,PI]
		phi, FLOAT, SCALAR: latitude phi(RAD), phi e [-90,90]
		
		OUTPUT(s): 1
		density, FLOAT, SCALAR: returns the atmospheric density at (r,theta,phi)
		'''
		h = r - self.RP # compute altitude from radial distance
		ans = self.density(h) # compute density
		
		return ans

	def rhovectorized(self, r):
		'''
		Returns atmospheric density, vector, at radial distance array r[:], (METERS)
		
		INPUT(s): 1
		r, FLOAT, ARRAY: radial distace r[:](METERS) at which atmospheric density is desired
		
		OUTPUT(s): 1
		density, FLOAT, ARRAY: returns the atmospheric density at r[:], KG/M3
		'''
		h      = np.zeros(len(r))
		ans    = np.zeros(len(r))
		RP_vec = np.ones(len(r))*self.RP
		h[:]   = r[:] - RP_vec[:]
		ans[:] = self.density_int(h[:])

		return ans


	def pressurevectorized(self, r):
		'''
		Returns atmospheric pressure, vector, at radial distance array r[:], (METERS)
		
		INPUT(s): 1
		r, FLOAT, ARRAY: radial distace r[:](METERS) at which atmospheric pressure is desired
		
		OUTPUT(s): 1
		density, FLOAT, ARRAY: returns the atmospheric pressure at r[:], N/M2
		'''
		h      = np.zeros(len(r))
		ans    = np.zeros(len(r))
		RP_vec = np.ones(len(r))*self.RP
		h[:]   = r[:] - RP_vec[:]
		ans[:] = self.pressure_int(h[:])
		return ans



	def temperaturevectorized(self, r):
		'''
		Returns atmospheric temperature, vector, at radial distance array r[:], (METERS)
		
		INPUT(s): 1
		r, FLOAT, ARRAY: radial distace r[:](METERS) at which atmospheric temperature is desired
		
		OUTPUT(s): 1
		density, FLOAT, ARRAY: returns the atmospheric temperature at r[:], N/M2
		'''
		h      = np.zeros(len(r))
		ans    = np.zeros(len(r))
		RP_vec = np.ones(len(r))*self.RP
		h[:]   = r[:] - RP_vec[:]
		ans[:] = self.temp_int(h[:])
		return ans


	def sonicvectorized(self, r):
		'''
		Returns atmospheric sonic speed, vector, at radial distance array r[:], (METERS)
		
		INPUT(s): 1
		r, FLOAT, ARRAY: radial distace r[:](METERS) at which atmospheric sonic is desired
		
		OUTPUT(s): 1
		density, FLOAT, ARRAY: returns the atmospheric sonic speed at r[:], m/s
		'''
		h      = np.zeros(len(r))
		ans    = np.zeros(len(r))
		RP_vec = np.ones(len(r))*self.RP
		h[:]   = r[:] - RP_vec[:]
		ans[:] = self.sonic_int(h[:])
		return ans

	def rbar(self, r):
		'''
		Returns non-dimensional rbar=r/RP
		
		INPUT(s): 1
		r, FLOAT, SCALAR/VECTOR: radial distace r[:](METERS)
		
		OUTPUT(s): 1
		rbar, FLOAT, SCALAR/VECTOR: returns the non-dimensional rbar
		'''
		ans = r/self.RP
		return ans

	def rho2(self, rbar, theta, phi):
		'''
		Returns density as a function of non-dimensional radial distance rbar, longitude theta, latitude phi
		
		INPUT(s): 3
		rbar, FLOAT, SCALAR: non-dimensional distance rbar
		theta, FLOAT, SCALAR: longitude theta(RADIANS), theta e [-PI,PI]
		phi, FLOAT, SCALAR: latitude phi(RAD), phi e [-PI/2,PI/2]
		
		OUTPUT(s): 1
		density, FLOAT, SCALAR: rho(rbar,theta,phi)
		'''
		r = rbar*self.RP
		ans = self.rho(r,theta,phi)
		return ans


	def rhobar(self, rbar, theta, phi):
		'''
		Returns non-dimensional density rhobar = rho / rho0
		
		INPUT(s): 3
		rbar, FLOAT, SCALAR: non-dimensional distance rbar
		theta, FLOAT, SCALAR: longitude theta(RADIANS), theta e [-PI,PI]
		phi, FLOAT, SCALAR: latitude phi(RAD), phi e [-90,90]
		
		OUTPUT(s): 1
		# rbar, FLOAT, SCALAR/VECTOR: returns the non-dimensional rhobar
		'''
		ans = self.rho2(rbar,theta,phi)/self.rho0
		return ans

	def checkAtmProfiles(self, h0, dh):
		'''
		Function to check the loaded atmospheric profile data

		INPUT(s):
		h0 - float, starting altitude, meters 
		dh - float, altitude increment, meters
		
		OUTPUT(s):
		4 arrays, 1 image output on console

		h_array contains altitude from Z=0 to Z=h_thres (atm-cutoff altitude), steps every 1000 m
		
		'''
		h_array = np.linspace(h0,self.h_thres,int(self.h_thres/dh))

		# compute profiles of T, P, rho, a using interpolated functions
		# vectorized functions are more efficient for this kind of computation.
		
		T_array = self.tempvectorized(h_array)
		P_array = self.presvectorized(h_array)
		r_array = self.densityvectorized(h_array)
		a_array = self.avectorized(h_array)

		
		fig = plt.figure()
		fig.set_size_inches([6.5, 3.25])
	

		plt.subplot(2,2,1)
		plt.plot(T_array,h_array*1E-3,'r-',linewidth=2.0)
		plt.xlabel("Temperature, K",fontsize=12)
		plt.ylabel("Altitude, km",fontsize=12)
		plt.xticks(fontsize=12)
		plt.yticks(fontsize=12)
		plt.grid('on',linestyle='-', linewidth=0.2)
		
		plt.subplot(2,2,2)
		plt.plot(P_array*1E-3,h_array*1E-3,'r-',linewidth=2.0)
		plt.xlabel("Pressure, kPa",fontsize=12)
		plt.ylabel("Altitude, km",fontsize=12)
		plt.xscale('log')
		plt.xticks(fontsize=12)
		plt.yticks(fontsize=12)
		plt.grid('on',linestyle='-', linewidth=0.2)

		plt.subplot(2,2,3)
		plt.plot(r_array,h_array*1E-3,'r-',linewidth=2.0)
		plt.xlabel("Density, kg/m3",fontsize=12)
		plt.ylabel("Altitude, km",fontsize=12)
		plt.xscale('log')
		plt.xticks(fontsize=12)
		plt.yticks(fontsize=12)
		plt.grid('on',linestyle='-', linewidth=0.2)

		plt.subplot(2,2,4)
		plt.plot(a_array,h_array*1E-3,'r-',linewidth=2.0)
		plt.xlabel("Speed of Sound, m/s",fontsize=12)
		plt.ylabel("Altitude, km",fontsize=12)
		plt.xticks(fontsize=12)
		plt.yticks(fontsize=12)
		plt.grid('on',linestyle='-', linewidth=0.2)

		ax = plt.gca()
		ax.tick_params(direction='in')
		ax.yaxis.set_ticks_position('both')
		ax.xaxis.set_ticks_position('both')

		plt.tight_layout()

		plt.show()

		return T_array, P_array, r_array, 

	def computeR(self, h):
		'''
		Returns radial distance r, as a function of altitude h, METERS
		
		INPUT(s): 1
		h, FLOAT, SCALAR: altitude h, METERS
		
		OUTPUT(s): 1
		r, FLOAT, SCALAR: returns the radial distance r=RP+h
		'''
		r = self.RP + h
		return r

	def computeH(self,r):
		'''
		Returns altitude h, as a function of radial distance h, METERS
		
		INPUT(s): 1
		r, FLOAT, SCALAR: radial distance r, METERS
		
		OUTPUT(s): 1
		h, FLOAT, SCALAR: returns the altitude h=r-RP
		'''
		h = r - self.RP
		return h

	def nonDimState(self,r,theta,phi,v,psi,gamma,drange):
		'''
		Computes non-dimensional state variables from dimensional variables

		INPUT(s): 7
		r, FLOAT, SCALAR/ARRAY: radial distance r, METERS
		theta, FLOAT, SCALAR/ARRAY: longitude theta, RADIANS, theta e [-PI,PI]
		phi, FLOAT, SCALAR/ARRAY: latitude phi, RADIANS, phi e [-PI/2,PI/2]
		v, FLOAT, SCALAR/ARRAY: velocity v, M/S
		psi, FLOAT, SCALAR/ARRAY: heading angle psi, RADIANS, psi e [ -PI, PI]
		gamma, FLOAT, SCALAR/ARRAY: flight path angle, RADIANS
		drange, FLOAT, SCALAR/ARRAY: downrange, METERS
		
		OUTPUT(s): 7
		rbar, FLOAT, SCALAR/ARRAY: nondimensional radial distance rbar
		theta, FLOAT, SCALAR/ARRAY: longitude theta, RADIANS, theta e [-PI,PI]
		phi, FLOAT, SCALAR/ARRAY: latitude phi, RADIANS, phi e [-PI/2,PI/2]
		vbar, FLOAT, SCALAR/ARRAY: non dimensional velocity vbar
		psi, FLOAT, SCALAR/ARRAY: heading angle psi, RADIANS, psi e [ -PI, PI]
		gamma, FLOAT, SCALAR: flight path angle, RADIANS
		drangebar, FLOAT/SCALAR: non-dimensional downrange drangebar
		'''
		rbar       = r / self.RP           # Non-dimensional entry radius
		vbar       = v / self.Vref         # Non-dimensional entry velocity, relative to planet
		drangebar  = drange / self.RP      # Non-dimensional entry downrange

		return rbar,theta,phi,vbar,psi,gamma,drangebar

	def dimensionalize(self,tbar,rbar,theta,phi,vbar,psi,gamma,drangebar):
		'''
		Computes dimensional state variables from non-dimensional variables

		INPUT(s): 7
		tbar, FLOAT, SCALAR/ARRAY: non-dimensional time tbar
		rbar, FLOAT, SCALAR/ARRAY: nondimensional radial distance rbar
		theta, FLOAT, SCALAR/ARRAY: longitude theta, RADIANS, theta e [-PI,PI]
		phi, FLOAT, SCALAR/ARRAY: latitude phi, RADIANS, phi e [-PI/2,PI/2]
		vbar, FLOAT, SCALAR/ARRAY: non dimensional velocity vbar
		psi, FLOAT, SCALAR/ARRAY: heading angle psi, RADIANS, psi e [ -PI, PI]
		gamma, FLOAT, SCALAR: flight path angle, RADIANS
		drangebar, FLOAT/SCALAR: non-dimensional downrange drangebar

		OUTPUT(s): 7
		r, FLOAT, SCALAR/ARRAY: radial distance r, METERS
		theta, FLOAT, SCALAR/ARRAY: longitude theta, RADIANS, theta e [-PI,PI]
		phi, FLOAT, SCALAR/ARRAY: latitude phi, RADIANS, phi e [-PI/2,PI/2]
		v, FLOAT, SCALAR/ARRAY: velocity v, M/S
		psi, FLOAT, SCALAR/ARRAY: heading angle psi, RADIANS, psi e [ -PI, PI]
		gamma, FLOAT, SCALAR/ARRAY: flight path angle, RADIANS
		drange, FLOAT, SCALAR/ARRAY: downrange, METERS
		'''
		
		t      = self.tau*tbar
		r      = rbar*self.RP
		v      = vbar*self.Vref 
		drange = drangebar*self.RP

		return t,r,theta,phi,v,psi,gamma,drange
		