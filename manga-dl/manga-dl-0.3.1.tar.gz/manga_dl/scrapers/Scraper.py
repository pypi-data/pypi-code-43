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

import logging
from typing import Optional, List, Set, Dict
from manga_dl.entities.Chapter import Chapter


class Scraper:
    """
    Specifies the Capabilities of a manga download site scraper
    """

    def __init__(
            self,
            _format: str = "cbz",
            destination: Optional[str] = None,
            languages: Optional[Set[str]] = None
    ):
        """
        Initializes the Scraper object
        :param _format: The format in which to store chapters
        :param destination: The destination directory in
                            which to store chapters
        :param languages: Set of languages for which to check
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.format = _format
        self.destination = destination
        if languages is None:
            self.languages = {"english", "gb", "us"}
        else:
            self.languages = languages

    @classmethod
    def name(cls) -> str:
        """
        :return: The name of the scraper
        """
        raise NotImplementedError()

    @classmethod
    def url_matches(cls, url: str) -> bool:
        """
        Checks whether or not an URL matches for the scraper
        :param url: The URL to check
        :return: Whether the URL is valid
        """
        raise NotImplementedError()

    def generate_url(self, _id: str) -> str:
        """
        Generates an URL based on an ID
        :param _id: The ID to use
        :return: The generated URL
        """
        raise NotImplementedError()

    def load_chapters(
            self,
            url: Optional[str] = None,
            _id: Optional[str] = None
    ) -> List[Chapter]:
        """
        Loads a list of Chapter objects for an URL or ID
        Only one of either an URL or an ID is required
        :param url: The URL
        :param _id: The ID
        :return: The list of chapters
        """
        if url is None and _id is None:
            self.logger.warning("Neither URL or ID provided. Can't continue.")
            return []
        elif url is not None and not self.url_matches(url):
            self.logger.warning("Invalid URL. Can't continue.")
            return []
        elif _id is not None:
            url = self.generate_url(_id)

        chapters = self._load_chapters(str(url))
        chapters = self._remove_other_languages(chapters)
        chapters = self._sort_chapters(chapters)
        chapters = self._deduplicate_chapters(chapters)
        chapters = self._combine_multipart_chapters(chapters)

        return chapters

    @staticmethod
    def _sort_chapters(chapters: List[Chapter]) -> List[Chapter]:
        """
        Sorts a list of chapters. First by their total chapter number,
        then their macro chapter number
        :param chapters:
        :return:
        """
        # Both sort steps are necessary!
        chapters.sort(
            key=lambda x: str(x.chapter_number).zfill(15)
        )
        chapters.sort(
            key=lambda x: str(x.chapter_number.split(".")[0]).zfill(15)
        )
        return chapters

    def _remove_other_languages(self, chapters: List[Chapter]) \
            -> List[Chapter]:
        """
        Removes unwanted languages from the chapter list
        :param chapters: The chapter list
        :return: The chapter list without unwanted language entries
        """
        return list(filter(lambda x: x.language in self.languages, chapters))

    def _combine_multipart_chapters(self, chapters: List[Chapter]) \
            -> List[Chapter]:
        """
        Combines multipart chapters with each other (e.g. 12.1 and 12.2)
        :param chapters: The list of chapter to work through
        :return: The new chapter list
        """

        if len(chapters) < 2:
            return chapters

        last_chapter = chapters.pop(0)
        combined_chapters = []  # type: List[Chapter]
        to_combine = []  # type: List[Chapter]
        diff = 1

        for chapter in chapters:

            new_chapter = last_chapter.macro_chapter != chapter.macro_chapter
            if chapter.micro_chapter == 1 and new_chapter:
                self.logger.debug("Marking chapter {} as {}".format(
                    chapter.chapter_number, chapter.macro_chapter
                ))
                chapter.chapter_number = str(chapter.macro_chapter)

            if last_chapter.macro_chapter == chapter.macro_chapter:

                same_chapter = \
                    last_chapter.micro_chapter + diff == chapter.micro_chapter

                if last_chapter.micro_chapter == 0 \
                        and chapter.micro_chapter == 2:
                    same_chapter = True
                    diff = 2

                if same_chapter:
                    to_combine.append(chapter)
                    diff += 1
                    continue

            if len(to_combine) > 0 and last_chapter.micro_chapter in [0, 1]:
                self._combine_chapters(last_chapter, to_combine)
                to_combine = []
                diff = 1

            combined_chapters.append(last_chapter)
            combined_chapters += to_combine
            to_combine = []
            last_chapter = chapter

        if len(to_combine) > 0 and last_chapter.micro_chapter in [0, 1]:
            self._combine_chapters(last_chapter, to_combine)
            to_combine = []

        combined_chapters.append(last_chapter)
        combined_chapters += to_combine

        return combined_chapters

    def _combine_chapters(self, chapter: Chapter, to_combine: List[Chapter]):
        """
        Adds chapters to a chapter
        :param chapter: The master chapter
        :param to_combine: The chapters to add
        :return: None
        """
        combined_numbers = [chapter.chapter_number]

        chapter.chapter_number = str(chapter.macro_chapter)
        for extra in to_combine:
            chapter.add_additional_url(extra.url)
            combined_numbers.append(extra.chapter_number)

        self.logger.debug("Combined chapters: {}".format(combined_numbers))

    def _deduplicate_chapters(self, chapters: List[Chapter]) -> List[Chapter]:
        """
        Removes duplicate chapters from a list
        The chapter to use is based on which scanlation group was most often
        found in the other chapters
        :param chapters: The chapters to work through
        :return: The deduplicated list of chapters
        """

        if len(chapters) < 2:
            return chapters

        groups = {}  # type: Dict[str, int]
        chapter_map = {}  # type: Dict[str, List[Chapter]]
        for chapter in chapters:
            if chapter.group not in groups:
                groups[str(chapter.group)] = 1
            else:
                groups[str(chapter.group)] += 1

            if chapter.chapter_number not in chapter_map:
                chapter_map[chapter.chapter_number] = []
            chapter_map[chapter.chapter_number].append(chapter)

        for chapter_number, elements in chapter_map.items():
            if len(elements) > 1:
                best = max(elements, key=lambda x: groups[str(x.group)])
                chapter_map[chapter_number] = [best]

        deduplicated = []
        for chapter in chapters:

            best_chapter = chapter_map[chapter.chapter_number][0]

            if best_chapter == chapter:
                deduplicated.append(chapter)
            else:
                self.logger.debug("Discarding duplicate chapter {}"
                                  .format(chapter))

        return deduplicated

    def _load_chapters(self, url: str) -> List[Chapter]:
        """
        Scraper-specific implementation that loads chapters from the website
        :param url: The URL to scrape
        :return: The list of chapters found while scraping
        """
        raise NotImplementedError()
