from datetime import datetime
from re import sub
from typing import List

import notmuch
from notmuch import Message

from not_much_fire.cache import Cache


class Database:
    def __init__(self, cache: Cache, notmuch_query: str):
        self.cache = cache
        self.notmuch_query = notmuch_query
        self.database = notmuch.Database()

    @property
    def filtered_messages(self) -> List[Message]:
        """Filter unread messages which have not been notified already.

        Queries Notmuch for unread messages and compare their timestamp
        against the last time notifying messages by the caches state.
        Messages which arrived before this timestamp are considered as
        already notified and therefore part of the returned list.
        """

        unfiltered_messages = notmuch.Query(
            self.database, self.notmuch_query
        ).search_messages()
        messages = []

        for message in unfiltered_messages:
            if self._get_message_date(message) > self.cache.last_update:
                messages.append(message)

        return messages

    def _get_message_date(self, message: Message) -> datetime:
        """Parses the `Date` header field of a message.

        The challenge is to convert the textual timestamp format into a
        internal presentation to make it comparable with the cached
        state.
        """

        date_string_pure = message.get_header("Date")
        date_string = sub("[\\+\\-].*?$", "", date_string_pure).strip()
        date = datetime.strptime(date_string, self.cache.date_format)
        return date
