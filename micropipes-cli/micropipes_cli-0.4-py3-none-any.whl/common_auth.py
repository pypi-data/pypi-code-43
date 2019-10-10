import os
import time
from datetime import datetime
import http.client
import urllib.parse
import json
from pathlib import Path
from jose import jwt

AUTH_FILE_SUFFIX = '.auth'
AUTH_DEFAULT = 'default'
CLI_DIR = '.mpipes'


def base_dir():
    basedir = os.path.join(str(Path.home()), CLI_DIR)
    if not os.path.exists(basedir):
        os.makedirs(basedir)
    return basedir


def get_default_authentication():
    basedir = base_dir()
    if os.path.exists(os.path.join(basedir, AUTH_DEFAULT)):
        with open(os.path.join(basedir, AUTH_DEFAULT), 'r') as f:
            return f.readline()
    return None


def set_default_authentication(auth_name):
    full = os.path.join(base_dir(), auth_name + AUTH_FILE_SUFFIX)
    if not os.path.exists(full):
        print('Auth not exists {}'.format(auth_name))
        return
    basedir = base_dir()
    afilename = os.path.basename(auth_name)
    if str(afilename).endswith(AUTH_FILE_SUFFIX):
        afilename = os.path.splitext(afilename)[0]
    with open(os.path.join(basedir, AUTH_DEFAULT), 'w') as f:
        f.write("{}".format(afilename))



def save_authentication_data(data, auth_name, set_as_default=False):
    full = os.path.join(base_dir(), auth_name + AUTH_FILE_SUFFIX)
    with open(full, 'w') as outfile:
        json.dump(data, outfile)
    if set_as_default:
        set_default_authentication(auth_name)



def load_authentication_data(authentication):
    full = os.path.join(base_dir(), authentication + AUTH_FILE_SUFFIX)
    if os.path.exists(full):
        with open(full) as json_file:
            return json.load(json_file)
    return None



def is_access_token_expired(data):
    if not data:
        return True
    issued = data['issued']
    expires_in = data['expires_in']
    till_expired = (issued + expires_in) - time.time()
    # print('{} secs. till expiration'.format(till_expired))
    if till_expired <= 0:
        return True
    else:
        return False



def get_access_token(authentication):
    auth_data = load_authentication_data(authentication)
    if is_access_token_expired(auth_data):
        if refresh_token(authentication):
            auth_data = load_authentication_data(authentication)
        else:
            return None
    if auth_data and 'access_token' in auth_data:
        return auth_data['access_token']
    return None



def get_default_access_token():
    active_auth = get_default_authentication()
    if not active_auth:
        return None
    return get_access_token(active_auth)


# device authorization flow implementation
def user_token_device_auth(options):
    # read stored previous token
    conn = http.client.HTTPSConnection(options.auth_domain)
    payload = {
        "client_id": options.auth_client_id,
        'audience': options.auth_api_identifier,
        'scope': 'offline_access openid profile email'
    }
    headers = {
        'content-type': 'application/x-www-form-urlencoded'
    }
    conn.request("POST", "/oauth/device/code", urllib.parse.urlencode(payload), headers)
    res = conn.getresponse()
    data = json.loads(res.read().decode())
    if not 'verification_uri_complete' in data:
        print(data)
        raise Exception('Unauthorized')
    else:
        print('Paste this url to your browser and authorize this app')
        print('User code is {}'.format(data['user_code']))
        print(data['verification_uri_complete'])
        # if self.show_ui:
        #    self.show_url_as_qrcode(data['verification_uri_complete'])

    request_expires = int(data['expires_in'])
    interval = int(data['interval'])
    device_code = data['device_code']

    start_checking = datetime.now()
    while (datetime.now() - start_checking).total_seconds() < request_expires:
        # if self.show_ui:
        #    cv2.waitKey(delay=10)
        time.sleep(interval)
        # check for token
        payload = {
            'client_id': options.auth_client_id,
            'grant_type': 'urn:ietf:params:oauth:grant-type:device_code',
            'device_code': device_code,
        }
        headers = {
            'content-type': 'application/x-www-form-urlencoded'
        }
        conn.request("POST", "/oauth/token", urllib.parse.urlencode(payload), headers)
        res = conn.getresponse()
        data = json.loads(res.read().decode())
        if not 'access_token' in data:
            print(data['error'])
            if data['error'] == 'access_denied':
                raise Exception('Unauthorized')
            else:
                continue
        else:
            data['client_id'] = options.auth_client_id
            data['auth_domain'] = options.auth_domain
            data['api_identifier'] = options.auth_api_identifier
            data['micropipes_domain'] = options.micropipes_domain
            data['micropipes_port'] = options.micropipes_port
            data['https'] = options.https
            data['issued'] = time.time()
            save_authentication_data(data, options.micropipes_domain, options.set_default)
            # if self.show_ui:
            #    cv2.destroyAllWindows()
            print('Authorized')
            return
            # return data['access_token']



def refresh_token(authentication):
    data = load_authentication_data(authentication)
    if not data:
        print('ERROR: have no data for: {}'.format(authentication))
        return False
    if not 'refresh_token' in data:
        print('ERROR: this authentication: {} dont support refresh token'.format(authentication))
        return False

    conn = http.client.HTTPSConnection(data['auth_domain'])
    payload = {
        "client_id": data['client_id'],
        'refresh_token': data['refresh_token'],
        'grant_type': 'refresh_token'
    }
    headers = {
        'content-type': 'application/x-www-form-urlencoded'
    }
    conn.request("POST", "/oauth/token", urllib.parse.urlencode(payload), headers)
    res = conn.getresponse()
    ndata = json.loads(res.read().decode())
    if not 'access_token' in ndata:
        print('ERROR: failed to refresh token')
        return False
    data['access_token'] = ndata['access_token']
    data['issued'] = time.time()
    data['expires_in'] = ndata['expires_in']
    save_authentication_data(data, authentication, False)
    return True


def validate_access_token(api_identifier, auth_domain, token):
    conn = http.client.HTTPSConnection(auth_domain)
    conn.request("GET", url='/.well-known/jwks.json')
    resp = conn.getresponse()
    if resp.status != 200:
        return None
    content = resp.read().decode(resp.headers.get_content_charset())
    jwks = json.loads(content)
    try:
        unverified_header = jwt.get_unverified_header(token)
        # print('unverified_header {}'.format(unverified_header))
    except jwt.JWTError as e:
        print("Invalid header. Use an RS256 signed JWT Access Token")
        return None
    if unverified_header["alg"] == "HS256":
        print("Invalid header. Use an RS256 signed JWT Access Token")
        return None
    rsa_key = {}
    for key in jwks["keys"]:
        if key["kid"] == unverified_header["kid"]:
            rsa_key = {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"]
            }
    # print('RSA key {}'.format(rsa_key))
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                # algorithms=ALGORITHMS,
                audience=api_identifier,
                issuer="https://" + auth_domain + "/"
            )
            # print('payload {}'.format(payload))
            return payload
        except jwt.ExpiredSignatureError:
            print("Token is expired")
            return None
        except jwt.JWTClaimsError:
            print("Incorrect claims, please check the audience and issuer")
            return None
        except Exception as e:
            print("Unable to parse authentication token")
            return None
    print("Unable to find appropriate key")
    return None


def get_user_info(auth_domain, token):
    conn = http.client.HTTPSConnection(auth_domain)
    headerz = {
        'authorization': "Bearer {}".format(token)
    }
    conn.request("GET", url='/userinfo', headers=headerz)
    resp = conn.getresponse()
    if resp.status != 200:
        return None
    return resp.read().decode(resp.headers.get_content_charset())