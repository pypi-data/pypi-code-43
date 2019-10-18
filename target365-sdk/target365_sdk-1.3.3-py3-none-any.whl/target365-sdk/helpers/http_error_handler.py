class HttpErrorHandler:
  def throwIfNotSuccess(self, response):  
    if (response.status_code < 200) or (response.status_code >= 300):
      self.throwError(response)

  def throwError(self, response):
    message = ""
    try:
      message = response.json()
    except:
      message = response.status_code
    raise HttpError(message)
    

class HttpError(Exception):
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)
