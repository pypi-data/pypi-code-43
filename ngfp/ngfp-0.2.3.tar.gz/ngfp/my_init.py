#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) Ant <ant@anthive.com>

import copy
import os
import random

import pyglet

import ngfp.config as cfg

from ngfp.dialog import LoadConfigOrUseCurrent


def MyInitStuff (self):

    random.seed()

    self.set_visible(False)

    self.png_path = cfg.png_path

    # screens, sizes and locations
    #   some of these change as the board changes size
    self.top_display = pyglet.canvas.get_display()
    self.top_screen = self.top_display.get_default_screen()
    self.full_screen_width = self.top_screen.width
    self.full_screen_height = self.top_screen.height
#    print ("Initial Window Size : ", self.full_screen_width, self.full_screen_height)
    self.windows_lst = self.top_display.get_windows()
    self.screen_width = self.windows_lst[0].width
    self.screen_height = self.windows_lst[0].height
    self.x, self.y = self.windows_lst[0].get_location()
#    print ("Smaller Window Location and Size : ", self.x, self.y, self.screen_width, self.screen_height)

    # initial window is blank and flickers i don't want 
    # to see it until it is resized later
    self.windows_lst[0].set_visible(False)

    # if there's a config file use it
    #  if there isn't set defaults specified in config.py
    LoadConfigOrUseCurrent ()

    # other useful constants
    self.board_squares = cfg.game_rows*cfg.game_cols
    self.window_cols = (cfg.game_cols+cfg.control_cols+3)
    self.window_rows = (cfg.game_rows+2)
    self.window_squares = self.window_rows*self.window_cols

    self.game_board_x_limit = 0
    self.game_board_y_limit = 0

    self.keys_held = []
    self.key = pyglet.window.key

    self.mouse_win_pos = 0

    self.fps = pyglet.window.FPSDisplay(self)

    # batches for rendering
    self.fixed_batch = pyglet.graphics.Batch()
    self.green_batch = pyglet.graphics.Batch()
    self.control_batch = pyglet.graphics.Batch()
    self.widget_batch = pyglet.graphics.Batch()
    self.fixed_board_batch = pyglet.graphics.Batch()
    self.variable_board_batch = pyglet.graphics.Batch()
    self.variable_guess_batch = pyglet.graphics.Batch()
    self.pointer_bottom_batch = pyglet.graphics.Batch()
    self.pointer_top_batch = pyglet.graphics.Batch()
    self.text_batch = pyglet.graphics.Batch()
    self.arrow_batch = pyglet.graphics.Batch()
    self.marble_batch = pyglet.graphics.Batch()
    self.marker_batch = pyglet.graphics.Batch()

    # colors need precedence order for arrows
    #   we only use as many colors to mark arrows we keep in history
    self.history_limit = 6
    self.color_batch_list = []
    for i in range(self.history_limit):
        self.color_batch_list.append(pyglet.graphics.Batch())

    # lists of sprites
    self.fixed_sprites = []
    self.fixed_board_sprites = []
    self.green_sprites = []
    self.board_sprites = []
    self.guess_sprites = []
    self.control_sprites = []
    self.widget_sprites = []
    self.top_sprites = []
    self.arrow_history_sprites = []
    self.history_color_sprites = []
    self.marble_sprites = []
    self.marker_sprites = []

    self.white_active_squares = []
    self.white_active_squares_position = []
    self.guess_active_squares = []
    self.guess_active_squares_position = []
    self.control_active_squares = []
    self.control_active_squares_position = []
    self.widget_active_squares = []
    self.widget_active_squares_position = []
    self.board_to_window_index = []

    self.game_bg_image  = pyglet.image.load(self.png_path + "mirrors/00_bg.png")
    self.white_bg_image = pyglet.image.load(self.png_path + "backgrounds/wbg.png")
    self.blue_bg_image  = pyglet.image.load(self.png_path + "backgrounds/bbg.png")
    self.green_bg_image = pyglet.image.load(self.png_path + "backgrounds/lgbg.png")
    self.gray_bg_image  = pyglet.image.load(self.png_path + "backgrounds/gbg.png")

    self.gcube_image = pyglet.image.load(self.png_path + "misc/gcube.png")
    self.cube_image  = pyglet.image.load(self.png_path + "misc/cube.png")

    self.pic_marker_list = [
        self.png_path + "markers/picMkCircle.png",
        self.png_path + "markers/picMkTriangle.png",
        self.png_path + "markers/picMkSquare.png",
        self.png_path + "markers/picMkVee.png"
        ]

    self.marker_images = []
    for i in range(len(self.pic_marker_list)):
        self.marker_images.append(pyglet.image.load(self.pic_marker_list[i]))

    self.pic_control_list = [
        self.png_path + "controls/picINew.png",
        self.png_path + "controls/picICheck.png",
        self.png_path + "controls/picIFlipBoards.png",
        self.png_path + "controls/picIOpen.png",
        self.png_path + "controls/picISave.png",
        self.png_path + "controls/picIAbout.png"
        ]

    self.control_images = []
    for i in range(len(self.pic_control_list)):
        self.control_images.append(pyglet.image.load(self.pic_control_list[i]))

    self.pic_marbles_list = [
        self.png_path + "marbles/red_marbles.png",
        self.png_path + "marbles/green_marbles.png",
        self.png_path + "marbles/blue_marbles.png",
        self.png_path + "marbles/yellow_marbles.png",
        self.png_path + "marbles/purple_marbles.png",
        self.png_path + "marbles/black_marbles.png"
        ]

    self.marble_images = []
    for i in range(len(self.pic_marbles_list)):
        self.marble_images.append(pyglet.image.load(self.pic_marbles_list[i]))

    self.pic_color_list = [
        self.png_path + "colors/red_half.png",
        self.png_path + "colors/green_half.png",
        self.png_path + "colors/blue_half.png",
        self.png_path + "colors/yellow_half.png",
        self.png_path + "colors/purple_half.png",
        self.png_path + "colors/black_half.png"
        ]

    self.color_images = []
    for i in range(len(self.pic_color_list)):
        self.color_images.append(pyglet.image.load(self.pic_color_list[i]))

    self.pic_arrow_list = [
        self.png_path + "arrows/picDLeftW.png",
        self.png_path + "arrows/picDRightW.png",
        self.png_path + "arrows/picDUpW.png",
        self.png_path + "arrows/picDDownW.png"
        ]

    self.arrow_images = []
    for i in range(len(self.pic_arrow_list)):
        self.arrow_images.append(pyglet.image.load(self.pic_arrow_list[i]))

    # arrow history list and current index, set up colors and marbles too...
    self.arrow_index = 0
    self.anim = []
    self.marble_seq = []
    anim_index = 0
    for i in range(self.history_limit):

        spr_a = pyglet.sprite.Sprite(self.arrow_images[0], batch=self.arrow_batch)
        spr_a.visible = False
        spr_b = pyglet.sprite.Sprite(self.arrow_images[0], batch=self.arrow_batch)
        spr_b.visible = False
        self.arrow_history_sprites.append([spr_a, spr_b])

        spr_c = pyglet.sprite.Sprite(self.color_images[i], batch=self.color_batch_list[i])
        spr_c.visible = False
        spr_d = pyglet.sprite.Sprite(self.color_images[i], batch=self.color_batch_list[i])
        spr_d.visible = False
        self.history_color_sprites.append([spr_c, spr_d])

        # set up a long looping animation
        marble_sequence = pyglet.image.ImageGrid(self.marble_images[i], 1, 16)
        self.marble_seq.append(marble_sequence)
        self.anim.append(pyglet.image.Animation.from_image_sequence(self.marble_seq[anim_index], 0.02, True))
        spr_e = pyglet.sprite.Sprite(self.anim[anim_index], batch=self.marble_batch)
        spr_e.visible = True
        spr_e.x = 0
        spr_e.y = 0
        spr_e.dx = 0
        spr_e.dy = 0
        self.marble_sprites.append(spr_e)
        anim_index += 1

        # now set up the short animation that plays once
        marble_sequence = marble_sequence[:1]
        self.marble_seq.append(marble_sequence)
        self.anim.append(pyglet.image.Animation.from_image_sequence(self.marble_seq[anim_index], 1, False))
        spr_e = pyglet.sprite.Sprite(self.anim[anim_index], batch=self.marble_batch)
        spr_e.visible = False
        spr_e.x = 0
        spr_e.y = 0
        spr_e.dx = 0
        spr_e.dy = 0
        self.marble_sprites.append(spr_e)
        anim_index += 1

    self.spr_mv_list = []

    for i in range(len(cfg.pic_list)):
        image = pyglet.image.load(cfg.pic_list[i])
        sprite = pyglet.sprite.Sprite(image)
        self.spr_mv_list.append([0, image, sprite, 0, 0])

    # these flags are for the widget pile list
    #     position is taken from widget list location index
    #     when self.widget_pile_list_counts[position] != 0 then the index
    #        can be used to get the number from this list to index into
    #         self.spr_mv_list for the image or sprite or ...
    self.widget_pile_list = [1,2,3,5,9,10,11,12,13,15,16,17,19,20,21,22,23,27,31,32]
    for i in self.widget_pile_list:
        self.spr_mv_list[i][0] = 1
    self.widget_pile_list_counts = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    self.widget_labels = []

    # eventually we're going to have to index any widget no matter how it
    # is rotated...
    self.widget_lookup_table = [0, 1, 2, 
                                3, 3,
                                4, 4, 4, 4,
                                5, 6, 7, 8,
                                9, 9,
                                10, 11,
                                12, 12,
                                13, 14, 15, 16,
                                17, 17, 17, 17,
                                18, 18, 18, 18,
                                19, 20
                               ]

    # speaking of rotating, we need to know how many places it 
    #   rotates through - of course 0 means it doesn't rotate at all
    # note that this aligns with self.widget_lookup_table
    self.widget_rotate_modulus = [0,0,0,2,4,0,0,0,0,2,0,0,2,0,0,0,0,4,4,0,0]

    # this says what the next widget will be in the sequence if it isn't 0
    self.widget_next_widget = [
    #   0 1 2 3 4 5 6 7 8 9 0 1 2
        0,0,0,4,3,6,7,8,5,0,0,0,0,
        14,13,0,0,18,17,
        0,0,0,0,
    #   23-26 
        24, 25, 26, 23,
    #   27-30
        28, 29, 30, 27,
    #   31, 32
        0, 0]

    # these flags are for the configuration of each group percentages images list
    # even numbers are left image indexes, odd are right, seven groups of two
    self.config_percent_list = [1,2,3,5,9,10,11,14,15,18,19,22,23,31]
    for i in self.config_percent_list:
        self.spr_mv_list[i][3] = 1

    self.property_labels = [
                            "Width",
                            "Height",
                            "Density",
                            "Fuzz"
                           ]

    self.widget_cl_labels = [
                          "Simple mirrors",
                          "Flipping mirrors",
                          "Box and sink",
                          "Axial mirrors",
                          "Rotators",
                          "One-way mirrors",
                          "PURE EVIL"
                         ]

    # 0 = nowhere, 1 = widget, 2 = board
    self.picked_up_from = 0
    self.picked_up = False

    # direction sets will make things easier later
    self.dir_left = []
    self.dir_right = []
    self.dir_up = []
    self.dir_down = []

    # some kind of limit to break out of loops
    self.tick_limit = 100 + (self.board_squares * 4)


