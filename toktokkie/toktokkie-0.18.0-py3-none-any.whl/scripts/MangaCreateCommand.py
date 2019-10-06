"""LICENSE
Copyright 2015 Hermann Krumrey <hermann@krumreyh.com>

This file is part of toktokkie.

toktokkie is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

toktokkie is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with toktokkie.  If not, see <http://www.gnu.org/licenses/>.
LICENSE"""

import os
import argparse
import requests
from toktokkie.Directory import Directory
from puffotter.graphql import GraphQlClient
from puffotter.os import makedirs
from subprocess import Popen
from toktokkie.metadata.Manga import Manga
from toktokkie.metadata.components.enums import IdType
from toktokkie.exceptions import MissingMetadata, InvalidMetadata
from manga_dl.scrapers.mangadex import MangaDexScraper
from toktokkie.scripts.Command import Command


class MangaCreateCommand(Command):
    """
    Class that encapsulates behaviour of the manga-create command
    """

    @classmethod
    def name(cls) -> str:
        """
        :return: The command name
        """
        return "manga-create"

    @classmethod
    def prepare_parser(cls, parser: argparse.ArgumentParser):
        """
        Prepares an argumentparser for this command
        :param parser: The parser to prepare
        :return: None
        """
        parser.add_argument("anilist_ids", nargs="+",
                            help="The anilist IDs of the manga "
                                 "series to create")

    def execute(self):
        """
        Executes the commands
        :return: None
        """
        for anilist_id in self.args.anilist_ids:

            client = GraphQlClient("https://graphql.anilist.co")

            query = """
            query ($id: Int) {
                Media (id: $id) {
                    title {
                        romaji
                        english
                    }
                    coverImage {
                        large
                        medium
                    }
                }
            }
            """
            data = client.query(query, {"id": anilist_id})["data"]
            title = data["Media"]["title"]["english"]
            if title is None:
                title = data["Media"]["title"]["romaji"]

            makedirs(title)
            makedirs(os.path.join(title, "Main"))
            makedirs(os.path.join(title, ".meta/icons"))

            mangadex_id = None
            try:
                directory = Directory(title)
                mangadex_id = \
                    directory.metadata.ids.get(IdType.MANGADEX, [None])[0]

            except (MissingMetadata, InvalidMetadata):

                cover_image = data["Media"]["coverImage"]["large"]
                cover_image = cover_image.replace("medium", "large")

                main_icon = os.path.join(title, ".meta/icons/main.")
                ext = cover_image.rsplit(".", 1)[1]

                img = requests.get(
                    cover_image, headers={"User-Agent": "Mozilla/5.0"}
                )
                if img.status_code >= 300:
                    med_url = cover_image.replace("large", "medium")
                    img = requests.get(
                        med_url, headers={"User-Agent": "Mozilla/5.0"}
                    )
                with open(main_icon + ext, "wb") as f:
                    f.write(img.content)

                if ext != "png":
                    Popen(["convert", main_icon + ext, main_icon + "png"])\
                        .wait()
                    os.remove(main_icon + ext)
                Popen([
                    "zip", "-j",
                    os.path.join(title, "cover.cbz"),
                    main_icon + "png"
                ]).wait()

            if mangadex_id is None:
                anilist_url = "https://anilist.co/manga/" + str(anilist_id)
                mangadex_search = "https://mangadex.org/quick_search/" + title
                print(title)
                print(anilist_url)
                Popen(["firefox", mangadex_search])

                mangadex_id = input("Mangadex ID/URL: ")
                if "https://mangadex.org/title/" in mangadex_id:
                    mangadex_id = mangadex_id \
                        .split("https://mangadex.org/title/")[1] \
                        .split("/")[0]

            scraper = MangaDexScraper(destination=os.path.join(title, "Main"))
            chapters = scraper.load_chapters(None, mangadex_id)

            special_chapters = []
            for chapter in chapters:

                try:
                    chap_zero = chapter.macro_chapter == 0
                    if "." in chapter.chapter_number or chap_zero:
                        raise ValueError()
                    int(chapter.chapter_number)

                except ValueError:
                    special_chapters.append(chapter.chapter_number)

            metadata = Manga(title, {
                "ids": {
                    "anilist": [str(anilist_id)],
                    "mangadex": [mangadex_id]
                },
                "special_chapters": special_chapters,
                "type": "manga"
            })
            metadata.write()
