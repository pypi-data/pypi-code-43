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
from pygame.constants import QUIT, KEYDOWN, KEYUP, K_UP, K_DOWN, K_LEFT, K_RIGHT, K_b, K_f, K_q, K_x, K_l, K_m, \
    K_PLUS, K_EQUALS, K_MINUS, KMOD_SHIFT, KMOD_CTRL, KMOD_ALT, KMOD_META, K_LCTRL, K_RCTRL, K_w, K_s, K_a, K_d

from .defs import *

levels = None
images = None
status = None
board = None
robbo = None

from . import screen, screen_rect, clock, clock_speed, skin, sounds, quit
from .board import Board
from .images import Images
from .status import Status

# Register all sprites — do not remove the line below
from .sprites import explode


clever_bears = False

MOVES = {
    K_UP: NORTH,
    K_DOWN: SOUTH,
    K_LEFT: WEST,
    K_RIGHT: EAST,
    K_w: NORTH,
    K_s: SOUTH,
    K_a: WEST,
    K_d: EAST
}

SCROLLS = {
    K_UP: SCROLL_UP,
    K_DOWN: SCROLL_DOWN,
    K_w: SCROLL_UP,
    K_s: SCROLL_DOWN
}


class EndLevel(Exception):
    """End level exception"""
    pass


class SelectLevel(Exception):
    """Level selected exception"""
    def __init__(self, level):
        self.level = level


class ChangeLevelSet(Exception):
    """Load levels exception"""
    pass


def update_sprites():
    board.sprites_update.update()
    board.sprites_blast.update()


def draw_sprites():
    screen.blit(board.background, board.rect, board.rect)
    board.sprites.draw(screen)
    pygame.display.flip()


def play_level(level):
    """The game loop"""
    pygame.mouse.set_visible(0)

    global clock_speed, clever_bears

    # Init global game objects
    global images, status, board
    images = Images(skin)

    status = Status(level)
    board = Board()

    screen.set_clip(screen_rect)
    board.init(levels[level])
    status.update()

    scrolling = 0       # are we scrolling?
    scroll_step = 0       # scrolling direction

    # Draw static sprites
    board.sprites.draw(screen)

    try:
        while True:
            # Check if robbo died and, if so, recreate board
            if not robbo.alive():
                # Wait
                for _ in range(6):
                    update_sprites()
                    draw_sprites()
                    clock.tick(clock_speed)
                # Cleanup board
                sounds.play(sounds.die)
                for sprite in board.sprites:
                    explode(sprite)
                for _ in range(12):     # timeout
                    if not board.sprites: break
                    update_sprites()
                    draw_sprites()
                    clock.tick(clock_speed)
                # Wait
                for _ in range(6):
                    update_sprites()
                    clock.tick(clock_speed)
                # Recreate board
                offset = board.scroll_offset[1]
                status.clear()
                board.init(levels[level])
                status.update()
                for sprite in board.sprites.sprites():
                    sprite.rect.move_ip(0, offset)
                board.scroll_offset = [0, offset]
                board.rect.move_ip(0, offset)
                board.sprites.draw(screen)

            # Test for chained bombs and trigger them
            chain = board.chain
            board.chain = []
            for item in chain:
                item.chain()

            move = None

            # Process user events
            for event in pygame.event.get():
                if event.type == QUIT:
                    quit()
                elif event.type == KEYDOWN:
                    # Robbo moves
                    mods = pygame.key.get_mods()
                    if event.key in MOVES:
                        move = MOVES[event.key]
                        if mods & KMOD_CTRL:
                            if event.key in SCROLLS:
                                scrolling = True
                                scroll_step = SCROLLS[event.key]
                        elif mods & KMOD_SHIFT:
                            robbo.fire(move)
                            move = None
                        else:
                            robbo.move_key(move)
                    # system keys
                    elif event.key == K_f:
                        if not pygame.display.toggle_fullscreen():
                            import robbo as main
                            flags = 0 if screen.get_flags() & pygame.FULLSCREEN else pygame.FULLSCREEN
                            main.screen = pygame.display.set_mode((640, 480), flags)
                            status.refresh()
                            status.update()
                            screen.set_clip(screen_rect)
                    elif event.key == K_l and mods & KMOD_CTRL and not mods & (KMOD_ALT | KMOD_META):
                        draw_sprites()
                        if mods & KMOD_SHIFT:
                            raise ChangeLevelSet()
                        else:
                            raise SelectLevel(status.select_level())
                    elif event.key == K_b and mods & KMOD_CTRL and not mods & (KMOD_ALT | KMOD_META | KMOD_SHIFT):
                        clever_bears = not clever_bears
                    elif event.key == K_m and mods & KMOD_CTRL and not mods & (KMOD_ALT | KMOD_META | KMOD_SHIFT):
                        sounds.mute = not sounds.mute
                    elif event.key == K_PLUS or event.key == K_EQUALS:
                        clock_speed *= 1.2
                    elif event.key == K_MINUS:
                        clock_speed /= 1.2
                    elif event.key == K_x and mods & KMOD_CTRL and not mods & (KMOD_SHIFT | KMOD_ALT | KMOD_META):
                        robbo.die()
                    elif event.key == K_q and mods & KMOD_CTRL and not mods & (KMOD_SHIFT | KMOD_ALT | KMOD_META):
                        quit()
                elif event.type == KEYUP:
                    if MOVES.get(event.key) == robbo.walking:
                        if move: robbo.update()
                        robbo.move_key(STOP)
                    elif event.key in (K_LCTRL, K_RCTRL):
                        scrolling = 0
                    if scrolling is True and SCROLLS.get(event.key) == scroll_step:
                        if pygame.key.get_mods() & KMOD_CTRL:
                            scrolling = False
                        else:
                            scrolling = 0
            pygame.event.pump()

            # Check if scrolling is needed
            if scrolling and (
                    (board.scroll_offset[1] >= 0 and scroll_step == SCROLL_UP) or
                    (board.rect.bottom <= screen_rect.height + SIZE and scroll_step == SCROLL_DOWN)
            ):
                scrolling = False if scrolling is True else 0
            else:
                if robbo.rect.top < screen_rect.top + 2*SIZE and board.scroll_offset[1] < 0:
                    if not isinstance(scrolling, bool):
                        scrolling = 3; scroll_step = SCROLL_UP
                elif robbo.rect.bottom > screen_rect.bottom - 2*SIZE and board.rect.bottom > screen_rect.height+SIZE:
                    if not isinstance(scrolling, bool):
                        scrolling = 3; scroll_step = SCROLL_DOWN
                elif scrolling and scrolling is not True:
                        scrolling -= 1

            # print(scrolling)

            update_sprites()

            robbo.update()

            if scrolling:
                for _ in range(4):
                    for sprite in board.sprites.sprites():
                        screen.blit(board.background, sprite.rect, sprite.rect)
                        sprite.rect.move_ip(0, scroll_step)
                    board.scroll_offset[1] += scroll_step    # decide current offset
                    board.rect.move_ip(0, scroll_step)
                    draw_sprites()
                    clock.tick(clock_speed*4)
            else:
                # Draw moving sprites
                draw_sprites()
                clock.tick(clock_speed)

    except EndLevel:
        sounds.play(sounds.finish)
        w, h = screen.get_size()
        fade = pygame.Surface((w, h))
        fade.convert()
        fade.fill((0,0,0))
        robbo.kill()
        draw_sprites()
        for i in range(w, -1, -1):
            screen.blit(fade, (i, 0))
            clock.tick(300)
            pygame.display.flip()
