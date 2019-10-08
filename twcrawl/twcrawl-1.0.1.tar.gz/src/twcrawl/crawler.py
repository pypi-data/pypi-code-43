import asyncio
import json
import logging
import sys
from abc import ABC, abstractmethod
from typing import List, TypeVar, Generic, Union, NoReturn, Iterator, Iterable
from sqlalchemy import and_, or_
from .models import session_scope, Session
from .twitter import *

T = TypeVar("T")


class BaseCrawler(ABC, Generic[T]):
    """Abstract base class for all crawlers."""
    timeout_seconds = 15 * 60  # Twitter limits are usually "per 15 minutes"

    def __init__(self, twitter: TwitterClient):
        self.twitter = twitter
        self.queue = asyncio.Queue()

    def schedule(self, job: T) -> None:
        self.queue.put_nowait(job)

    def log(self, msg: str) -> None:
        """Helper to log progress."""
        print("[" + self.__class__.__name__ + "] " + msg)  # temporary solution only

    async def run(self) -> None:
        try:
            await self.__get_and_exec_job()
        except asyncio.QueueEmpty:
            await asyncio.sleep(5)  # <- first, give the other tasks some time
            self.done()
        finally:
            await asyncio.sleep(0)

    @abstractmethod
    def exec(self, job: T) -> None:
        """Implement to execute the crawlers task."""
        pass

    @abstractmethod
    def done(self) -> None:
        """Implement to issue new tasks when all existing tasks are complete."""
        pass

    async def __get_and_exec_job(self):
        """Pulls a job from the queue and executes it. Might raise QueueEmpty exception."""
        job = self.queue.get_nowait()
        try:
            self.exec(job)
            self.queue.task_done()
        except RateLimitError:
            self.log(f"Rate limit reached. Sleep {self.timeout_seconds} seconds…")
            await asyncio.sleep(self.timeout_seconds)
            self.queue.put_nowait(job)


class UsersCrawler(BaseCrawler[Union[str, List[int]]]):
    """Crawler to fetch Twitter profiles either by screen name of IDs."""

    def exec(self, job: Union[str, List[int]]) -> None:
        if isinstance(job, str):
            self.__exec_screen_name(job)
        else:
            self.__exec_list_of_ids(job)

    def __exec_screen_name(self, screen_name: str) -> None:
        self.log(f"Crawl user profile of @{screen_name}...")
        with session_scope() as session:
            self.twitter.user(screen_name, session)
            session.commit()

    def __exec_list_of_ids(self, ids: List[int]) -> None:
        assert (len(ids) <= 100)
        self.log(f"Crawl user profiles of {len(ids)} yet unknown accounts...")
        with session_scope() as session:
            self.twitter.users(ids, session)
            session.commit()

    def done(self) -> None:
        # find users without even a screen_name (just empty IDs)
        with session_scope() as session:
            users = session.query(User).filter(User.profile_crawled_at.is_(None)).all()
            self.log(f"Found {len(users)} to crawl...")
            # Twitter API only allows to fetch in blocks of up to 100 IDs
            for n in range(0, len(users), 100):
                block_of_ids = list(map(lambda u: u.id, users[n:n + 100]))
                self.schedule(block_of_ids)


class RelationsCrawler(BaseCrawler[str]):
    """Crawler to fetch all friends of a given Twitter users screen name.

    (Note: A friend in Twitters definition is somebody you follow.)
    """

    def exec(self, screen_name: str) -> None:
        self.log(f"Crawl friends of @{screen_name}...")
        ids = self.twitter.friends_ids(screen_name)
        self.log(f"Found {len(ids)} friends for @{screen_name}.")
        with session_scope() as session:
            user = session.query(User).filter_by(screen_name=screen_name).one()
            user.friends = User.find_or_create(session, ids)
            user.friends_crawled_at = datetime.now()
            session.commit()

    def done(self) -> None:
        with session_scope() as session:
            users = session.query(User).filter(and_(
                User.screen_name.isnot(None),
                User.friends_crawled_at.is_(None),
                User.protected.is_(False)
            )).order_by(
                User.followers_count.desc()
            ).limit(5).all()
            for user in users:
                self.schedule(user.screen_name)
            self.log(f"Added {len(users)} users to the queue.")


class StatusesCrawler(BaseCrawler[str]):
    """Crawler to fetch all statuses (=tweets) by a given Twitter users screen name."""

    def exec(self, screen_name: str) -> None:
        self.log(f"Download tweets for @{screen_name}...")
        with session_scope() as session:
            user = session.query(User).filter_by(screen_name=screen_name).one()
            user.statuses_crawled_at = datetime.now()
            self.twitter.statuses(screen_name, session, since_id=user.most_recent_status_id())
            session.commit()
            self.log(f"Downloaded {len(user.statuses)} tweets for @{screen_name}.")

    def done(self) -> None:
        with session_scope() as session:
            users = session.query(User).filter(and_(
                User.screen_name.isnot(None),
                or_(
                    User.statuses_crawled_at.is_(None),
                    User.statuses_crawled_at < datetime.now() - timedelta(days=5)
                ),
                User.protected.is_(False)
            )).order_by(
                User.followers_count.desc()
            ).limit(1).all()
            for user in users:
                self.schedule(user.screen_name)
                self.log(f"Added @{user.screen_name} users to the queue.")


async def __run_forever(crawler: BaseCrawler) -> None:
    """Internal helper to run a crawler forever with asyncio."""
    while True:
        try:
            await crawler.run()
        except KeyboardInterrupt:
            print("\n --- INTERRUPT SIGNAL RECEIVED --- \n")
            sys.exit(0)
        except:
            logging.error("Unexpected exception occurred!", exc_info=True)
            sys.exit(-1)


async def crawl(args) -> NoReturn:
    """Initiates the crawling process."""
    with open('config.json') as config_file:
        config = json.load(config_file)
        twitter = TwitterClient(config["twitter"])
    users_crawler = UsersCrawler(twitter)
    if args.users:
        for user in args.users:
            users_crawler.schedule(user.strip())
    relations_crawler = RelationsCrawler(twitter)
    statuses_crawler = StatusesCrawler(twitter)
    await asyncio.wait(map(__run_forever, [
        users_crawler,
        relations_crawler,
        statuses_crawler
    ]))
