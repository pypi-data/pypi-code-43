import os, sys
import pygame
from pygame.locals import *

pygame.init()
pygame.mixer.init()

screen_flags = 0
if "--fullscreen" in sys.argv:
    screen_flags |= pygame.FULLSCREEN
if hasattr(pygame, "SCALED"):
    screen_flags |= pygame.SCALED

screen = pygame.display.set_mode((320, 240), screen_flags)
clock = pygame.time.Clock()

click_pos = None
motions = []
move_pos = None
while True:
    events = pygame.event.get()
    keys_raw = pygame.key.get_pressed()
    screen.fill((255, 255, 255))

    for e in events:
        if e.type == QUIT or e.type == KEYDOWN and e.key == K_ESCAPE:
            sys.exit()
        if e.type == MOUSEBUTTONDOWN:
            print("CLICKED")
            click_pos = e.pos
            motions = []
        if e.type == MOUSEBUTTONUP:
            click_pos = None
            motions = []
        if e.type == MOUSEMOTION:
            if click_pos is not None:
                motions.append(e.rel)
            move_pos = e.pos

    if click_pos is not None:
        pygame.draw.circle(screen, (200, 200, 100), click_pos, 5, 1)
        start_pos = click_pos
        for m in motions:
            mx, my = m
            sx, sy = start_pos
            next_pos = sx + mx, sy + my
            pygame.draw.line(screen, (200, 200, 100), start_pos, next_pos)
            start_pos = next_pos

    if move_pos is not None:
        pygame.draw.circle(screen, (200, 100, 200), move_pos, 3)

    pygame.draw.circle(screen, (100, 100, 200), pygame.mouse.get_pos(), 8, 1)

    pygame.display.flip()
    clock.tick(30)
