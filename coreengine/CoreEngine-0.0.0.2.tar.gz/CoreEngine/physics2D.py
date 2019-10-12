import math
import os
import pygame


# 2D Physics

def sprite_collision(sprt_object, sprites_list, dokill=False) -> list:
    """
    tests sprite collision to sprite group
    :param sprt_object: single sprite
    :param sprites_list: sprite group
    :param dokill: bool  (true:kills sprite)
    :return:
    """
    return pygame.sprite.spritecollide(sprt_object, sprites_list, dokill)


def sprite_group_collision(group_a, group_b, dokill_a=False, dokill_b=False) -> dict:
    """
    tests if groups collide
    :param group_a: sprite group a
    :param group_b: sprite group b
    :param dokill_a: bool (true kills sprite)
    :param dokill_b: bool (true kills sprite)
    :return: dict containing sprites that colide
    """
    return pygame.sprite.groupcollide(group_a, group_b, dokill_a, dokill_b)


def raw_rect_collision(object_a, object_list):
    """
    rect collision - optimized for physics ; require specific input
    :param object_a: single pygame.Rect
    :param object_list: list of rects
    :return: rects that collide
    """
    return [obj for obj in object_list if obj.colliderect(object_a)]


# 2D Physics Object

class PhysicsBody2D(object):
    def __init__(self, pos, size):
        self.pos = pos
        self.x, self.y = pos
        self.size = size
        self.rect = pygame.Rect(*self.pos, *self.size)

    def move(self, movement, collision_objects: list):
        """
        checks if movement is possible otherwise return dict with bool indicate collisions
        :param movement: vector movement
        :param collision_objects: list of collision rect
        :return: dict containing collision obj and marker
        """
        self.x += movement[0]
        self.rect.x = int(self.x)
        hit_objects_list = raw_rect_collision(self.rect, [obj.rect for obj in collision_objects])
        collision_types = {
            'top': False, 'bottom': False, 'right': False, 'left': False, 'slant_bottom': False, 'data': []
        }

        for block in hit_objects_list:
            markers = [False, False, False, False]
            if movement[0] > 0:
                self.rect.right = block.left
                collision_types['right'] = True
                markers[0] = True
            elif movement[0] < 0:
                self.rect.left = block.right
                collision_types['left'] = True
                markers[1] = True
            collision_types['data'].append([block, markers])
            self.x = self.rect.x

            self.y += movement[1]
            self.rect.y = int(self.y)
            hit_objects_list = raw_rect_collision(self.rect, collision_objects)
            for block in hit_objects_list:
                markers = [False, False, False, False]
                if movement[1] > 0:
                    self.rect.bottom = block.top
                    collision_types['bottom'] = True
                    markers[2] = True
                elif movement[1] < 0:
                    self.rect.top = block.bottom
                    collision_types['top'] = True
                    markers[3] = True
                collision_types['data'].append([block, markers])
                self.y = self.rect.y

            return collision_types
