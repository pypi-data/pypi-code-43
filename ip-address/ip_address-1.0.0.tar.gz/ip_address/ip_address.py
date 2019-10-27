import requests

def get():
    ip = requests.get("https://ident.me").text

    return ip