"""LICENSE
Copyright 2015 Hermann Krumrey <hermann@krumreyh.com>

This file is part of manga-dl.

manga-dl is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

manga-dl is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with manga-dl.  If not, see <http://www.gnu.org/licenses/>.
LICENSE"""

import re
import json
import cfscrape
from typing import List
from manga_dl.entities.Chapter import Chapter
from manga_dl.scrapers.Scraper import Scraper


class MangaDexScraper(Scraper):
    """
    Scraper for mangadex.org
    """

    @classmethod
    def name(cls) -> str:
        """
        :return: The name of the scraper
        """
        return "mangadex"

    @classmethod
    def url_matches(cls, url: str) -> bool:
        """
        Checks whether or not an URL matches for the scraper
        :param url: The URL to check
        :return: Whether the URL is valid
        """
        return bool(re.match(r"^https://mangadex.org/title/[0-9]+", url))

    def generate_url(self, _id: str) -> str:
        """
        Generates an URL based on an ID
        :param _id: The ID to use
        :return: The generated URL
        """
        return "https://mangadex.org/title/" + _id

    def _load_chapters(self, url: str) -> List[Chapter]:
        """
        Loads the chapters from mangadex.org
        :param url: The URL to scrape
        :return: The chapters found for the series
        """
        scraper = cfscrape.create_scraper()

        mangadex_id = url.split("https://mangadex.org/title/")[1].split("/")[0]
        manga_url = "https://mangadex.org/api/manga/" + str(mangadex_id)

        resp = scraper.get(manga_url)

        if resp.status_code >= 300:
            self.logger.warning("Unsuccessful request ({})"
                                .format(resp.status_code))
            self.logger.debug(resp.text)
            return []

        series_info = json.loads(resp.text)
        series_title = series_info["manga"]["title"]
        chapter_list = series_info.get("chapter", {})

        if self.destination is None:
            destination = series_title
        else:
            destination = self.destination

        chapters = []

        for chapter_id, chapter in chapter_list.items():
            chapter_url = "https://mangadex.org/api/chapter/" + str(chapter_id)
            chapters.append(Chapter(
                chapter_url,
                chapter["lang_code"],
                series_title,
                chapter["chapter"],
                destination,
                self.format,
                self.get_image_pages,
                chapter["title"],
                chapter["group_name"]
            ))

        return chapters

    @staticmethod
    def get_image_pages(_self: Chapter, url: str) -> List[str]:
        """
        Callback method for the Chapter object.
        Loads the correct image URL for a page
        :param _self: The chapter that calls this method
        :param url: The base chapter URL
        :return: The page image URLs
        """
        scraper = cfscrape.create_scraper()
        resp = scraper.get(url)

        if resp.status_code >= 300:
            _self.logger.warning("Unsuccessful request ({})"
                                 .format(resp.status_code))
            _self.logger.debug(resp.text)
            return []

        chapter_info = json.loads(resp.text)
        image_urls = []

        server = chapter_info["server"]
        if server == "/data/":
            server = "CF!https://mangadex.org/data/"  # Cloudflare protected

        chapter_hash = chapter_info["hash"]
        base_url = server + chapter_hash + "/"

        for page in chapter_info["page_array"]:
            image_urls.append(base_url + page)

        return image_urls
