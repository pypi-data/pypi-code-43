import sys

from auger.api.credentials import Credentials
from .cloud.auth import AugerAuthApi
from .cloud.utils.exception import AugerException


class AugerAuth(object):

    def __init__(self, ctx):
        self.ctx = ctx
        self.credentials = ctx.credentials

    def login(self, username, password, organization, url=None):
        try:
            self.credentials.token = None
            self.credentials.save()

            if url is None:
                url = self.credentials.api_url

            token = AugerAuthApi(self.ctx).login(
                username, password, organization, url)

            self.credentials.token = token
            self.credentials.username = username
            self.credentials.api_url = url
            self.credentials.organization = organization
            self.credentials.save()

            self.ctx.log(
                'You are now logged in on %s as %s.' % (url, username))

        except Exception as exc:
            self.ctx.log(str(exc))

    def logout(self):

        if self.credentials.token is None:
            self.ctx.log('You are not logged in Auger.')
            sys.exit(1)
        else:
            self.credentials.token = None
            self.credentials.api_url = None
            self.credentials.organization = None
            self.credentials.save()
            self.ctx.log('You are logged out of Auger.')

    def whoami(self):
        if self.credentials.token is None:
            self.ctx.log('Please login to Auger...')
            sys.exit(1)
        else:
            self.ctx.log(
                '%s %s %s' % (
                    self.credentials.username,
                    self.credentials.organization,
                    self.credentials.api_url))
