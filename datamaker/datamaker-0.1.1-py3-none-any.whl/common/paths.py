import os


abs_path = os.path.abspath(os.path.dirname(__file__))

metadata_path = abs_path + "/metadata/"
formats_path = metadata_path + "formats.json"
parameters_path = metadata_path + "parameters.json"

static_path = abs_path + "/static/"
cities_path = static_path + "cities.json"
countries_path = static_path + "countries.json"
names_path = static_path + "names.json"
states_path = static_path + "states.json"
streets_path = static_path + "streets.json"
