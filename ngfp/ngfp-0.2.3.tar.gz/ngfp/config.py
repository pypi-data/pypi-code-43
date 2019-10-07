#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) Ant <ant@anthive.com>

import copy
import json
from pathlib import Path, PurePath
import os


# the path to the images
#print (os.path.basename(__file__))
png_path = os.path.dirname(__file__) + "/png/"
#print (png_path)


# the basic game unit for images and moving is
img_pix = 64


half_img_pix = img_pix//2


# animation pixels moved (it must be a factor of img_pix otherwise
#   the marble won't match with the grid of coordinates - i.e. there's
#   no wiggle room in the collision detection)...
tic_pix = img_pix // 2


# some space for widget piles at the right
control_cols = 5


# dialog cancelled operation
dialog_cancelled = False


#   save game location and initial file
# you can always save/load other names, 
# this is just a suggestion...
suggested_fn = "save.json"
this_fn_to_open = None
this_fn_to_save = None

home = Path.home()
saved_dir = None


# save file directory
if (os.name == "posix"):
    home = Path.home()
    data_path = home / Path(".local/share/ngfp")
else:
    print ("  Ngfp doesn't know where to set data_path for OS : ", os.name)
    print ("This is where a user would save their games.")


# configure location and file
config_filename = "config_ngfp.json"
if (os.name == "posix"):
    home = Path.home()
    config_path = home / Path(".config/ngfp")
    full_config_filename = config_path / config_filename
else:
    print ("  Ngfp doesn't know where to set config_path for OS : ", os.name)
    print ("This is where the game saves configuration parameters.")


# when loading a game from a file we put stuff in
# these spots so that DrawBoard can use them.
# changing dimensions in the config dialog also uses
# these.
new_game_cols = None
new_game_rows = None
new_board = None
new_widget_counts = None


# which board to show, a toggle between 0, 1  when Key F1 is pressed
#    but we start at 2 for a new board and it's random to start...
# 0 - puzzle to solve
# 1 - guesses placed
# 2 - blank background
#
show_board = 2
do_random_board = True


# current, default and changed parameters

min_cols = 1      # this actually works
min_rows = 6      # for the moment
max_cols = 22     # on 1920 x 1080
max_rows = 13     # on 1920 x 1080

game_cols = 6     # width
game_rows = 6     # height
density = 25      # percent of the board filled up modified by density_fuzz
density_fuzz = 10
class_weights = [100, 75, 5, 5, 5, 15, 5]

default_game_cols = 6     # width
default_game_rows = 6     # height
default_density = 25      # percent of the board filled up modified by density_fuzz
default_density_fuzz = 10
default_class_weights = [100, 75, 5, 5, 5, 15, 5]


# need to keep track of the current square
square = None

# if the user has to wait until something 
#  (usually the animation) is done
no_user_actions = False


# labels for configuration dialog

property_labels = [
    "Width",
    "Height",
    "Density",
    "Fuzz"
    ]

widget_class_labels = [
    "Simple mirrors",
    "Flipping mirrors",
    "Box and sink",
    "Axial mirrors",
    "Rotators",
    "One-way mirrors",
    "PURE EVIL"
    ]

pic_list = [
    png_path + "mirrors/00_bg.png",           # background
    png_path + "mirrors/01_normal.png",       # simple mirrors: left: \
    png_path + "mirrors/02_normal.png",       # simple mirrors: right: /
    png_path + "mirrors/03_flip2.png",        # simple flipping mirrors: left: \
    png_path + "mirrors/04_flip2.png",        # simple flipping mirrors: right: /
    png_path + "mirrors/05_flip4.png",        # quad flipping mirrors: left: \
    png_path + "mirrors/06_flip4.png",        # quad flipping mirrors: bounce: o
    png_path + "mirrors/07_flip4.png",        # quad flipping mirrors: right: /
    png_path + "mirrors/08_flip4.png",        # quad flipping mirrors: bounce: o
    png_path + "mirrors/09_block.png",        # box and sink: box: bounce: o  (reflect all)
    png_path + "mirrors/10_sink.png",         # box and sink: sink: grab: x  (absorb all)
    png_path + "mirrors/11_axial.png",        # axial mirrors: simple vertical: |
    png_path + "mirrors/12_axial.png",        # axial mirrors: simple horizontal: -
    png_path + "mirrors/13_axial2.png",       # axial mirrors: flipping vertical: ||
    png_path + "mirrors/14_axial2.png",       # axial mirrors: flipping horizontal: =
    png_path + "mirrors/15_rotator.png",      # rotators simple counterclockwise: left: \\
    png_path + "mirrors/16_rotator.png",      # rotators simple clockwise: right: //
    png_path + "mirrors/17_rotator2.png",     # rotators flipper clockwise: left: []
    png_path + "mirrors/18_rotator2.png",     # rotators flipper counterclockwise: right: ][
    png_path + "mirrors/19_half.png",         # 1-way mirrors: left: lower reflects: \<-
    png_path + "mirrors/20_half.png",         # 1-way mirrors: left: upper reflects: ->\
    png_path + "mirrors/21_half.png",         # 1-way mirrors: right: lower reflects: ->/
    png_path + "mirrors/22_half.png",         # 1-way mirrors: right: upper reflects: /<-
    png_path + "mirrors/23_half4.png",        # flipping 1-way mirrors: left: lower reflects: rotates clockwise: \\\<-
    png_path + "mirrors/24_half4.png",        # flipping 1-way mirrors: right: upper reflects: rotates clockwise: ///<-
    png_path + "mirrors/25_half4.png",        # flipping 1-way mirrors: left: upper reflects: rotates clockwise: ->\\\
    png_path + "mirrors/26_half4.png",        # flipping 1-way mirrors: right: lower reflects: rotates clockwise: ->///
    png_path + "mirrors/27_half4.png",        # flipping 1-way mirrors: left: upper reflects: rotates counterclockwise: ->\\\
    png_path + "mirrors/28_half4.png",        # flipping 1-way mirrors: right: upper reflects: rotates counterclockwise: ///<-
    png_path + "mirrors/29_half4.png",        # flipping 1-way mirrors: left: lower reflects: rotates counterclockwise: \\\<-
    png_path + "mirrors/30_half4.png",        # flipping 1-way mirrors: right: lower reflects: rotates counterclockwise: ->///
    png_path + "mirrors/31_move.png",         # moving mirror: left: -->\X\--> ---->\X\
    png_path + "mirrors/32_move.png",         # moving mirror: right: <--/X/<-- /X/<----
    png_path + "mirrors/33_bg.png"            # background
]

# this indexes the above picture list so we know which ones are
# used for labels on the configure screen
config_percent_list = [1,2,3,5,9,10,11,14,15,18,19,22,23,31]


