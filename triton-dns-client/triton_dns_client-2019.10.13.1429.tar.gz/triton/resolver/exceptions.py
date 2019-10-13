class GenericResolverException(Exception):
    pass


class NameserversNotFound(GenericResolverException):
    pass


class BadDomainName(GenericResolverException):
    pass


class DomainNotFound(GenericResolverException):
    pass
