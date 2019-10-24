from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, List

from datafiles import converters, datafile


if TYPE_CHECKING:
    from .views.public import Profile


@dataclass
class Credentials:
    username: str
    password: str

    def __str__(self) -> str:
        return f"@{self.username}"

    def __repr__(self) -> str:
        masked = "▒" * len(self.password)
        return f"Credentials(username={self.username!r}, password={masked})"


@datafile("../data/accounts/{self.username}.yml", defaults=True)
class Account:
    username: str
    tweets: int = 0
    following: int = 0
    followers: int = 0
    likes: int = 0
    joined: datetime = datetime(year=2006, month=3, day=21)

    @classmethod
    def from_profile(cls, profile: "Profile"):
        return cls(
            username=profile.username,
            tweets=profile.tweets,
            following=profile.tweets,
            followers=profile.followers,
            likes=profile.likes,
            joined=profile.joined,
        )

    def __str__(self) -> str:
        return (
            f"@{self.username}"
            f" is {round(self.account_age_in_years, 2)} years old"
            f" and has tweeted {self.tweets} times"
            f" at a rate of {round(self.tweets_per_hour, 2)} tweets/hour"
            f" with {self.followers} followers"
        )

    @property
    def account_age(self) -> timedelta:
        return datetime.now() - self.joined

    @property
    def account_age_in_hours(self) -> float:
        return self.account_age.total_seconds() / 3600

    @property
    def account_age_in_years(self) -> float:
        return self.account_age_in_hours / 24 / 365.25

    @property
    def tweets_per_hour(self) -> float:
        return self.tweets / self.account_age_in_hours


@datafile("../data/blocklist.json", defaults=True)
class Blocklist:
    bots: List[Account] = field(default_factory=list)


class DateTimeConverter(converters.Converter):
    # pylint: disable=arguments-differ,unused-argument
    @classmethod
    def to_preserialization_data(cls, python_value, **kwargs):
        if isinstance(python_value, datetime):
            return python_value.isoformat()
        return python_value

    @classmethod
    def to_python_value(cls, deserialized_data, **kwargs):
        return datetime.fromisoformat(deserialized_data)


converters.register(datetime, DateTimeConverter)
