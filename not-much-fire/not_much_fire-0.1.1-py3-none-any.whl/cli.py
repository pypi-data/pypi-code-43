import click

from not_much_fire.cache import Cache
from not_much_fire.database import Database
from not_much_fire.notifier import Notifier

_APP_NAME = "not-much-fire"


@click.command()
@click.option(
    "--notmuch-query",
    help="Used to query the unread messages from the Notmuch database",
    type=str,
    default="is:unread and is:inbox",
    show_default=True,
    metavar="<query>",
)
def main(notmuch_query: str):
    """A simple Notmuch notification tool.

    Requests Notmuch for new unread messages and send notifications to
    the desktop environment. Already notified messages get not shown
    again for a whole day. If they remain unread, they get are handled
    again on the next day.
    """

    cache = Cache(_APP_NAME)
    database = Database(cache, notmuch_query)
    notifier = Notifier(_APP_NAME)

    for message in database.filtered_messages:
        notifier.notify_message(message)

    cache.update()
