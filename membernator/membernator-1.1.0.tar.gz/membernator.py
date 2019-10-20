#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
membernator is a tool that can be used to scan membership cards and establish
if they're valid or not against a CSV database.

Usage:
    membernator [options] --database FILE
    membernator (-h | --help)
    membernator --version

Options:
    -h  --help       Shows the help screen
    --version        Outputs version information
    --database FILE  Path to the CSV database
    --id_col ID      "id" column in the CSV database. [default: ID]
    --name_col NAME  "name" column in the CSV database. [default: NAME]
    --time SEC       Delay in secs between scans. [default: 2.5]
    --width WIDTH    Width in pixels. Use 0 for fullscreen. [default: 800]
    --height HEIGHT  Height in pixels. Use 0 for fullscreen. [default: 480]
    --logfile LOG    Path to the logfile. [default: log.csv]
"""

import sys
import os
import csv
import gettext

from datetime import datetime

try:
    from docopt import docopt  # Creating command-line interface
except ImportError:
    sys.stderr.write(
        "docopt is not installed: this program won't run correctly.")

# l18n
t = gettext.translation('membernator', 'locales', fallback=True)  # pylint:disable=C0103
_ = t.gettext

# Make pygame import silent
from contextlib import redirect_stdout
with redirect_stdout(None):
    import pygame

# Only import the bits and pieces we need from pygame
pygame.font.init()
pygame.display.init()
pygame.display.set_caption('Membernator')

# Some initial variables
__version__ = "1.1.0"
TITLE_FONT = "Cantarell Extra Bold"
BODY_FONT = "Cantarell Bold"

# Set some colours
BLACK = 0, 0, 0
DARK_GREY = 40, 40, 40
GREY = 100, 100, 100
LIGHT_GREY = 200, 200, 200
RED = 180, 38, 34
GREEN = 37, 110, 51
CYAN = 40, 200, 200
PURP = 70, 10, 140
BLUE = 80, 80, 250
WHITE = 255, 255, 255


def display():
    """Set display options"""
    global screen, SCREEN_WIDTH, SCREEN_HEIGHT  # pylint:disable=invalid-name

    try:
        SCREEN_WIDTH = int(ARGS['--width'])
        SCREEN_HEIGHT = int(ARGS['--height'])
    except ValueError:
        sys.exit("Error: '--width' and '--height' must be integers")

    size = SCREEN_WIDTH, SCREEN_HEIGHT
    if size == (0, 0):
        screen = pygame.display.set_mode((size), pygame.FULLSCREEN)
        # Fullscreen needs those values to be recalculated
        SCREEN_WIDTH, SCREEN_HEIGHT = pygame.display.get_surface().get_size()
    else:
        screen = pygame.display.set_mode((size), pygame.NOFRAME)


def pannel_line(text, color, font, height):
    """Write a line of text at the center of a pannel"""
    label = font.render(text, 1, color)
    text_rect = label.get_rect(center=(SCREEN_WIDTH/2, height))
    screen.blit(label, text_rect)


def wait():
    """Makes the program halt for 'time' seconds or until a key is pressed"""
    clock = pygame.time.Clock()
    waiting = True

    try:
        time = float(ARGS['--time'])
    except ValueError:
        sys.exit("Error: '--time' must be a floating point number")

    while waiting:
        # Takes the time between each loop and convert to seconds
        delta = clock.tick(60) / 1000
        time -= delta
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if (event.key == pygame.K_ESCAPE and
                        pygame.key.get_mods() & pygame.KMOD_CTRL):
                    sys.exit()
                else:
                    waiting = False

        if time <= 0:
            waiting = False


def drawpannel(title, titlebgcolour, bgcolour,
               line_1, line_2, line_3, line_4, line_5):
    """Draws a pannel with a title and 5 lines of text"""
    screen.fill(bgcolour)
    pygame.draw.rect(screen, (titlebgcolour), (50, 50, SCREEN_WIDTH-110, 110))
    titlefont = pygame.font.SysFont(TITLE_FONT, 120)
    label = titlefont.render(title, 1, WHITE)
    text_rect = label.get_rect(center=(SCREEN_WIDTH/2, 105))
    screen.blit(label, text_rect)

    textfont = pygame.font.SysFont(BODY_FONT, 50)

    pannel_line(line_1, LIGHT_GREY, textfont, SCREEN_HEIGHT/5)
    pannel_line(line_2, LIGHT_GREY, textfont, SCREEN_HEIGHT*2.5/5)
    pannel_line(line_3, LIGHT_GREY, textfont, SCREEN_HEIGHT*3.5/5)
    pannel_line(line_4, LIGHT_GREY, textfont, SCREEN_HEIGHT*4/5)
    pannel_line(line_5, LIGHT_GREY, textfont, SCREEN_HEIGHT)

    pygame.display.flip()
    # We need this for the pannel to switch back to "SCAN" automatically
    wait()
    press_return = pygame.event.Event(pygame.KEYDOWN, {'key':pygame.K_RETURN})
    pygame.event.post(press_return)


def inputpannel(title, titlebgcolour, bgcolour, line_1, line_2, valid_total):
    """Draws the pannel with the input box"""
    text = ''
    done = False

    while not done:
        screen.fill(bgcolour)
        pygame.draw.rect(screen, (titlebgcolour), (50, 50, SCREEN_WIDTH-110, 110))
        titlefont = pygame.font.SysFont(TITLE_FONT, 120)
        label = titlefont.render(title, 1, WHITE)
        text_rect = label.get_rect(center=(SCREEN_WIDTH/2, 105))
        screen.blit(label, text_rect)

        textfont = pygame.font.SysFont(BODY_FONT, 50)

        pannel_line(line_1, LIGHT_GREY, textfont, SCREEN_HEIGHT*2.5/5)
        pannel_line(line_2, LIGHT_GREY, textfont, SCREEN_HEIGHT*3/5)

        # Draw the input box and handle text input
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if (event.key == pygame.K_ESCAPE and
                        pygame.key.get_mods() & pygame.KMOD_CTRL):
                    sys.exit()
                elif event.key == pygame.K_RETURN:
                    done = True
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                else:
                    text += event.unicode

        text_input = textfont.render(text, True, GREY)
        input_box = pygame.Rect((SCREEN_WIDTH-400)/2, SCREEN_HEIGHT*3.5/5, 140, 50)
        input_box.w = max(400, text_input.get_width()+10) # Resize the box if the text is too long
        pygame.draw.rect(screen, GREY, input_box, 2)
        screen.blit(text_input, (input_box.x+5, input_box.y+5))

        # Draw the valid_total rectangle
        text_valid = textfont.render(str(valid_total), True, LIGHT_GREY)
        text_valid_rect = text_valid.get_rect()
        valid_rect_size = max(75, text_valid.get_width()+20)
        valid_rect = pygame.Rect((SCREEN_WIDTH-valid_rect_size),
                                (SCREEN_HEIGHT-valid_rect_size),
                                valid_rect_size, valid_rect_size)
        pygame.draw.rect(screen, GREEN, valid_rect, 0)
        text_valid_rect.center = valid_rect.center
        screen.blit(text_valid, text_valid_rect)

        pygame.display.flip()

    return text


def welcome():
    """Draw a welcome pannel"""
    drawpannel(_('WELCOME'), GREY, DARK_GREY,
             '',
             _('To start, press any key'),
             _('Press [Ctrl] + [Esc] to quit at any time'),
             '',
             '')


def count_valid(logdict):
    """Count the number of valid cards scanned."""
    try:
        valid_total = int(logdict[-1]["Valid Total"]) # fails if the logfile is
    except IndexError:                                # empty
        valid_total = 0

    return valid_total


def validate(csvdict, logdict, text):
    """Validate the scanned card"""
    valid = False
    seen = False
    name = None
    valid_total = count_valid(logdict)

    for row in csvdict:
        if text == row[ARGS['--id_col']]:
            valid = True
            name = row[ARGS['--name_col']]
    for row in logdict:
        if text == row[ARGS['--id_col']]:
            seen = True
    if valid and not seen:
        valid_total += 1

    return valid, valid_total, seen, name


def logger(logdict, valid, valid_total, text, name):
    """Write scanned cards to the logfile"""
    scan_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Keep track of scanned cards
    logdict.append({"Scan Time":scan_time, "Valid":valid, "Valid Total":valid_total,
                    ARGS['--id_col']:text, ARGS['--name_col']:name})

    # Write to the logfile
    with open(ARGS['--logfile'], 'a+', newline='') as log:
        log_write = csv.DictWriter(log, fieldnames=["Scan Time", "Valid",
                    "Valid Total", ARGS['--id_col'], ARGS['--name_col']])
        if os.stat(ARGS['--logfile']).st_size == 0:  # only write header for new files
            log_write.writeheader()
        log_write.writerow(logdict[len(logdict)-1])  # only write last entry

    return logdict


def showpannel(valid, seen, name):
    """The pannels shown to the user"""
    if (valid == True) and (seen == True):
        drawpannel(_('VALID'), CYAN, DARK_GREY,
                 '',
                 _('This card has already be scanned'),
                 _('Name: ') + name,
                 '',
                 '')
    elif (valid == True) and (seen == False):
        drawpannel(_('VALID'), GREEN, DARK_GREY,
                 '',
                 _('This card is valid'),
                 _('Name: ') + name,
                 '',
                 '')
    else:
        drawpannel(_('INVALID'), RED, DARK_GREY,
                 '',
                 _('This card is invalid'),
                 '',
                 '',
                 '')


def text_input():
    """Manage the  user's text input"""

    logdict = []
    # Initialise values from the logfile
    if os.path.isfile(ARGS['--logfile']):
        with open(ARGS['--logfile'],  newline='') as log:
            for row in csv.DictReader(log):
                logdict.append(row)
    valid_total = count_valid(logdict)

    with open(ARGS['--database'], newline='') as csvfile:
        csvdict = csv.DictReader(csvfile)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if (event.key == pygame.K_ESCAPE and
                            pygame.key.get_mods() & pygame.KMOD_CTRL):
                        sys.exit()
                    else:
                        text = inputpannel(_('READY TO SCAN'), BLUE, DARK_GREY,
                                         _("Scan a card or type the member's"),
                                         _('ID number and press [Enter]'),
                                          valid_total)
                        csvfile.seek(0) # Read the entire file each time
                        valid, valid_total, seen, name = validate(csvdict,
                                                                  logdict, text)
                        logdict = logger(logdict, valid, valid_total, text, name)
                        showpannel(valid, seen, name)


def main():
    """Main function"""
    global ARGS
    ARGS = docopt(__doc__, version="membernator %s" % __version__)
    display()
    welcome()
    text_input()


if __name__ == "__main__":
    main()
