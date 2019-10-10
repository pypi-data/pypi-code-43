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
import sys
import shutil
import argparse
import yaml
from pkg_resources import resource_listdir
import pygame
from pygame.constants import K_UP, K_DOWN, K_RETURN

from .defs import *
from .levels import load_levels

clock = None
clock_speed = None
screen = None
screen_rect = None
skin = 'default'

parser = argparse.ArgumentParser()
parser_screen = parser.add_mutually_exclusive_group()
parser_screen.add_argument('-f', '--fullscreen', help="start in fullscreen", action='store_true')
parser_screen.add_argument('-w', '--window', help="start in window", action='store_true')
parser.add_argument('-s', '--skin', help="selected skin set", type=str)
parser.add_argument("levelset", help="name of the level set to install", nargs='*')


level_sets = ['original']
levelset = 'original'

levels = {}


def save():
    from . import game, sounds
    config = {
        'levelset': levelset,
        'levels': levels,
        'cleverbears': game.clever_bears,
        'fullscreen': bool(screen.get_flags() & pygame.FULLSCREEN),
        'skin': skin,
        'mute': sounds.mute,
    }
    yaml.dump(config, open(CONFIG_FILE, 'w'), default_flow_style=False)


def quit():
    save()
    pygame.quit()
    sys.exit(0)


def select_levelset():
    screen.set_clip(screen.get_rect())
    X, Y, W, H = 64, 432, 512, 32
    rect = pygame.Rect(X, Y, W, H)

    font = pygame.font.Font(None, 46)

    try:
        level = level_sets.index(levelset)
    except ValueError:
        level = level_sets.index('original')

    while True:
        text = font.render(level_sets[level].upper(), 0, (255, 255, 255))
        screen.fill((0, 0, 0), rect)
        w = text.get_width()
        screen.blit(text, (X + (W-w)//2, Y))
        pygame.display.flip()
        event = pygame.event.wait()
        if event.type == pygame.QUIT:
            quit()
        elif event.type == pygame.KEYDOWN:
            if event.key == K_UP:
                level = (level - 1) % len(level_sets)
            if event.key == K_DOWN:
                level = (level + 1) % len(level_sets)
            if event.key == K_RETURN:
                screen.fill((0, 0, 0), rect)
                return level_sets[level]
        pygame.event.pump()


def main():
    args = parser.parse_args()

    try:
        config_file = open(CONFIG_FILE, 'r')
        try:
            config = yaml.load(config_file, Loader=yaml.SafeLoader)
        except TypeError:
            config = yaml.load(config_file)
    except FileNotFoundError:
        config = {}

    if args.fullscreen:
        flags = pygame.FULLSCREEN
    elif args.window:
        flags = 0
    else:
        flags = pygame.FULLSCREEN if config.get('fullscreen', True) else 0

    pygame.init()
    pygame.display.set_caption('PyRobbo')
    pygame.key.set_repeat(0,0)

    global skin, level_sets, levelset, levels, clock, clock_speed, screen, screen_rect
    if args.skin is not None:
        skin = args.skin
    else:
        skin = config.get('skin', skin)
    clock = pygame.time.Clock()
    clock_speed = 8
    screen = pygame.display.set_mode((640, 480), flags)
    screen_rect = pygame.Rect((64, 32), (512, 384))

    if args.levelset:
        install = [arg for arg in args.levelset if arg.endswith('.dat') and os.path.isfile(arg)]
        if install:
            try:
                user_levels_dir = os.path.join(USER_DATA_DIR, 'levels')
                os.makedirs(user_levels_dir, exist_ok=True)
            except OSError:
                pass
            else:
                for i in install:
                    try:
                        shutil.copy(i, user_levels_dir)
                    except (OSError, IOError):
                        pass
                    else:
                        config['levelset'] = os.path.basename(i)[:-4]

    levels = config.get('levels', {})
    level_sets = set(dat[:-4] for dat in resource_listdir('robbo', 'levels') if dat.endswith('.dat'))
    for data_dir in DATA_DIRS:
        try:
            level_sets |= set(dat[:-4] for dat in os.listdir(os.path.join(data_dir, 'levels')) if dat.endswith('.dat'))
        except FileNotFoundError:
            continue
    level_sets |= set(dat[:-4] for dat in os.listdir('.') if dat.endswith('.dat'))
    levelset = config.get('levelset', levelset)
    level_sets = list(level_sets)
    level_sets.sort()
    level = config.get('levels', {}).get(levelset, 0)

    from . import game, sounds
    game.clever_bears = config.get('cleverbears', False)
    sounds.mute = config.get('mute', sounds.mute)

    while True:
        try:
            game.levels = load_levels(levelset)
        except:
            import traceback
            traceback.print_exc()
            li = level_sets.index(levelset)
            del level_sets[li]
            levelset = level_sets[li % len(level_sets)]
        else:
            while level < len(game.levels):
                try:
                    levels[levelset] = level
                    save()
                    game.play_level(level)
                except game.SelectLevel as selected:
                    if 0 <= selected.level < len(game.levels):
                        level = selected.level
                except game.ChangeLevelSet:
                    selected = select_levelset()
                    if selected != levelset:
                        try:
                            newlevels = load_levels(selected)
                        except:
                            import traceback
                            traceback.print_exc()
                            level_sets.remove(selected)
                        else:
                            levelset = selected
                            level = levels.get(levelset, 0)
                            game.levels = newlevels
                else:
                    level += 1
            levelset = level_sets[(level_sets.index(levelset) + 1) % len(level_sets)]
            level = 0

