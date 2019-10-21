import os
import requests
import json

KEY_RESULT_VALUE = "result"

def sendUpdateRequest(c):
    try:
        job = os.environ['AI_MAKER_JOB_ID']
        pod_name = os.environ['HOSTNAME']
        token = os.environ['AI_MAKER_TOKEN']
        url = os.environ['AI_MAKER_HOST']
        user_id = os.environ['USER_INFO_USER_ID']
	user_type = os.environ['USER_INFO_USER_TYPE']
	project_name = os.environ['USER_INFO_PROJECT_NAME']
	x_api_key = os.environ['USER_INFO_X_API_KEY']
	goc_enable = os.environ['GOC_PAAS_AUTH_ENABLE']
    except KeyError as e:
        print ("[KeyError] Please assign {} value".format(str(e)))
        return -1
    if (goc_enable) {
	switch (user_type) {
	    case 1:
                user_type = "tenant_admin"
                break;
	    case 2:
                user_type = "member"
                break;
	}
    }
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
        job = os.environ['AI_MAKER_JOB_ID']
        model = os.environ['AI_MAKER_MODEL_ID']
        token = os.environ['AI_MAKER_TOKEN']
        url = os.environ['AI_MAKER_HOST']
        user_id = os.environ['USER_INFO_USER_ID']
	user_type = os.environ['USER_INFO_USER_TYPE']
	project_name = os.environ['USER_INFO_PROJECT_NAME']
	x_api_key = os.environ['USER_INFO_X_API_KEY']
	goc_enable = os.environ['GOC_PAAS_AUTH_ENABLE']
    except KeyError as e:
        print ("[KeyError] Please assign {} value".format(str(e)))
        return -1
    if (goc_enable) {
	switch (user_type) {
	    case 1:
                user_type = "tenant_admin"
                break;
	    case 2:
                user_type = "member"
                break;
	}
    }
    HEADERS = {"content-type" : "application/json",
               "Authorization" : "bearer "+token,
               "user-id" : user_id,
               "user-role" : user_type,
               "project" : project_name,
               "x-api-key" : x_api_key}
    body = json.dumps({ KEY_RESULT_VALUE : result })
    url = url+"/api/v1/ai-maker/callback/results/jobs/"+job+"/models/"+model+"/validations"
    return requests.post(url, data = body, headers = HEADERS)
