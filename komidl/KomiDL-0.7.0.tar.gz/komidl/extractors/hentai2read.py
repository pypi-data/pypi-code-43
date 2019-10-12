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
"""This module contains the Hentai2Read extractor class"""

import os
import re

from komidl.exceptions import ExtractorFailed

from .extractor import Extractor


class Hentai2ReadEX(Extractor):
    """
    An extractor for Hentai2Read.com

    The image URLs come from a JavaScript variable embedded in the first page
    of the gallery (gData). Another quirk is that galleries on this site are
    spread throughout multiple pages.
    """
    def __init__(self):
        super().__init__()
        self.name = "Hentai2Read"
        self.url = "https://www.hentai2read.com"
        self._PAGE_PATTERN = r"https?://(?:www\.)?hentai2read\.com.*"
        self._GALLERY_PATTERN = r"https?://(?:www\.)?hentai2read\.com/[^/]*"
        self._IMG_DOMAIN = "https://static.hentaicdn.com/hentai"

    # =========================================================================
    # Testing
    # =========================================================================
    def get_tests(self):
        tests = ({"url": "https://hentai2read.com/im_yours_muririn/",
                  "img_urls": ["https://static.hentaicdn.com/hentai/26490/1/ccdn0001.jpg",
                               "https://static.hentaicdn.com/hentai/26490/1/ccdn0002.jpg",
                               "https://static.hentaicdn.com/hentai/26490/1/ccdn0003.jpg",
                               "https://static.hentaicdn.com/hentai/26490/1/ccdn0004.jpg",
                               "https://static.hentaicdn.com/hentai/26490/1/ccdn0005.jpg",
                               "https://static.hentaicdn.com/hentai/26490/1/ccdn0006.jpg",
                               "https://static.hentaicdn.com/hentai/26490/1/ccdn0007.jpg",
                               "https://static.hentaicdn.com/hentai/26490/1/ccdn0008.jpg",
                               "https://static.hentaicdn.com/hentai/26490/1/ccdn0009.jpg"
                               ],
                  "size": 19,
                  "tags": {"Title": "I'm Yours",
                           "URL": "https://hentai2read.com/im_yours_muririn/",
                           "Artists": "Muririn",
                           "Authors": "Muririn",
                           "Category": ["Adult", "Big Breasts", "Oneshot"],
                           "Content": ["Bondage", "Creampie",
                                       "Female Dominance", "Hand Job",
                                       "Happy Sex", "Paizuri",
                                       "Partial Censorship", "School Girls"],
                           "Languages": "English"}},
                 {"url": "https://hentai2read.com/asgirls/",
                  "img_urls": ["https://static.hentaicdn.com/hentai/17152/2/hcdn0001.jpg",
                               "https://static.hentaicdn.com/hentai/17152/2/hcdn0002.jpg",
                               "https://static.hentaicdn.com/hentai/17152/2/hcdn0003.jpg",
                               "https://static.hentaicdn.com/hentai/17152/2/hcdn0004.jpg",
                               "https://static.hentaicdn.com/hentai/17152/2/hcdn0005.jpg",
                               "https://static.hentaicdn.com/hentai/17152/2/hcdn0006.jpg",
                               "https://static.hentaicdn.com/hentai/17152/2/hcdn0007.jpg",
                               "https://static.hentaicdn.com/hentai/17152/2/hcdn0008.jpg",
                               "https://static.hentaicdn.com/hentai/17152/2/hcdn0009.jpg"
                               ],
                  "size": 16,
                  "tags": {"Title": "Asgirls",
                           "URL": "https://hentai2read.com/asgirls/",
                           "Artists": "KUROKAWA Izumi",
                           "Authors": "KUROKAWA Izumi",
                           "Category": ["Adult", "Big Breasts", "Compilation",
                                        "Doujinshi"],
                           "Languages": "English",
                           "Content": ["Creampie", "Defloration",
                                       "Large Dicks", "Maids", "Prostitution",
                                       "Stockings"]}},
                 )
        return tests

    # =========================================================================
    # Getters
    # =========================================================================

    @staticmethod
    def _get_title(soup):
        title = soup.title.string
        return title.split("(")[0].strip()

    @staticmethod
    def _get_gallery_size(datavar):
        """Returns the total number of images in gallery"""
        for line in datavar:
            if "images" in line:
                return len(line.split(","))-1
        return None

    @staticmethod
    def _first_chapter(url, soup):
        """Return the URL for the first chapter of the series"""
        links = soup.find_all("a")
        for link in links:
            gallery_regex = os.path.join(url, r"\d/")
            if re.match(gallery_regex, link['href']):
                return link['href']
        raise ExtractorFailed(f"Could not scrape information from URL: {url}")

    def _get_datavar(self, url, soup):
        """Returns a list of all items in the gData variable

        gData is a variable in the site's JavaScript and is retrieved from the
        gallery page. It is useful for finding the gallery size and getting
        the image URLs.
        """
        # Download the first available gallery page
        gallery_url = self._first_chapter(url, soup)
        gallery_soup = self._get_soup(gallery_url)
        # Get all instances of <script>
        scripts = gallery_soup.find_all("script")
        # Look for the tags that contain content
        #   (assume var gData is the first inst.)
        data = [tag for tag in scripts if len(tag.contents) > 0][0]
        # Strip the content, then split and strip each line to make a list
        return [line.strip() for line in data.contents[0].strip().splitlines()]

    def get_size(self, url, soup, args):
        datavar = self._get_datavar(url, soup)
        return self._get_gallery_size(datavar)

    def get_gallery_urls(self, url, soup, args):
        datavar = self._get_datavar(url, soup)

        url_list = []
        size = self._get_gallery_size(datavar)
        size_len = len(str(abs(size)))
        for line in datavar:
            if "images" in line:
                data_array = line.split(" ")[2]
                url_array = data_array.split(",")[:-1]

        for item in url_array:
            url = self._build_url(item)
            filename = self._build_filename(url, size_len)
            url_list.append([filename, url])
        return url_list

    def get_tags(self, url, soup, args):
        plural_words = {"Language", "Artist", "Author"}
        soup_tags = {"Title": self._get_title(soup), "URL": url}
        tags = soup.find_all("li", {"class": "text-primary"})
        for tag in tags:
            if tag.b and tag.find_all("a"):
                key = tag.b.string
                key = f"{key}s" if key in plural_words else key
                items = self._clean_tags(tag)
                soup_tags[key] = items
        return soup_tags

    # =========================================================================
    # Misc. functions
    # =========================================================================

    def _build_url(self, item):
        """Return a URL for an item

        Removes any quotes, brackets, and backslashes.
        """
        image = re.sub(r'[\\"\[\]]', "", item)
        return self._IMG_DOMAIN + image

    @staticmethod
    def _build_filename(url, len_size):
        """Return a filename based on the image's URL and gallery size"""
        file_ = url.split("/")[-1]
        ext = file_.split(".")[-1]
        name = file_.split(".")[0][-len_size:]
        return f"{name}.{ext}"

    @staticmethod
    def _clean_tags(tags):
        """
        Build list from tags for the dictionary and format all entries
        """
        items = [item.string for item in tags.find_all("a")]
        # Remove empty "-" placeholder used by site
        items = ["" if item == "-" else item for item in items]
        # Remove newline char
        items = [re.sub(r"\n", "", item) for item in items]
        # Remove bracket content
        items = [item.split("(")[0].strip()
                 if "(" in item else item for item in items]
        return items
