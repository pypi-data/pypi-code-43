import os
from CoreEngine.tile import AnimatedTile
from CoreEngine.spritesheetcreator import SpriteSheetCreator
from CoreEngine.utility import load_image
import json
import pygame

"""
if your developing your own map format ; please use this as template
"""


class DataAdapter(object):
    def __init__(self):
        self.map_size = None
        self.tile_Size = None

    def prepare_data(self):
        """
        prepare your data here - let empty if there is no need to
        :return: None
        """
        pass

    def force_redraw(self, surface):
        """
        forces to redraw whole map onto surface
        :param surface: pygame.Surface of whole map
        :return: None
        """
        raise NotImplementedError("whole map needs to be rendered")

    def render_animated_tiles(self, surface, rect=None):
        """
        re-render only animated tiles
        :param surface: pygame.Surface of map
        :param rect: pygame.Rect representing visible area that has to be redrawn
        :return: None
        """
        raise NotImplementedError("tiles wont be animated without that function")

    def render(self, surface, rect=None):
        """
        renders sprites of sprite group onto surface
        :param surface: pygame.Surface
        :param rect: pygame.Rect -> update specific area
        :return: None
        """
        raise NotImplementedError("sprites have to be rendered or they wont appear")

    def update(self, delta):
        """
        update sprites
        :param delta: delta time
        :return: None
        """
        raise NotImplementedError("sprites needs to get updated")


# --- This class is for CoreEngines own Format and requires specific files --- #
class TiledMap(DataAdapter):
    def __init__(self, filename, path=""):
        DataAdapter.__init__(self)
        self.path = path

        self._map_dictionary = json.load(open(os.path.join(path, filename), "r"))

        self.map_size = self._map_dictionary["PROPERTIES"]["MAPSIZE"]
        self.tile_size = self._map_dictionary["PROPERTIES"]["TILESIZE"]
        self._tiles = self._map_dictionary["TILES"]

        self._tile_data = {}
        self._animated_tiles = []

        self.main_sprites = pygame.sprite.LayeredDirty()

    def prepare_data(self):
        """
        prepares data for first use - exported into function to save memory and avoid cpu overhead
        :return: None
        """
        for tiledata in self._map_dictionary["REFERENCE"]:
            data = self._map_dictionary["REFERENCE"][tiledata]

            self._tile_data[tiledata] = {}
            self._tile_data[tiledata]["TYPE"] = data["TYPE"]

            if data["TYPE"] == "STATIC":
                if data["ISSHEET"]:
                    spritesheet = SpriteSheetCreator(data["FILENAME"], self.path)
                    image = spritesheet.get_image_clip(data["CLIP"])
                else:
                    image = load_image(data["FILENAME"], self.path, self.tile_size, colorkey=None)

                self._tile_data[tiledata]["IMAGE"] = image
            else:
                spritesheet = SpriteSheetCreator(data["FILENAME"], self.path)
                frames = [spritesheet.get_image_clip(clip) for clip in data["FRAMES"]]
                duration = int(data["DURATION"])

                self._tile_data[tiledata]["FRAMES"] = frames
                self._tile_data[tiledata]["DURATION"] = duration

    def force_redraw(self, surface):
        """
        redraws all tiles onto map
        :param surface: pygame.Surface
        :return: None
        """
        index = 0
        self._animated_tiles.clear()
        for y in range(self.map_size[1]):
            for x in range(self.map_size[0]):
                num = self._tiles[index]
                tile = self._tile_data[str(num)]
                if tile["TYPE"] == "STATIC":
                    surface.blit(tile["IMAGE"], (x * 32, y * 32))
                else:
                    self._animated_tiles.append(AnimatedTile((x * 32, y * 32), tile["FRAMES"], tile["DURATION"]))

                index += 1

    def render_animated_tiles(self, surface, rect=None):
        """
        render new animations
        :param surface: pygame.Surface
        :param rect: rect determines if its necessary to blit the tile
        :return: None
        """
        # todo render only if they changed may be ineffective due lag spikes
        for tile in self._animated_tiles:
            if rect.x-tile.rect.x <= tile.rect.x <= rect.right and rect.y-tile.rect.y <= tile.rect.y <= rect.bottom:
                if tile.is_dirty:
                    tile.render(surface)

    def render(self, surface, rect = None):
        """
        render sprites here
        :param surface: pygame.Surface
        :return: None
        """
        self.main_sprites.draw(surface)

    def update(self, delta):
        """
        updates sprites and tile animations
        :param delta: delta time
        :return: None
        """
        for tile in self._animated_tiles:
            tile.update()

        self.main_sprites.update()
        # todo if bottleneck : export to C Code
