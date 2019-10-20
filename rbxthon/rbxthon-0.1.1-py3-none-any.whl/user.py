from bs4 import BeautifulSoup
import requests
import json

class User:
     #/users/{id}
    @staticmethod
    def UsernameById(self, id):
        return requests.get(url='http://api.roblox.com/users/' + str(id))