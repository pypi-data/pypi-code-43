import math
import time

import pygame

from CoreEngine.physics2D import PhysicsBody2D


# todo update animations

class Entity(pygame.sprite.DirtySprite):
    """
    parent Entity class
    """

    def __init__(self, pos, size):
        pygame.sprite.DirtySprite.__init__(self)
        self.dirty = 1
        self._layer = 0
        self.visible = True

        self.physics_body = PhysicsBody2D(pos, size)
        self.rect = self.physics_body.rect  # transfer rect reference
        self._horizontal_flipped = False
        self._vertical_flipped = False

    def update(self, *args):
        pass

    @property
    def layer(self):
        """
        get layer
        :return: self._layer
        """
        return self._layer

    @layer.setter
    def layer(self, value):
        """
        set layer - value transform to int
        :param value: new layer
        :return: None
        """
        self._layer = int(value)

    def set_position(self, new_pos):
        """
        set position
        :param new_pos:
        :return:
        """
        self.physics_body.rect.x = new_pos[0]
        self.physics_body.rect.y = new_pos[1]

    def move(self, momentum, objects=None):
        """
        move and check for collisions
        :param momentum: vector movement
        :param objects: default None otherwise list of objects
        :return: physics body.move dict
        """
        if objects is None:
            objects = []
        assert type(object) != list
        return self.physics_body.move(momentum, objects)

    def set_flip(self, horflip=False, verflip=False):
        """
        set flip flag for image
        :param horflip: horizontal flip : bool
        :param verflip: horizontal flip :bool
        :return: None
        """
        self._horizontal_flipped = horflip
        self._vertical_flipped = verflip

    def get_entity_angle(self, entity_2):
        """
        get angle to another entity
        :param entity_2: CoreEngine.Entity obj
        :return: angle
        """
        x1 = self.rect.x + int(self.rect.size[0] / 2)
        y1 = self.rect.y + int(self.rect.size[1] / 2)
        x2 = entity_2.rect.x + int(entity_2.rect.size[0] / 2)
        y2 = entity_2.rect.y + int(entity_2.rect.size[1] / 2)
        angle = math.atan((y2 - y1) / (x2 - x1))
        if x2 < x1:
            angle += math.pi
        return angle

    def get_center(self):
        """
        get center of : self
        :return: center of : self
        """
        x = self.rect.x + int(self.rect.size[0] / 2)
        y = self.rect.y + int(self.rect.size[1] / 2)
        return [x, y]


class SimpleEntity(Entity):
    """
    simplified Entity obj for None-animated Entities
    default dirty is set to 2
    """

    def __init__(self, image, size, pos):
        Entity.__init__(self, pos, size)
        self.image = image
        self.dirty = 2


class ComplexEntity(Entity):
    """
    complex entity class for animated Entities
    """

    def __init__(self, animationset, position, size, startanimation="IDLE"):
        Entity.__init__(self, position, size)
        self.animationset = animationset  # set of animations
        self.position = position  # init pos
        self._current_animation = startanimation  # start animation
        try:
            self.image = self.animationset[self._current_animation]["FRAMES"][0]
        except Exception as err:
            print(err)
            print("Check AnimationSet Syntax with print(CoreEngine.animationSyntax)  or use SimpleEntity instead")
            raise SystemExit
        self.doAnimation = True

    def update(self, *args):
        """
        update sprite mechanics here
        :param args: *args
        :return: None
        """
        self.update_animation(*args)

    def update_animation(self, *args):
        """
        updates animation
        :param args: args
        :return: None
        """
        if self.doAnimation:
            self.dirty = 1
            self.image = self.animationset[self._current_animation]["FRAMES"][math.floor(
                (time.time() % self.animationset[self._current_animation]["TICKS"]) * len(
                    self.animationset[self._current_animation]["FRAMES"]) / self.animationset[self._current_animation][
                    "TICKS"])]

            if self._horizontal_flipped or self._vertical_flipped:
                self.image = pygame.transform.flip(self.image, self._horizontal_flipped, self._vertical_flipped)

    @property
    def animation(self):
        """
        get animation
        :return: None
        """
        return self._current_animation

    @animation.setter
    def animation(self, ani: str):
        """
        set animation
        :param ani: str
        :return: None
        """
        self._current_animation = ani

    def toggle_animation(self, toggle: bool):
        """
        toggle animation
        :param toggle: bool
        :return: None
        """
        self.doAnimation = toggle

    def force_stop_animation(self):
        self.doAnimation = False
