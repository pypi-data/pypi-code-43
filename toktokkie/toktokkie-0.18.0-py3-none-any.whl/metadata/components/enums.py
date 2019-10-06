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

from enum import Enum
from typing import List, Dict


class IdType(Enum):
    """
    Enumeration of all possible ID types
    """
    TVDB = "tvdb"
    IMDB = "imdb"
    MYANIMELIST = "myanimelist"
    ANILIST = "anilist"
    KITSU = "kitsu"
    ISBN = "isbn"
    VNDB = "vndb"
    MANGADEX = "mangadex"


class MediaType(Enum):
    """
    Enumeration that defines all possible media types
    """
    BOOK = "book"
    BOOK_SERIES = "book_series"
    MOVIE = "movie"
    TV_SERIES = "tv"
    VISUAL_NOVEL = "visual_novel"
    MANGA = "manga"


valid_id_types = {
    MediaType.BOOK: [
        IdType.ISBN,
        IdType.ANILIST,
        IdType.MYANIMELIST,
        IdType.KITSU
    ],
    MediaType.BOOK_SERIES: [
        IdType.ISBN,
        IdType.ANILIST,
        IdType.MYANIMELIST,
        IdType.KITSU
    ],
    MediaType.MOVIE: [
        IdType.IMDB,
        IdType.ANILIST,
        IdType.MYANIMELIST,
        IdType.KITSU
    ],
    MediaType.TV_SERIES: [
        IdType.TVDB,
        IdType.ANILIST,
        IdType.MYANIMELIST,
        IdType.KITSU
    ],
    MediaType.VISUAL_NOVEL: [
        IdType.VNDB
    ],
    MediaType.MANGA: [
        IdType.ISBN,
        IdType.ANILIST,
        IdType.MYANIMELIST,
        IdType.KITSU,
        IdType.MANGADEX
    ]
}  # type: Dict[MediaType, List[IdType]]
"""
Valid ID types for the various Media types
"""

required_id_types = {
    MediaType.BOOK: [
    ],
    MediaType.BOOK_SERIES: [
    ],
    MediaType.MOVIE: [
        IdType.IMDB
    ],
    MediaType.TV_SERIES: [
        IdType.TVDB
    ],
    MediaType.VISUAL_NOVEL: [
        IdType.VNDB
    ],
    MediaType.MANGA: [
    ]
}  # type: Dict[MediaType, List[IdType]]
"""
Required ID Types for the various Media Types
"""
