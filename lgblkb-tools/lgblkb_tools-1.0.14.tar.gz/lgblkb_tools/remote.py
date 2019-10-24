from abc import abstractmethod

from fabric import Connection

from . import Folder,logger

class SshMan(object):

	def __init__(self,fabric_connection: Connection,remote_workdir: Folder):
		self.conn: Connection=fabric_connection
		# if isinstance(remote_workdir,str): remote_workdir=remote_projects_dir.create(
		# 	remote_workdir)
		assert isinstance(remote_workdir,Folder),f"'remote_workdir' is neither a Folder nor a string."
		self.work_folder: Folder=remote_workdir
		# if self.conn.run(f'[ -d "{remote_workdir.path}" ] && echo "exist" || echo "not exist"',warn=True).stdout.strip()=='not exist':
		# 	simple_logger.info('Creating folder %s on remote host.',remote_workdir.path)
		# 	self.conn.run(f'mkdir -p {remote_workdir.path}')
		pass

	def check_exists(self,program_name):
		which_result=self.conn.run(f'which {program_name}',warn=True)
		if which_result.failed: return False
		else:
			logger.info(f'"%s" already exists.',program_name)
			return True

	def apt_install(self,*package_names,forced=False):
		names=list()
		for package_name in package_names:
			pack_names=[x for x in package_name.split(" ") if x]
			names.extend(pack_names)

		if not forced:
			for package_name in names.copy():
				if self.check_exists(package_name):
					names.remove(package_name)
					logger.info('Skipping installation of "%s".',package_name)

		for package_name in names:
			self.run(f'sudo apt-get install {package_name} -y')
			package_path=self.conn.run(f'which {package_name}',warn=True).stdout.strip()
			logger.debug('"%s" path: %s',package_name,package_path)

	@abstractmethod
	def initial_setup(self,*args,**kwargs):
		pass

	@abstractmethod
	def execute(self,*args,**kwargs):
		pass

	def run(self,command,**kwargs):
		logger.info('Running !!!%s!!!',command)
		return self.conn.run(command,**kwargs)

	def put(self,local,remote,preserve_mode=True,absolute_remote=False):
		if not absolute_remote: remote=self.work_folder.get_filepath(remote)
		logger.info('Putting from !!!%s!!! to !!!%s!!!',local,remote)
		out=self.conn.put(local,remote=remote,preserve_mode=preserve_mode)
		return out

	def get(self,remote,local=None,preserve_mode=True):
		logger.info('Getting from !!!%s!!! to !!!%s!!!',remote,local)
		out=self.conn.get(remote,local=local,preserve_mode=preserve_mode)
		return out

	def cd(self,path):
		return self.conn.cd(path=path)

	def cd_to_working_dir(self):
		return self.cd(self.work_folder.path)

	def prefix(self,command):
		return self.conn.prefix(command=command)

	def sudo(self,command,**kwargs):
		return self.conn.sudo(command=command,**kwargs)

# class SshFolder(Folder):
#
# 	def __init__(self,remote_path,pseudo=False,parent=None,**conn_kwargs):
# 		super(SshFolder,self).__init__(remote_path,pseudo=True,parent=parent,propagate_type=True)
# 		self.pseudo=pseudo
# 		if parent is None:
# 			self.fabric_conn=Connection(**conn_kwargs)
# 		else:
# 			# self.sshman: SshMan=parent.sshman
# 			# self.sshman.work_folder=self
# 			self.fabric_conn=parent.fabric_conn
# 		self.sshman=SshMan(self.fabric_conn,self)
#
# 	def _mkdir(self,child_dirpath):
# 		with self.sshman.cd_to_working_dir():
# 			self.sshman.conn.run(f'mkdir -p {child_dirpath}')
# 		return os.path.join(self.path,child_dirpath)
#
# 	def children(self):
# 		with self.sshman.cd_to_working_dir():
# 			item_names=self.sshman.run('ls').stdout.strip().split('\n')
# 		return list(map(lambda x:os.path.join(self.path,x),item_names))
#
# 	def delete(self):
# 		with self.sshman.cd_to_working_dir():
# 			self.sshman.run(f"""
# cd ..
# rm -r {self.path}
# """)
#
# 	def clear(self):
# 		with self.sshman.cd_to_working_dir():
# 			self.sshman.run(f'rm -rf *')
#
# 	def md5(self,remote_filepath):
# 		return self.sshman.conn.run(f'md5sum {remote_filepath}',warn=True).stdout.strip().split(' ')[0]
#
# 	def upload_item(self,local_itempath,only_children=True):
# 		item_base_name=os.path.split(local_itempath)[-1]
# 		if os.path.isdir(local_itempath):
# 			if only_children:
# 				for item_to_upload in Folder(local_itempath).children():
# 					self.upload_item(item_to_upload,only_children=False)
# 				pass
# 			else:
# 				remote_folder=self.create(item_base_name)
# 				for local_sub_item_path in Folder(local_itempath).children():
# 					remote_folder.upload_item(local_sub_item_path)
# 		else:
# 			local_checksum=utils.md5(local_itempath)
# 			remote_filepath=self.get_filepath(item_base_name)
# 			while True:
# 				self.sshman.run(f"""rm {remote_filepath}""",warn=True)
# 				self.sshman.put(local_itempath,remote_filepath,absolute_remote=True)
# 				if local_checksum==self.md5(remote_filepath): return remote_filepath
#
# 	def run(self,command,**kwargs):
# 		return self.sshman.run(command=command,**kwargs).stdout.strip()
#
# 	def run_with_cd(self,command,**kwargs):
# 		with self.sshman.cd_to_working_dir():
# 			return self.run(command,**kwargs)
#
# 	def get(self,remote,local=None,preserve_mode=True):
# 		return self.sshman.get(remote,local=local,preserve_mode=preserve_mode)
#
# 	def put(self,local,remote,preserve_mode=True,absolute_remote=False):
# 		return self.sshman.put(local,remote,preserve_mode=preserve_mode,absolute_remote=absolute_remote)
