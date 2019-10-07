import json, requests, urllib3

# fix cert warnigns

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# set device brightness

def leddevicesetbrightness (deviceid, brightness,session, ip, port):

    headers = {
        'Authorization': 'Bearer ' + session['access_token'],
        'Content-Type': 'application/json',
        'Accept': '*/*',
    }

    data = '{"command":"sync","value":' + str(brightness) + '}'

    response = requests.put('https://' + ip + ':' + port + '/v1/devices/' + deviceid , headers=headers, data=data, verify=False)

    if response.status_code == 200:

        return True

    else:

        return False

# set device output

def leddevicesetoutput (deviceid, output,session, ip, port):

    headers = {
        'Authorization': 'Bearer ' + session['access_token'],
        'Content-Type': 'application/json',
        'Accept': '*/*',
    }

    data = '{"command":"config-output","value":' + str(output) + '}'

    response = requests.put('https://' + ip + ':' + port + '/v1/devices/' + deviceid , headers=headers, data=data, verify=False)

    if response.status_code == 200:

        return True

    else:

        return False
