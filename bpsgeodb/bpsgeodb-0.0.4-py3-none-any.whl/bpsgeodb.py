import sys
import os
import http.client
import json
from time import time


class ApiService:
  def __init__(self):
    self.__access_token = ""
    self.__tokenttl = int(time())
    self.__authorization_host = os.getenv("BPS_AUTH_HOST")
    self.__api_host = os.getenv("BPS_API_HOST")
    self.__client_id = os.getenv("BPS_CLIENT_ID")
    self.__client_secret = os.getenv("BPS_CLIENT_SECRET")
    self.__audience = os.getenv("BPS_API_AUDIENCE")
    self.__api_version = os.getenv("BPS_API_VERSION")
    try:
      self.assert_initialization()
    except AssertionError as error:
      print(error)
      print("please set your BPS env variables")
      raise Exception("Can not continue without all initialization conditions are met") 
    self.__payload = json.dumps({ 
      "client_id": self.__client_id,
      "client_secret": self.__client_secret,
      "audience": self.__audience,
      "grant_type": "client_credentials"
    })

  def assert_initialization(self):
    assert (self.__authorization_host), "missing BPS_AUTH_HOST"
    assert (self.__api_host), "missing BPS_AUTH_HOST"
    assert (self.__client_id), "missing BPS_CLIENT_ID"
    assert (self.__client_secret), "missing BPS_CLIENT_SECRET"
    assert (self.__audience), "missing BPS_API_AUDIENCE"
    assert (self.__api_version), "missing BPS_API_VERSION"

  def authorize(self):
    headers = { 'content-type': "application/json" }
    conn = http.client.HTTPSConnection(self.__authorization_host)
    conn.request("POST", "/oauth/token", self.__payload, headers)
    data = self.assert_response(conn.getresponse())
    token = json.loads(data.decode("utf-8"))
    conn.close()
    assert ("access_token" in token), "Could not get access token" + token
    self.__access_token = token["access_token"]
    self.settokenttl(token["expires_in"])

  def settokenttl(self,seconds):
    self.__token_ttl = int(time()) + seconds

  def token_expired(self):
    return self.__token_ttl < int(time())

  def assert_response(self,response):
    res_status = "%s " % response.status
    res_status += response.reason
    assert (response.status == 200) , res_status
    return response.read()

  def getData(self,endpoint):
    if self.token_expired():
      self.authorize()
    headers = { 'authorization': "Bearer " + self.__access_token }
    conn = http.client.HTTPSConnection(self.__api_host)
    request_endpoint = "/geodb_api/" + self.__api_version + "/" + endpoint
    conn.request("GET", request_endpoint, headers=headers)
    data = self.assert_response(conn.getresponse())
    return json.loads(data.decode("utf-8"))
    

