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
from typing import List, Optional
from toktokkie.metadata.Manga import Manga
from toktokkie.metadata.components.enums import MediaType, IdType
from manga_dl.scrapers.mangadex import MangaDexScraper
from manga_dl.entities.Chapter import Chapter
from puffotter.os import makedirs, listdir, replace_illegal_ntfs_chars
from puffotter.print import pprint
from toktokkie.Directory import Directory
from toktokkie.scripts.Command import Command
from toktokkie.renaming.Renamer import Renamer
from zipfile import ZipFile


class MangaUpdateCommand(Command):
    """
    Class that encapsulates behaviour of the manga-update command
    """

    @classmethod
    def name(cls) -> str:
        """
        :return: The command name
        """
        return "manga-update"

    @classmethod
    def prepare_parser(cls, parser: argparse.ArgumentParser):
        """
        Prepares an argumentparser for this command
        :param parser: The parser to prepare
        :return: None
        """
        cls.add_directories_arg(parser)
        parser.add_argument("--dry-run", action="store_true",
                            help="Does not download or rename anything")
        parser.add_argument("--no-check-newest-chapter-length",
                            action="store_true",
                            help="Deactivates checking the latest chapter "
                                 "for completeness")
        parser.add_argument("--skip-special", action="store_true",
                            help="Skips updating special chapters")

    def execute(self):
        """
        Executes the commands
        :return: None
        """
        for directory in self.load_directories(
                self.args.directories, [MediaType.MANGA]
        ):
            metadata = directory.metadata  # type: Manga
            print(metadata.name)

            self.execute_rename(directory)

            chapters = self.load_chapters(metadata)
            if chapters is None:
                continue

            if not self.args.no_check_newest_chapter_length:
                self.check_latest_chapter_completeness(metadata, chapters)
            self.update_main_chapters(metadata, chapters)

            if not self.args.skip_special:
                self.update_special_chapters(metadata, chapters)

            if not self.args.dry_run:
                self.execute_rename(directory)

    def execute_rename(self, directory: Directory):
        """
        Renames the current directory content. Automatically checks if the
        dry-run flag is set. If it is set, prints out any chapters that
        would have been renamed
        :param directory: The directory whose conet should be renamed
        :return: None
        """
        self.logger.info("Running rename")
        if not self.args.dry_run:
            directory.rename(noconfirm=True)
        else:
            ops = Renamer(directory.metadata).get_active_operations()
            for op in ops:
                print(op)

    @staticmethod
    def load_chapters(metadata: Manga) -> Optional[List[Chapter]]:
        """
        Loads chapter information from mangadex.org
        :param metadata: The metadata for which to load the chapters
        :return: Either a list of chapters or None if no mangadex ID was found
        """

        mangadex_ids = metadata.ids.get(IdType.MANGADEX)
        if mangadex_ids is None or len(mangadex_ids) == 0:
            pprint("No mangadex ID for {}".format(metadata.name), fg="lred")
            return None

        mangadex_id = mangadex_ids[0]

        chapters = MangaDexScraper().load_chapters(None, mangadex_id)
        return chapters

    def check_latest_chapter_completeness(
            self,
            metadata: Manga,
            chapters: List[Chapter]
    ):
        """
        Checks the latest regular chapter for completeness.
        This is necessary since some groups release their chapters in parts
        (i.e. 10.1 and then 10.2). manga-dl merges these chapter parts, so
        we only need to check if the local files has less pages.
        :param metadata: The metadata of the series to check
        :param chapters: The chapters for the series
        :return: None
        """

        main_chapters = list(filter(lambda x: not x.is_special, chapters))
        current_files = listdir(metadata.main_path)
        current_latest = len(current_files)

        if current_latest == 0:
            return

        try:
            current_chapter = list(filter(
                lambda x: int(x.chapter_number) == current_latest,
                main_chapters
            ))[0]
        except IndexError:  # If mangadex does not have the latest chapter
            return

        past_file = current_files[current_chapter.macro_chapter - 1][1]
        with ZipFile(past_file, "r") as zip_obj:
            filecount = len(zip_obj.namelist())
        pagecount = len(current_chapter.pages)

        if filecount < pagecount:
            if not self.args.dry_run:
                pprint("Updating chapter {}".format(current_chapter),
                       fg="lgreen")
                os.remove(past_file)
                current_chapter.download(past_file)
            else:
                pprint("Updated Chapter found: {}".format(current_chapter),
                       fg="lyellow")
        elif filecount != pagecount:
            self.logger.warning(
                "Page counts do not match for chapter {}: "
                "Ours:{}, Theirs:{}".format(
                    current_chapter, filecount, pagecount
                )
            )

    def update_main_chapters(self, metadata: Manga, chapters: List[Chapter]):
        """
        Updates the regular chapters of the series
        :param metadata: The metadata of the series
        :param chapters: The chapters of the series
        :return: None
        """
        current_latest = len(listdir(metadata.main_path))

        main_chapters = list(filter(
            lambda x: not x.is_special
            and int(x.chapter_number) > current_latest,
            chapters
        ))

        maxchar = max(metadata.name)

        total_chapters = len(main_chapters) + current_latest

        downloaded = []  # type: List[str]
        for c in main_chapters:
            if current_latest + 1 != c.macro_chapter:
                pprint("Missing chapter {}, expected {}".format(
                    current_latest + 1,
                    c.chapter_number,
                ), fg="lred")
                break
            current_latest += 1

            if c.chapter_number in downloaded:
                continue
            downloaded.append(c.chapter_number)

            name = "{}{} - Chapter {}.cbz".format(
                maxchar,
                metadata.name,
                c.chapter_number.zfill(len(str(total_chapters)))
            )
            dest = os.path.join(metadata.main_path, name)
            if not self.args.dry_run:
                print("Downloading Chapter {}".format(c))
                c.download(dest)
            else:
                pprint("Found chapter: {}".format(c), fg="lyellow")

    def update_special_chapters(
            self,
            metadata: Manga,
            chapters: List[Chapter]
    ):
        """
        Updates the special chapters of the series
        :param metadata: The metadata of the series
        :param chapters: The chapters of the series
        :return: None
        """
        special_chapters = list(filter(lambda x: x.is_special, chapters))

        try:
            special_fill = len(max(
                metadata.special_chapters,
                key=lambda x: len(x)
            ))
        except ValueError:
            special_fill = 0

        for c in special_chapters:

            name = "{} - Chapter {}.cbz".format(
                metadata.name,
                c.chapter_number.zfill(special_fill)
            )

            path = os.path.join(
                metadata.special_path, replace_illegal_ntfs_chars(name)
            )

            if os.path.exists(path):
                continue
            elif c.chapter_number not in metadata.special_chapters:

                if self.args.dry_run:
                    pprint("Found unknown chapter {}".format(c.chapter_number),
                           fg="lyellow")
                else:
                    pprint("Adding chapter {} to metadata".format(c),
                           fg="lgreen")
                    chapter_entries = metadata.special_chapters
                    chapter_entries.append(c.chapter_number)
                    metadata.special_chapters = chapter_entries
                    metadata.write()
                    makedirs(metadata.special_path)
                    c.download(path)
            else:
                if not self.args.dry_run:
                    makedirs(metadata.special_path)
                    c.download(path)
                else:
                    pprint("Found chapter: {}".format(c), fg="lyellow")
