#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) Ant <ant@anthive.com>

import pyglet
import copy
from time import sleep

import ngfp.config as cfg

from ngfp.background import DrawBordersAndBackgrounds
from ngfp.labels import AddLabels
from ngfp.randboard import InitRandomBoardItems


def ClearSquareMarkers (self):

#    print ("ClearSquareMarkers mouse_win_pos : ", self.mouse_win_pos)
    value = self.board_to_window_index.index(self.mouse_win_pos)
    how_many_markers = len(self.marker_images)
    for i in range(how_many_markers):
        self.board[value][i+2] = False
        self.marker_sprites[(value*how_many_markers)+i].visible = False


def ClearAllMarkers (self):

#    print ("ClearAllMarkers")
    value = len(self.board)
    how_many_markers = len(self.marker_images)
    for i in range(value):
        for j in range(how_many_markers):
            self.board[i][j+2] = False
            self.marker_sprites[(i*how_many_markers)+j].visible = False


def ToggleMarker (self, mark):

#    print ("ToggleMarker mark, mouse_win_pos : ", mark, self.mouse_win_pos)
    try:
        value = self.board_to_window_index.index(self.mouse_win_pos)
        how_many_markers = len(self.marker_images)
        self.board[value][mark+2] = not(self.board[value][mark+2])
        self.marker_sprites[(value*how_many_markers)+mark].visible = not(self.marker_sprites[(value*how_many_markers)+mark].visible)
    except:
        pass


def RestartGame (self):

    #print ("RestartGame")
    ClearAllMarkers (self)

    # reset and then recount the widget pile count list
    try:
        del self.widget_pile_list_counts
    except AttributeError:
        pass

    self.widget_pile_list_counts = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

    # ok, now recount what is on the board
    value = len(self.board)
    for i in range(value):
        mirror_value = self.board[i][0]
        if (mirror_value != 0):
            lookup_value = self.widget_lookup_table[mirror_value] - 1
            self.widget_pile_list_counts[lookup_value] += 1

    # clear guesses
    value = len(self.board)
    for i in range(value):
        self.board[i][1] = 0

    # make any guess sprites look like the background
    if (len(self.guess_sprites) != 0):
        for j in range(len(self.guess_sprites)):
            self.guess_sprites[j].image = self.game_bg_image


def ClearAndResizeBoard (self):


    # ok, let's see...
    self.set_visible(True)

    # use the current cfg values
    self.density = cfg.density
    self.density_fuzz = cfg.density_fuzz
    self.class_weights = cfg.class_weights

    # don't forget these...
    self.board_squares = cfg.game_rows*cfg.game_cols
    self.window_rows = (cfg.game_rows+2)
    self.window_cols = (cfg.game_cols+cfg.control_cols+3)
    self.window_squares = self.window_rows*self.window_cols

    # adjust the main window size to fit

    self.screen_width = ((cfg.game_cols+cfg.control_cols+3) * cfg.img_pix)
    self.screen_height = ((cfg.game_rows+2) * cfg.img_pix)

    self.game_x = (self.full_screen_width//2) - (self.screen_width//2)
    self.game_y = (self.full_screen_height//2) - ((self.screen_height//2))

    self.set_location(self.game_x, self.game_y)
    self.set_size(self.screen_width, self.screen_height)

    # ok, let's see...
#   self.set_visible(True)


    # delete old board and set up new one, but
    #   DrawBoard really gets rid of all the various 
    #   lists,sprites and indexes
    try:
        del self.board
    except AttributeError:
        pass
    self.board = []

    self.board = [[0 for i in range(6)] for j in range(self.board_squares)]

    try:
        del self.widget_pile_list_counts
    except AttributeError:
        pass

    self.widget_pile_list_counts = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

    # move the gcube
    try:
        self.gcube.x = cfg.img_pix * (cfg.game_cols+1)
    except:
        pass


def DrawBoard (self):

    if (cfg.show_board == 2):

        self.cube.visible = False
        self.gcube.visible = False

        if (len(self.fixed_sprites) != 0):
            for j in range(len(self.fixed_sprites)):
                #self.fixed_sprites[j].visible = False
                self.fixed_sprites[j].delete()
            del self.fixed_sprites
            self.fixed_sprites = []

        if (len(self.fixed_board_sprites) != 0):
            for j in range(len(self.fixed_board_sprites)):
                #self.fixed_board_sprites[j].visible = False
                self.fixed_board_sprites[j].delete()
            del self.fixed_board_sprites
            self.fixed_board_sprites = []

        if (len(self.board_sprites) != 0):
            for j in range(len(self.board_sprites)):
                #self.board_sprites[j].visible = False
                self.board_sprites[j].delete()
            del self.board_sprites
            self.board_sprites = []

        if (len(self.green_sprites) != 0):
            for j in range(len(self.green_sprites)):
                #self.green_sprites[j].visible = False
                self.green_sprites[j].delete()
            del self.green_sprites
            self.green_sprites = []

        if (len(self.white_active_squares) != 0):
            del self.white_active_squares
            self.white_active_squares = []

        if (len(self.white_active_squares_position) != 0):
            del self.white_active_squares_position
            self.white_active_squares_position = []

        if (len(self.dir_left) != 0):
            del self.dir_left
            self.dir_left = []

        if (len(self.dir_right) != 0):
            del self.dir_right
            self.dir_right = []

        if (len(self.dir_up) != 0):
            del self.dir_up
            self.dir_up = []

        if (len(self.dir_down) != 0):
            del self.dir_down
            self.dir_down = []

        if (len(self.guess_sprites) != 0):
            for j in range(len(self.guess_sprites)):
                #self.guess_sprites[j].visible = False
                self.guess_sprites[j].delete()
            del self.guess_sprites
            self.guess_sprites = []

        if (len(self.guess_active_squares) != 0):
            del self.guess_active_squares
            self.guess_active_squares = []

        if (len(self.guess_active_squares_position) != 0):
            del self.guess_active_squares_position
            self.guess_active_squares_position = []

        if (len(self.board_to_window_index) != 0):
            del self.board_to_window_index
            self.board_to_window_index = []

        if (len(self.control_sprites) != 0):
            for j in range(len(self.control_sprites)):
                #self.control_sprites[j].visible = False
                self.control_sprites[j].delete()
            del self.control_sprites
            self.control_sprites = []

        if (len(self.control_active_squares) != 0):
            del self.control_active_squares
            self.control_active_squares = []

        if (len(self.control_active_squares_position) != 0):
            del self.control_active_squares_position
            self.control_active_squares_position = []

        if (len(self.marker_sprites) != 0):
            for j in range(len(self.marker_sprites)):
                #self.marker_sprites[j].visible = False
                self.marker_sprites[j].delete()
            del self.marker_sprites
            self.marker_sprites = []

        if (len(self.widget_active_squares) != 0):
            del self.widget_active_squares
            self.widget_active_squares = []

        if (len(self.widget_active_squares_position) != 0):
            del self.widget_active_squares_position
            self.widget_active_squares_position = []

        if (len(self.arrow_history_sprites) != 0):
            for j in range(len(self.arrow_history_sprites)):
                self.arrow_history_sprites[j][0].visible = False
                self.arrow_history_sprites[j][1].visible = False

        if (len(self.history_color_sprites) != 0):
            for j in range(len(self.history_color_sprites)):
                self.history_color_sprites[j][0].visible = False
                self.history_color_sprites[j][1].visible = False

        if (len(self.marble_sprites) != 0):
            for j in range(len(self.marble_sprites)):
                self.marble_sprites[j].visible = False

        if (cfg.do_random_board == True):
#            print ("DrawBoard Draw Random Board")

            ClearAndResizeBoard (self)
            InitRandomBoardItems (self)
            DrawBordersAndBackgrounds (self)
            cfg.do_random_board = False
#            print ("DrawR self.wpl ", self.widget_pile_list)
#            print ("DrawR self.wplc ", self.widget_pile_list_counts)
        else:
            # it's a newly loaded board
#            print ("DrawBoard Draw Loaded Board")

            cfg.game_cols = cfg.new_game_cols
            cfg.game_rows = cfg.new_game_rows
            # we use ClearAndResizeBoard to put the window on
            # the screen in the right spot
            ClearAndResizeBoard (self)
            del self.board
            self.board = copy.deepcopy(cfg.new_board)
            del self.widget_pile_list_counts
            self.widget_pile_list_counts = copy.deepcopy(cfg.new_widget_counts)
            DrawBordersAndBackgrounds (self)
#            print ("DrawL self.wpl ", self.widget_pile_list)
#            print ("DrawL self.wplc ", self.widget_pile_list_counts)

        AddLabels (self)

        # draw game grid
#        print ("DrawBoard show board 2", cfg.show_board)
#        print ("DrawBoard initial board start", self.board)
        y_pos = cfg.img_pix
        x_pos = cfg.img_pix
        self.game_board_x_lower_limit = x_pos
        self.game_board_y_lower_limit = y_pos
#       win_pos = ((self.window_rows - 2) * self.window_cols) + 1
        win_pos = self.window_cols + 1

        for x in range(cfg.game_rows):
            x_pos = self.game_board_x_lower_limit
            for y in range(cfg.game_cols):
                board_position = (cfg.game_cols * x) + y
#                print ("BP WP x y: ", board_position, win_pos, x, y)
                self.fixed_board_sprites.append( pyglet.sprite.Sprite( self.game_bg_image, batch=self.fixed_board_batch, x = x_pos, y = y_pos))
                image = self.spr_mv_list[self.board[board_position][0]][1]
                self.board_sprites.append( pyglet.sprite.Sprite( image, batch=self.variable_board_batch, x = x_pos, y = y_pos))
                image = self.spr_mv_list[self.board[board_position][1]][1]
                self.guess_sprites.append( pyglet.sprite.Sprite( image, batch=self.variable_guess_batch, x = x_pos, y = y_pos))
                self.guess_active_squares.append(win_pos)
                self.guess_active_squares_position.append([x_pos,y_pos])
                self.board_to_window_index.append(win_pos)
                for z in range(len(self.marker_images)):
                    self.marker_sprite = pyglet.sprite.Sprite( self.marker_images[z], batch=self.marker_batch, x = x_pos, y = y_pos)
                    if (self.board[board_position][z+2] == True):
                        self.marker_sprite.visible = True
                    else:
                        self.marker_sprite.visible = False
                    self.marker_sprites.append(self.marker_sprite)
                x_pos += cfg.img_pix
                win_pos += 1
            y_pos += cfg.img_pix
            win_pos += (cfg.control_cols + 3)
        self.game_board_x_upper_limit = x_pos
        self.game_board_y_upper_limit = y_pos
        cfg.show_board = 1

#        print ("Guess active squares", self.guess_active_squares)
#        print ("Guess active square positions", self.guess_active_squares_position)
#        print ("board_to_window_index", self.board_to_window_index)
#        print ("game board limits ", self.game_board_x_lower_limit, self.game_board_x_upper_limit,
#            self.game_board_y_lower_limit, self.game_board_y_upper_limit)
#        print ("DrawBoard board initial board finish", self.board)
#        print ("widget_pile_list_counts ", self.widget_pile_list_counts)

    elif (cfg.show_board == 0):

        self.cube.visible = True
        self.gcube.visible = False

        for j in range(len(self.board_sprites)):
            self.board_sprites[j].visible = True
        for j in range(len(self.guess_sprites)):
            self.guess_sprites[j].visible = False
#        print ("DrawBoard draw show board 0", len(self.board_sprites), len(self.guess_sprites), cfg.show_board)

    else:

        self.cube.visible = False
        self.gcube.visible = True

        for j in range(len(self.board_sprites)):
            self.board_sprites[j].visible = False
        for j in range(len(self.guess_sprites)):
            self.guess_sprites[j].visible = True
#        print ("DrawBoard draw show board 1", len(self.board_sprites), len(self.guess_sprites), cfg.show_board)


