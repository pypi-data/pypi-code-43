name = "apispreadsheets"

import requests

def get_base_url():
    return "http://127.0.0.1:8000/data/"
    # return "https://api-woyera.com/api/data/"

def get_output_format(output_format):
    return "jsonRow" if output_format is None else output_format

def create_get_url(url, output_format, access_key, secret_key, rows):
    if access_key is not None and secret_key is not None:
        url += "?accessKey=" + access_key + "&secretKey=" + secret_key
        data_prefix = "&"
    else:
        data_prefix = "?"

    data_query_param = data_prefix + "dataFormat=" + output_format
    url += data_query_param

    if rows is not None:
        if '?' in url:
            url += "&rows=" + str(rows)
        else:
            url += "?rows=" + str(rows)

    return url

def create_post_headers(accessKey, secretKey):
    headers = {}

    if accessKey is not None and secretKey is not None:
        headers['accessKey'] = accessKey
        headers['secretKey'] = secretKey

    return headers

def post_data(file_id, data_format=None, access_key=None, secret_key=None, data=None):
    base_url = get_base_url()

    check_paramter_errors(data_format, access_key, secret_key, data=data)

    output = get_output_format(data_format)

    url = base_url + str(file_id) + "/"
    headers = create_post_headers(access_key, secret_key)

    r = requests.post(url, headers=headers, json={'data': data, 'format': output})

    post_status_code = r.status_code

    return post_status_code


def get_data(file_id, data_format=None, access_key=None, secret_key=None, rows=None):
    base_url = get_base_url()

    check_paramter_errors(data_format, access_key, secret_key, rows=rows)

    output = get_output_format(data_format)

    id_url = base_url + str(file_id) + "/"
    url = create_get_url(id_url, output, access_key, secret_key, rows)

    r = requests.get(url)

    get_status_code = r.status_code

    if get_status_code == 200:
        return r.json()
    elif get_status_code == 400:
        raise ValueError("The file is private. Please provide access and secret keys")
    elif get_status_code == 401:
        raise ValueError("The Access or Secret key is invalid")
    elif get_status_code == 404:
        raise ValueError("This file ID does not exist. Please find the correct ID from your dashboard")
    else:
        raise ValueError("There was something wrong on our server. Try again or contact us at info@apispreadsheets.com if the problem persists")


def check_paramter_errors(output_format, accessKey, secretKey, rows=None, data=None):
    if output_format not in ['jsonRow', 'jsonColumn', 'matrix'] and output_format is not None:
        raise ValueError("Output format must be jsonRow, jsonColumn or matrix or not used. Default is jsonRow")

    if (accessKey is None and secretKey is not None) or (secretKey is None and accessKey is not None):
        raise ValueError("Both access and secret key parameters must have values or not be used")

    if rows is not None:
        try:
            int(rows)
        except:
            raise ValueError("Rows parameter must be an integer")

    if data is not None:
        if type(data) != dict and type(data) != list:
            raise ValueError("Data must either be a hashmap or a list")
        else:
            if len(data) == 0:
                raise ValueError("Data must not be empty")
