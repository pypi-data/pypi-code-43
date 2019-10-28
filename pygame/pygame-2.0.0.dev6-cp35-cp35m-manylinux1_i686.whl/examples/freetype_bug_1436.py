import sys, os
import pygame
from pygame.locals import *
from unicodedata import normalize

try:
    import pygame.freetype as freetype
except ImportError:
    print("No FreeType support compiled")
    sys.exit()

colors = {
    "white": pygame.Color("white"),
    "teal": pygame.Color(80, 160, 145),
    "black": pygame.Color("black"),
}


STRING = normalize("NFKD", "La località della città")
SIZE = 64


def run():
    pygame.init()

    fontdir = os.path.dirname(os.path.abspath(__file__))
    print(fontdir)
    print(os.path.join(fontdir, "data", "sans.ttf"))
    font = freetype.Font(os.path.join(fontdir, "data", "sans.ttf"))

    screen = pygame.display.set_mode((800, 600))
    screen.fill(colors["white"])

    font.underline_adjustment = 0.5
    font.pad = True

    font.render_to(screen, (32, 25), "NFKC", size=16)
    font.render_to(
        screen,
        (32, 52),
        normalize("NFKC", STRING),
        colors["white"],
        colors["teal"],
        size=SIZE,
    )

    font.render_to(screen, (32, 200), "NFKD", size=16)

    font.render_to(
        screen,
        (32, 232),
        normalize("NFKD", STRING),
        colors["white"],
        colors["teal"],
        size=SIZE,
    )

    metrics = font.get_metrics(STRING, size=SIZE)
    print(metrics)

    pygame.display.flip()

    while 1:
        if pygame.event.wait().type in (QUIT, KEYDOWN, MOUSEBUTTONDOWN):
            break

    pygame.quit()


if __name__ == "__main__":
    run()
