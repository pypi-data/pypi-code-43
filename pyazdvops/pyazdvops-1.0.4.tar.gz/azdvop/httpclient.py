import requests, logging, json, redis, datetime, base64, dateutil.parser, time
from requests.auth import HTTPBasicAuth

logger = logging.getLogger(__name__)

class HttpRedis:
  client = None
  expiry = 1

  def __init__(self, host = 'localhost', port = 6379, password = None, expiry = 1):
    self.client = redis.Redis(host=host, port=port, password=password)
    self.expiry = expiry
  
  def checksum(self, *obj):
    return reduce(lambda x,y : x^y, [hash(item) for item in obj])

  def get(self, url, body = None):
    checksum = self.checksum(url, body)
    r = self.client.get(checksum)
    if r:
      logger.debug('HIT from cache')
      return r
    else:
      return None

  def save(self, url, response, body = {}):
    checksum = self.checksum(url, body)
    expiry = datetime.timedelta(hours=self.expiry)
    self.client.set(checksum, response, ex = expiry)

class Response:
  headers = {}
  payload = None

  def __init__(self, headers = {}, payload = None):
    self.headers = headers
    self.payload = payload

class HttpClient:
  error_codes = [203, 400, 401, 403, 404, 500]
  auth = None
  redis_client = HttpRedis()
  cache_expire_hours = 1

  def __init__(self, pat):
    omitted = pat[:5]
    for i in range(len(pat) - 5):
      omitted = omitted + '*'
    logger.debug('Initializing with pat {omitted}'.format(omitted = omitted))
    self.auth = HTTPBasicAuth('', pat)
  
  def set_redis(self, redis_client, expiry_hour):
    self.redis_client = redis_client
    self.cache_expire_hours = expiry_hour
  
  def get_redis(self, checksum):
    if self.redis_client is None:
      return None

    r = self.redis_client.get(checksum)
    if r:
      r = json.loads(r)
      expiry_date = dateutil.parser.parse(r['expiry'])
      now_date = datetime.datetime.now()
      expiry = time.mktime(expiry_date.timetuple())
      now = time.mktime(now_date.timetuple())

      if ((now - expiry)/3600) > 1:
        logger.debug('MISS from cache.')
        self.redis_client.delete(checksum)
        return None
      logger.debug('HIT from cache.')
    else:
      logger.debug('MISS from cache.')
    return r

  def set_redis(self, response, checksum):
    expiry = datetime.datetime.now() + datetime.timedelta(hours=1)
    headers = {}
    for key in response.headers:
      headers[key] = base64.b64encode(response.headers[key])
    r = {
      'headers': headers,
      'payload': response.text,
      'expiry': expiry.strftime('%Y%m%d%H%M%S')
    }
    if self.redis_client is not None:
      self.redis_client.set(checksum, json.dumps(r))
    return r

  def handle_response(self, response):
    if response.status_code in self.error_codes:
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
      return Response(response.headers, response.text)

  def do_get(self, url, headers = {}):
    r = requests.get(url, auth = self.auth)
    return self.handle_response(r)

  def get(self, url, headers = {}, cache = True):
    logger.debug('GET ' + url + ', Headers: ' + json.dumps(headers))

    if cache:
      r = self.redis_client.get(url)
      if r is None:
        r = self.do_get(url, headers)
        self.redis_client = HttpRedis()
        self.redis_client.save(url, r.payload)
      return r
    else:
      return self.do_get(url, headers)

  def do_post(self, url, body, headers = {}):
    r = requests.post(url, auth = self.auth, headers=headers, data=json.dumps(body))
    r = self.handle_response(r)
    return Response(r.headers, r.text)

  def post(self, url, body, headers = {}, cache = False):
    logger.debug('POST ' + url + ', Headers: ' + json.dumps(headers) + ', Body: ' + json.dumps(body))
    if cache:
      checksum = self.calculate_hash({
        'url': url,
        'body': body
      })
      r = self.get_redis(checksum)
      if r is None:
        r = self.do_post(url, body, headers)
        r = self.set_redis(r, checksum)
    else:
      return self.do_post(url, body, headers)

  def patch(self, url, body, headers = {}):
    logger.debug('PATCH {}, Headers: {}, Body: {}'.format(url, json.dumps(headers), json.dumps(body)))
    r = requests.patch(url, auth = self.auth, headers = headers, data = json.dumps(body))
    return self.handle_response(r)