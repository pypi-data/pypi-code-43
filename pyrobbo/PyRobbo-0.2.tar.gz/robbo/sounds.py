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

mute = False


def play(sound):
    if not mute:
        sound.play()


blaster = pygame.mixer.Sound(resource_stream('robbo', 'sounds/blaster.wav'))
bomb = pygame.mixer.Sound(resource_stream('robbo', 'sounds/bomb.wav'))
bullet = pygame.mixer.Sound(resource_stream('robbo', 'sounds/bullet.wav'))
die = pygame.mixer.Sound(resource_stream('robbo', 'sounds/die.wav'))
door = pygame.mixer.Sound(resource_stream('robbo', 'sounds/door.wav'))
finish = pygame.mixer.Sound(resource_stream('robbo', 'sounds/finish.wav'))
key = pygame.mixer.Sound(resource_stream('robbo', 'sounds/key.wav'))
lastscrew = pygame.mixer.Sound(resource_stream('robbo', 'sounds/lastscrew.wav'))
life = pygame.mixer.Sound(resource_stream('robbo', 'sounds/life.wav'))
push = pygame.mixer.Sound(resource_stream('robbo', 'sounds/push.wav'))
screw = pygame.mixer.Sound(resource_stream('robbo', 'sounds/screw.wav'))
shoot = pygame.mixer.Sound(resource_stream('robbo', 'sounds/shoot.wav'))
teleport = pygame.mixer.Sound(resource_stream('robbo', 'sounds/teleport.wav'))
wallshoot = pygame.mixer.Sound(resource_stream('robbo', 'sounds/wallshoot.wav'))
spawn = pygame.mixer.Sound(resource_stream('robbo', 'sounds/spawn.wav'))
