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
"""This module contains the Imgur extractor class"""

from .extractor import Extractor


class ImgurEX(Extractor):
    """
    An extractor for Imgur.com

    When downloading galleries, Imgur supports various img/file formats.
    For a file '<ID>.gifv', '<ID>.jpg' also exists as a preview screenshot.
    Thus, it is unreliable to set all URLs as '.jpg' and rely on receiving an
    HTTP 404 error and letting Scraper's _retry_download_image() get the actual
    file. The workaround used is to use '<ID>.gifv' to request the HTML page
    for the image, and extract the true URL from there. The drawback is that
    the number of requests made for an album is doubled.

    Tags are non-existant for Imgur so the assumption is that the language is
    English.
    """
    def __init__(self):
        super().__init__()
        self.name = "Imgur"
        self.url = "https://www.imgur.com"
        self._PAGE_PATTERN = r"https?://(?:www\.)?imgur\.com.*"
        self._GALLERY_PATTERN = r"https?://(?:www\.)?imgur\.com/" + \
                                r"(?:a|gallery)/\w{5,7}/?"
        self._IMG_DOMAIN = "https://i.imgur.com/"

    # =========================================================================
    # Testing
    # =========================================================================
    def get_tests(self):
        tests = ({"url": "https://imgur.com/a/ZbNwy",
                  "img_urls": ["https://i.imgur.com/OtQ8qWE.png",
                               "https://i.imgur.com/HQx4kIf.png",
                               "https://i.imgur.com/HVjsGfg.png",
                               "https://i.imgur.com/RSH9anK.jpg"
                               ],
                  "size": 20,
                  "tags": {"Title": "My Pixel art wallpapers",
                           "URL": "https://imgur.com/a/ZbNwy",
                           "Languages": "English"}},
                 #{"url": "https://imgur.com/gallery/5YEv0i0",
                 # "img_urls": ["https://i.imgur.com/0MuVb3Q.mp4"],
                 # "size": 1,
                 # "tags": {"Title": "In the Zone! (sound helps)",
                 #          "URL": "https://imgur.com/gallery/5YEv0i0",
                 #          "Languages": "English"}},
                 {"url": "https://imgur.com/a/TnUGfAs",
                  "img_urls": ["https://i.imgur.com/biEef76.jpg",
                               "https://i.imgur.com/MXY2976.jpg"
                               ],
                  "size": 2,
                  "tags": {"Title": "Imgur-TnUGfAs",
                           "URL": "https://imgur.com/a/TnUGfAs",
                           "Languages": "English"}},
                 )

        return tests

    # =========================================================================
    # Getters
    # =========================================================================

    @staticmethod
    def _get_title(url, soup):
        raw_title = soup.title.string.strip()
        title = '-'.join(raw_title.split('-')[:-1]).strip()
        if title == "Imgur: The magic of the Internet" or not title:
            # No title set by the uploader, use the Imgur gallery ID
            album_id = (url.split("/")[-1] if url[-1] != "/"
                        else url.split("/")[-2])
            title = f"Imgur-{album_id}"
        return title

    def get_size(self, url, soup, args):
        image_tags = soup.findAll("div", {"class": "post-image-container"})
        return len(image_tags)

    def _image_url(self, img_tag):
        """For an image tag, return the image's true URL with extension

        Using '.gifv', we can obtain an HTML page that hosts the
        image/video. Videos use the <source> tag and images use the
        <img> tag. Note that there will always be at least one <img> tag
        due to the favicon.
        """
        img_id = img_tag.get('id')
        site_url = f"{self._IMG_DOMAIN}{img_id}.gifv"

        image_soup = self._get_soup(site_url)
        img_url = image_soup.find("img")["src"]
        video_tag = image_soup.find("source")
        if video_tag:
            img_url = video_tag["src"]

        return f"https:{img_url}"

    def get_gallery_urls(self, url, soup, args):
        url_list = []
        size = self.get_size(url, soup, args)
        size_len = len(str(size))
        img_tags = soup.findAll("div", {"class": "post-image-container"})
        img_urls = (self._image_url(tag) for tag in img_tags)

        for img_num, img_url in enumerate(img_urls):
            base_name = str(img_num).zfill(size_len)
            extension = img_url.split('.')[-1]
            filename = f"{base_name}.{extension}"
            url_list.append([filename, img_url])

        return url_list

    def get_tags(self, url, soup, args):
        soup_tags = {"Title": self._get_title(url, soup),
                     "Languages": "English",
                     "URL": url}
        return soup_tags
