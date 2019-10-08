import tweepy
from contextlib import contextmanager
from datetime import datetime, timedelta
from email.utils import parsedate_tz
from typing import Dict, List
from twitter import Twitter, OAuth, TwitterHTTPError
from .models import User, Session, Status


class RateLimitError(Exception):
    """Triggered whenever Twitter responds with `rate limit exceeded` message."""
    pass


@contextmanager
def twitter_scope(client):
    """Provide a client scope which automatically handle rate limit exceptions."""
    try:
        yield client
    except TwitterHTTPError as err:
        if err.e.code == 429:
            raise RateLimitError
        else:
            raise err


@contextmanager
def tweepy_scope(client):
    """Provide a Tweepy client scope which automatically handle rate limit exceptions."""
    try:
        yield client
    except tweepy.RateLimitError:
        raise RateLimitError


class TwitterClient:
    def __init__(self, config: Dict[str, str]):
        self.client = Twitter(auth=OAuth(
            config['access_token'],
            config['access_token_secret'],
            config['consumer_key'],
            config['consumer_secret']
        ))
        auth = tweepy.OAuthHandler(
            config['consumer_key'],
            config['consumer_secret']
        )
        auth.set_access_token(
            config['access_token'],
            config['access_token_secret']
        )
        self.tweepy = tweepy.API(auth)

    def user(self, screen_name: str, session: Session) -> User:
        """Fetches the Twitter profile of the given users screen name."""
        with twitter_scope(self.client) as twitter:
            user_obj = twitter.users.show(screen_name=screen_name)
            return self.__to_user(user_obj, session)

    def users(self, ids: List[int], session: Session) -> List[User]:
        """Fetches the Twitter profile of the given list of users IDs."""
        with twitter_scope(self.client) as twitter:
            ids_string = ",".join(str(id) for id in ids)
            try:
                query = twitter.users.lookup(user_id=ids_string)
                return list(map(lambda obj: self.__to_user(obj, session), query))
            except TwitterHTTPError as err:
                if err.e.code == 404:
                    return list(map(lambda user_id: self.__to_deleted_user(user_id, session), ids))
                else:
                    raise

    def friends_ids(self, screen_name: str) -> List[int]:
        """Fetches the IDs of the givens screen names friends on Twitter."""
        with twitter_scope(self.client) as twitter:
            try:
                query = twitter.friends.ids(screen_name=screen_name)
                return query["ids"]
            except TwitterHTTPError as err:
                if err.e.code == 404 or err.e.code == 401:
                    return list()
                else:
                    raise

    def statuses(self, screen_name: str, session: Session, since_id: int = None) -> List[Status]:
        try:
            return self.__get__statuses(screen_name, session, since_id)
        except tweepy.TweepError as err:
            if err is not None and err.response is not None and (err.response.status_code == 404 or err.response.status_code == 401):
                return list()
            else:
                raise

    def __get__statuses(self, screen_name: str, session: Session, since_id) -> List[Status]:
        with tweepy_scope(self.tweepy) as api_endpoint:
            cursor = tweepy.Cursor(
                api_endpoint.user_timeline,
                screen_name=screen_name,
                count=200,
                tweet_mode="extended",
                since_id=since_id
            )
            return list(map(lambda obj: self.__to_status(obj, session), cursor.items()))

    def __to_user(self, obj, session: Session) -> User:
        """Converts the Twitters JSON object to a User models."""
        user = session.query(User).filter(User.id == obj["id"]).one_or_none()
        if user is None:
            user = User(id=obj["id"])
            session.add(user)
        user.name = obj["name"]
        user.screen_name = obj["screen_name"]
        user.description = obj["description"]
        user.location = obj["location"]
        user.url = obj["url"]
        user.protected = obj["protected"]
        user.verified = obj["verified"]
        user.friends_count = obj["friends_count"]
        user.followers_count = obj["followers_count"]
        user.listed_count = obj["listed_count"]
        user.statuses_count = obj["statuses_count"]
        user.favourites_count = obj["favourites_count"]
        user.created_at = self.__to_datetime(obj["created_at"])
        user.profile_crawled_at = datetime.now()
        return user

    def __to_deleted_user(self, user_id: int, session: Session) -> User:
        """Stores the passed ID as an ID of a deleted user in the database."""
        user = session.query(User).filter(User.id == user_id).one_or_none()
        if user is None:
            user = User(id=user_id)
            session.add(user)
        user.screen_name = None
        user.profile_crawled_at = datetime.now()
        return user

    def __to_status(self, obj, session: Session) -> Status:
        status = session.query(Status).filter(Status.id == obj.id).one_or_none()
        if status is None:
            status = Status(id=obj.id)
            session.add(status)
        status.author_user_id = obj.author.id
        status.created_at = obj.created_at
        status.text = obj.full_text
        status.in_reply_to_status_id = obj.in_reply_to_status_id
        status.retweet_count = obj.retweet_count
        status.favorite_count = obj.favorite_count
        return status

    def __to_datetime(self, val: str) -> datetime:
        time_tuple = parsedate_tz(val.strip())
        dt = datetime(*time_tuple[:6])
        return dt - timedelta(seconds=time_tuple[-1])
