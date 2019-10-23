import json
def headers(header_string):
    tmp = {}
    if(header_string.startswith("POST")):
        tmp["POST_DATA"] = {}
        for pair in header_string.split("\r\n\r\n")[1].split("&"):
            tmp["POST_DATA"][pair.split("=")[0]] = pair.split("=")[1]
    for header in header_string.split("\r\n\r\n")[0].split("\r\n")[1:]:
        tmp[header.split(": ")[0]] = header.split(": ")[1]
    return tmp

def parse(request):
    parsed = {}
    parsed["method"] = request.split()[0]
    parsed["url"] = request.split()[1]
    parsed["headers"] = headers(request)
    return parsed

def build_response(response_dict):
    http_version = response_dict["http-version"]
    http_status = response_dict["status"]
    del response_dict["status"]
    del response_dict["http-version"]
    response_str = f"{http_version} {http_status}"

    if(isinstance(response_dict["content"], dict)):
        response_dict["content-type"] = "application/json"
        response_dict["content"] = json.dumps(response_dict["content"])

    if(isinstance(response_dict["content"], list)):
        for header in response_dict["content"][0]:
            response_dict[header.split(": ")[0]] = header.split(": ")[1]
        response_dict["content"] = response_dict["content"][1]

    for key, value in response_dict.items():
        if not(key == "content" or key == http_status or key == http_version):
            response_str = response_str + "\r\n" + key + ": " + value

    response_str += "\r\n\r\n" + response_dict["content"]
    return response_str
