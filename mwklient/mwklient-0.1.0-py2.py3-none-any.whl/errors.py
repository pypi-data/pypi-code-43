class MwKlientError(RuntimeError):
    pass


class MediaWikiVersionError(MwKlientError):
    pass


class APIDisabledError(MwKlientError):
    pass


class MaximumRetriesExceeded(MwKlientError):
    pass


class APIError(MwKlientError):

    def __init__(self, code, info, kwargs):
        self.code = code
        self.info = info
        super(APIError, self).__init__(code, info, kwargs)


class InsufficientPermission(MwKlientError):
    pass


class UserBlocked(InsufficientPermission):
    pass


class EditError(MwKlientError):
    pass


class ProtectedPageError(EditError, InsufficientPermission):

    def __init__(self, page, code=None, info=None):
        super(ProtectedPageError, self).__init__()
        self.page = page
        self.code = code
        self.info = info

    def __str__(self):
        if self.info is not None:
            return self.info
        return 'You do not have the "edit" right.'


class FileExists(EditError):
    pass


class LoginError(MwKlientError):

    def __init__(self, site, code, info):
        super(LoginError, self).__init__(
            site,
            {'result': code, 'reason': info}  # For backwards-compability
        )
        self.site = site
        self.code = code
        self.info = info

    def __str__(self):
        return self.info


class OAuthAuthorizationError(LoginError):
    pass


class AssertUserFailedError(MwKlientError):

    def __init__(self):
        super(AssertUserFailedError, self).__init__(
            'By default, mwklient protects you from accidentally editing '
            'without being logged in. If you actually want to edit without '
            'logging in, you can set force_login on the Site object to False.'
        )

    def __str__(self):
        return self.args[0]


class EmailError(MwKlientError):
    pass


class NoSpecifiedEmail(EmailError):
    pass


class NoWriteApi(MwKlientError):
    pass


class InvalidResponse(MwKlientError):

    def __init__(self, response_text=None):
        super(InvalidResponse, self).__init__(
            'Did not get a valid JSON response from the server. Check that '
            'you used the correct hostname. If you did, the server might '
            'be wrongly configured or experiencing temporary problems.',
            response_text
        )
        self.response_text = response_text

    def __str__(self):
        return self.args[0]


class InvalidPageTitle(MwKlientError):
    pass
