from splinter import Browser

from .models import Account, Blocklist, Credentials
from .views.private import Profile as PrivateProfile
from .views.public import Profile as PublicProfile


def check(browser: Browser, username: str, *, display=print):
    profile = PublicProfile(browser, username=username)
    account = Account.from_profile(profile)
    display(account)


def crawl(browser: Browser, username: str):
    profile = PublicProfile(browser, username=username)
    account = Account.from_profile(profile)
    Blocklist().bots.append(account)  # pylint: disable=no-member


def block(browser: Browser, username: str, password: str, *, display=print):
    # TODO: Implement block command
    credentials = Credentials(username, password)
    profile = PrivateProfile(browser, username=username, credentials=credentials)
    account = Account(username, tweets=profile.tweets)
    display(account)
