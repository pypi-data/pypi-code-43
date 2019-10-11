import os

def exists(filename):
	return os.path.isfile(filename)

def write_file_contents(data, filename="default-policies.json"):
    sd_file = open(filename, "w")
    sd_file.write(data)
    sd_file.close()

def get_file_contents(filename="service-description.jsonld"):
    sd_file = open(filename, "r")
    sd = sd_file.read()
    sd_file.close()
    return sd
