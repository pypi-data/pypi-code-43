from PIL import Image
import numpy as np
import random

import pprint
import timeit


class Sprite:
    def __init__(self, label, x1, y1, x2, y2):
        self._check_valid_constructor(label, x1, y1, x2, y2)
        self.__label = label
        self.__top_left = (x1, y1)
        self.__bottom_right = (x2, y2)
        self.__width = x2 - x1 + 1
        self.__height = y2 - y1 + 1

    def _check_valid_constructor(self, *args):
        if not any(isinstance(arg, int) for arg in args)\
                or any(int(arg) < 0 for arg in args)\
                or args[3] < args[1] or args[4] < args[2]:
            raise ValueError("Invalid coordinates")

    @property
    def label(self):
        return self.__label

    @property
    def top_left(self):
        return self.__top_left

    @property
    def bottom_right(self):
        return self.__bottom_right

    @property
    def width(self):
        return self.__width

    @property
    def height(self):
        return self.__height


class SpriteSheet:
    def __init__(self, fd, background_color=None):
        self.__fd = fd
        self.__background_color = background_color
        self.__sprites = {}
        self.__label_map = []

    def __set_image(self):
        try:
            self.__image = Image.open(self.__fd)
        except AttributeError:
            self.__image = self.__fd
        except FileNotFoundError:
            raise FileNotFoundError(f"{self.__fd} is not found")

    def __check_valid(self):
        self.__set_image()
        if self.__image.mode == 'P':
            raise ValueError("'The image mode 'P' is not supported")

    @property
    def background_color(self):
        return self.find_most_common_color(self.__image
                                           ) if not self.__background_color else self.__background_color

    @staticmethod
    def find_most_common_color(image):
        """Find image most common color

        Arguments:
            image {PIL.Image}
        """
        colors = image.getcolors(image.width * image.height)
        max_occurence, most_present = 0, 0
        try:
            for c in colors:
                if c[0] > max_occurence:
                    (max_occurence, most_present) = c
            return most_present
        except TypeError:
            raise Exception("Too many colors in the image")
        else:
            raise Exception()

    def find_sprites(self):
        """Waypoint 3: 

        Arguments:
            image {Pillow.Image} -- an image object

        Returns:
            sprites {dict} -- a dictionary of key-value pair where kwy is the
                sprite label and value is the sprite Spite object
            label_map {list} -- a list of maped label where background pixel is 
                labeled 0 and other pixels is labeled aas its sprite label
        """
        self.__check_valid()

        if not self.__sprites and not self.__label_map:
            sprites = {}
            direction = [(-1, 1), (0, 1), (1, 1), (-1, 0),
                         (1, 0), (-1, -1), (0, -1), (1, -1)]
            pixels = np.asarray(self.__image)

            image_width = self.__image.width
            image_height = self.__image.height

            background_color = list(self.background_color)

            label = 0  # define first label

            # loop through every pixels
            label_map = np.zeros((image_height, image_width), dtype=int)

            for i in range(len(pixels)):
                for j in range(len(pixels[0])):
                    if pixels[i, j].tolist() != background_color and not label_map[i, j]:
                        label += 1
                        sprites.update({label: []})
                        label_map[i, j] = label
                        curr_pixels = [(i, j)]
                        while curr_pixels:
                            pixel = curr_pixels.pop(0)
                            for (x, y) in direction:
                                if 0 <= (pixel[0] + x) < len(pixels) and 0 <= (pixel[1] + y) < len(pixels[0]) \
                                        and pixels[pixel[0] + x, pixel[1] + y].tolist() != background_color \
                                        and not label_map[pixel[0] + x, pixel[1] + y]:
                                    label_map[pixel[0] + x, pixel[1] +
                                              y] = label_map[pixel[0], pixel[1]]
                                    curr_pixels.append(
                                        (pixel[0] + x, pixel[1] + y))
                                    sprites[label].append(
                                        (pixel[0] + x, pixel[1] + y))

            # Make Sprite obj
            for label, px in sprites.items():
                y1 = min(px, key=lambda x: x[0])[0]
                x1 = min(px, key=lambda x: x[-1])[-1]
                y2 = max(px, key=lambda x: x[0])[0]
                x2 = max(px, key=lambda x: x[-1])[-1]
                sprites[label] = Sprite(label, x1, y1, x2, y2)

            self.__sprites = sprites
            self.__label_map = label_map.tolist()

        return (self.__sprites, self.__label_map)

    def create_sprite_labels_image(self, background_color=(255, 255, 255)):
        """Waypoint 4:

        Arguments:
            sprites {dict} -- a key:value pair of sprite label and its Sprite object
            label_map {list} -- a list of label_map 

        Returns:
            [type] -- [description]
        """
        self.__check_valid()
        sprites, label_map = self.find_sprites()
        mode = 'RGB' if len(background_color) == 3 else 'RGBA'
        size = (len(label_map[0]), len(label_map))
        new_image = Image.new(mode, size, background_color)
        px = new_image.load()

        colors = []

        for label, sprite in sprites.items():
            color = list(np.random.choice(range(256), size=3))
            while color in colors:
                color = list(np.random.choice(range(256), size=3))

            if mode == 'RGBA':
                color = tuple(color + [255])
            else:
                color = tuple(color)

            x1, y1 = sprite.top_left
            x2, y2 = sprite.bottom_right

            for r_idx, row in enumerate(label_map):
                for c_idx, col in enumerate(row):
                    if col == label:
                        px[c_idx, r_idx] = color

            for x in range(sprite.width):
                px[x1 + x, y1] = color
                px[x2 - x, y2] = color
            for y in range(sprite.height):
                px[x1, y1 + y] = color
                px[x2, y2 - y] = color

        return new_image
