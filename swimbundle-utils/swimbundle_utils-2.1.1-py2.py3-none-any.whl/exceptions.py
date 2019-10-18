

class SwimlaneIntegrationException(Exception):
    """Thrown when an Exception in a Swimlane task is expected"""
    pass


class SwimlaneIntegrationAuthException(SwimlaneIntegrationException):
    """Thrown when an Exception in a Swimlane auth task is expected"""
    pass

