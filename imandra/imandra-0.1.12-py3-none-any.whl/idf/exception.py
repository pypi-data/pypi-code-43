import json

class PyiplError(Exception):
    def __init__(self, *args, **kwargs):
        self.text = args[0]
        super(PyiplError, self).__init__(*args, **kwargs)
    def __repr__(self):
        return str(self.text)

class ErrorDecodingJSON(PyiplError):
    pass
class ErrorConvertingRegionToPython(PyiplError):
    pass
class PyiplRequestError(PyiplError):
    pass
class ErrorProcessingDeclaredTypes(PyiplError):
    pass
class ErrorProcessingExpressions(PyiplError):
    pass
class ErrorProcessingStateClass(PyiplError):
    pass
class ErrorProcessingActionReceive(PyiplError):
    pass
class IPLError(PyiplError):
    pass
class JobStatusError(PyiplError):
    pass
class GSBucketAccessError(PyiplError):
    pass
class InvalidJSON(PyiplError):
    pass

errdict = \
  { "ErrorDecodingJSON"               : ErrorDecodingJSON
  , "ErrorConvertingRegionToPython"   : ErrorConvertingRegionToPython
  , "PyiplRequestError"               : PyiplRequestError
  , "ErrorProcessingDeclaredTypes"    : ErrorProcessingDeclaredTypes
  , "ErrorProcessingExpressions"      : ErrorProcessingExpressions
  , "ErrorProcessingStateClass"       : ErrorProcessingStateClass
  , "ErrorProcessingActionReceive"    : ErrorProcessingActionReceive
  , "IPLError"                        : IPLError
  , "JobStatusError"                  : JobStatusError
  , "GSBucketAccessError"             : GSBucketAccessError
  }


def process_errors(responce):

    if responce.ok:
        return responce.text

    try:
        err = json.loads(responce.text)
    except:
        raise InvalidJSON("API Server returned invalid JSON: " + responce.text)
   
    if err.get("error") == "ipl-gen":
        raise IPLError(err.get("body"))
            
    if err.get("error") == "py-to-ipl":
        err = err.get("body", {})
        
    etype = err.get("ErrorType", "")
    text = err.get("ErrorBody", "")
    ex = errdict.get(etype, PyiplError)
    raise ex(text)
