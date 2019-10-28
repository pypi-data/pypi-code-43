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

import os
import shutil
import logging
import cfscrape
import requests
from puffotter.os import makedirs
from typing import Callable, List
from typing import Optional
from subprocess import Popen, DEVNULL


class Chapter:
    """
    Class that models a manga chapter
    """

    def __init__(
            self,
            url: str,
            language: str,
            series_name: str,
            chapter_number: str,
            destination_dir: str,
            _format: str,
            page_load_callback: Callable[['Chapter', str], List[str]],
            title: Optional[str] = None,
            group: Optional[str] = None
    ):
        """
        Initializes the manga chapter
        :param url: The URL used to fetch page image URLs
        :param language: The language of the chapter
        :param series_name: The name of the series
        :param chapter_number: The chapter number of this chapter
        :param destination_dir: The destination directory in which to store
                                downloaded files by default
        :param _format: The format in which to store the chapter when
                        downloading by default
        :param title: The title of the chapter
        :param group: The group that scanlated this chapter
        :param page_load_callback:
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.url = url
        self.language = language
        self.series_name = series_name
        self.chapter_number = chapter_number
        self.destination_dir = destination_dir
        self.format = _format
        self._page_load_callback = page_load_callback
        self._pages = []  # type: List[str]
        self._additional_urls = []  # type: List[str]
        self._last_additional_urls = []  # type: List[str]
        self.group = group
        self.title = title

        if self.chapter_number == "" or chapter_number == "0":
            self.chapter_number = "0.0"

    @property
    def name(self) -> str:
        """
        :return: The name of the chapter
        """
        name = "{} - Chapter {}".format(self.series_name, self.chapter_number)
        if self.title is not None and self.title != "":
            name += " - " + self.title
        if self.group is not None and self.group != "":
            name += " ({})".format(self.group)
        return name

    @property
    def pages(self) -> List[str]:
        """
        Lazy-loads the URLs of the chapter's page images
        :return: The list of page images, in the correct order
        """
        new_urls = self._last_additional_urls != self._additional_urls
        if len(self._pages) == 0 or new_urls:
            self._pages = self._page_load_callback(self, self.url)
            for url in self._additional_urls:
                self._pages += self._page_load_callback(self, url)
            self._last_additional_urls = list(self._additional_urls)
        return self._pages

    @property
    def macro_chapter(self) -> int:
        """
        Calculates the 'macro' chapter number. For example:
            12 -> 12
            15.5 -> 15
            EX4 -> 4
        :return: The macro chapter number
        """
        macro = self.chapter_number.split(".")[0]
        macro_num = ""
        for char in macro:
            if char.isnumeric():
                macro_num += char
        return int(macro_num)

    @property
    def micro_chapter(self) -> int:
        """
        Calculates the 'micro' chapter number. For example:
            12 -> 0
            15.5 -> 5
            EX4 -> 0
        :return: The micro chapter number
        """
        try:
            micro = self.chapter_number.split(".")[1]
            micro_num = ""
            for char in micro:
                if char.isnumeric():
                    micro_num += char
            return int(micro_num)
        except IndexError:
            return 0

    @property
    def is_special(self) -> bool:
        """
        :return: Whether or not this is a 'special' chapter (Omake etc)
        """
        if "." in self.chapter_number or self.macro_chapter == 0:
            return True
        else:
            try:
                int(self.chapter_number)
                return False
            except ValueError:
                return True

    def add_additional_url(self, url: str):
        """
        Adds an additional URL.
        Useful for multi-part chapters
        :param url: The URL to add
        :return: None
        """
        self._additional_urls.append(url)

    def download(
            self,
            file_path_override: Optional[str] = None,
            format_override: Optional[str] = None
    ) -> str:
        """
        Downloads the chapter to a local file or directory
        :param file_path_override: Overrides the automatically generated
                                   destination file path
        :param format_override: Overrides the class-wide format
        :return: The path to the downloaded chapter file/directory
        """
        _format = self.format if format_override is None else format_override

        tempdir = os.path.join("/tmp", self.name)
        makedirs(tempdir, delete_before=True)

        dest_path = os.path.join(self.destination_dir, self.name)
        if file_path_override:
            dest_path = file_path_override
        if not dest_path.endswith("." + _format) and _format != "dir":
            dest_path += "." + _format

        makedirs(os.path.dirname(dest_path))

        index_fill = len(str(len(self.pages)))
        downloaded = []
        for i, image_url in enumerate(self.pages):

            cloudflare = False
            if image_url.startswith("CF!"):
                image_url = image_url[3:]
                cloudflare = True

            ext = image_url.rsplit(".", 1)[1]
            filename = "{}.{}".format(str(i).zfill(index_fill), ext)
            image_file = os.path.join(tempdir, filename)

            self.logger.info("Downloading image file {} to {}"
                             .format(image_url, image_file))

            if cloudflare:
                scraper = cfscrape.create_scraper()
                content = scraper.get(image_url).content
                with open(image_file, "wb") as f:
                    f.write(content)
            else:
                resp = requests.get(
                    image_url, headers={"User-Agent": "Mozilla/5.0"}
                )
                if resp.status_code >= 300:
                    self.logger.warning("Couldn't download image file {}"
                                        .format(image_file))
                else:
                    with open(image_file, "wb") as f:
                        f.write(resp.content)

            downloaded.append(image_file)

        if len(downloaded) == 0:
            self.logger.warning("Couldn't download chapter {}".format(self))
        else:
            if _format in ["cbz", "zip"]:
                self.logger.debug("Zipping Files")
                Popen(["zip", "-j", dest_path] + downloaded,
                      stdout=DEVNULL, stderr=DEVNULL).wait()
                shutil.rmtree(tempdir)
            elif _format == "dir":
                os.rename(tempdir, dest_path)
            else:
                self.logger.warning("Invalid format {}".format(_format))

        return dest_path

    def __str__(self) -> str:
        """
        :return: The string representation of the object
        """
        return self.name

    def __eq__(self, other: object) -> bool:
        """
        Checks for equality with other objects
        :param other: The other object
        :return: Whether or not the objects are  the same
        """
        if not isinstance(other, Chapter):
            return False
        else:
            return other.url == self.url
