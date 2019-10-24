# pylint: disable=unused-argument,unused-variable,expression-not-assigned,no-member

import pytest
from freezegun import freeze_time

from ..models import Account, Credentials


def describe_credentials():
    @pytest.fixture
    def credendials():
        return Credentials("username", "password")

    def describe_repr():
        def it_hides_password(expect, credendials):
            expect(
                repr(credendials)
            ) == "Credentials(username='username', password=▒▒▒▒▒▒▒▒)"

    def describe_str():
        def it_includes_username(expect, credendials):
            expect(str(credendials)) == "@username"


def describe_account():
    @pytest.fixture
    def account():
        return Account("foobar")

    def describe_init():
        def it_defaults_to_now_for_joined(expect, account):
            expect(account.datafile.data) == {
                "tweets": 0,
                "following": 0,
                "followers": 0,
                "likes": 0,
                "joined": "2006-03-21T00:00:00",
            }

        def it_handles_existing_isoformat_joined_strings(expect, account):
            account.joined = "2006-03-21T01:02:03"
            expect(account.datafile.data) == {
                "tweets": 0,
                "following": 0,
                "followers": 0,
                "likes": 0,
                "joined": "2006-03-21T01:02:03",
            }

    def describe_str():
        @freeze_time("2019-09-29")
        def it_computes_tweet_rate(expect, account):
            expect(str(account)) == (
                "@foobar is 13.52 years old "
                "and has tweeted 0 times "
                "at a rate of 0.0 tweets/hour with 0 followers"
            )
