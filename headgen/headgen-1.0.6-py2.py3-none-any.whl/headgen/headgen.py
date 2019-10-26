"""!
@file
@brief Simple header files generator
This generator was written during making
labs on с language for faster coding
No license here. Use the way you want
I GIVE NO WARRANTY FOR CHANGING SYSTEM HEADERS
ASSERT THAT YOU ARE IN THE DIRECTORY 
WITH YOUR FILES. YO WILL BE ASKED FOR THAT
"""

import os
import datetime
from typing import List


class HeadersGenerator:
	"""!
	@brief class for generating Headers
	@param[in] params dict of params
	"""
	def __init__(self, **params):
		self.settings = params

	"""!
	@brief Creates protection name for a file
	@param[in] str start name of the file
	@param[in] str end file ending without a dot
	@example self.__protection("list", "h") -> __LIST_H__
	@return str
	"""
	@staticmethod
	def __protection(start:str, end:str) -> str:
		end = end.replace(".", "")
		start_up = start.upper()
		end_up = end.upper()
		res = f"__{start_up}_{end_up}__"
		return res
	

	"""!
	@brief gets th name of the file
	@param[in] file file to be handeled
	@return str
	"""
	@staticmethod
	def __get_file_name(path:str) -> str:
		import ntpath
		head, tail = ntpath.split(path)
		file = tail or ntpath.basename(head)
		res = file.split(".")[0]
		return res


	"""!
	@brief beatifies signature
	@param[in] line line to be handeled
	@return str
	@example int sum(int a, int b) //&signature -> int sum(int a, int b);
	"""
	@staticmethod
	def __beautify_signature(line:str) -> str:
		stripped = line.strip()
		splitted_line = stripped.split("//")
		signature_stripped = splitted_line[0].strip() 
		beautified = signature_stripped + ";\n\n"
		return beautified
	
	"""!
	@brief Creates current date str
	@return str
	"""
	@staticmethod
	def __current_time() -> str:
		res = datetime.datetime.now()
		res = res.strftime("%d %B %Y (%d.%m.%Y) At: %H:%M:%S")
		return res

	"""!
	@brief gets function's name
	@param[in] str signature
	@return str
	"""
	def __get_names_from_signatures(self, signatures: list) -> str:
		res = list()
		for signature in signatures: 
			splitted = signature.split("(")[0]
			splitted_spaces = splitted.split()
			# taking last element as it is
			# a name of the functions
			res.append(splitted_spaces.pop())
		return res
	
	
	"""!
	@brief adds preprocess to include
	@param[in] includes List[str]
	@return List[str]
	"""
	def __beautify_includes(self, includes : List[str]) -> List[str]:
		for index, inc in enumerate(includes):
			includes[index] = "#include " + inc
		return includes 
			
	"""!
	@brief Sorts include names
	@param[in] List[str] list of includes
	@return List[str]
	"""
	def __sort_includes(self, includes: List[str]) -> List[str]:
		res = sorted(includes, reverse = True)
		builtins = [inc for inc in res if "<" in inc]
		other = [inc for inc in res if "<" not in inc]
		builtins = sorted(builtins, key = len, reverse = True)
		other  = sorted(other, key = len, reverse = True)
		res = builtins + other
		return res

	"""!
	@brief Findes all includes in the file
	@param[in] file file to be readed
	@return List[str]
	"""
	def __find_includes(self, file: str) -> List[str]:
		res = list()
		with open(file, "r") as opened_file:
			for line in opened_file:
				if ">includes" in line:
					while "*/" not in line:
						line = next(opened_file)
						
						if "*/" in line:
							break
						else:
							res.append(line.strip()) 
			return res
		
	"""!
	@brief Finds functions signatures and docs
	@param[in] str file file to be readed 
	@return List[str]
	"""
	def __find_functions(self, file: str) -> List[str]:
		res = list()
		documentated = 0
		with open(file, "r") as opened_file:
			for line in opened_file:
				if ">signature" in line:
					sign = self.__beautify_signature(line)
					res.append(sign)
				if ">documentation" in line:
					documentated += 1
					doc = ""
					while True:
						new = next(opened_file).strip()
						if ">signature" in new: 
							break
						else:
							doc += new + "\n"
					doc += self.__beautify_signature(new)
					res.append(doc)
		return res, documentated
		
	"""!
	@brief Finds defines 
	@param[in] str file file to be readed 
	@return List[str]
	"""
	def __find_defines(self, file:str) -> List[str]:
		res = list()
		with open(file, "r") as opened_file:
			for line in opened_file:
				if ">defines" in line:
					while "*/" not in line:
						line = next(opened_file)
						
						if "*/" in line:
							break
						else:
							res.append(line) 
			return res

	"""!
	@brief Finds structures in the file
	@param[in] str file file to be readed 
	@return List[str]
	"""
	def __find_structures(self, file: str) -> List[str]:
		res = list()
		found = 0
		with open(file, "r") as opened_file:
			for line in opened_file:
				if ">structure" in line:
					found += 1
					while "*/" not in line:
						line = next(opened_file)
						if "*/" in line:
							res.append("\n")
							break
						else:
							res.append(line)


			return res, found
	
	"""!
	@brief Finds enums in the file
	@param[in] str file file to be readed 
	@return List[str]
	"""
	def __find_enums(self, file: str) -> List[str]:
		res = list()
		found = 0
		with open(file, "r") as opened_file:
			for line in opened_file:
				if ">enum" in line:
					found += 1
					while "*/" not in line:
						line = next(opened_file)
						if "*/" in line:
							res.append("\n")
							break
						else:
							res.append(line)
			return res, found
		
	"""!
	@brief finds al C files
	@return list of their paths
	"""
	def __all_files(self, dir) -> List[str]:
		res = list()
		for *root, files in os.walk(dir):
			for file in files:
				if file.endswith(".c"):
					res.append(os.path.join(root[0], file))
		return res

	"""!
	@brief Inits header info
	@param[in] str file file name
	@param[in] List[str] functions list of signatures
	@param[in] List[str] list of structures
	@param[in] List[str] list of enums
	@param[in] List[str] f_names names of functions
	@return str
	"""
	def __generate_info(self, file:str, sigs:list, documentated:int, structures:int, enums:int, f_names:str) -> str:
		pattern = "/*\nThis header file was generated automaticaly!\n"
		
		data = self.__current_time()
		pattern += f"Generated at: {data}\n"
  
		pattern += f"Amount of functions        : {len(sigs)}\n"
		pattern += f"Amount of documentated     : {documentated}\n"
		pattern += f"All functions documentated : {documentated == len(sigs)}\n"
		pattern += f"Amount of structures       : {structures}\n"
		pattern += f"Amount of enums            : {enums}\n"
		pattern += f"Function's names: \n" + f_names + "\n*/\n\n"

		return pattern
		
	"""!
	@brief beautifies names of signatures for info
	@param[in] List[str] names names of functions
	@return str
	"""    
	def __beautify_names_of_signatures(self, names:list) -> str:
		res = ""
		names = sorted(names)
		for _,  name in enumerate(names):
			res += "{:4g} > ".format(_ + 1) + name + "\n"
		return res
	
	"""!
	@brief list of includes to string
	@param[in] includes 
	"""
	def __string_includes(self, includes:list) -> str:
		res = "\n".join(includes)
		return res + "\n\n"
	
	"""!
	@brief Creates header for a single file
	@param[in] file File for header
	@return None
	"""
	def __create_header(self, file:str) -> None:
		#Finding and beutifying includes
		includes = self.__find_includes(file)
		includes = self.__sort_includes(includes)
		includes = self.__beautify_includes(includes)
		includes = self.__string_includes(includes)
  
		#finding structures
		structures, found_structs = self.__find_structures(file)
  
		#finding anв beautifying signatures
		signatures, documentated = self.__find_functions(file)
		signatures_names = self.__get_names_from_signatures(signatures)
		signatures_names = self.__beautify_names_of_signatures(signatures_names)
		
		#finding enums
		enums, found_enums = self.__find_enums(file)
		
		#finding defines
		defs = self.__find_defines(file)
  
  
		ending = self.settings["header_ending"]
		file_name = self.__get_file_name(file)
		header_file = file_name + ending
		
		# protection name for ifndef
		protection = self.__protection(file_name, ending)
		
		with open(header_file, "w") as header:
			   
			# Writing info for header
			info = self.__generate_info(
											file, 
											signatures,
											documentated,
											found_structs, 
											found_enums, 
											signatures_names
											)
			header.write(info)
					
			if self.settings["protection_with_pragma"]:
				header.write("#pragma once\n\n")

			elif self.settings["protection_with_ifndef"]:
				if_pattern = f"#ifndef {protection}\n#define {protection}\n\n"
				header.write(if_pattern)

			header.write(includes)		

			for _ in defs:
				header.write(_)

			header.write("\n\n")
				
			for struct in structures:
				header.write(struct)

			for en in enums:
				header.write(en)
			
			for func in signatures:
				header.write(func)
			
			if (
				self.settings["protection_with_ifndef"] and\
				not self.settings["protection_with_pragma"]
				):
				header.write(f"#endif // {protection}")
			header.write("\n\n")
	
	def __ask_for(self, what):
		if self.settings["ask"]:
			while 1:
				res = input(what + "<y/n>?: ")
				if (res.lower() in ("", "y", "yes")):
					return True
				elif (res.lower() in ("n", "no", "not")):
					return False
				else:
					print("Incorrect answer!")
		else:
			return True
 
 
	def __clean_ignore(self, files):
		try:
			with open(".headignore", "r") as file:
				ignore_files = file.readlines()
				ignore_files = [_.strip() for _ in ignore_files]
			for ig_file in ignore_files:
				for file in files:
					if ig_file in file:
						files.remove(file)
			return files
		except FileNotFoundError:
			return files

	
	"""!
	@brief Creates headers for all files
	""" 
	def create_headers(self) -> None:
		current_dir = os.getcwd()
		mes = "\nDo you want to search files in this directory: \n    * " + current_dir + "  "
		if not self.__ask_for(mes):
			exit()
		
		files = self.__all_files(current_dir)
		if files:
			files = self.__clean_ignore(files)
			
		if files:
			print("\nHeaders will be created for this files: ")
			for file in files:
				print("    *", file)
			print()
				
			mes = "Do you agree "
			if not self.__ask_for(mes):
				exit()
			print()
			for file in files:
				print("Creating header for: \n    *", file)
				try:
					self.__create_header(file)
				except:
					print("    * Error while creating header!")
			print("\nFinished!")
		else:
			print("No files were found!")	

		
	
if __name__ == '__main__':
	from argparse import ArgumentParser
	from pprint import pprint
	settings = {
				"protection_with_pragma" : False,
				"protection_with_ifndef" : True,
				"encoding" : "utf-8",
				"header_ending" : ".h",
				}

	parser = ArgumentParser()
	
	parser.add_argument("-p"  , "--pragma"       , help = "Set pragma protection.",               action = "store_true",    required = False)
	parser.add_argument("-if" , "--ifndef"       , help = "Set ifndef protection.",               action = "store_true",    required = False, default = True)
	parser.add_argument("-enc", "--encoding"     , help = "Encoding of the file.",                default = "utf-8",        required = False, type = str)
	parser.add_argument("-a"  , "--ask"          , help = "Wу will ask you before doing anything", action = "store_true", required = False)
	args = parser.parse_args()


	settings["protection_with_pragma"] = args.pragma
	settings["protection_with_ifndef"] = args.ifndef
	settings["encoding"] = args.encoding
	settings["ask"] = args.ask
	
	generator = HeadersGenerator(**settings)
	generator.create_headers()