import requests

from lib.logging import error
from sys import exit

def crash(msg):
    error(msg)
    exit(1)

def get(url):
    response = requests.get(url)
    return response.text