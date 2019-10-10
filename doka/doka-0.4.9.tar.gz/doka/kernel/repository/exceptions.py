class RepositoryException(Exception):
    _message = None

    def __init__(self):
        super().__init__(self._message)


class EntityExistsException(RepositoryException):
    _message = "Entity exists"


class EntityNotExistsException(RepositoryException):
    _message = "Entity not exists"
