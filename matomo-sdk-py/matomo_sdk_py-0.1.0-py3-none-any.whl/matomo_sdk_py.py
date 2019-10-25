import requests
SKIP_PING=False
def ping_matomo(action_name, action_base, idsite, uuid_val, matomo_url):
  """
  Gather anonymous usage statistics

  action_name - same field in matomo
  action_base - website URL in matomo, e.g. https://example.com
  idsite - integer representing ID of website in matomo
  uuid_val - matomo field "uid"
  matomo_url - URL of matomo host, eg https://example.matomo.cloud
  """
  # if any previous failure, just skip it completely
  global SKIP_PING # http://stackoverflow.com/questions/423379/ddg#423596 
  if SKIP_PING:
      return

  from urllib.parse import urljoin, urlencode

  # build action url
  # https://stackoverflow.com/questions/9718541/reconstructing-absolute-urls-from-relative-urls-on-a-page#comment51058834_9718651
  action_url = urljoin(action_base, action_name)

  # https://stackoverflow.com/a/39144239/4126114
  req_i = {
    "idsite": idsite,
    "rec": 1,
    "action_name": action_name,
    "uid": uuid_val,
    "url": action_url
  }
  payload = {"requests": ["?"+urlencode(req_i)]}

  # use POST instead of GET to avoid arguments showing up in the clear
  # https://developer.matomo.org/api-reference/tracking-api
  try:
    response = requests.post(matomo_url, json=payload, timeout=1) # 1 second
  except requests.exceptions.ConnectionError as error:
    # just ignore the failure to connect
    # in order not to obstruct the CLI
    SKIP_PING=True
    pass
  except requests.exceptions.ReadTimeout as error:
      # also ignore
      SKIP_PING=True
      pass

