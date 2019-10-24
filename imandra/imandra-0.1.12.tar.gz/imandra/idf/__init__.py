import os.path 
import requests
import urllib

from .decomposition import Decomposition
from .exception import process_errors
from ..auth import Auth
from .sampler import Sampler

API = "https://www.imandra.ai/"

def decompose(code, api_url=None, auth_token=None):
    # Get auth token
    if auth_token == None:
        if decompose.token == None:
            auth = Auth()
            decompose.token = auth.token
        auth_token = decompose.token
            
    headers = { 'X-Auth': auth_token }

    if api_url == None:
        api_url = API

    r = requests.post\
      ( os.path.join(api_url, "api/ipl-worker/enqueue_py")
      , data = code
      , headers = headers
      )
    job_hash = process_errors(r)

    return Decomposition(job_hash, api_url, headers)
   

decompose.token = None

