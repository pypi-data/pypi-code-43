import requests

base_url = "https://dev.twinthread.com"


def store_access_token(access_token):
  creds = open(".credentials",'w')
  creds.write(access_token)
  creds.close()

def get_access_token():
  try:
    creds = open(".credentials",'r')
    access_token =creds.read()
    creds.close()
    return access_token
  except FileNotFoundError:
    raise Exception("No credentials found. Please login before running this command.")


def login(username, password):
    response = requests.post(f"{base_url}/Token", {
        "grant_type": "password",
        "username": username,
        "password": password
    })
    
    if response.status_code != 200:
        raise Exception("Invalid credentials")
        
    access_token = response.json()["access_token"]
    store_access_token(access_token)

    return access_token

def post(route, body={}):
  access_token = get_access_token()
  headers = {"Authorization": f"Bearer {access_token}" }
  response = requests.post(f"{base_url}/api{route}", data=body, headers=headers)
  
  if response.status_code != 200:
      raise Exception("Request failed")

  try: 
    return response.json() 
  except: 
    raise Exception("Invalid server response. Please check query.")
        