"""Page objects for Twitter views that require authentication."""

from __future__ import annotations

import re
import time
from datetime import datetime

import log
from selenium.common.exceptions import NoSuchFrameException
from splinter import Browser
from splinter.driver import ElementAPI

from ..models import Credentials
from .base import View
from .mixins import ProfileMixin


class Private(View):  # pylint: disable=abstract-method
    def __init__(
        self,
        browser: Browser,
        *,
        username: str,
        credentials: Credentials,
        goto: bool = True,
    ):
        self.username = username
        self._credentials = credentials
        super().__init__(browser, goto=goto)

    @property
    def _active(self) -> bool:
        return self._browser.url == self._url and not bool(self._signin_link)

    @property
    def _signin_link(self) -> ElementAPI:
        return self._browser.find_by_id("signin-link")


class Profile(ProfileMixin, Private):
    @property
    def _url(self) -> str:
        return f"https://twitter.com/{self.username}"

    def _goto(self) -> Profile:
        log.info(f"Visiting {self._url}")
        self._browser.visit(self._url)
        time.sleep(0.5)

        if not bool(self._signin_link):
            log.info(f"Assuming {self._credentials} is already logged in")
            return self

        if not self._browser.is_text_present("New to Twitter?"):
            log.info("Expanding login form")
            self._signin_link.first.click()
            time.sleep(0.5)

        log.info(f"Submitting credentials for {self._credentials}")
        self._browser.fill("session[username_or_email]", self._credentials.username)
        self._browser.fill("session[password]", self._credentials.password)
        self._browser.find_by_css(".js-submit").click()

        return self

    @property
    def tweets(self) -> int:
        match = re.search(r"([\d.]+)(K?) Tweets", self._browser.html)
        assert match
        count = float(match.group(1))
        if match.group(2):
            count *= 1000
        return int(count)

    @property
    def following(self) -> int:
        link = self._browser.find_link_by_href(f"/{self.username}/following").first
        text = link["title"]
        return int(text.replace(",", ""))

    @property
    def followers(self) -> int:
        link = self._browser.find_link_by_href(f"/{self.username}/followers").first
        text = link["title"]
        return int(text.replace(",", ""))

    @property
    def likes(self) -> int:
        log.critical("TODO: determine number of likes")
        return 0

    @property
    def joined(self) -> datetime:
        match = re.search(r"Joined ([A-Z][a-z]+ \d+)", self._browser.html)
        assert match
        return datetime.strptime(match.group(1), "%B %Y")

    def more(self) -> ProfileMore:
        self._browser.find_by_css('[aria-label="More"]').click()
        return ProfileMore(
            self._browser,
            username=self.username,
            credentials=self._credentials,
            goto=False,
        )


class ProfileMore(Private):
    @property
    def _url(self) -> str:
        return f"https://twitter.com/{self.username}"

    @property
    def _active(self) -> bool:
        return self._browser.url == self._url and self._browser.is_text_present(
            "Add/remove from Lists"
        )

    def _goto(self) -> ProfileMore:
        return Profile(
            self._browser, username=self.username, credentials=self._credentials
        ).more()

    def block(self) -> ProfileBlock:
        self._browser.find_by_text(f"Block @{self.username}").click()
        return ProfileBlock(
            self._browser,
            username=self.username,
            credentials=self._credentials,
            goto=False,
        )

    def report(self) -> ProfileReport:
        self._browser.find_by_text(f"Report @{self.username}").click()
        return ProfileReport(
            self._browser,
            username=self.username,
            credentials=self._credentials,
            goto=False,
        )


class ProfileBlock(Private):
    @property
    def _url(self) -> str:
        return f"https://twitter.com/{self.username}"

    @property
    def _active(self) -> bool:
        return self._browser.url == self._url and self._browser.is_text_present(
            "They will not be able to follow you"
        )

    def _goto(self) -> ProfileBlock:
        return ProfileMore(
            self._browser, username=self.username, credentials=self._credentials
        ).block()

    def cancel(self) -> Profile:
        self._browser.find_by_text("Cancel").click()
        return Profile(
            self._browser,
            username=self.username,
            credentials=self._credentials,
            goto=False,
        )

    def block(self) -> Profile:
        self._browser.find_by_text("Block").click()
        return Profile(
            self._browser,
            username=self.username,
            credentials=self._credentials,
            goto=False,
        )


class ProfileReport(Private):
    @property
    def _url(self) -> str:
        return NotImplemented

    @property
    def _active(self) -> bool:
        try:
            with self._browser.get_iframe(0) as iframe:
                return iframe.is_text_present(
                    "Help us understand the problem", wait_time=5
                )
        except NoSuchFrameException:
            return False

    def _goto(self) -> ProfileReport:
        return ProfileMore(
            self._browser, username=self.username, credentials=self._credentials
        ).report()

    def cancel(self) -> Profile:
        self._browser.find_by_css('[aria-label="Back"]').click()
        return Profile(
            self._browser,
            username=self.username,
            credentials=self._credentials,
            goto=False,
        )
