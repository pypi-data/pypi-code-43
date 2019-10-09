import visa

rm = visa.ResourceManager()

class Apex():
	def __init__(ip='192.168.1.8', model='2641B'):
		self.name = 'Apex-'+ model
		self.address = ip
		self.instr = None

	def open(self):
		self.instr = rm.open_resource(self.address)
		# configure instument and communication
		self.instr._visa.read_termination = '\n'
		self.instr._visa.timeout = 60000
		self.instr.write('SPAVERAGE0\n')	# disable average mode
		self.instr.write('SPXUNT1\n')		# set x-unit to wavelength
		self.instr.write('SPLINSC1')		# set y-scale unit to dBm
		self.instr.write('SPSWPMSK-100\n')	# set noise mask to -100 dBm
		self.instr.write('SPAUTONBPT1')		# auto-choose number of points
		self.instr.write('SPSWPRES1.44')	# set resolution 1.44pm/180MHz
        self.instr.write('SPINPUT0') 		# physical SM optical input
        self.instr.write('SPPOLAR0') 		# sum both polarizations


	def setup(self, wl_from=None, wl_to=None, # valid if wl_cent is none
					wl_cent=None, span=None,  
					res=None,  # 1.44pm/180MHz
					):
		if wl_from is not None and wl_to is not None:
        	self.instr.write('SPSTRTWL%.3g\n'%wl_from)
        	self.instr.write('SPSTOPTWL%.3g\n'%wl_to)
		if wl_cent is not None and span is not None:
			self.instr.write('SPSPANWL%.3g\n'%span)
        	self.instr.write('SPCTRWL%.3g\n'%wl_cent)
        if res is not None:
			self.instr.write('SPSWPRES%.3g'%res)
        	"""5MHz/0.16pm, 180MHz/1.44pm, 2GHz/16pm, 10GHz/80pm,
			20GHz/160pm, 50GHz/0.4nm, 100MHz/0.8pm, 200GHz/1.6nm,
			400GHz/3.2nm"""

	def sweep(self, sweep_type='single'):
		try:
			sweep_type = ['auto',
						  'single',
						  'repeat',
						  'stop'].index(action)  # assign a number
		except:
			print('Warning: "%s" is not a valid sweep type')
			print("Choose from 'auto', 'single', 'repeat', 'stop'.")
			return
		return self.instr.ask('SPSWP%d\n'%sweep_type)

	def get_sweep(self, trace=1 ,sweep_first=False, save_to=None):
		if sweep_first:
			self.sweep()
		p_dBm = self.instr.ask('SPDATAL%d'%trace)  
		if save_to is not None:
			pass  # TODO save to file
		return p_dBm


	def close(self):
		self.instr.close()
