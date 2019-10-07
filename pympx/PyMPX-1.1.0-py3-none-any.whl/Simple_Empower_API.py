# -------------------------------------------------------------------------------
# Simple Empower API
# v1.0
# - Created by OK 28.11.17
# - Simple object based module to handle routine tasks that might be carried out as part of a normal data load process
#
# Example Usage:
#e = Empower(site_file = r"C:\Empower Sites\Test Site\Test Site.eks",
#			data_sub_folder = "Data Load",
#			username = "Supervisor",
#			password = "----",
#			version = "9.1",
#			script_sub_sub_folder = "02. Batch Processes\_Scripts")
#
#e.run_batch(['Housekeep'])
#e.get_mapping_from_field(0, 'ProjectStr', 'ProjectCode', 'EAS_Projects')
#e.zip_site(['Data Files', 'Dashboards'])
#
# -------------------------------------------------------------------------------

# Imports
import os
import pandas as pd
from empower_utils import utils as mpxu, logconfig
import zipfile
import datetime as dt
import getpass
import msvcrt
import sys
import subprocess


class Empower:
	'''
	Class for managing routine data update tasks
	
	Parameters:
	* site_file: full path of the site file, e.g. eks file, including file extension
	* data_sub_folder: data folder within site folder for working data e.g. source data files, mapping files, scripts
	* username: supervisor username
	* version: Empower version used for the site, e.g. '9.3' 
	* password_mode: How to process password; 'simple', 'getpass', 'encrypted'
	* password: Optional, supervisor password if simple password mode in use
	* metapraxis_folder: Optional, file path of the Metapraxis Program Files folder (containing '\Empower 9.1\' etc.)
	* site_folder: Optional, allows location to be specified for local files if this can't be derived from site path (e.g. for SQL sites)
	* script_sub_sub_folder: Optional, folder within data_sub_folder where scripts are stored
	* existing_log: Optional, existing empower utils log if on already exists as part of a larger process
	* log_level: Optional, default 'INFO'. Specifies the level of logs to include from 'INFO', 'DEBUG', 'VERBOSE'

	Methods:
	* log_message: adds a message to the log
	* run_importer_script: runs a script from a scripts folder using Importer
	* run_batch: runs a specified list of batch commands
	* zip_site: creates an archive of the eks and metadata files, plus additional specified folders (sub folders not included unless specifically specified)
	* export_elements: provides a list of element details from a chosen dimension
	* export_structure: provides a structure from a chosen dimension and structure
	* get_mapping_from_field: generates EAS and IAS files automatically, based on shortname and a chosen field for a chosen structure
	'''
	
	def welcome(self, prompt_file):
		'''
		Function to display a welcome prompt when the Empower class is initialised, and to ensure the user wishes to proceed before running a function.
		
		Parameters:
		* empower_class: Empower class calling this function
		* prompt_file: Text file containing a prompt that should be displayed to screen
		'''
		
		# Log that the prompt file is being used
		self.log.verbose('Welcome prompt displayed from file: {}'.format(prompt_file))
		
		# Display the prompt to screen
		self.log.debug('Opening welcome prompt: {}'.format(prompt_file))
		with open(os.path.join(self.cwd, prompt_file), 'r') as f:
			for line in f:
				print(str(line).strip())
				
		# Get the user to validate that they are happy to proceed
		self.log.debug('Checking the current user in the os environment variables')
		current_user = os.environ['USERNAME']
		try:
			response = input('Enter "Y" to confirm you would like to proceed, or "N" to abort: ')
		except KeyboardInterrupt:
			raise KeyboardInterrupt('This process has been halted')		
		if response.lower()[0] == 'y':
			self.log.info('Confirmation provided; current user is "{}"'.format(current_user))
		else:
			self.log.info('Confirmation not provided; processed will be halted')
			raise KeyboardInterrupt('This process has been halted')
	
		
	def __init__(self, site_file, data_sub_folder, username, version, password_mode,
				password = None,
				metapraxis_folder = r'C:\Program Files\Metapraxis',
				site_folder = None,
				script_sub_sub_folder = '',
				existing_log = None,
				log_level = 'INFO',
				welcome_prompt = None):
		'''
		Initiates the Empower object by doing the following:
		(1) Imports required modules
		(2) Checks validity of parameters
		(3) Begins a log file
		'''
		
		# Get required parameters
		self.site_folder = site_folder or os.path.dirname(site_file)
		self.site_file = site_file
		self.cwd = os.path.join(self.site_folder, data_sub_folder)
		self.script_folder = os.path.join(self.cwd, script_sub_sub_folder)
		self.version = str(version)
		self.empower_folder = os.path.join(metapraxis_folder, 'Empower {}'.format(self.version))
		self.username = username
		self.password_mode = str(password_mode).lower()
		self.log_level = str(log_level).upper()
		
		# Get parameters that may be collected later; encode the password if one has already been provided
		self.elements = dict()
		self.structures = dict()
		self._password = password if password else None
		
		# Establish other parameters
		#batch_exe = 'Empower Batch Console.exe' if self.version > '9.1' else 'Empower Batch.exe' -- need to await batch console being implemented in Empower Utils
		batch_exe = 'Empower Batch.exe'
		importer_exe = 'Empower Importer Console.exe'
		self.batch = os.path.join(self.empower_folder, batch_exe)
		self.importer = os.path.join(self.empower_folder, importer_exe) 

		# ----------------------------------------------------------------------------
		# Validate provided parameters
		parameter_check_list = [self.site_folder, 
								self.cwd, 
								self.empower_folder,
								self.script_folder,
								self.batch,
								self.importer]
		
		assert all(os.path.exists(path) for path in parameter_check_list), 'Provided file(s) / folder(s) do not exist: \n{}'.format(
																																	',\n'.join([path for path in parameter_check_list 
																																	if not os.path.exists(path)])
																																	)
		
		assert self.password_mode in ['simple', 'getpass', 'encrypted'], 'Invalid password_mode provided. Use "simple", "getpass", "encrypted"'
		
		assert (self.password_mode == 'simple') or (self._password == None), 'Password should (only) be supplied for "simple" password mode'
		
		assert self.log_level in ['INFO', 'VERBOSE', 'DEBUG'], 'Invalid log_level provided. Use "INFO", "VERBOSE", "DEBUG"'
		
		# ----------------------------------------------------------------------------
		# Get a log folder and a logger (if one doesn't already exist)
		# Logging config override
		log_config_override={'version': 1,'disable_existing_loggers': False,
							'formatters': {
								'detailed': {'class': 'logging.Formatter','format': '%(asctime)s %(levelname)-8s : %(process)-5s : %(module)-17s@%(lineno)-5s: %(message)s','datefmt':'%Y-%m-%d %H:%M:%S'},
								'simple': {'class': 'logging.Formatter','format': '%(asctime)s %(levelname)-8s : %(message)s','datefmt':'%Y-%m-%d %H:%M:%S'}
											},
							'handlers': {'console': {'class': 'logging.StreamHandler','formatter': 'simple','level': self.log_level,}},
							'root': {'handlers': ['console'],'level': self.log_level,},
							}
		# Create a new log; or use a provided log
		if existing_log == None:
			self.log_folder = os.path.join(self.cwd,'Log Files')
			if not os.path.exists(self.log_folder):
					os.mkdir(self.log_folder)
			self.log = logconfig.get_logger(config = log_config_override)
			self.logging_queue, self.listener = logconfig.add_file_handler(self.log,log_directory=self.log_folder)
		else:
			self.log = existing_log
			
		# ----------------------------------------------------------------------------
		# Complete initiation
		self.log.info('Initiated process successfully for: {}'.format(os.path.basename(self.site_folder)))
		self.log.info('Working from directory: {}'.format(self.cwd))
		self.log.info('Logs are being written to {}'.format(self.log_folder))
		if script_sub_sub_folder != '':
			self.log.info('Default folder for scripts to run is: {}'.format(self.script_folder))
			
		# Use the welcome prompt if provided
		if welcome_prompt:
			self.welcome(welcome_prompt)
	
	@property
	def password(self):
		'''	Lazy load - collects the password on demand, using the specified mode.'''
		# If the password isn't defined yet, collect it and store it
		if self._password == None:
			# Get the password
			self.log.debug('Collecting password for first time usage; password mode is: {}'.format(self.password_mode))
			# - Simple mode
			if self.password_mode == 'simple':
				raise ValueError('Simple password mode was specified; but no password provided')
			# - Getpass mode
			elif self.password_mode == 'getpass':
				# TODO - enable getpass.getpass() for Jupyter Notebooks
				#self._password = getpass.getpass('Please enter the Supervisor password: ')
				self._password = get_password()
			# - Encrypted password mode
			else:
				# Get an encrypted password
				self._password = get_secure_password(self)
			
		# Once finished, or if the password had already been defined; return it
		return self._password

	def log_message(self, message, debug_only = False):
		'''
		Adds a message to the log.
		
		Parameters:
		* debug_only: Optional, default False; if True the message will only be logged when the API is run in DEBUG mode
		'''
		# Validate provided parameters
		assert type(message) == str, 'log_message: log_message requires a string be provided; nessage provided was of type: {}'.format(type(message))
		
		# TODO - enable VERBOSE mode
		
		# Log in info or debug mode depending on debug_only
		self.log.debug(str(message)) if debug_only else self.log.info(str(message))
	
	def run_importer(self, script_file, params = []):
		'''
		Runs a specified importer script, from the data load / script folder, with provided commands
		
		Parameters:
		* Script file: script file within the data folder, or the script sub folder if specified
		* Params: list of parameters to provide to the script
		'''
		# Get the full file path of the script to run
		script = os.path.join(self.script_folder, script_file)
		
		# Validate provided parameters
		assert os.path.exists(script), 'run_importer: provided script does not exist: {}'.format(script)
		
		# Log and run
		self.log.verbose('Running Importer Script {} using {}'.format(script, self.importer))
		mpxu.run_empower_importer_script(script = script,
										parameters = params,
										empower_importer_executable = self.importer)
		
	def run_batch(self, commands, comment = ''):
		'''
		Creates and runs specified batch commands, with the created script placed in the data load folder.
		
		Parameters:
		* commands: empower batch script file, or list of batch commands to execute; login details and 'silent exit' are not required
		* comment: Optional, comments to include in the temp batch script file that will be written
		'''
		
		# Assert that this is not encrypted password mode, as this would require run_batch_secure
		assert (self.password_mode != 'encrypted'), 'run_batch: encrypted password mode does not support run_batch function; use run_batch_secure instead'
		
		# Validate provided parameters
		# Commands can be provided as a list of commands
		if type(commands) == list:
			assert all(type(i) == str for i in commands), 'run_batch: each command in the commands list must be a string'
			batch_commands = commands
			
			# Log and run the script
			self.log.debug('run_batch: commands have been provided by a list')
			self.log.verbose('Running Empower Batch script with {} commands using {}'.format(len(batch_commands), self.batch))
		
		# Otherwise, commands should be provided as a script file in the scripts folder, or elsewhere
		else:
			assert os.path.exists(commands) or os.path.exists(os.path.join(self.script_folder, commands)), 'run_batch: run_batch requires a script file or list of commands; but {} was provided'.format(str(commands))
			
			# Log and run the script
			self.log.debug('run_batch: commands have been provided via a file')
			self.log.verbose('Running Empower Batch script {} commands using {}'.format(commands, self.batch))
			
			# If the script file exists, go and get the commands
			if os.path.exists(commands):
				commands_file = commands
				
			else:
				commands_file = os.path.join(self.script_folder, commands)
			with open(commands_file, 'r') as f:
				self.log.debug('run_batch: generating list of commands from provided file {}'.format(commands_file))
				batch_commands = [line.strip() for line in f if not line.lower().startswith(('sitefile', 'user', 'password', 'silent'))]
		
		# Get the temp script to write to
		script = os.path.join(self.script_folder, 'temp_batch_script.ebat')
		
		try:
			mpxu.create_and_run_ebat_file(self.batch, script, comment = comment, 
										  sitefile = self.site_file, 
										  user = self.username, 
										  password = self.password, 
										  commands = batch_commands, 
										  #empower_batch_success_code= 0 if self.version == '9.1' else 1,
										  empower_batch_success_code = 1)
		finally:
			# Once complete, erase the temp script to avoid saving the password down into a file
			self.log.debug('run_batch: erasing temporary script')
			with open(script, 'w') as s:
				s.write('temp script')

	def run_batch_secure(self, commands, exclude_login_details = False):
		'''
		Runs specified Empower Importer / Batch commands by passing to Importer using STD-In, to avoid temporarily writing to a script file
		Supports Importer machine locked passwords through password_mode = 'encrypted'
		
		Parameters:
		* commands: empower batch script file, or list of batch commands to execute; login details and 'silent exit' are not required
		* exclude_login_details: Optional, default False; specifies if initial Empower Batch login details should be added before a script. Not required if script includes in-line login (e.g. empower-export-elements command)
		'''
		# Validate provided parameters
		# Commands can be provided as a list of commands
		if type(commands) == list:
			assert all(type(i) == str for i in commands), 'run_batch_secure: each command in the commands list must be a string'
			commands_list = commands
			
			# Log and run the script
			self.log_message('Running Empower Batch script with {} commands using {}'.format(len(commands_list), self.importer))
		
		# Otherwise, commands should be provided as a script file in the scripts folder, or elsewhere
		else:
			assert os.path.exists(commands) or os.path.exists(os.path.join(self.script_folder, commands)), 'run_batch_secure: run_batch requires a script file or list of commands; but {} was provided'.format(str(commands))
			
			# Log and run the script
			self.log_message('Running Empower Batch script {} commands using {}'.format(commands, self.importer))
			
			# If the script file exists, go and get the commands
			if os.path.exists(commands):
				commands_file = commands
				
			else:
				commands_file = os.path.join(self.script_folder, commands)
			with open(commands_file, 'r') as f:
				commands_list = [line.strip() for line in f if not line.lower().startswith(('site-file', 'user', 'password', 'silent'))]
		
		# Create the call line - the "-" instructs Importer to accept standard in
		call_line=[self.importer, '-']

		# Call importer with STDIO open to pass commands
		proc=subprocess.Popen(args=call_line, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		
		# Assemble a command string to pass through STDIO to Empower Importer
		# - Include login details
		if not exclude_login_details:
			proc.stdin.write('site-file {}\n'.format(self.site_file).encode('utf-8'))
			proc.stdin.write('user {}\n'.format(self.username).encode('utf-8'))
			if self.password_mode == 'encrypted':
				proc.stdin.write('set-encrypted-parameter pwd={}\n'.format(self.password).encode('utf-8'))
				proc.stdin.write('password ${pwd}\n'.encode('utf-8'))
			else:
				proc.stdin.write('password {}\n'.format(self.password).encode('utf-8'))
		
		# - Pass the commands
		for command in commands_list:
			#self.log_message('Passing command to importer: {}'.format(command), debug_only = True)
			proc.stdin.write('{}\n'.format(command).encode('utf-8'))
		
		# - Append commands needed for STDIO to function with Importer
		proc.stdin.write('wait\nquit\n'.encode('utf-8'))
		
		proc.stdin.flush()
		proc.stdin.close()
		output = proc.stdout.read()
		errors = proc.stderr.read()
		try:
			std_err =str(errors.decode('utf-8'))
		except UnicodeDecodeError:
			std_err =str(errors.decode('cp1252'))
		
		
		#Close the process and capture errors / logs
		proc.communicate() 
		self.log.debug("STDERR:")
		self.log.debug(std_err)
		self.log.debug('Return Code: {}'.format(str(proc.returncode)))
		if proc.returncode!=18:
			self.log.error('Empower Importer failed and returned Code: '+str(proc.returncode)+'\n'+std_err)
			
	def zip_site(self, include_site_files = True, additional_folders = [], target_folder = None ):
		'''
		Zips up contents of site folder, places in a named, dated zip file in the data load folder.
		EKS / Site file and 'Metadata Files' are included unless specified otherwise
		Specify other folders to include, and each file from that folder will be added.
		Sub folders need to be specified separately; e.g. to include an 'Archive' folder within the 'Dashboards Folder', specify ['Dashboards', 'Dashboards\Archive']
		
		Parameters:
		* include_site_files: Optional, default True; states whether the metadata files folder and eks file of the site should be included in the zip
		* additional_folders: Optional, default []; list of folders and subfolders within the site folder to include in the zip file
		* target_folder: Optional, default None; sub-folder within the data sub folder to place the zip file
		'''
		
		# Name the output with autozip, site name, date
		date_str = dt.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
		site_name = os.path.basename(self.site_folder)
		zip_name = 'autozip_' + site_name + '_' + date_str + '.zip'
		
		# Get full list of folders to zip; force it to include Metadata Files unless specified otherwise
		default_folders = ['Metadata Files'] if include_site_files else []
		folders = set(default_folders + additional_folders)
		
		# Validate provided parameter
		assert all(os.path.exists(os.path.join(self.site_folder, i)) for i in folders), 'zip_site: provided folder(s) do not exist: \n{}'.format(',\n'.join([path for path in folders 
																																				if not os.path.exists(os.path.join(self.site_folder, path))])
																																				) 
		
		self.log_message('Creating zip archive of: {} ...'.format(', '.join(folders)))
		
		# Get a zip file that we can start adding things to
		with zipfile.ZipFile(os.path.join(self.cwd, target_folder or '', zip_name), 'w') as output_zip:
			
			# Add the eks / site file
			if include_site_files:
				output_zip.write(self.site_file)
			
			# Work through each required folder
			for folder in folders:
				
				# Get the full path of the folder, and the items inside it
				root = os.path.join(self.site_folder, folder)
				items = os.listdir(root)
				# Get all of the files inside the folder (items that aren't folders)
				files = [os.path.join(root, i) for i in items if not os.path.isdir(os.path.join(root, i))]
				
				self.log_message('Adding "{}" to archive...'.format(folder), debug_only = True) 
				
				# Add each file to the zip
				for file in files:
					
					output_zip.write(file)
				
				self.log_message('"{}" added successfully.'.format(folder), debug_only = True) 
				
		self.log_message('Zip archive "{}" created.'.format(zip_name))
				
	def export_elements(self, dimension):
		'''
		Creates and runs an generic script to get elements from a chosen dimension, with fields specified
		This will be stored in a dimension-labelled dictionary (Empower.elements)
		
		Parameters:
		* dimension: index of the dimension of elements to export, counts from 0
		'''
		
		# Validate provided parameters
		assert (type(dimension) == int) & (dimension >= 0), 'export_elements: dimension should be an integer greater than or equal to zero; {} was provided'.format(dimension)
		
		# Get paths of a temp script and the output
		#script = os.path.join(self.script_folder, 'temp_importer_script.eimp')
		output = os.path.join(self.script_folder, 'temp_script_output.csv')
		
		# Write the export commands using the already provided empower info
		# Use secure password method for encrypted mode
		if self.password_mode == 'encrypted':
			export_command = ['set-encrypted-parameter pwd={}'.format(self.password)
							 ,'empower-export-elements "{}" "{}"'.format(self.site_file, self.username) + ' ${pwd} ' + '{}'.format(dimension)
							 ,'csv-encode'
							 ,'save-file "{}"'.format(output)]
			
		else:	
			export_command = ['empower-export-elements "{}" "{}" "{}" {}'.format(self.site_file, 
																				 self.username, 
																				 self.password, 
																				 dimension)
							 ,'csv-encode'
							 ,'save-file "{}"'.format(output)]
		
		# Log and run
		self.log_message('Exporting elements for dimension {}'.format(dimension))
		self.run_batch_secure(export_command, exclude_login_details = True)
		
		# Read the output to a data frame, and add to the collected data for empower elements
		# - use dimension index as key
		self.elements.update({dimension: pd.read_csv(output, encoding = 'ANSI')})
		
		
	def export_structure(self, dimension, structure):
		'''
		Creates and runs a generic script to get a structure from a chosen dimension.
		This will be stored in a dimension and structure labelled dictionary (Empower.structures)
		
		Parameters:
		* dimension: index of the dimension of elements to export, counts from 0
		* structure: shortname of the structure to export
		'''
		
		# Validate provided parameters
		assert (type(dimension) == int) & (dimension >= 0), 'export_structure: dimension should be an integer greater than or equal to zero; {} was provided'.format(dimension)
		assert type(structure) == str, 'export_structure: structure should be provided as a string, but type {} was provided'.format(type(structure))
		
		# Get paths of a temp script and the output  
		output = os.path.join(self.script_folder, 'temp_script_output.csv')
		
		# Write the export commands using the already provided empower info
		# Use secure password method for encrypted mode
		if self.password_mode == 'encrypted':
			export_command = ['set-encrypted-parameter pwd={}'.format(self.password)
							 ,'empower-export-structure "{}" "{}"'.format(self.site_file, self.username) + ' ${pwd} ' + '{} {}'.format(dimension, structure)
							 ,'csv-encode'
							 ,'save-file "{}"'.format(output)]
			
		else:
			export_command = ['empower-export-structure "{}" "{}" "{}" {} {}'.format(self.site_file, 
																					 self.username, 
																					 self.password, 
																					 dimension, 
																					 structure)
							 ,'csv-encode'
							 ,'save-file "{}"'.format(output)]
			
		# Log and run
		self.log_message('Exporting structure {} from dimension {}'.format(structure, dimension))
		self.run_batch_secure(export_command, exclude_login_details = True)
		
		# Read the output to a data frame, and add to the collected data for empower structures
		# - use dimension index and structure shortname as keys
		self.structures.update({dimension: {structure: pd.read_csv(output, encoding = 'ANSI')}})

	def get_mapping_from_field(self, dimension, structure, field, mapping_name, 
							   subfolder = '',
							   include_count = False,
							   include_parent = False,
							   include_physid = False):
		'''
		Generates EAS and IAS files by exporting structures from Empower, using Shortname for IAS, and using a specified field as EAS.
		
		To generate valid mappings:
		- shortnames will be de-duplicated
		- elements with the field not populated will be excluded
		- elements that are parents of other elements will be excluded (only 'leaf' level elements will be included)
		
		Parameters:
		* dimension: index of dimension who's elements to export
		* structure: shortname of structure containing subset of the elements from the dimension required for this mapping 
		* field: shortname of the field to use as EAS
		* mapping_name: prefix of EAS / IAS files, will have '_EAS.txt' or '_IAS.txt' appended once saved
		* subfolder: subfolder within the Data Load folder to save mappings to
		* include_count: generate a '_Count.txt' file, to use for the 'Datapoints=X' command in relational ASCII sources, where each element has a separate data column
		* include_parent: generate a '_Parent.txt' file, to use for consolidations outside of Empower
		* include_physid: generate a '_Physid.txt' file, to use for importer bulk loading
		'''
		
		# Validate provided parameters
		if include_parent or include_physid:
			raise NotImplementedError('Parent / PhysID mapping not yet implemented')
		assert (type(dimension) == int) & (dimension >= 0), 'get_mapping_from_field: dimension should be an integer greater than or equal to zero; {} was provided'.format(dimension)
		assert type(structure) == str, 'get_mapping_from_field: structure should be provided as a string, but type {} was provided'.format(type(structure))
		assert type(field) == str, 'get_mapping_from_field: field should be provided as a string, but type {} was provided'.format(type(field))
		assert type(mapping_name) == str, 'get_mapping_from_field: mapping_name should be provided as a string, but type {} was provided'.format(type(mapping_name))
		assert os.path.exists(os.path.join(self.cwd, subfolder)), 'get_mapping_from_field: subfolder provided does not exist: {}'.format(subfolder)
		
		self.log_message('Creating mapping files for {} from dimension {} and structure {} using field {}'.format(mapping_name, dimension, structure, field))
		
		# Get the elements and the structure as DataFrames; if they haven't been exported yet, export them
		try:
			elements = self.elements[dimension]
		except KeyError:
			self.export_elements(dimension)
			elements = self.elements[dimension]
		
		try:
			structure = self.structures[dimension][structure]
		except KeyError:
			self.export_structure(dimension, structure)
			structure = self.structures[dimension][structure]

		sn = 'Short Name'
		required_fields = [sn, field]
		
		self.log_message('Processing mapping files for {}'.format(mapping_name))
		
		# Get the child elements from the structure (where their phys ID does not appear as a parent of another element
		parent_mask = structure['ID'].isin(structure['Parent ID'])
		children = structure[~parent_mask]
				
		# Merge the fields from the elements list with the elements in the required structure, keep required fields
		merged = pd.merge(left = elements,				   
						  right = children, 
						  left_on = sn,
						  right_on = sn, 
						  how = 'right')[required_fields]

		# De-duplicate on shortname, drop missing field EAS values
		merged.drop_duplicates(subset = sn, inplace = True)
		merged.dropna(axis = 0, subset = [field], inplace = True)
		
		# Write to output files
		output_folder = os.path.join(self.cwd, subfolder)
		EAS_file = os.path.join(output_folder, '{}_EAS.txt'.format(mapping_name))
		IAS_file = os.path.join(output_folder, '{}_IAS.txt'.format(mapping_name))
		Count_file = os.path.join(output_folder, '{}_Count.txt'.format(mapping_name))
		PID_file = os.path.join(output_folder, '{}_Physid.txt'.format(mapping_name))
		Parent_file = os.path.join(output_folder, '{}_Parent.txt'.format(mapping_name))
		
		# IAS
		merged[sn].to_csv(IAS_file, header = False, index = False, encoding = 'ANSI')
		# EAS - use a space separator for the csv function to ensure values containing spaces are quoted
		merged[field].to_csv(EAS_file, header = False, index = False, sep = ' ', encoding = 'ANSI')
		# Count
		if include_count:
			with open(Count_file, 'w') as f:
				f.write(str(len(merged)))
				
	def set_calculation(self, dimension, use_shortnames = True,
                    calc_file = None, 
                    calculation = None, framework = -1, virtual = True, elements = []):
		'''
		Function to run the calc setter utility. Runs either from a calc file, or can set a targeted calculation
		A single calculation can be applied to an element, or list of elements.
		Alternatively, a tab-separated file can be provided giving calculations to apply to different elements 
		- this should comprise a first field of Element Shortname, followed by a second field containing the required calculation.
		
		Parameters:
		* dimension: 0-indexed dimension number to apply calculations to
		* use_shortnames: Optional, default True; specifies that the provided calculation is written using shortnames (rather than Physids)
		* calc_file: Optional, default None; file path of a file containing the required calculations
		- The following parameters will be used if a calc file is not provided
		* calculation: Optional, default None; string specifying the calculation to apply
		* framework: Optional, default -1; physid of the framework to apply the calculations to (-1 is default)
		* elements: Element shortname or list of element shortnames to apply calculation to
		
		Example:
		e.set_calculation(dimension = 0, calc_file = 'update_calculations.tsv')
		e.set_calculation(dimension = 8, calculation = 'Sales |- COGS', virtual = False, elements = 'GProfit')
		e.set_calculation(dimension = 0, use_shortnames = False, calculation = '@100 | @200', elements = 'NSales')
		'''

		# Assert that this is not encrypted password mode, as this is not yet supported
		assert (self.password_mode != 'encrypted'), 'set_calculation: encrypted password mode is not yet supported for this function'
		
		# Validate provided paraneters
		assert type(dimension) == int, 'dimension: must provide dimension for calculations, as 0-indexed integer'
		assert type(use_shortnames) == bool, 'use_shortnames: must be True (default) or False, but {} was provided'.format(str(use_shortnames))
		assert calc_file or calculation, 'Either a calculation file, or a calculation must be provided'
		if calc_file:
			assert os.path.exists(calc_file) or os.path.exists(os.path.join(self.script_folder, calc_file)), 'calc_file: provided calculation file does not exist: {}'.format(calc_file)
		else:
			assert type(calculation) == str, 'calculation: must be provided as a string'
			assert type(virtual) == bool, 'virtual: Virtual must be True or False'
			assert (type(elements) == str) or (type(elements) == list), 'elements: must provide a shortname, or list of shortnames'
			if type(elements) == list:
				assert len(elements) > 0, 'elements: must provide a shortname, or list of shortnames'
				assert all(type(i) == str for i in elements), 'elements: must provide a shortname, or list of shortnames'
		
		# Get the calculation setter
		calc_set_exe = os.path.join(self.empower_folder, 'Empower Calculation Setter.exe')
		assert os.path.exists(calc_set_exe), 'Calculation Setter not found in {}; ensure this has been installed correctly'.format(self.empower_folder)
		
		# Create a call line based on the required parameters
		call_line = []
		
		call_line.append('-site "{}" '.format(self.site_file))
		call_line.append('-user "{}" '.format(self.username))
		call_line.append('-password "{}" '.format(self.password))
		call_line.append('-dimension {} '.format(dimension))
		if use_shortnames:
			call_line.append('-shortnames ')
		
		# If using a calculation file, provide that
		if calc_file:
			self.log_message('Setting calculations for dimension {}; using file {}...'.format(dimension, calc_file))
			if os.path.exists(calc_file):
				call_line.append('-file {}'.format(calc_file))
			else:
				call_line.append('-file {}'.format(os.path.join(self.script_folder, calc_file)))
		
		# Otherwise provide all the required details for the calculation    
		else:
			self.log_message('Setting calculations {}, for dimension {}...'.format(calculation, dimension))
			call_line.append('-framework {} '.format(framework))
			call_line.append('-calculation "{}" '.format(calculation))
			call_line.append('-{} '.format('virtual' if virtual else 'real'))
			call_line.append(' '.join(elements) if type(elements) == list else elements)
			
		# Run the calc setter, and capture the response
		return_value=subprocess.run([calc_set_exe, call_line], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		
		if return_value.returncode != 0:
			self.log_message('Calculation Setter failed, and returned code {}'.format(return_value.returncode))
			raise RuntimeError('Calculation Setter has failed')
		else:
			self.log_message('Calculation(s) set successfully.')
			self.log_message(return_value.stdout.decode('ansi'), debug_only = True)
			self.log_message(return_value.stderr.decode('ansi'), debug_only = True)
    
# -------------------------------------------------------------------------------------------------------------------------------------------------------
# General functions
# 

def get_password(prompt = 'Please enter password: '):
	'''
	get_password collects and returns a user input password, provided via command prompt, and anonymously displays '*' in place of password characters
	
	This is required as an alternative to Python's getpass.getpass, which is not properly supported via windows console
	
	Parameters:
	* prompt: Optional, default 'Please enter password: '; message to display to screen to prompt for password input
	'''
	
	# Ensure there is a space after the prompt message
	actual_prompt = prompt if prompt[-1] == ' ' else '{} '.format(prompt)
	
	# Setup special characters that may be provided by the user and need handling
	return_char = '\r'.encode('utf-8')
	newline_char = '\n'.encode('utf-8')
	ctrl_c_char = '\003'.encode('utf-8')
	backspace_char = '\b'.encode('utf-8')
	trailing_space_char = b'\x00'
	
	#Prompt the user to enter their password
	sys.stdout.write(actual_prompt)
	sys.stdout.flush()
	
	# Start with a blank password, and user msvcrt getch to collect characters as they are written to the console
	pw = str()

	# Keep collecting until enter is pressed, or keyboard interrupt is provided
	while True:
		c = msvcrt.getch()
		
		# Ignore trailing space - getch function sometimes returns this after every key press and it should be ignored
		if c != trailing_space_char:
			if c == return_char or c == newline_char:
				break # end on "enter"
			if c == ctrl_c_char:
				raise KeyboardInterrupt # raise an error if "control c" is provided
			if c == backspace_char:
				# If backspace is provided, remove the last character of the password, and re-write the '*'s to screen 
				sys.stdout.write('\r{}{}'.format(actual_prompt, ' ' * len(pw))) # remove the existing password
				pw = pw[:-1] # remove the last character
				sys.stdout.write('\r{}{}'.format(actual_prompt, '*' * len(pw))) # re-write the *s
				sys.stdout.flush()
			else:
				# If it is a normal character, add it to the collected password and write another star to screen
				pw = pw + str(c, 'utf-8')
				sys.stdout.write('*')
				sys.stdout.flush()

	# Move the console onto the next line
	sys.stdout.write('\n')
	
	# Return
	return pw

	
def get_secure_password(EmpowerClass):
	'''
	get_secure_password collects a user password and encrypts it using importer; to provide a more secure process
	The password is initially collected using get_password, and subsequently encrypted, stored, and used
	
	This must be run by an "Empower" object; as it needs to call importer
	
	This is used in conjunction with "encrypted" password_mode; and requires that:
	- Importer scripts requiring a password received the encrytped password, then set an encrypted password parameter for use
	- Batch scripts use the run_batch_secure function
	'''
	
	# Create the call line - the "-" instructs Importer to accept standard in
	call_line=[EmpowerClass.importer, '-']

	# Call importer with STDIO open to pass commands
	proc=subprocess.Popen(args=call_line, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

	# Pass in a password encryption script; collect the password on demand using the get_password function
	proc.stdin.write('encrypt-text -machine-locked {}'.format(get_password()).encode('utf-8'))
	proc.stdin.flush()
	proc.stdin.close()
	
	# Collect the response
	output = proc.stdout.read()
	errors = proc.stderr.read()
	try:
		std_err =str(errors.decode('utf-8'))
	except UnicodeDecodeError:
		std_err =str(errors.decode('cp1252'))

	#Close the process and capture errors / logs
	proc.communicate() 
	EmpowerClass.log.debug("Getting encrypted password...")
	EmpowerClass.log.debug("STDERR:")
	EmpowerClass.log.debug(std_err)
	EmpowerClass.log.debug('Return Code: {}'.format(str(proc.returncode)))
	if proc.returncode!=0:
		EmpowerClass.log.error('Empower Importer failed and returned Code: '+str(proc.returncode)+'\n'+std_err)
	EmpowerClass.log.debug("Encrypted password collected.")	
	return output.decode('utf-8').strip()
