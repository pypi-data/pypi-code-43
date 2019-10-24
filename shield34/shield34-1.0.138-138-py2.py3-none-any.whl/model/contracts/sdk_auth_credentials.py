class SdkCredentials:
    apiKey = ""
    apiSecret = ""
    machineIdentifier = ""

    def __init__(self, api_key="", api_secret="", machine_identifier=""):
        self.apiKey = api_key
        self.apiSecret = api_secret
        self.machineIdentifier = machine_identifier

