import datetime
import logging

import attr

from impetuous.ext import API, SECRET, LudicrousConditions, Submission

logger = logging.getLogger(__name__)


@attr.s(frozen=True)
class Freshdesk(API):

    identifier = 'freshdesk'
    pattern = attr.ib()
    server = attr.ib()
    api_key = attr.ib(metadata={SECRET: True})

    def discover(self, impetuous, *entries):
        for entry in entries:
            time_spent = '%02i:%02i' % divmod(entry.duration_in_minutes, 60)
            for ticket_id in self.discover_by_pattern(entry, self.pattern):
                yield entry, Submission(ticket_id, {
                    'time_spent': time_spent,
                    'executed_at': entry.start.astimezone(datetime.timezone.utc).isoformat(),
                    'note': entry.comment,
                    'billable': '[billable]' in entry.comment,  # TODO consider using a tag/text pattern or something
                    'timer_running': not 'if I have anything to do with it',
                })

    async def agent(self, impetuous):
        return FreshdeskHttpAgent(self)


class FreshdeskHttpAgent(object):

    def __init__(self, api):
        import aiohttp
        self.api = api
        self.sess = aiohttp.ClientSession(auth=aiohttp.BasicAuth(self.api.api_key, 'X'))
        self.close = self.sess.close

    async def submit(self, sub):
        import aiohttp
        where = self.api.server + '/api/v2/tickets/{}/time_entries'.format(sub.key)
        resp = await self.sess.post(where, json=sub.data)
        try:
            resp.raise_for_status()
        except aiohttp.ClientResponseError as e:
            raise LudicrousConditions(e, "While submitting to {}: {}".format(resp.request_info.url, await resp.text()))
        else:
            return await resp.json()
