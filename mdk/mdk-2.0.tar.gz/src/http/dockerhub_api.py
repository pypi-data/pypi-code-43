"""class: DockerHubAPI"""
from typing import Dict, Mapping

import click

from ..cli import log_printer as log
from ..errors import AuthenticationError, RequestError
from .request  import Connection


class DockerhubApi():
    """handle all interactions with the DockerHub API"""
    def __init__(self):
        self.docker_connection = Connection("hub.docker.com")
        self.bearer_token = None
        while self.bearer_token is None:
            log.notify("log in to DockerHub")

            try:
                self.authenticate()
            except AuthenticationError as err:
                log.error("logging into DockerHub", err.message)
            else:
                log.success("logged in to DockerHub")


    def auth_get(
            self,
            endpoint: str,
            headers: Mapping[str, str] = None):
        """makes authenticated http GET requests to the DockerHub API"""
        if self.bearer_token is None:
            raise AuthenticationError("Tried to access protected endpoint without bearer token.")

        header_builder = {"Authorization": "Bearer {}".format(self.bearer_token)}
        if headers is not None:
            for key, val in headers.items():
                header_builder[key] = val

        reponse, _ = self.docker_connection.get(
            endpoint,
            headers=header_builder,
        )
        return reponse


    def auth_post(
            self,
            endpoint: str,
            body: Dict = None,
            headers: Mapping[str, str] = None):
        """makes authenticated http POST requests to the DockerHub API"""
        if self.bearer_token is None:
            raise AuthenticationError("Tried to access protected endpoint without bearer token.")

        header_builder = {
            "Authorization": "Bearer {}".format(self.bearer_token),
            "Content-Type": "application/json",
        }
        if headers is not None:
            for key, val in headers.items():
                header_builder[key] = val

        reponse, _ = self.docker_connection.post(
            endpoint,
            body=body,
            headers=header_builder
        )
        return reponse


    def authenticate(self):
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

        response, _ = self.docker_connection.post(
            "/v2/users/login",
            body={
                "username": username,
                "password": password,
            },
        )

        if "token" not in response:
            raise AuthenticationError('no token receieved during Dockerhub authentication')

        self.bearer_token = response["token"]


    def tags(self, org: str, repo: str):
        """pull all tags from a repo"""
        tag_request = self.auth_get("/v2/repositories/{}/{}/tags".format(org, repo))
        if not "results" in tag_request:
            raise RequestError("DockerHub tag request returned no results")
        return tag_request["results"]
