import os
import requests
import json

KEY_RESULT_VALUE = "result"

def sendUpdateRequest(c):
    try:
        job = str(os.environ['AI_MAKER_JOB_ID'])
        pod_name = str(os.environ['HOSTNAME'])
        token = str(os.environ['AI_MAKER_TOKEN'])
        url = str(os.environ['AI_MAKER_HOST'])
        user_id = str(os.environ['USER_INFO_USER_ID'])
        user_type = str(os.environ['USER_INFO_USER_TYPE'])
        project_name = str(os.environ['USER_INFO_PROJECT_NAME'])
        x_api_key = str(os.environ['USER_INFO_X_API_KEY'])
        goc_enable = str(os.environ['GOC_PAAS_AUTH_ENABLE'])
    except KeyError as e:
        print ("[KeyError] Please assign {} value".format(str(e)))
        return -1
    if goc_enable == True:
        if user_type == "1":
            user_type = "tenant_admin"
        if user_type == "2":
            user_type = "member"
    HEADERS = {"content-type" : "application/json",
               "Authorization" : "bearer "+token,
               "user-id" : user_id,
               "user-role" : user_type,
               "project" : project_name,
               "x-api-key" : x_api_key}
    body = json.dumps({ KEY_RESULT_VALUE : c })
    url = url+"/api/v1/ai-maker/callback/results/jobs/"+job+"/pod/"+pod_name
    return requests.post(url, data = body, headers = HEADERS)

def saveValidationResult(result):
    try:
        job = str(os.environ['AI_MAKER_JOB_ID'])
        model = str(os.environ['AI_MAKER_MODEL_ID'])
        token = str(os.environ['AI_MAKER_TOKEN'])
        url = str(os.environ['AI_MAKER_HOST'])
        user_id = str(os.environ['USER_INFO_USER_ID'])
        user_type = str(os.environ['USER_INFO_USER_TYPE'])
        project_name = str(os.environ['USER_INFO_PROJECT_NAME'])
        x_api_key = str(os.environ['USER_INFO_X_API_KEY'])
        goc_enable = str(os.environ['GOC_PAAS_AUTH_ENABLE'])
    except KeyError as e:
        print ("[KeyError] Please assign {} value".format(str(e)))
        return -1
    if goc_enable == True:
        if user_type == "1":
            user_type = "tenant_admin"
        if user_type == "2":
            user_type = "member"
    HEADERS = {"content-type" : "application/json",
               "Authorization" : "bearer "+token,
               "user-id" : user_id,
               "user-role" : user_type,
               "project" : project_name,
               "x-api-key" : x_api_key}
    body = json.dumps({ KEY_RESULT_VALUE : result })
    url = url+"/api/v1/ai-maker/callback/results/jobs/"+job+"/models/"+model+"/validations"
    return requests.post(url, data = body, headers = HEADERS)
