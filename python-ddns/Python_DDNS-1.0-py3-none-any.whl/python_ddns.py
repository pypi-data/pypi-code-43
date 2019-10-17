# pylint: disable=invalid-name, missing-docstring, inconsistent-return-statements
import configparser
import socket
import sys
import requests


BASE_URL = "https://api.cloudflare.com/client/v4/zones/"
CONFIG = configparser.ConfigParser()
CONFIG.read("config.conf")

# Shamlessly taken from stackoverflow https://stackoverflow.com/a/28950776/11542276
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('1.1.1.1', 1))
        host = s.getsockname()[0]
    finally:
        s.close()
    return host

def check_record():
    record = {}
    record["type"] = "A"
    record["name"] = CONFIG['Cloudflare']['name']
    output = send(record, 1)
    if output:
        return output

def add_record(ip):
    record = {}
    record["type"] = "A"
    record["name"] = CONFIG['Cloudflare']['name']
    record['content'] = ip
    record['proxied'] = CONFIG['Cloudflare']['proxied'] == 'True'
    output = send(record, 2)
    if not output['success']:
        try:
            error_code = output['errors'][0]['error_chain'][0]['code']
        except KeyError:
            error_code = output['errors'][0]['code']
        # This error code means the record can not be proxied. Likely due to a private IP
        if error_code == 9041:
            record['proxied'] = False
            r = send(record, 2)
            if r.json()['success']:
                print("The record was created successfully")
        else:
            print("There was an error\n")
            print(output['errors'])
    if output['success']:
        print("The record was created successfully")

def update_record(ip, record_id):
    record = {}
    record["type"] = "A"
    record["name"] = CONFIG['Cloudflare']['name']
    record['content'] = ip
    output = send(record, 3, record_id)
    if not output['success']:
        print("There was an error:")
        print(output)


def send(content, which, extra=None):
    headers = {'Authorization': CONFIG['Cloudflare']['API_Token'],
               "X-Auth-Email": CONFIG['Cloudflare']['Email'],
               "Content-Type": "application/json"}
    zone = CONFIG['Cloudflare']['Zone']
    api_url = BASE_URL+zone+"/dns_records"
    if which == 1:
        r = requests.get(api_url, params=content, headers=headers).json()
        if r['result']:
            return r['result'][0]['id']
    elif which == 2:
        return requests.post(api_url, json=content, headers=headers).json()
    elif which == 3:
        api_url = api_url+"/"+extra
        return requests.put(api_url, json=content, headers=headers).json()

def quick_test():
    if CONFIG == 0:
        raise FileNotFoundError

def main():
    if sys.argv[1] == "-t":
        quick_test()
        sys.exit()
    check = check_record()
    if check:
        update_record(get_ip(), check)
    else:
        add_record(get_ip())
