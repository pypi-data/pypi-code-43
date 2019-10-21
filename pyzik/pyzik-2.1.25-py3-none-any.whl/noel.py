# -*- coding: utf-8 -*-
"""
Created on Sat Aug 10 12:37:38 2019

@author: https://github.com/noelprint/pynoelshack/blob/master/pynoelshack.py
"""
import re
import requests
from PIL import ImageGrab

class NShackError(Exception):
    pass


class NShack:
    API_URL = 'http://www.noelshack.com/api.php'

    def upload(self, file):
        with open(file, 'rb') as f:
            r = requests.post(self.API_URL, files={'fichier': f})

        if not 'www.noelshack.com' in r.text:
            raise NShackError(r.text)
        return self.parse(r.text)

    def parse(self, url):
        return re.sub(r'www\.noelshack\.com/([0-9]+)-([0-9]+)-([0-9]+)-',
                      r'image.noelshack.com/fichiers/\1/\2/\3/',
                      url)

    def clip2Noel(self,filename):
        if ".jpg" not in filename:
            filename += '.jpg'
        img = ImageGrab.grabclipboard()
        print(img)
        img.save(filename, 'JPEG')
        return self.upload(filename)
        
            
            
        