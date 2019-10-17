# HTTP Client with Redis!
import logging, json, redis, requests, datetime
from requests.auth import HTTPBasicAuth

logger = logging.getLogger(__name__)
error_codes = [203, 400, 401, 403, 404, 500]

def checksum(*obj):
  return reduce(lambda x,y : x^y, [hash(item) for item in obj])

def handle_response(response):
  if response.status_code in error_codes:
    try:
      logger.critical('Status code: {status_code}, Body: {body}'.format(
        status_code = str(response.status_code),
        body = response.text
      ))
    except UnicodeEncodeError:
      logger.critical(u'Status code: {status_code}, Body: {body}'.format(
        status_code = str(response.status_code),
        body = response.text
      ))
    raise Exception('Failed to perform request.')
  else:
    return response.json()

class HttpClient:
  _auth = HTTPBasicAuth(None, None)
  _redis = redis.Redis()
  _cache_expiry = 1
  
  def __init__(self, pat, redis_host = 'localhost', redis_port = 6379, redis_password = None, cache_expiry = 1):
    omitted = pat[:5]
    for i in range(len(pat) - 5):
      omitted = omitted + '*'
    logging.debug('Initializing client with pat {}'.format(omitted))
    self._auth = HTTPBasicAuth('', pat)
    self._redis = redis.Redis(redis_host, redis_port, password = redis_password)
    self._cache_expiry = cache_expiry
  
  def set_redis(self, host, port, password = None, cache_expiry = 1):
    self._redis = redis.Redis(host, port, password=password)
    self._cache_expiry = cache_expiry

  def get(self, url, headers = {}, cache = True):
    logger.debug('GET {url}, Headers: {headers}'.format(url=url, headers=json.dumps(headers)))
    if cache:
      key = checksum(url)
      response = self._redis.get(key)
      if response:
        return json.loads(response)
    
    response = requests.get(url, auth = self._auth)
    response = handle_response(response)
    if cache and response:
      key = checksum(url)
      self._redis.set(key, json.dumps(response), ex=datetime.timedelta(hours=self._cache_expiry))
    return response
  
  def post(self, url, body, headers = {}, cache = False):
    logger.debug('POST {url}, Headers: {headers}'.format(url = url, headers=json.dumps(headers)))
    if cache:
      key = checksum(url, json.dumps(body))
      response = self._redis.get(key)
      if response:
        return json.loads(response)
    
    response = requests.post(url, auth=self._auth, headers=headers, data=json.dumps(body))
    response = handle_response(response)
    if cache and response:
      key = checksum(url, json.dumps(body))
      self._redis.set(key, json.dumps(response), ex=datetime.timedelta(hours=self._cache_expiry))
    return response

  def patch(self, url, body, headers = {}):
    logger.debug('PATCH {url}, Headers: {headers}'.format(url=url, headers=headers))
    response = requests.patch(url, auth=self._auth, headers=headers,data=json.dumps(body))
    return handle_response(response)
