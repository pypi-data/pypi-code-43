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
"""This module contains the KomiDL class"""

import os
import re
import sys
import shutil
from typing import List
from argparse import Namespace

from PIL import Image
from requests.exceptions import HTTPError

import komidl.constants as constants
from komidl.scraper import Scraper
from komidl.extractors import get_extractors
from komidl.extractors.extractor import Extractor
from komidl.exceptions import ExtractorFailed, InvalidURL


class KomiDL:
    """Match URLs to extractors and start the download procedure.

    This class is responsible for handling the URLs, and any actions
    before/after the scraping and downloading (ex. listing extractors,
    archive downloads, etc.).
    Furthermore, this class owns instances of all extractors and does
    matching between URL to extractor.

    """
    def __init__(self, args: Namespace):
        self._args = args
        self._extractors = get_extractors()
        self._scraper = Scraper()

    @staticmethod
    def _check_protocol(url: str) -> str:
        """Return a URL with a protocol appended.

        If a protocol is missing from the URL, print a warning and
        return the URL using the HTTP protocol.
        """
        if not re.match(r"(?:http|https)://", url):
            print("Warning: No protocol specified in URL, trying HTTP")
            url = f"http://{url}"
        return url

    def _get_extractor(self, url: str) -> Extractor:
        """Return the appropriate extractor for the URL.

        If no appropriate extractor is found, an ExtractorFailed
        exception is raised.
        """
        for extractor in self._extractors:
            if extractor.is_page(url):
                return extractor
        raise ExtractorFailed(f"Extractor not found for site: {url}")

    @staticmethod
    def _archive_dir(path: str, frm: str, dest: str) -> None:
        """Archive the directory and contents to the destination folder.

        Parameters
        ----------
        path:   The path of the directory to archive
        frm:    The archive format to use
        dest:   The path to save the archive to
        """
        _, base = os.path.split(path)
        archive = f"{path}.{frm}"
        archive_pattern = rf"{re.escape(archive)}.*\.{frm}"
        old_path = path

        if os.path.isfile(archive):
            duplicates = sum(1 for file in os.listdir(dest)
                             if re.match(archive_pattern, file))
            old_path = path
            base = f"{base} ({duplicates})"
            path = f"{path} ({duplicates})"
            os.rename(old_path, path)

        shutil.make_archive(path, frm, root_dir=dest, base_dir=base)
        os.rename(path, old_path)

    @staticmethod
    def _export_pdf(path: str, dest: str) -> None:
        """Export all images from the directory to PDF

        Parameters
        ----------
        path:   The path of the directory containing images
        dest:   The path to save the PDF to
        """
        _, folder_name = os.path.split(path)
        # Recursively traverse directory, get all file paths
        file_paths = (os.path.join(root, file)
                      for root, _, files in os.walk(path)
                      for file in files)

        # Get all valid image files from path and open with PIL
        valid_imgs = (file for file in file_paths
                      if file.split('.')[-1] in constants.IMAGE_FORMATS)
        pil_imgs = (Image.open(img) for img in valid_imgs)

        def convert_rgb(img):
            """Convert all PIL Image objects to RGB."""
            if img.mode != "RGB":
                # Filename is necessary for sequential image ordering
                filename = img.filename
                img = img.convert('RGB')
                img.filename = filename
            return img

        pil_rgb = (convert_rgb(img) for img in pil_imgs)

        # Order images by sorting with filename and separate out title image
        title_img, *content = sorted(pil_rgb, key=lambda img: img.filename)

        # Construct the PDF filename based on existing files in dest dir
        pdf_pattern = rf"{re.escape(folder_name)}.*\.pdf"
        duplicates = sum(1 for file in os.listdir(dest)
                         if re.match(pdf_pattern, file))

        pdf_filename = f"{folder_name}.pdf"
        if duplicates > 0:
            pdf_filename = f"{folder_name} ({duplicates}).pdf"

        # Export all images to PDF
        title_img.save(pdf_filename, "PDF", resolution=100.0, save_all=True,
                       append_images=content)

    def list(self) -> None:
        """List all extractors"""
        for e in self._extractors:
            name_str = f"[{e.name}]"
            print(f"{name_str:<18}| {e.url}")

    def download(self, urls: List[str]) -> None:
        """Download all images from the list of URLs.

        For each URL, an appropriate extractor is found and used to
        download all images and tags. After downloading, export
        operations may be done if specified in the runtime options
        (args).

        Parameters
        ----------
        urls : list [str]
            A list of gallery URLs to download
        """
        for url in urls:
            url = self._check_protocol(url)
            try:
                self._scraper.extractor = self._get_extractor(url)
                gallery = self._scraper.scrape(url, self._args)
            except (ValueError, InvalidURL, ExtractorFailed, HTTPError) as e:
                print(f"{e.__class__.__name__}: {e}")
                continue
            except (FileNotFoundError) as e:
                print(f"{e.__class__.__name__}: {e}")
                sys.exit(1)
            finally:
                self._scraper.reset()

            # Optional gallery export operations
            if self._args.pdf:
                self._export_pdf(gallery, self._args.directory)

            if self._args.archive:
                self._archive_dir(gallery, self._args.archive,
                                  self._args.directory)

            # If an export option was chosen, check if gallery should be kept
            if self._args.pdf or self._args.archive:
                if not self._args.keep:
                    shutil.rmtree(gallery)
