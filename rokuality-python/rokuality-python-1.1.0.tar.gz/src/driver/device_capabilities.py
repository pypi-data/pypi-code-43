import json

class DeviceCapabilities:

    json_caps = None

    def __init__(self):
       self.json_caps = {}

    """
	Adds a capability object that will be passed to the Driver session start. Please
    see the README for a detailed descripton on what capabilities are required for
    a session start and which capabilities are optional.

	:param name: String - The name of the capability. See README for complete list.
	:param value: Object - The capability value.
	"""
    def add_capability(self, name, value):
        self.json_caps[name] = value
        print (self.json_caps)
    
    def get_capabilities_as_json(self):
        return json.dumps(self.json_caps)

    def remove_capability(self, name):
        self.json_caps.pop(name)
