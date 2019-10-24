from os import walk

def get_filenames(path):
	f = []
	for (dirpath, dirnames, filenames) in walk(path):
		f.extend(filenames)
		break
	return f