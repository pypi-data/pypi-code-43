class RequestError(RuntimeError):
    
    def __init__(self, res):
        super(RequestError, self).__init__(res["message"])
