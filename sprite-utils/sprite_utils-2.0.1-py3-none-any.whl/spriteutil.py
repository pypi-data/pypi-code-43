from PIL import Image
import numpy as np


class Sprite:
    """
    An object represent a sprite

    :raise ValueError: if one or more arguments label, x1, y1, x2,
        and y2 is not positive integer, or if the arguments x2 and
        y2 is not equal or greater respectively than x1 and y1
    """
    def __init__(self, label, x1, y1, x2, y2):
        self.__check_valid_params(label, x1, y1, x2, y2)
        self.__label = label
        self.__x1 = x1
        self.__y1 = y1
        self.__x2 = x2
        self.__y2 = y2

    @property
    def label(self):
        return self.__label

    @property
    def top_left(self):
        return (self.__x1, self.__y1)

    @property
    def bottom_right(self):
        return (self.__x2, self.__y2)

    @property
    def width(self):
        return self.__x2 - self.__x1 + 1

    @property
    def height(self):
        return self.__y2 - self.__y1 + 1
    
    def add(self, x, y):
        self.__x1 = min(self.__x1, x)
        self.__y1 = min(self.__y1, y)
        self.__x2 = max(self.__x2, x)
        self.__y2 = max(self.__y2, y)
    
    @staticmethod
    def __check_valid_params(*args):
        if not any([isinstance(arg, int) and int(arg) >= 0 for arg in args])\
            or args[3] < args[1] or args[4] < args[2]:
            raise ValueError("Invalid coordinates")


class SpriteSheet:
    """
    A SpriteSheet module
    """
    def __init__(self, fd, background_color=None):
        """
        :params fd: the name and path (a string) that references an image file in the local file system;
            + a pathlib.Path object that references an image file in the local file system ;
            + a file object that MUST implement read(), seek(), and tell() methods, and be opened in binary mode;
            + a Image object.
        :params background_color: that identifies the background color (i.e., transparent color) of the image.
            The type of background_color argument depends on the images' mode:
                + an integer if the mode is grayscale;
                + a tuple (red, green, blue) of integers if the mode is RGB;
                + a tuple (red, green, blue, alpha) of integers if the mode is RGBA. The alpha element is optional.
                    If not defined, while the image mode is RGBA, the constructor considers the alpha element to be 255.
        """
        self.image_object = self.__get_image_object(fd)
        self.__background_color = background_color
        self.__sprites = None
        self.__label_map = None

    
    @staticmethod
    def __get_image_object(fd):
        """
        Read file and return an PIL Image object

        :returns image_object: a Image object
        """
        if isinstance(fd, Image.Image):
            return fd
        try:
            image_object = Image.open(fd)
            return image_object
        except IOError:
            raise TypeError("fd is not valid")

    @staticmethod
    def __find_most_common_color(image_object):
        """
        Return the most common color in an image

        :params image_object: an image object created with PIL

        :returns max_color: most repeated color of the image
        """
        size = np.prod(image_object.size)
        colors_count = image_object.getcolors(maxcolors=size)

        # return a tuple of (max_color_count, max_color)
        _, max_color = max(colors_count, key=lambda v: v[0])
        return max_color

    @property
    def background_color(self):
        """
        :returns the background color of the image that was passed 
            to the constructor of the class SpriteSheet. 
            If the argument background_color that was passed to the constructor of this class was None, 
            the function of the read-only property background_color calls the static method 
            find_most_common_color to determine the background color of the image
        """
        if self.__background_color:
            return self.__background_color
        return self.__find_most_common_color(self.image_object)

    
    def find_sprites(self):
        """
        Loop through an image object and return all sprite

        :params image: a PIL image object
        
        :returns a tuple (sprites, label_map)
        """
        width, height = self.image_object.size
        label_map = np.zeros([height, width], dtype=int)
        directions = [(-1, 1), (0, 1), (1, 1), (-1, 0),
                    (1, 0), (-1, -1), (0, -1), (1, -1)]
        pixels = np.asarray(self.image_object)
        sprites = {}
        sprite_count = 0
        for y in range(len(pixels)):
            for x in range(len(pixels[0])):
                # if pixel color is foreground
                if pixels[y, x].tolist() != list(self.background_color) and not label_map[y, x]:

                    # create a sprite object for this pixel
                    sprite_count += 1
                    sprite = Sprite(label=sprite_count, x1=x, y1=y, x2=x, y2=y)
                    label_map[y, x] = sprite_count
                    visited_pixel = [(x, y)]

                    # check nearest neighbors for a valid label
                    while visited_pixel:
                        labeled_x, labeled_y = visited_pixel.pop()
                        for direction in directions:
                            adjacent_x = labeled_x + direction[1]
                            adjacent_y = labeled_y + direction[0]
                            if len(pixels[0]) > adjacent_x >= 0 and len(pixels) > adjacent_y >= 0\
                                and pixels[adjacent_y, adjacent_x].tolist() != list(self.background_color)\
                                and not label_map[adjacent_y, adjacent_x]:
                                visited_pixel.append((adjacent_x, adjacent_y))
                                sprite.add(adjacent_x, adjacent_y)
                                label_map[adjacent_y, adjacent_x] = sprite_count
                    sprites[sprite_count] = sprite

        # assign as private variables
        self.__sprites = sprites
        self.__label_map = label_map.tolist()

        return (sprites, label_map.tolist())

    def create_sprite_labels_image(self, background_color=(255, 255, 255)):
        """
        Draws the masks of the sprites at the exact same position that the sprites were in the original image
        
        :params sprites: a key, value pair of sprite label and its Sprite object
        :params label_map: a list of label_map 
        :params background_color: image background color. Just accept (red, green, blue)
                tuple or (red, green, blue, alpha)
        
        :returns new_image: an image of equal dimension (width and height) as the original image
        """
        if not self.__sprites and not self.__label_map:
            self.find_sprites()

        if not isinstance(background_color, tuple):
            background_color = (255, 255, 255)
        mode = 'RGB' if len(background_color) == 3 else 'RGBA'
        size = (len(self.__label_map[0]), len(self.__label_map))
        new_image = Image.new(mode, size, background_color)
        px = new_image.load()

        colors = []

        for label, sprite in self.__sprites.items():

            color = list(np.random.choice(range(256), size=3))
            while color in colors:
                color = list(np.random.choice(range(256), size=3))

            if mode == 'RGBA':
                color = tuple(color + [255])
            else: 
                color = tuple(color)

            x1, y1 = sprite.top_left
            x2, y2 = sprite.bottom_right

            for r_idx, row in enumerate(self.__label_map):
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
