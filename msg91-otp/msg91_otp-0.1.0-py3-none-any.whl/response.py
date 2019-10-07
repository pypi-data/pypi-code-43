class ServiceResponse:
    def __init__(self, status, message, **kwargs):
        self.status = status
        self.message = message
        if 'identifier' in kwargs:
            self.identifier = kwargs.get('identifier')

    def __repr__(self):
        return f"<ServiceResponse: {self.status}: {self.message}>"
