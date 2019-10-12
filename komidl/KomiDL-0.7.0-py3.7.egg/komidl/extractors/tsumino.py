# KomiDL - A gallery downloader
# Copyright (C) 2019 DNSheng
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
"""This module contains the Tsumino extractor class"""

import re
import json

from urllib.parse import quote
import requests

from komidl.exceptions import ExtractorFailed
from .extractor import Extractor


class TsuminoEX(Extractor):
    """
    An extractor for Tsumino.com

    Unfortunately, this website tracks requests based on galleries and will
    require the completion of captcha. As a result, the user will have to
    manually visit the website every ~4 galleries.

    All galleries hosted appear to be in English and use JPGs.
    """
    def __init__(self):
        super().__init__()
        self.name = "Tsumino"
        self.url = "https://www.tsumino.com"
        self._PAGE_PATTERN = r"https?://(?:www\.)?tsumino\.com.*"
        self._GALLERY_PATTERN = (r"https?://(?:www\.)?tsumino\.com/"
                                 r"[Bb]ook/[Ii]nfo/[0-9]+/[^/]+/?")
        self._IMG_DOMAIN = "https://www.tsumino.com/Image/Object?name="
        requests.packages.urllib3.disable_warnings()

    # =========================================================================
    # Testing
    # =========================================================================
    # pylint: disable=line-too-long,unused-variable
    def get_tests(self):
        tests = ({"url": "http://www.tsumino.com/Book/Info/47994/ntr-kanojo-case-2-netosis-kasumi-haruno-",
                  "img_urls": ["https://www.tsumino.com/Image/Object?name=oJapP/7ab2WGMB0hU7/EcQ%3D%3D",
                               "https://www.tsumino.com/Image/Object?name=lFj0PpwnCjwMyKErxQ6n/Q%3D%3D",
                               "https://www.tsumino.com/Image/Object?name=cSvIijGcmYwDnEAsy/uZlw%3D%3D",
                               "https://www.tsumino.com/Image/Object?name=Fcag3NPrMNr426l%2B4fXzFA%3D%3D",
                               "https://www.tsumino.com/Image/Object?name=LzP9VveY3F0Y42syY9qw7g%3D%3D"
                               ],
                  "size": 29,
                  "tags": {"Title": "NTR Kanojo Case. 2: NetoSis -Kasumi Haruno-",
                           "URL": "http://www.tsumino.com/Book/Info/47994/ntr-kanojo-case-2-netosis-kasumi-haruno-",
                           "Group": "Vpan's EXTASY",
                           "Artists": "Satou Kuuki",
                           "Category": "Doujinshi",
                           "Languages": "English",
                           "Tags": ["Ahegao", "Big Ass", "Blackmail",
                                    "Bloomers", "Blowjob", "Condom",
                                    "Cosplay", "Crossdressing",
                                    "Crotchless / Breastless"]}},
                 )

    # =========================================================================
    # Getters
    # =========================================================================

    @staticmethod
    def _get_title(soup):
        raw_title = soup.title.string
        # Remove the " | Tsumino" bit
        index = [pos for pos, char in enumerate(raw_title) if char == "|"][-1]
        full_title = raw_title[0:index].strip()
        # Note: Format goes: Romaji | English | Japanese
        # Sometimes the English doesn't exist, so Romaji becomes English
        romaji = full_title.split("|")[0].strip()
        # Note the second value is Japanese (eng, jpn = romaji.split('/'))
        english, _ = romaji.split("/")
        return english.strip()

    @staticmethod
    def _get_gallery_id(url):
        if url[-1] == "/":
            return url.split("/")[-3]
        return url.split("/")[-2]

    def get_size(self, url, soup, args):
        size_element = soup.find("div", {"class": "book-data", "id": "Pages"})
        size = size_element.string.strip()
        return int(size)

    def _get_img_urls(self, id_):
        """A POST operation to retrieve/construct image URLs"""
        referer = f"http://www.tsumino.com/Read/View/{id_}"
        self._session.headers.update({"Referer": referer})
        response = self._session.post("http://www.tsumino.com/Read/Load",
                                      data={'q': id_})
        if response.status_code == 404:
            raise ExtractorFailed("Captcha error - visit the site and "
                                  "complete the captcha or try again later")
        data = json.loads(response.content.decode("utf-8"))
        return [self._format_img_url(url) for url in data["reader_page_urls"]]

    def get_gallery_urls(self, url, soup, args):
        url_list = []
        size = self.get_size(url, soup, args)
        # Length of gallery size for zero-appending filenames
        size_len = len(str(size))
        id_ = self._get_gallery_id(url)
        img_urls = self._get_img_urls(id_)
        for img_num in range(1, size+1):
            base_name = str(img_num).zfill(size_len)
            filename = f"{base_name}.jpg"
            url_list.append([filename, img_urls[img_num-1]])
        return url_list

    def get_tags(self, url, soup, args):
        soup_tags = {"Title": self._get_title(soup), "URL": url}
        soup_tags["Tags"] = self._get_content_tags(soup)
        soup_tags["Category"] = self._get_category_tags(soup)
        soup_tags["Languages"] = "English"
        soup_tags["Artists"] = self._get_artist_tags(soup)
        soup_tags["Group"] = self._get_group_tags(soup)
        soup_tags["Parody"] = self._get_parody_tags(soup)
        soup_tags["Characters"] = self._get_character_tags(soup)
        return soup_tags

    @staticmethod
    def _get_content_tags(soup):
        content = soup.find("meta", {"name": "description"})["content"]
        tags = content.split(":")[-1].split(",")
        return [item.strip() for item in tags]

    @staticmethod
    def _get_category_tags(soup):
        return soup.find("a", {"data-type": "Category"})["data-define"]

    @staticmethod
    def _get_artist_tags(soup):
        artist_list = soup.find_all("a", {"data-type": "Artist"})
        return [artist["data-define"] for artist in artist_list]

    @staticmethod
    def _get_group_tags(soup):
        if soup.find("a", {"data-type": "Group"}):
            group_list = soup.find_all("a", {"data-type": "Group"})
            return [group["data-define"] for group in group_list]
        return []

    @staticmethod
    def _get_parody_tags(soup):
        if soup.find("a", {"data-type": "Parody"}):
            parody_tag = soup.find("a", {"data-type": "Parody"})
            return parody_tag["data-define"]
        return []

    @staticmethod
    def _get_character_tags(soup):
        if soup.find("a", {"data-type": "Character"}):
            char_list = soup.find_all("a", {"data-type": "Character"})
            return [char["data-define"] for char in char_list]
        return []

    # ===============================================================================
    # Misc. functions
    # ===============================================================================

    def _format_img_url(self, url):
        clean_url = quote(url)
        return f"{self._IMG_DOMAIN}{clean_url}"
