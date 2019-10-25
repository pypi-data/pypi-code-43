"""class: DockerHubAPI"""
import click
from requests import post, Request, Session

from . import log_printer as log
from .errors import AuthenticationError, RequestError


class DockerhubApi():
    """handle all interactions with the DockerHub API"""
    def __init__(self):
        self.token = None
        while self.token is None:
            log.notify("log in to DockerHub")

            try:
                token = self.get_token()
            except AuthenticationError as err:
                log.error("logging into DockerHub", err.message)
            else:
                self.token = token
                log.success("logged in to DockerHub")


    def authenticated_request(self, method, endpoint, data=None):
        """makes http requests to the DockerHub API"""
        session = Session()
        req = Request(
            method,
            url="https://hub.docker.com/v2/{}".format(endpoint),
            headers={"Authorization": "Bearer {}".format(self.token)},
        )
        prepped = req.prepare()
        if data:
            prepped.data = data
        res = session.send(prepped)
        return res.json()


    @staticmethod
    def get_token() -> str:
        """get DockerHub API key"""
        username = click.prompt(
            log.indent("username", 1),
            type=str,
        )
        password = click.prompt(
            log.indent("password", 1),
            hide_input=True,
            type=str,
        )
        token_request = post(
            "https://hub.docker.com/v2/users/login",
            data={
                "username": username,
                "password": password,
            }
        )

        if token_request.status_code != 200:
            raise AuthenticationError('Dockerhub authentication failed')

        token_response = token_request.json()
        if "token" not in token_response:
            raise AuthenticationError('no token receieved during Dockerhub authentication')

        token = token_response["token"]  # type: str
        return token


    def tags(self, org, repo):
        """pull all tags from a repo"""
        tag_request = self.authenticated_request(
            "GET",
            "repositories/{}/{}/tags".format(org, repo),
        )
        if not "results" in tag_request:
            raise RequestError("DockerHub tag request returned no results")
        return tag_request["results"]
