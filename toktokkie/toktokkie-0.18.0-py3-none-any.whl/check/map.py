"""
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
"""

from toktokkie.metadata.components.enums import MediaType
from toktokkie.check.BookChecker import BookChecker
from toktokkie.check.MangaChecker import MangaChecker
from toktokkie.check.BookSeriesChecker import BookSeriesChecker
from toktokkie.check.TvSeriesChecker import TvSeriesChecker
from toktokkie.check.MovieChecker import MovieChecker
from toktokkie.check.VisualNovelChecker import VisualNovelChecker

checker_map = {
    MediaType.BOOK: BookChecker,
    MediaType.BOOK_SERIES: BookSeriesChecker,
    MediaType.TV_SERIES: TvSeriesChecker,
    MediaType.MOVIE: MovieChecker,
    MediaType.VISUAL_NOVEL: VisualNovelChecker,
    MediaType.MANGA: MangaChecker
}
"""
A dictionary mapping media types to checker classes
"""
