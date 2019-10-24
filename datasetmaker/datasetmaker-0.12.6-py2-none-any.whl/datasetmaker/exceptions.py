class EntityNotFoundException(ValueError):
    """Entity not found"""


class MissingConceptError(ValueError):
    """Value not in concepts"""


class PackageValidationException(ValueError):
    """Base class for DDF package validation errors"""


class PackageInvalidYearException(PackageValidationException):
    """Invalid year"""


class PackageMissingConceptsException(PackageValidationException):
    """No concepts file"""


class PackageInvalidBooleanException(PackageValidationException):
    """Invalid boolean format"""


class PackageInvalidDayException(PackageValidationException):
    """Invalid day format"""


class PackageInvalidDomainConstraint(PackageValidationException):
    """Domain constraint not passed"""
