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

from toktokkie.metadata.Metadata import Metadata
from toktokkie.metadata.Book import Book
from toktokkie.metadata.BookSeries import BookSeries
from toktokkie.metadata.Movie import Movie
from toktokkie.metadata.Manga import Manga
from toktokkie.metadata.TvSeries import TvSeries
from toktokkie.metadata.VisualNovel import VisualNovel
from toktokkie.metadata.components.enums import MediaType
from toktokkie.metadata.helper.functions import get_metadata, \
    get_metadata_class, create_metadata
