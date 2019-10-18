#!/usr/bin/env python3
from PIL import Image
import random


class Sprite:
    def __init__(self, label, x1, y1, x2, y2):
        self.__argument_type_checker([label, x1, y1, x2, y2])
        self._label = label
        self._x1 = x1
        self._y1 = y1
        self._x2 = x2
        self._y2 = y2

    def __argument_type_checker(self, number_ls):
        """
        Check type of each element and raise ValueError
        if any element in number_ls was not satisfying conditions.
        :param number_ls:
        :return: a ValueError if any element in number_ls was not satisfying conditions.
        """

        for item in number_ls:
            if type(item) != int or item < 0:
                raise ValueError('Invalid coordinates.')

        if (not number_ls[3] >= number_ls[1]) or (not number_ls[-1] >= number_ls[2]):
            raise ValueError('Invalid coordinates.')

    @property
    def label(self):
        return self._label

    @property
    def top_left(self):
        return self._x1, self._y1

    @property
    def bottom_right(self):
        return self._x2, self._y2

    @property
    def width(self):
        return (self._x2 - self._x1) + 1

    @property
    def height(self):
        return (self._y2 - self._y1) + 1


class LabelMap:
    """
    A 2D array of integers of equal dimension (width and height) 
    as the original image where the sprites are packed in. 
    The label_map array maps each pixel of the image passed to the function
    to the label of the sprite this pixel corresponds to, 
    or 0 if this pixel doesn't belong to a sprite (e.g., background color).
    """
    def __init__(self):
        self.label_map = []
        self.max_x = 0
        self.max_y = 0


    def init_map(self, amount_row, amount_column):
        """
        Initialization the map follow the amount is provided and
        set the max value for row and column.
        """
        self.max_x = amount_row
        self.max_y = amount_column

        for row in range(amount_row):
            elements = []
            for column in range(amount_column):
                elements.append(0)
            self.label_map.append(elements)

    def set_pixel_label(self, x, y, label):
        """
        Set label for a pixel.
        """
        self.label_map[x][y] = label

    def check_pixel(self, x, y):
        """
        Check a pixel's position is have label or not. 
        """
        return self.label_map[x][y] == 0

    def get_max_row(self):
        """
        Get the max value of the row.
        """
        return self.max_x

    def get_max_column(self):
        """
        Get the max value of the column.
        """
        return self.max_y

    def get_label_map(self):
        """
        Get the label map.
        """
        return self.label_map



class SpriteSheet:

    def __init__(self, fb, background_color=None):
        self.image = fb
        self.color = background_color 
        self.sprites = {}
        self.label_map = []
        self.sprite_labels_image = []

    @property
    def background_color(self):
        if self.color is not None:
            return self.color
        else:
            return self.find_most_common_color(self.image)

    @staticmethod
    def find_most_common_color(image):
        """
        Find the Most Common Color in an Image.
        :param image:
        :return:
        an integer if the mode is grayscale;
        a tuple (red, green, blue) of integers (0 to 255) if the mode is RGB;
        a tuple (red, green, blue, alpha) of integers (0 to 255) if the mode is RGBA.
        """
        colors = image.getcolors(image.size[0] * image.size[1])
        return sorted(colors, key=lambda x: x)[-1][1]

    def __check_image(self):
        try:
            self.image = Image.open(self.image)
            if (self.image.mode == 'P'): raise ValueError("The image mode 'P' is not supported")
        except FileNotFoundError:
            raise FileNotFoundError("No such file or directory. Please check again!")
        except AttributeError:
            self.image = self.image
            if (self.image.mode == 'P'): raise ValueError("The image mode 'P' is not supported")
        

    def __get_background_color(self):
        """
        Identifies the background color of a image.
        """

        if self.image.mode == 'RGBA':
            return (0, 0, 0, 0)

        return self.find_most_common_color(self.image)

    
    def __create_label(self, sprites):
        """
        Create a label which is unique strictly positive integers and 
        no particular order with other keys in dictionary sprites.
        """
        number = random.randint(1, 256)

        while number in sprites.keys():
            number = random.randint(1, 256)

        return number

    def __update_sprites(self, sprites):
        """
        Map each value of each key to Sprite object.
        """
        
        for key, value in sprites.items():
            min_y = min(value, key=lambda x: x[0])[0]
            min_x = min(value, key=lambda x: x[1])[1]

            max_y = max(value, key=lambda x: x[0])[0]
            max_x = max(value, key=lambda x: x[1])[1]
            
            sprites[key] = Sprite(key, min_y, min_x, max_y, max_x)
        
        return sprites

    def __check_pixel_derection(self, pixel, list_wait, sprites, label_map, background_color, label):
        """
        Check neighbours of a pixels in 8 directions, update the value inside
        list_wait, sprites and label_map.
        """
        direct = [[0, 1], [1, 1], [1, 0], [1, -1],
                [0, -1], [-1, -1], [-1, 0], [-1, 1]]

        max_x = label_map.get_max_row()
        max_y = label_map.get_max_column()

        for each in direct:
            x, y = pixel[1], pixel[0]
            x += each[0]
            y += each[1]
    
            if 0 <= x < max_x and 0 <= y < max_y:
                if self.image.getpixel((y, x)) != background_color and label_map.check_pixel(x, y):
                    label_map.set_pixel_label(x, y, label)
                    pixel = (y, x)
                    sprites[label].append(pixel)
                    list_wait.append(pixel)

        return list_wait, sprites, label_map

    def find_sprites(self):
        """
        Find all the sprites of an image.
        """
        self.__check_image()

        if not self.sprites and not self.label_map:
            label_map = LabelMap()
            label_map.init_map(self.image.size[1], self.image.size[0])

            sprites = {}
            label = self.__create_label(sprites)
            background_color = self.background_color

            for row in range(self.image.size[1]):
                for column in range(self.image.size[0]):
                    current_p = (column, row)
                    color = self.image.getpixel(current_p)

                    if color != background_color and label_map.check_pixel(row, column):
                        sprites[label] = [current_p]
                        list_wait = [current_p]

                        while(list_wait):
                            pixel = list_wait.pop(0)
                            list_wait, sprites, label_map = self.__check_pixel_derection(
                                pixel, list_wait, sprites, label_map, background_color, label)

                        label = self.__create_label(sprites)

            self.sprites = self.__update_sprites(sprites)
            self.label_map = label_map.get_label_map()

        return self.sprites, self.label_map


    def __random_color(self, label_color):
        """
        Generate a tuple of color which is not in the value of label_color dict.
        """
        color = tuple([random.randint(0, 255),random.randint(0, 255),random.randint(0, 255)])

        while color in label_color.values():
            color = tuple([random.randint(0, 255),random.randint(0, 255),random.randint(0, 255)])
        
        return color


    def __generate_color_dict(self, sprites, background_color):
        """
        Generate a dictionary of color corresponding with each label in the sprites.
        """

        label_color = {0: background_color}
        
        for key in sprites.keys():
            label_color[key] = self.__random_color(label_color)
        
        return label_color


    def __change_image_pixel_color(self, max_row, max_column, label_map, label_color, image):
        """
        Change each pixel corresponding with each label in the label_map.
        """
        for row in range(max_row):
            for column in range(max_column):
                color = label_color[label_map[row][column]]
                image.putpixel((column, row), color)

        return image


    def __change_bounding_boxes_color(self, sprites, label_color, image):
        """
        Change each pixel which is the bounding box of the sprite corresponding with each label.
        """
        for key, value in sprites.items():
            color = label_color[key]

            for each in range(value.top_left[0], value.bottom_right[0]):
                image.putpixel((each, value.top_left[1]), color)
                image.putpixel((each, value.bottom_right[1]), color)

            for item in range(value.top_left[1], value.bottom_right[1]):
                image.putpixel((value.top_left[0], item), color)
                image.putpixel((value.bottom_right[0], item), color)

        return image

    def create_sprite_labels_image(self, background_color=()):
        """
        Draws the masks of the sprites at the exact same position 
        that the sprites were in the original image
        with with a random uniform color (one color per sprite mask).
        """
        self.__check_image()

        if not self.sprite_labels_image:
            if len(background_color) == 0:
                background_color = (255, 255, 255)

            sprites, label_map = self.find_sprites()

            max_row = len(label_map)
            max_column = len(label_map[0])

            image = Image.new('RGB', (max_column, max_row), background_color)

            label_color = self.__generate_color_dict(sprites, background_color)

            image = self.__change_image_pixel_color(max_row, max_column, label_map, label_color, image)
            image = self.__change_bounding_boxes_color(sprites, label_color, image)

            self.sprite_labels_image = image

        return self.sprite_labels_image
