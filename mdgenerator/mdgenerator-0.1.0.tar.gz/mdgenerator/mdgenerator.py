import os
import numpy as np
import pandas as pd

def generate_file_structure(target_dir, output_dir = os.getcwd()):
	code = "```\n"
	os.chdir(target_dir)
	for root, dirs, files in os.walk("."):
		path = root.split(os.sep)
		if not os.path.basename(root) == ".":
			code += ((len(path) - 2) * '|   ') + '├── ' + os.path.basename(root) + '\n'
		for file in files:
			code += ((len(path) - 1) * '|   ') + '├── ' + file + '\n'
	code += "```"
	os.chdir(output_dir)
	f = open("file-structure.md","w+")
	f.write(code)
	f.close()

def generate_table(data):
	if isinstance(data, pd.DataFrame):
		pass
	elif isinstance(data, np.ndarray) and (data.ndim == 2):
		data = pd.DataFrame(data[1:], columns = data[0])
	elif isinstance(data, list) and (np.array(data).ndim == 2):
		data = pd.DataFrame(data[1:], columns = data[0])
	else:
		raise ValueError('Please provide either a pandas dataframe or a 2-D numpy array or a 2-D python list')
	table = '|' + '|'.join(data.columns) + '|'
	table += '\n' + '|---' * len(data.columns) + '|\n'
	table += '\n'.join(data.apply(lambda x: '|' + '|'.join(x) + '|', axis = 1))
	return table
