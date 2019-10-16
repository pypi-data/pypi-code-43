import requests

config_endpoint = "https://storage.googleapis.com/inscribe-public-config-assets/wrapper-config.json"
config_response = requests.get(config_endpoint)
config = config_response.json()
