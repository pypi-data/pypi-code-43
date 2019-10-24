import random
import uuid
import json
import os
import os.path
import urllib

import hashlib
import base64 
import requests

def get_secrets():
    rchar = lambda: random.SystemRandom().choice(get_secrets.chars) 
    verifier = bytes(rchar() for _ in range(32))
    challenge = hashlib.sha256(verifier).digest()
    challenge = base64.b64encode(challenge, altchars=b"-_")
    challenge = challenge.replace(b"=",b"")
    return verifier, challenge

get_secrets.chars = b'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

class Auth:
    def __init__(self):
        self.auth0_base_host  = "auth.imandra.ai"
        self.auth0_client_id  = "q2yGHBTLmJSia35zCOdkUpEecj9mQl6o"
        self.auth0_audience   = "https://www.imandra.ai/api"
        self.imandra_web_host = "https://www.imandra.ai"
        self.http_port        = None

        self.folder_path      =  os.path.join(os.environ['HOME'], ".imandra")

        self.redirect_uri = self.imandra_web_host + "/pkce-callback"
        if self.http_port:
            self.redirect_uri += "?redirect_port=" + str(self.http_port)

        self.ensure_folder()
        self.ensure_token()
        

    def ensure_folder(self):
        device_id_path = os.path.join(self.folder_path, "device_id")
        if not os.path.exists(self.folder_path):
            os.mkdir(self.folder_path)
        if not os.path.exists(device_id_path):
            self.device_id = str(uuid.uuid4())
            with open(device_id_path, 'w') as device_id_file:
                device_id_file.write(self.device_id)
        else:
            with open(device_id_path, 'r') as device_id_file:
                self.device_id = device_id_file.read()
                
       
    def ensure_token(self):
        token_path = os.path.join(self.folder_path, "login_token")
        if os.path.exists(token_path):
            with open(token_path, 'r') as token_file:
                self.token = token_file.read().strip()
            return
        
        self.verifier, self.challenge = get_secrets()
        link = self.make_link()
        print("We need to authenticate you! Please open: \n{}".format(link))
        code_str = str(input("Enter the code provided on the page above: "))
        self.token = self.exchange_tokens(code_str)
        
        with open(token_path, 'w') as token_file:
            token_file.write(self.token)
        
    def make_link(self):
        params = urllib.parse.urlencode(\
          { "audience"       : self.auth0_audience
          , "response_type"  : "code"
          , "client_id"      : self.auth0_client_id
          , "code_challenge" : self.challenge
          , "code_challenge_method" : "S256"
          , "redirect_uri"   : self.redirect_uri
          })
        return "https://{}/{}?{}".format(self.auth0_base_host, "authorize", params)
    
    
    def exchange_tokens(self, code_str):
        tkn = \
          { "grant_type"    : "authorization_code"
          , "client_id"     : self.auth0_client_id
          , "code_verifier" : self.verifier.decode("utf-8") 
          , "code"          : code_str
          , "redirect_uri"  : self.redirect_uri
          } 
        url = "https://{}/{}".format(self.auth0_base_host, "oauth/token")
        r = requests.post(url, json=tkn)
        if not r.ok:
            raise ValueError(r.text)
        auth_token = r.json()
        headers = \
          { "Authorization" : "Bearer {}".format(auth_token['access_token'])
          , "X-Device-Id"   : self.device_id
          } 
        url = "{}/{}".format(self.imandra_web_host, "api/login-token-for")
        r = requests.get(url, headers=headers)
        if not r.ok:
            raise ValueError(r.text)
        return r.text
