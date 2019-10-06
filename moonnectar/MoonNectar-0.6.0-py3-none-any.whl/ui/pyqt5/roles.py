from enum         import Enum, unique
from PyQt5.QtCore import Qt

@unique
class UserRoles(Enum):
    AlbumSortByAlbum  = Qt.UserRole + 1
    AlbumSortByArtist = Qt.UserRole + 2
    AlbumSortByTrack  = Qt.UserRole + 3


