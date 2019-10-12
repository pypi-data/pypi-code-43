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
"""This module contains the Scraper class"""

import os
import sys
import imghdr
import shutil
import asyncio
from argparse import Namespace
from typing import List, Tuple

import aiofiles
import requests
from aiohttp import ClientSession
from bs4 import BeautifulSoup, Tag

import komidl.status as status
import komidl.constants as constants
from komidl.exceptions import ExtractorFailed, InvalidURL


class Scraper:
    """Download all images from a URL with an extractor.

    The Scraper class given a URL and extractor will work to create
    directories and download the images, as well as write tags to files.

    File downloading is heavily IO bound, and thus is performed
    asynchronously.

    Scraper also has a session object that is shared among methods, and
    is used for all non-asynchronous web requests. Asynchronous web
    requests use a 'ClientSession' from aiohttp in context, but it
    shares the headers of the session object.
    """
    def __init__(self, extractor=None):
        self.extractor = extractor
        self._session = requests.Session()
        self._session.headers = {"User-Agent": constants.USER_AGENT,
                                 "Accept-encoding": "gzip, deflate"}
        requests.packages.urllib3.disable_warnings()
        self._downloaded = 0

    @staticmethod
    def _soup_request(session: requests.Session, url: str) -> Tag:
        """Returns a BS4 soup from the URL's response

        The request is done using the session.
        """
        request = session.get(url, verify=False)
        request.raise_for_status()
        content = request.content
        return BeautifulSoup(content, "html.parser")

    def reset(self) -> None:
        """Resets the state of the Scraper after use"""
        # Reset download counter
        self._downloaded = 0

    @staticmethod
    def _get_extension(url: str) -> Tuple[str, str]:
        """Returns the path and extension of a URL.

        Acts exactly like os.path.splitext(), but without the '.' char
        in the extension.
        """
        path, ext = os.path.splitext(url)
        return path, ext[1:]

    @staticmethod
    async def _write_image(response: str, path: str) -> None:
        """Saves the response of an image request to the path"""
        async with aiofiles.open(path, "wb") as img:
            await img.write(await response.read())

    @staticmethod
    async def _retry_request(session, path: str, url: str) -> None:
        """Retries downloading an image with alternate file extensions

        Alternate image formats are defined in constants.COMMON_FORMATS.

        Raises an ExtractorFailed exception if all attempts using
        alternate image extensions have been exhausted.
        """
        _, current_ext = Scraper._get_extension(url)
        other_exts = (ext for ext in constants.COMMON_FORMATS
                      if ext != current_ext)
        # Exhaustively try other image formats
        for ext in other_exts:
            new_url = Scraper._change_extension(url, ext)
            response = await session.get(new_url)
            if response.status == 200:
                await Scraper._write_image(response, path)
                break
        else:
            raise ExtractorFailed(f"Extractor returned an invalid URL: {url}")

    async def _image_request(self, status_bar, path: str, url: str) -> None:
        """Downloads an image from the URL and saves it to the path.

        Failure to download an image (HTTP 404) may be caused by a wrong
        extension from the extractor. On failure, various other
        extensions are exhaustively tried. If the image can't be
        downloaded, then download of the whole gallery is failed.

        It may be possible that the file extension in the 'url' or
        'path' parameters are inaccurate, so after a successful
        download the magic bytes of the image are checked and the image
        may be renamed with the appropriate extension.

        Downloading an image increments the counter and updates the
        status bar.
        """
        # Attempt download of image from URL to file path
        async with ClientSession(headers=self._session.headers) as session:
            response = await session.get(url)
            if response.status == 200:
                await self._write_image(response, path)
            elif response.status == 404:
                await self._retry_request(session, path, url)
            else:
                raise InvalidURL(f"Server error encountered at: {url}")

        # Detect and fix extension
        await self._fix_extension(path)

        # Increment counter & update status
        self._downloaded += 1
        status_bar.update(self._downloaded)

    def _download_images(self, status_bar, urls) -> None:
        """Asynchronously downloads images from the gallery urls"""
        # Make the asynchronous image requests
        futures = [self._image_request(status_bar, path, url)
                   for path, url in urls]
        asyncio.run(asyncio.wait(futures))

    @staticmethod
    async def _fix_extension(image: str) -> None:
        """Renames the image's file extension based on the magic bytes

        If magic bytes could not be found, the image's extension is not
        modified.
        """
        _, cur_ext = Scraper._get_extension(image)
        actual_ext = imghdr.what(image)
        if actual_ext is not None:
            if cur_ext != actual_ext:
                new_image = Scraper._change_extension(image, actual_ext)
                os.rename(image, new_image)

    @staticmethod
    def _change_extension(url: str, ext: str) -> str:
        """Replaces the URL's file extension."""
        base_url, _ = os.path.splitext(url)
        return f"{base_url}.{ext}"

    @staticmethod
    def _create_dir(title: str, root_dir: str, overwrite: bool = False) -> str:
        """Creates a directory to hold all downloaded files.

        The directory is created in the destination (root_dir)
        directory, which is defined by the --directory argument (by
        default it is the directory the user was in when they ran the
        script).

        If the destination directory does not exists, an exception is
        raised.

        If 'overwrite' is set, then any existing folder is automatically
        overwritten. Otherwise, a prompt will appear to give the user
        the option to overwrite or create the directory with a new name.

        Returns the full path of the newly created directory.
        """
        root_dir = os.path.abspath(root_dir)
        dest = os.path.join(root_dir, title)

        try:
            os.mkdir(dest)
        except FileExistsError:
            if not overwrite:
                prompt_msg = f"{dest} already exists. Overwrite?"
                overwrite = status.prompt(prompt_msg)
            if overwrite:
                shutil.rmtree(dest)
            else:
                duplicates = sum(1 for dir_ in os.listdir(root_dir)
                                 if title in dir_)
                dest = f"{dest} ({duplicates})"
            os.mkdir(dest)

        return dest

    @staticmethod
    def _append_path(path: str, urls: List[List[str]]) -> Tuple[str, str]:
        """Appends the path to all image paths in gallery_urls."""
        for img, url in urls:
            yield os.path.join(path, img), url

    @staticmethod
    def _create_subdirs(urls: List[List[str]]) -> None:
        """Create all sub-directories from paths in gallery_urls."""
        img_paths = (os.path.split(img) for img, _ in urls)
        for sub_dir, _ in img_paths:
            os.makedirs(sub_dir, exist_ok=True)

    def scrape(self, url: str, args: Namespace) -> str:
        """Scrapes an image gallery at the URL.

        Using the extractor set within the object, if the URL given is a
        gallery then it is used to scrape.

        Raises an InvalidURL exception if the given URL or scraped image
        URL could not be requested.

        Raises an ExtractorFailed exception if an error was encountered
        within the extractor.

        Raises a ValueError exception if any argument values are
        incorrect.

        Returns the full path of the directory containing all scraped
        images.
        """
        soup = self._soup_request(self._session, url)

        if not self.extractor.is_gallery(url):
            raise InvalidURL(f"'{url}' is not a valid image gallery for the "
                             f"'{self.extractor.name}' extractor")
        try:
            directory = self.scrape_gallery(soup, url, args)
        finally:
            self.extractor.reset()

        return directory

    def scrape_gallery(self, soup: Tag, url: str, args: Namespace) -> str:
        """Scrape a URL and download all images.

        Tags are written to a file if the --tags option is selected.

        In the process, the directory to hold all scraped info is
        created.
        """
        # Gather info for progress bar img downloading, create dest directory
        tags = self.extractor.get_tags(url, soup, args)
        title = self._build_title(tags)
        path = self._create_dir(title, args.directory, overwrite=args.yes)
        _, dirname = os.path.split(path)
        size = self.extractor.get_size(url, soup, args)

        # Start scraping process
        msg = f'Downloading: {dirname}'
        with status.progress(msg, constants.STATUSBAR_LEN, size) as status_bar:
            gallery_urls = self.extractor.get_gallery_urls(url, soup, args)
            # Append the destination path to the file names
            img_urls = list(Scraper._append_path(path, gallery_urls))
            # Create the sub-directories if needed
            self._create_subdirs(img_urls)
            # Start downloading images
            self._download_images(status_bar, img_urls)

            # Write tags
            if args.tags:
                self._write_tags(tags, path)

        return path

    @staticmethod
    def _build_title(tags: dict) -> str:
        """Build a name for the directory containing downloaded images"""
        def langs_tostr(langs: str) -> str:
            """Return language as an ISO 639-1 abbreviation"""
            # Get the first language if the value is a list
            if isinstance(langs, list):
                language, *_ = langs
            else:
                language = langs
            return constants.LANG_TO_ISO[language.title()]

        def build_credit_tag(tags: dict) -> str:
            """Credit the author/artist/group in the title

            Priority of: Authors -> Artists -> Groups -> UNKNOWN
            """
            credit = tags.get('Authors',
                              tags.get('Artists',
                                       tags.get('Groups',
                                                'Unknown')))
            if isinstance(credit, list):
                return "x".join(name.upper() for name in credit)
            return credit.upper()

        title = tags.get('Title', 'UNTITLED')
        language = langs_tostr(tags['Languages'])
        credit = build_credit_tag(tags)
        chapters = tags.get('Chapters')
        chapter_tag = f"[{chapters}] " if chapters else " "
        return f"[{credit}][{language}]{chapter_tag}{title}"

    @staticmethod
    def _write_tags(tags: dict, path: str) -> None:
        """Writes tags to a text file path"""
        info_str = Scraper._tags_tostr(tags)
        info_file = os.path.join(path, "info.txt")
        with open(info_file, "w") as file_:
            file_.write(info_str)

    @staticmethod
    def _tags_tostr(tags: dict) -> str:
        """Returns tags as a string of format: 'KEY:ITEM,ITEM,ITEM'"""
        valid_keys = [key for key in tags if tags[key]]
        item_strs = (','.join(tags[key]) if isinstance(tags[key], list)
                     else tags[key] for key in valid_keys)
        tag_strs = (f"{key}:{item_str}\n"
                    for key, item_str in zip(valid_keys, item_strs))
        return "".join(tag_strs)
