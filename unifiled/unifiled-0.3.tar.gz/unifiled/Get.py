import json, requests, urllib3

# fix cert warnigns

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# get devices function

def leddevices (session, ip, port):

    headers = {
        'Content-Type': 'application/json',
        'Accept': '*/*',
        'Authorization': 'Bearer ' + session['access_token'],
    }

    response = requests.get('https://192.168.255.41:20443/v1/devices', headers=headers, verify=False)

    output = json.loads(response.content)

    if response.status_code == 200:

        return output

    else:

        return False

# get groups function

def ledgroups (session, ip, port):

    headers = {
        'Content-Type': 'application/json',
        'Accept': '*/*',
        'Authorization': 'Bearer ' + session['access_token'],
    }

    response = requests.get('https://192.168.255.41:20443/v1/groups', headers=headers, verify=False)

    output = json.loads(response.content)

    if response.status_code == 200:

        return output

    else:

        return False
