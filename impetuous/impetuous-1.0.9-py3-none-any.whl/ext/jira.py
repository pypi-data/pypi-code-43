import asyncio
import logging

import attr

from impetuous.ext import API, SECRET, LudicrousConditions, Submission

logger = logging.getLogger(__name__)


@attr.s(frozen=True)
class Jira(API):

    identifier = 'jira'
    pattern = attr.ib()
    server = attr.ib()
    basic_auth = attr.ib(metadata={SECRET: True},
                         converter=lambda value: tuple(value.split(':', 1)))

    def discover(self, impetuous, *entries):
        for entry in entries:
            for issuekey in self.discover_by_pattern(entry, self.pattern):
                yield entry, Submission(issuekey, {
                    'started': entry.start.strftime('%Y-%m-%dT%H:%M:%S.000%z'),
                    'timeSpentSeconds': entry.duration_in_minutes * 60,
                    'comment': entry.comment,
                })

    async def agent(self, impetuous):
        return JiraHttpAgent(self)


class JiraHttpAgent(object):

    session_params = {}

    def __init__(self, api):
        import aiohttp
        self.api = api
        session_params = dict(auth=aiohttp.BasicAuth(*api.basic_auth))
        session_params.update(self.session_params)
        self.sess = aiohttp.ClientSession(**session_params)
        self.close = self.sess.close

    async def submit(self, sub):
        import aiohttp
        where = self.api.server + '/rest/api/2/issue/{}/worklog'.format(sub.key)
        resp = await self.sess.post(where, json=sub.data, params={'notifyUsers': 'false'})
        try:
            resp.raise_for_status()
        except aiohttp.ClientError as e:
            raise LudicrousConditions(f"Error response from {resp.request_info.url}", e)
        else:
            return await resp.json()

@attr.s
class JiraOverUnix(Jira):
    """Only used in testing ..."""

    socket = attr.ib()

    async def agent(self, impetuous):
        import aiohttp
        class JiraOverUnixHttpAgent(JiraHttpAgent):
            session_params = {
                "connector": aiohttp.UnixConnector(path=self.socket)
            }
        return JiraOverUnixHttpAgent(self)

