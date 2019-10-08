from contextlib import contextmanager
from typing import List, Optional
from sqlalchemy import Boolean, BigInteger, create_engine, Column, DateTime, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import NoResultFound

Base = declarative_base()
engine = create_engine('sqlite:///data/twitter.sqlite3')
Session = sessionmaker(bind=engine)

user_relationship = Table(
    'user_relationship', Base.metadata,
    Column('followee_user_id', Integer, ForeignKey("user.id"), primary_key=True),
    Column('follower_user_id', Integer, ForeignKey("user.id"), primary_key=True)
)


class User(Base):
    """ORM entity to store Twitter users."""
    __tablename__ = "user"
    id = Column(BigInteger, primary_key=True)
    name = Column(String(250))
    screen_name = Column(String(250))
    description = Column(Text)
    location = Column(Text)
    url = Column(Text)
    protected = Column(Boolean)
    verified = Column(Boolean)
    friends_count = Column(Integer)
    followers_count = Column(Integer)
    listed_count = Column(Integer)
    statuses_count = Column(Integer)
    favourites_count = Column(Integer)
    created_at = Column(DateTime)
    profile_crawled_at = Column(DateTime)
    friends_crawled_at = Column(DateTime)
    friends = relationship(
        "User",
        secondary=user_relationship,
        primaryjoin=id == user_relationship.c.followee_user_id,
        secondaryjoin=id == user_relationship.c.follower_user_id,
        backref="followers"
    )
    statuses_crawled_at = Column(DateTime)
    statuses = relationship(
        "Status",
        primaryjoin="User.id==Status.author_user_id",
        backref="author",
        order_by="desc(Status.id)"
    )

    def most_recent_status_id(self) -> Optional[int]:
        """Fetches the ID of the most recent status of the user or returns None otherwise."""
        if len(self.statuses) > 0:
            return self.statuses[0].id
        else:
            return None

    @staticmethod
    def find_or_create(session: Session, ids: List[int]) -> List["User"]:
        """Fetches all users with the given IDs or creates new ones."""
        users = list()
        for user_id in ids:
            try:
                user = session.query(User).filter_by(id=user_id).one()
            except NoResultFound:
                user = User(id=user_id)
                session.add(user)
            users.append(user)
        return users


class Status(Base):
    """ORM entity to store any Tweet posted by a user in our database."""
    __tablename__ = "status"
    id = Column(BigInteger, primary_key=True)
    author_user_id = Column(BigInteger, ForeignKey('user.id'))
    text = Column(Text)
    in_reply_to_status_id = Column(BigInteger, ForeignKey("status.id"))
    retweet_count = Column(Integer)
    favorite_count = Column(Integer)
    created_at = Column(DateTime)


def init_models():
    """Creates the required database file and tables."""
    Base.metadata.create_all(engine)


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
