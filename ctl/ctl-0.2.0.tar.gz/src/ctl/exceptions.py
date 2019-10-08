# TODO py3 implements PermissionError, probably extend that?
class PermissionDenied(Exception):
    def __init__(self, grainy_namespace, level):
        super(PermissionDenied, self).__init__(
            "You do not have '{}' permission to this namespace: {}".format(
                level, grainy_namespace
            )
        )


class OperationNotExposed(Exception):
    def __init__(self, op):
        super(OperationNotExposed, self).__init__("{} is not exposed".format(op))


class UsageError(ValueError):
    """
	ctl operation usage error
	"""

    pass


class ConfigError(ValueError):
    pass
