#!/usr/bin/env python
import pygame
import pygame.gfxdraw
import math


def draw_aacircle(surface, color, pos, radius, width=0):

    r, g, b = color
    position_x, position_y = pos
    alpha_max = 255

    i, j, fade, prev_fade = radius, 0, 0, 0

    def draw_points(x, y, color):
        surface.set_at((
            position_x + (x * (-1) ** (0 % 2)),
            position_y + (y * (-1) ** (0 // 2))
        ), color)
        surface.set_at((
            position_x + (x * (-1) ** (1 % 2)),
            position_y + (y * (-1) ** (1 // 2))
        ), color)
        surface.set_at((
            position_x + (x * (-1) ** (2 % 2)),
            position_y + (y * (-1) ** (2 // 2))
        ), color)
        surface.set_at((
            position_x + (x * (-1) ** (3 % 2)),
            position_y + (y * (-1) ** (3 // 2))
        ), color)

        surface.set_at((
            position_x + (y * (-1) ** (0 // 2)),
            position_y + (x * (-1) ** (0 % 2))
        ), color)
        surface.set_at((
            position_x + (y * (-1) ** (1 // 2)),
            position_y + (x * (-1) ** (1 % 2))
        ), color)
        surface.set_at((
            position_x + (y * (-1) ** (2 // 2)),
            position_y + (x * (-1) ** (2 % 2))
        ), color)
        surface.set_at((
            position_x + (y * (-1) ** (3 // 2)),
            position_y + (x * (-1) ** (3 % 2))
        ), color)

    draw_points(i, 0, alpha_max)

    while i > j:
        fade = math.ceil(math.sqrt(radius**2 - j**2))
        if fade < prev_fade:
            i -= 1
        alpha = int(fade / radius * alpha_max)
        # draw_points(i, j, (r, g, b, 255))
        # print(fade, alpha)
        # draw_points(i, j, (r, g, b, alpha))

        # draw_points(i - 1, j, (r, g, b, alpha_max - alpha))
        draw_points(i -1, j, (r, g, b, alpha_max - alpha))
        draw_points(i, j, (r, g, b, alpha))

        # draw_points(i, j, (r, g, b, alpha))
        # draw_points(i + 1, j - 1, (r, g, b, alpha_max - alpha))
        prev_fade = fade
        j += 1



def main():
    pygame.init()
    screen = pygame.display.set_mode((500,500))
    screen.fill((255, 0, 0))
    s = pygame.Surface(screen.get_size(), pygame.SRCALPHA, 32)
    draw_aacircle(s, color=(0,0,0), pos=(300, 300), radius=50, width=1)
    # pygame.gfxdraw.aacircle(s, color=(0,0,0), pos=(300, 300), radius=50, width=1)
    pygame.gfxdraw.aacircle(s, 100, 100, 50, (0, 0, 0))

    screen.blit(s, (0, 0))
    pygame.display.flip()
    try:
        while 1:
            event = pygame.event.wait()
            if event.type == pygame.QUIT:
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.unicode == 'q':
                    break
            pygame.display.flip()
    finally:
        pygame.quit()

if __name__ == '__main__':
    main()
