import json, requests, urllib3

# fix cert warnigns

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# login function

def ledlogin (user, password, ip, port):

    headers = {
        'Content-Type': 'application/json',
        'Accept': '*/*',
    }

    data = '{"username":"' + user + '","password":"' + password + '"}'

    try:

        response = requests.post('https://' + ip + ':' + port + '/v1/login', headers=headers, data=data, verify=False)

    except requests.exceptions.RequestException as e:  # This is the correct syntax

        return None

    output = json.loads(response.content)

    if response.status_code == 200:

        return output

    elif response.status_code == 403:

        return False

    else:

        return None
