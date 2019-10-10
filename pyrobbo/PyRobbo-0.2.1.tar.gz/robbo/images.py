# coding: utf8
# Copyright (C) 2019 Maciej Dems <maciej.dems@p.lodz.pl>
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of GNU General Public License as published by the
# Free Software Foundation; either version 3 of the license, or (at your
# opinion) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
import pygame

from pkg_resources import resource_stream


MAGNET_R = 0
MAGNET_L = 1
WALL_GRAY = 2
WALL_RED = 3
SCREW = 4
BULLET = 5
BOX = 6
KEY = 7
BOMB = 8
DOOR = 9
QUESTION = 10
BEAR1 = 11
BEAR2 = 12
BIRD1 = 13
BIRD2 = 14
CAPSULE1 = 15
CAPSULE2 = 16
VOID = 17
BOX_SLIDE = 18
LIFE = 20
STARS3 = 21
STARS2 = 22
STARS1 = 23
GRASS = 24
WALL_GREEN = 25
DEVIL1 = 26
DEVIL2 = 27
BUTTERFLY1 = 28
BUTTERFLY2 = 29
BLAST_H1 = 30
BLAST_H2 = 31
BLAST_V1 = 32
BLAST_V2 = 33
S_PARTS = 34
S_LIFES = 35
S_KEYS = 36
S_BULLETS = 37
S_LEVEL = 38
FORCE1 = 39
FORCE2 = 49
TELEPORT1 = 40
TELEPORT2 = 41
GUN_E = 45
GUN_S = 46
GUN_W = 47
GUN_N = 48
ROBBO_E1 = 50
ROBBO_E2 = 51
ROBBO_S1 = 52
ROBBO_S2 = 53
ROBBO_W1 = 54
ROBBO_W2 = 55
ROBBO_N1 = 56
ROBBO_N2 = 57


class Images(object):
    """
    Class responsible for visuals managements

    Unlike sounds this is kept in class, so multiple skin pack can be selected.
    """

    def __init__(self, skin='default'):
        self.image = pygame.image.load(resource_stream('robbo', 'skins/'+skin+'/icons.png')).convert_alpha()
        self.digits = pygame.image.load(resource_stream('robbo', 'skins/'+skin+'/digits.png')).convert_alpha()

    def _get_icon_rect(self, n):
        """
        Get icon location in the skin image
        """
        return pygame.Rect(34*(n%10)+2, 34*(n//10)+2, 32, 32)

    def get_icon(self, n):
        """Funkcja zwraca obrazek o danym numerze"""
        rect = pygame.Rect(0,0, 32,32)
        img = pygame.Surface((32,32)).convert_alpha()
        img.fill((0,0,0,0))
        img.blit(self.image, rect, self._get_icon_rect(n))
        return img

    def _get_digit_rect(self, n):
        """Funkcja zwraca rect danej cyfry"""
        return pygame.Rect(18*n,0,16,32)

    def get_digits(self):
        """Funkcja zwraca tablicę zawierającą dane cyfry"""
        digits = []
        rect = pygame.Rect(0,0, 16,32)
        for n in range(10):
            img = pygame.Surface((16,32)).convert_alpha()
            img.fill((0,0,0,0))
            img.blit(self.digits, rect, self._get_digit_rect(n))
            digits.append(img)
        return digits
