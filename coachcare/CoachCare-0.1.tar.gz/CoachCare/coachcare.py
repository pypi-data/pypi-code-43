from __future__ import absolute_import
import json
import os, sys
from urllib.parse import urlencode
import requests
import secrets
from requests import Response
from Crypto.Cipher import AES
from CoachCare.constants import BASE_HEADER, URL, GET_HEADER, BASE_DIR, CONFIG_DIR, EXTERNAL_CONFIG_DIR, BASE_URL, AUTH_VERSION, WEBHOOK_API_VERSION
from CoachCare.constants import logging
from CoachCare.coachcare_exceptions import BadResponse, InvalidRouteData, AuthenticationError
from enum import Enum
from datetime import datetime
from typing import List, Dict, Tuple, Set, Callable, Iterable

logging = logging.getLogger(__name__)

class API(object):
    def __init__(self, token=None, version=None):
        self.token = token
        self.version = version
        self.base_url = BASE_URL
        self.recur_count = 0
        if version in ['3.0', '2.0', '1.0']:
            self.url = self.base_url + self.version
        else:
            self.url = URL
        self.endpoint = {
            'authenticate':self.url+'/login',
            'validate':self.url+'/token',
            'post_account':self.url+'/account',
            'patch_account':self.url+'/account/{}',
            'account_id':self.url+'/account/{}',
            'account_access':self.url+'/access/account/',
            'post_body_measurement':self.url+'/measurement/body',
            'get_body_measurement':self.url+'/measurement/body{}',
            'body_measurement_summary':self.url + '/measurement/body/summary/',
            'delete_body_measurement': self.url + '/measurement/body/{}',
            'patch_body_measurement': self.url + '/measurement/body/{}',
            'organizations':self.url + '/access/organization',
            'post_association': self.url + '/association',
            'delete_association': self.url + '/association/{}/{}',
            'patch_association': self.url + '/association/{}/{}',
            'session_id':self.url + '/session',
            'get_webhook_scopes': self.url + '/notification/webhook/scope',
            'create_webhook_subscription': self.url + '/notification/webhook/subscription',
            'get_webhook_subscription_by_id': self.url + '/notification/webhook/subscription/{}',
            'delete_webhook_subscription': self.url + '/notification/webhook/subscription/{}',
            'patch_webhook_subscription': self.url + '/notification/webhook/subscription/{}',
            'get_all_webhooks_by_org':self.url + '/notification/webhook/subscription'
             }
        self.mandatory_fields = {
            "post_account": set(["firstName", "lastName","email", 
                                 "accountType", "phone", "gender"]),
            "patch_account":set(["account"]),
            "post_body_measurement":set(["recordedAt", "device","weight"]),
            "get_body_measurement":set(["account", "startDate", "unit"]),
            "body_measurement_summary":set([]),
            "post_association":set(["account", "organization"]), 
            "delete_association":set(["account", "organization"]), 
            "account_access":set([]),
            "organizations":set([]),
            "session_id":set([]),
            "account_id":set([]),
            "create_webhook_subscription": set(["organization", "url","secret","scopes","isActive","includeDetailedPayload"]),
            "get_webhook_subscription_by_id":set([]),
            "get_webhook_scopes": set([]),
            "patch_webhook_subscription": set([]),
            "delete_webhook_subscription": set([]),
            "get_all_webhooks_by_org":set([])
             }
        self.header = None
        self.set_header()

    def set_api_version(self, version):
        if version in ['3.0', '2.0', '1.0']:
            self.url = self.base_url + version

    def set_header(self):
        if self._type() == "Auth":
            self.header = BASE_HEADER
        else:
            self.header = {**GET_HEADER, **{'Authorization':'{0}'.format(self.token)}}

    def _type(self)->str:
        return self.__class__.__name__

    def _validate_data(self,data, route)->bool:
        try:
            mandatory_fields = self.mandatory_fields[route]
        except KeyError as ke:
            logging.error("[CoachCare]in validate_data KeyError: {} not a valid method:\n{}".format(route, ke))
            return False
        if not mandatory_fields.issubset(set(data)):
            diff = mandatory_fields - set(data)
            logging.error("[CoachCare]in validate_data missing fields {} which are mandatory fields".format(diff))
            return False
        return True

    def _get_error_message(self, response)->str:
        msg = ""
        if isinstance(response, Response):
            if response.content:
                response = json.loads(response.content.decode("utf-8"))
            else:
                logging.error("[CoachCare::get_error_message] No response found")
        else:
            response = json.loads(response.decode("utf-8"))
        if "code" in  response:
            msg += response["code"] + ", "
        if "message" in response:
            msg += response["message"]
        return msg

    def _is_authentication_error(self, response):
        error = self._get_error_message(response)
        if "session not found" in error.lower():
            # re-authenticate and try again
            logging.error("Authentication error!")
            return True
        return False
        
    def request(self,request_type, endpoint, params=None, data=None,inurl=None,log=False,**kwargs)->Dict:
        all_data = {}
        li = [params, data, kwargs]
        for d in li: 
            if isinstance(d, dict):
                all_data.update(d)        
        if self._validate_data(all_data, endpoint):
            request_type = request_type.lower()
            assert request_type in ["post", "get", "patch", "delete"]
            try:
                method = getattr(requests, request_type)
            except AttributeError as ae:
                logging.error("[CoachCare::request] AttributeError erorr...")
                logging.error("[CoachCare::request] Error: " + str(ae))
                raise AttributeError()
            resp = self._get_response(method, endpoint, inurl=inurl, params=params,data=data)
            if resp.content:
                OK = range(200,300)
                if resp.status_code in OK:
                    message = resp.content.decode("utf-8")
                    return json.loads(message)
                else:
                    #raise BadResponse(str(resp.status_code) +" " + self._get_error_message(resp))
                    return None
            else:
                #logging.warning("[CoachCare::request] InvlaidRouteData: "+str(kwargs))
                logging.debug("[CoachCare::request] No Response recieved")
                #raise InvalidRouteData(kwargs)
                return None
        return None

    def _get_response(self,method, endpoint, inurl=None, params=None, data=None)->Response:
        resp = None
        if data:
            if not inurl and not params:
                resp = method(self.endpoint[endpoint], data=data, headers=self.header)
            elif inurl:
                resp = method(self.endpoint[endpoint].format(inurl), data=data, headers=self.header)
            elif params:
                resp = method(self.endpoint[endpoint].format(inurl), params=urlencode(params), headers=self.header)
        elif inurl:
            if data:
                resp = method(self.endpoint[endpoint].format(inurl),data=data, headers=self.header)
            elif params:
                resp = method(self.endpoint[endpoint].format(inurl),params=params, headers=self.header)
            else:
                resp = method(self.endpoint[endpoint].format(inurl), headers=self.header)
        elif params:
            resp = method(self.endpoint[endpoint], params=urlencode(params), headers=self.header)
        else:
            resp = method(self.endpoint[endpoint], headers=self.header)
        return resp

class Auth(API):
    def __init__(self,device_type=None, account_type=None, email=None, password=None, version=None):
        if version:
            API.__init__(self, version=version)
        else:
            API.__init__(self, version=AUTH_VERSION)
        ck = CredentialKeeper()
        CREDS = ck.get_creds()
        self.email = CREDS[0]
        self.pwd = CREDS[1]
        self.device_type = Device.ios.name
        self.account_type = Account.provider.name
        if email:
            self.email = email
        if password:
            self.pwd = password
        if device_type:
            try:
                device_type = getattr(Device, account_type)
                self.device_type = device_type
            except:
                self.device_type = Device.ios.name
        if account_type:
            self.account_type = account_type
        self.data = self._create_data(self.device_type, self.account_type)

    def _create_data(self, device_type, account_type)->Dict:
        data = {
            'email':self.email,
            'password':self.pwd,
            'deviceType':Device.get_device(device_type).value,
            'allowedAccountTypes':Account.get_account(account_type).value
            #'allowedAccountTypes':["3", "4"]
            }
        return data

    def _format_token(self,token):
        return "SELVERA " + token.strip()

    def _get_bearer_token(self,resp):
        """extracts Bearer token from POST response"""
        if not resp.ok:
            return False
        if self.data['deviceType'] in [dev.value for dev in Device]:
            return self._format_token(dict(resp.json())["token"])

    def _is_data_valid(self)->bool:
        if self.data["deviceType"] is False or self.data["allowedAccountTypes"] is False:
            return False
        return True

    def authenticate(self ):
        """Authenticates with coachcare api, and returns Bearer Token to be used by CoachCare.py interface."""
        logging.debug("[Auth] Authenticating")
        if self._is_data_valid():
            resp = requests.post(self.endpoint["authenticate"], data=json.dumps(self.data), headers=self.header)
            if resp.status_code == 200:
                json_resp = json.loads(resp.content) 
                logging.debug("[Auth] recieved token")
                #logging.debug("[Auth] response "+ str(json.loads(resp.content)))
                parsed_resp = self._get_bearer_token(resp)
            else:
                resp_dict = json.loads(resp.content.decode("utf-8"))
                logging.error("[Auth] Posted to: "+ self.endpoint["authenticate"])
                logging.error("[Auth] Data: "+ str(self.data) + "  Headers: "+ str(self.header))
                logging.error("[Auth]  "+ str(resp_dict))
                #raise AuthenticationError(resp_dict["message"])
                return False
            if parsed_resp:
                # set baseclass token
                self.token = parsed_resp
                return parsed_resp
        return False

class CoachCare(API):

    def __init__(self,token=None):
        super(CoachCare, self).__init__(token=token)
        if self.header["Authorization"] == "False":
            logging.error("[CoachCare] AUTHENICATION FAILED")
            raise AuthenticationError("Authentication Failed!")

    def change_auth(self, email, password, account_type=None):
        self.token = Auth(email=email, password=password, account_type=account_type).authenticate()

    def post_account(self,data):
        """Creates a new account. Password for the account is generated automatically"""
        return self.request(request_type="post", endpoint="post_account", data=data)

    def get_account_by_id(self, ID):
        logging.debug("[CoachCare] get_account_by_id called with id({})".format(ID))
        return self.request(request_type="get", endpoint="account_id", inurl=ID)

    def get_account_access(self, **params):
        """Gets listings of accessible accounts for an account"""
        resp = self.request(request_type="get", endpoint="account_access", params=params)
        #///for testing only
        #if "data" in resp:
        #    return resp["data"]
        return resp

    def patch_account(self, id, **kwargs):
        logging.debug("[CoachCare] Patching account data")
        return self.request(request_type="patch", endpoint="patch_account", inurl=id, data=kwargs)

    def get_organizations(self):
        """ Gets list of organizations """
        resp = self.request(request_type="get", endpoint="organizations")
        if "data" in resp:
            return resp["data"]
        return resp
        
    def get_body_measurement(self, **kwargs):
        """ Gets body measurement"""
        logging.info("[CoachCare] get_body_measurement called")
        if self._validate_data(kwargs, "get_body_measurement"):
            r = requests.get(self.endpoint["get_body_measurement"].format("?" + urlencode(kwargs)), headers=self.header)
            OK = range(200,300)
            if r.status_code in OK: 
                return json.loads(r.content.decode("utf-8"))
            logging.error("BadResponse error: " + str(r.status_code) + " " + self._get_error_message(r))
            raise BadResponse(str(r.status_code) + " " + self._get_error_message(r))
        logging.error("InvlaidRouteData: "+str(kwargs))
        raise InvalidRouteData(self.mandatory_fields["get_body_measurement"])

    def get_body_measurement_summary(self, **kwargs):
        self.set_api_version("3.0")
        resp = self.request(request_type="get",endpoint="body_measurement_summary", params=kwargs )
        self.set_api_version("2.0")
        return resp

    def post_body_measurement(self,**kwargs):
        """ Posts body measurement to API """
        logging.debug("[CoachCare] post_body_measurement called..")
        response = self.request("post", endpoint="post_body_measurement", data=kwargs, log=False)
        return response

    def get_session_id(self):
        """ Gets ID of current session """
        logging.info("[CoachCare] get_session_id called..")
        return self.request("get", endpoint="session_id")["id"]

    def post_association(self, **kwargs):
        logging.info("[CoachCare] post_association called..")
        return self.request(request_type="post", endpoint="post_association", data=kwargs)

    def delete_association(self, **kwargs):
        logging.info("[CoachCare] delete_association called..")
        if self._validate_data(kwargs,"delete_association" ):
            resp = requests.delete(self.endpoint["delete_association"].format(kwargs["account"], kwargs["organization"]), headers=self.header)
            OK = range(200,300)
            if resp.status_code in OK:
                if resp.content:
                    logging.debug("[CoachCare] response:" +str(json.loads(resp.content.decode("utf-8"))))
                    return json.loads(resp.content.decode("utf-8"))
                return True
            else:
                logging.error("[CoachCare] Error: " + self._get_error_message(resp))
                raise BadResponse(str(resp.status_code) + self._get_error_message(resp))
        raise InvalidRouteData(kwargs)

class Webhook(API):
    def __init__(self,token=None, version=None):
        self.token = token
        self.version = WEBHOOK_API_VERSION
        if not token:
            self.token = Auth().authenticate()
        if version:
            self.version = version
        super(Webhook, self).__init__(token=self.token, version=self.version)
        self.config_dir = EXTERNAL_CONFIG_DIR
        self.config_filename = "webhook_config.json"
        self.init_dir = EXTERNAL_CONFIG_DIR
        self.save_init_filename = "webhook_init.json"
        self.MAX_SUBSCRIPTIONS = 4 #/// max is 5 per documentation
        self.sub_list = []
        self.subscription_list = []

    def setup_webhook(self):
        logging.info("[Webhook] Initializing webhook...")
        # prevent multiple webhooks from being created
        
        # Does config file exist
        if os.path.isfile(self.config_dir + self.config_filename):
            try:
                # try to read data from json object
                org_id, url = self._get_org_id_and_url_from_config()
                self.subscription_list = self._get_webhook_subscription_list(org_id)
                self.sub_list = self.subscription_list

                if len(self.subscription_list) == 0:
                    print("[Webhook] No subscriptions")
                    # no webhook subscriptions create_new subscription based on config
                    logging.debug("[Webhook] no subs creating new sub..")
                    self._create_sub_based_on_config(org_id, url)
                else:
                    #print("[Webhook] subscription list: {}".format(json.dumps(self.subscription_list, indent=2)))
                    logging.debug("[Webhook] subscription list: {}".format([{"id":x["id"],"url":x["url"]} for x in self.subscription_list]))
                    # check to see if there is a sub with the correct url
                    subscription_exist = self._subscriptions_exists(url)
                    self.subscription_list = self._format_subscription_time()

                    # if not subscription_exists:
                    logging.debug("[Webhook] Subscription with url specified in config Does Not exist...")
                    if len(self.subscription_list) >= self.MAX_SUBSCRIPTIONS:
                        # delete oldest subscription
                        self._delete_oldest_n_subscription(n=1)

                    # create new sub based on config
                    self._create_sub_based_on_config(org_id, url)
                    #else:
                    #    logging.debug("[Webhook] Subscription from config already exists")
                        # cache results
                    #    self._save(selected_sub)
            except KeyError as e:
                logging.error("[Webhook] file '{}' was not configured properly\n \
                The following fields should be included in the json object:\n\t'organization','url'\n".format(self.config_filename, e))

        # No webhook_config no org id or url
        else:
            logging.error("[Webhook] file '{}' not found please create Webhook config file to configure webhook notifications".format(self.config_filename))

    def _get_org_id_and_url_from_config(self)->tuple:
        init_config = {}
        try:
            with open(self.config_dir + self.config_filename) as f:
                init_config = json.load(f)
            # try to read data from json object
            org_id = init_config['organization']
            url = init_config['url']
            return org_id, url
        except json.decoder.JSONDecodeError as e:
            logging.error("[Webhook] file '{}' was not configured properly\n \
            The following fields should be included in the json object:\n\t'organization','url'\n{} ".format(self.config_filename, e))
        except KeyError as ke:
            logging.error("[Webhook] file '{}' was not configured properly\n \
            The following fields should be included in the json object:\n\t'organization','url'\n{} ".format(self.config_filename, e))

    def _create_sub_based_on_config(self, org_id, url):
        logging.debug("[Webhook] Creating new webhook subscription")
        payload = self._create_webhook_payload(org_id, url)
        self.create_webhook_subscription(payload)
        logging.debug("[Webhook] Saving payload info")
        self._save(payload)

    def _delete_oldest_n_subscription(self, n=1):
        logging.debug("[Webhook] Max number of subs({}) already exists deleting {} oldest subscription".format(self.MAX_SUBSCRIPTIONS, n))
        if len(self.subscription_list) > 0:
            self.subscription_list = sorted(self.subscription_list, key=lambda x: x['createdAt'])
            if n <= len(self.subscription_list):
                n_oldest_sub = self.subscription_list[0:n]
            else:
                n_oldest_sub = self.subscription_list
            for i in range(len(n_oldest_sub)):
                logging.debug("[Webhook] deleting webhook with id({})".format(n_oldest_sub[i]["id"]))
                self.delete_webhook_subscription(id=n_oldest_sub[i]["id"])

    def _subscriptions_exists(self, url)->bool:
        subscription_exists = False
        for sub in self.subscription_list:
            if sub['url'] == url:
                subscription_exists = True
                break
        return subscription_exists

    def _format_subscription_time(self)->List:
        for sub in self.subscription_list:
            sub['createdAt'] = self._format_utc_time(sub["createdAt"])
        return self.subscription_list

    def _get_webhook_subscription_list(self, org_id)->List:
        # get existing webhooks (if any)
        webhooks =  self.get_all_webhooks_by_org(**{'organization': org_id})
        if webhooks:
            self.subscription_list = webhooks.get("data", [])
        return self.subscription_list

    def create_webhook_subscription(self, kwargs):
        """Takes params to create subscription\n
        eg.  {"organization": "6932",\n 
                                "url": https://url_to_webhook_listener.com,\n
                                "secret": "test_secret",(optional) \n
                                "scopes": "account", (optional)\n
                                "isActive": True, (optional)\n
                                "includeDetailedPayload": False (optional)\n
                                }\n"""
        logging.debug("[Webhook] ")
        logging.debug("[Webhook] creating webhook subscription with org id: {} and url:{}".format(kwargs.get("organization", "N/A"), kwargs.get("url", "N/A")))
        return requests.post(self.endpoint["create_webhook_subscription"], params=kwargs, headers=self.header )
    
    def patch_webhook_subscription(self, id, **kwargs):
        # return requests.patch(self.endpoint["patch_webhook_subscription"].format(id), data=kwargs )
        return self.request("patch",endpoint="patch_webhook_subscription",inurl=id ,data=kwargs)

    def delete_webhook_subscription(self, id):
        logging.debug("[Webhook] Deleting webhook subscription")
        return self.request("delete", endpoint="delete_webhook_subscription", inurl=id)

    def get_webhook_subscription(self, id):
        return self.request("get", endpoint="get_webhook_subscription_by_id" , inurl=id)

    def get_all_webhooks_by_org(self, **kwargs):
        """expects {"organization":org_id}"""
        if kwargs:
            return self.request("get", endpoint="get_all_webhooks_by_org", params=kwargs)
        return self.request("get", endpoint="get_all_webhooks_by_org")

    def _create_webhook_payload(self, organization_id, url, secret=None, scopes=None, isActive=True, includeDetailedPayload=True)->Dict:
        payload = {}
        logging.debug("[Webhook] create_webhook_payload organization id: {}".format(organization_id))
        payload["organization"] = organization_id
        payload["url"] = url
        payload['isActive'] = isActive
        payload['includeDetailedPayload'] = includeDetailedPayload
        payload['secret'] = secret
        payload['scopes'] = scopes
        if not secret:
            payload['secret'] = secrets.token_urlsafe(20)
        if not scopes:
            #//// Account needed to capture edit events, association needed to capture create events
            payload['scopes'] = ["association","account"]
        logging.debug("[Webhook] webhook payload (secret omitted): {}".format({x:y for x, y in payload.items() if x !="secret"}))
        return payload

    def _format_utc_time(self, time_str):
        return datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S.%f+00")

    def _save(self, payload):
        #validate input
        with open(self.init_dir +  self.save_init_filename, 'w') as f:
            json.dump(payload, f)
   
class CredentialKeeper(object):
    def __init__(self):
        self.dir = EXTERNAL_CONFIG_DIR
        #self.dir = CONFIG_DIR
        self.config_file = EXTERNAL_CONFIG_DIR + "auth_config.json"
        self.key1 = b'\x19}a\x9a\xe7\x05\xa5\x92l)\xa0\xe6\x15\x8c]\xfa'
        self.key2 = b'\x0f4\x07`#\r\x86\x8c\x86\xb6\x97b\xec\xe7w\x1b'
        self.obj = AES.new(self.key1, AES.MODE_CFB, self.key2)
        self.set_up()

    def set_up(self):
        logging.debug("[CredentialKeeper] setting up")
        creds = {}
        pass_exists = os.path.isfile(self.dir + "pass.bin")
        usr_exists = os.path.isfile(self.dir + "usr.bin")
        config_exists = os.path.isfile(self.config_file)
        if not pass_exists and not usr_exists and not config_exists:
            logging.error("[CredentialKeeper] No Credentials Provided or cached!\nNo auth_config.json, pass.bin, or usr.bin exits\
                            \nPlease place credentials in auth_config.json file with email and password fields")
            raise AuthenticationError("No auth_config.json file found OR no cached credentials")
        elif pass_exists and usr_exists:
        # check if config is not NONE (use case is new username/password needs to be set)
            logging.debug("[CredentialKeeper] pass_exists and usr_exists")
            if config_exists:
                creds = self.read_creds_from_config()
                if creds and creds["email"] != "None" and creds["password"] != "None":
                    self.set_creds(creds["email"], creds["password"])
                    creds["email"] = creds["password"] = "None"
                    with open(self.config_file, "w") as f:
                        f.write(json.dumps(creds))
        elif config_exists:
            logging.debug("[CredentialKeeper] config_exists")
            try:
                with open(self.config_file, "r") as f:
                    creds = json.load(f)
                if creds["email"] != "None" and creds["password"] != "None":
                    #print("[Credential Keeper] Writing NONE to auth_config file")
                    self.set_creds(creds["email"], creds["password"])
                    creds["email"] = creds["password"] = "None"
                    with open(self.config_file, "w") as f:
                        f.write(json.dumps(creds))
                else:
                    #auth_config fields are None
                    #print("[CredentialKeeper] auth_config fields are None")
                    try:
                        assert pass_exists and usr_exists
                    except AssertionError as e:
                        # no credentials provided or cached
                        logging.error("[CredentialKeeper] No Credentials Provided or cached!\nNo auth_config.json, pass.bin, or usr.bin exits\
                                        \nPlease place credentials in auth_config.json file with email and password fields")
                        raise(AuthenticationError("No Credentials Provided\nPlease place credentials in auth_config.json file with email and password fields"))
            except FileNotFoundError:
                logging.error("[CredentialKeeper] Credential Keeper auth_config.json file is not formatted properly or non-existant check: {}".format(self.config_file))
        else:
            logging.error("[CredentialKeeper] Error in setup")

    def read_creds_from_config(self)->Dict:
        try:
            with open(self.config_file, "r") as f:
                creds = json.load(f)
                return creds
        except FileNotFoundError as e:
            logging.error("[CredentialKeeper] Credential Keeper auth_config.json file is not formatted properly or non-existant check: {}".format(self.config_file))
            return None

    def set_creds(self, username, password):
        logging.debug("[CredentialKeeper] setting creds")
        with open(self.dir + "pass.bin", 'wb') as f:
            f.write(self.obj.encrypt(password.encode("utf-8")))
        with open(self.dir + "usr.bin", 'wb') as f:
            f.write(self.obj.encrypt(username.encode("utf-8")))

    def get_auth_config(self):
        creds = None
        try:
            with open(self.config_file, "r") as f:
                creds = json.load(f)
        except json.JSONDecodeError as e:
            logging.error("[CredentialKeeper] " + str(e))
        return creds

    def load_from_cache(self)->Tuple:
        logging.debug("[CredentialKeeper] loading from cache")
        obj2 = AES.new(self.key1, AES.MODE_CFB, self.key2)
        with open(self.dir + "pass.bin", 'rb') as f:
            pwd = f.read()
        with open(self.dir + "usr.bin", 'rb') as f:
            usr = f.read()
        try:
            password = obj2.decrypt(pwd).decode("utf-8")
            username = obj2.decrypt(usr).decode("utf-8")
        except UnicodeDecodeError as e:
            logging.error("[CredentialKeeper] " + str(e))

        return (username, password)

    def is_new_config(self)->bool:
        config_exists = os.path.isfile(self.config_file)
        if config_exists:
            creds = self.get_auth_config()
            if "email" not in creds: return False
            if "password" not in creds: return False
            if creds["email"] != "None" and creds["password"] !="None":
                return True
            return False
        else:
            return False

    def get_creds(self):
        logging.debug("[CredentialKeeper] getting creds")
        #obj2 = AES.new(self.key1, AES.MODE_CFB, self.key2)
        pass_exists = os.path.isfile(self.dir + "pass.bin")
        usr_exists = os.path.isfile(self.dir + "usr.bin")
        config_exists = os.path.isfile(self.config_file)
        if self.is_new_config():
            creds = self.get_auth_config()
            if creds["email"] != "None" and creds["password"] != "None":
                #write bin
                self.set_creds(creds["email"], creds["password"])
                return (creds["email"], creds["password"])
        try:
            return self.load_from_cache()
        except FileNotFoundError as e:
            logging.error("[CredentialKeeper] " + str(e))

    def reset_creds(self, username, password):
        logging.debug("[CredentialKeeper] reseting creds")
        pass_exists = os.path.isfile(self.dir + "pass.bin")
        usr_exists = os.path.isfile(self.dir + "usr.bin")
        if pass_exists and usr_exists:
            os.remove(self.dir + "usr.bin")
            os.remove(self.dir + "pass.bin")
        self.set_creds(str(username), str(password))

class Account(Enum):
    admin = '1'
    provider = '2'
    client = '3'

    @classmethod
    def get_account(cls, account):
        for acnt in cls:
            if acnt.name == str(account).lower() or acnt.value == str(account).lower():
                return acnt
        return cls.provider
    
    @classmethod
    def accounts(cls):
        return [acnt for acnt in cls]

class Device(Enum):
    website = '1'
    ios = '2'
    android = '3'
    
    @classmethod
    def get_device(cls, device):
        for dev in cls:
            if dev.name == str(device).lower() or dev.value == str(device).lower():
                return dev
        return cls.ios

    @classmethod
    def device(cls):
        return [dev for dev in cls]

