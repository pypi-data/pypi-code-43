#!/usr/bin/env python3 
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) Ant <ant@anthive.com>

import pyglet
import sys

import ngfp.config as cfg

from ngfp.dialog import DoDialogControlAction
from ngfp.marbles import DoLeftClickWhiteAction


def WidgetPutClear (self):

    self.picked_up = False
    self.picked_up_from = 0
    self.picked_up_window_square = -1
    self.picked_up_widget = 0
    self.picked_up_widget_index = 0
    self.picked_up_sprite.image = self.white_bg_image
    self.picked_up_sprite.x = 0
    self.picked_up_sprite.y = 0
    self.picked_up_sprite.visible = False

    # put the cube home
    self.cube.x = 0
    self.cube.y = 0
    self.cube.visible = True


def WidgetPick (self, x, x_rec, y, y_rec, win_pos, pick_from, widget_index, widget_spr_index):

    self.picked_up = True
    self.picked_up_from = pick_from
    self.picked_up_window_square = win_pos
    self.picked_up_widget = widget_spr_index
    self.picked_up_widget_index = widget_index
    self.picked_up_sprite.image = self.spr_mv_list[widget_spr_index][1]
    self.picked_up_sprite.x = x - cfg.half_img_pix - 4
    self.picked_up_sprite.y = y - cfg.half_img_pix - 4
    self.picked_up_sprite.visible = True

    # something in progress hide cube
    self.cube.visible = False


def DoLeftClickWidgetAction (self, x, x_rec, y, y_rec, win_pos):

    widget_index = self.widget_active_squares.index(win_pos)
    widget_spr_index = self.widget_pile_list[widget_index]
#    print ("widget_index ", widget_index, " what is count?", self.widget_pile_list_counts[widget_index])
#    print ("widget_spr_index ", widget_spr_index)
    if ((self.picked_up_from == 0) or (self.picked_up_from == 1)):
        if (self.widget_pile_list_counts[widget_index] == 0):
#            print ("Widget count is zero, nothing to do...")
            pass
        elif (self.picked_up == True):
            if (win_pos == self.picked_up_window_square):

                WidgetPutClear (self)
#                print ("Dropped ", widget_index)
            else:

                WidgetPick (self, x, x_rec, y, y_rec, win_pos, 1, 
                    widget_index, widget_spr_index)
#                print ("Picked up other widget ", widget_index)
        else:
            WidgetPick (self, x, x_rec, y, y_rec, win_pos, 1, 
                widget_index, widget_spr_index)
#            print ("Picked up ", widget_index)
    elif (self.picked_up_from == 2):
#        print ("widget to put back", self.picked_up_widget)
        WidgetPutClear (self)


def GuessPut (self, x, x_rec, y, y_rec, win_pos, board_index):

    self.guess_sprites[board_index].image = self.spr_mv_list[self.picked_up_widget][1]
    self.board[board_index][1] = self.picked_up_widget
    if (self.picked_up_from == 1):
        self.widget_pile_list_counts[self.picked_up_widget_index] -= 1

    WidgetPutClear (self)


def GuessPick (self, x, x_rec, y, y_rec, win_pos, board_index):

    self.picked_up = True
    self.picked_up_from = 2
    self.picked_up_window_square = win_pos
    self.picked_up_widget = self.board[board_index][1]
    self.picked_up_sprite.image = self.guess_sprites[board_index].image
    self.guess_sprites[board_index].image = self.game_bg_image
    self.board[board_index][1] = 0
    self.picked_up_widget_index = self.widget_lookup_table[self.picked_up_widget] - 1
    self.widget_pile_list_counts[self.picked_up_widget_index] += 1
    self.picked_up_sprite.x = x - cfg.half_img_pix - 4
    self.picked_up_sprite.y = y - cfg.half_img_pix - 4
    self.picked_up_sprite.visible = True


def DoLeftClickGuessAction (self, x, x_rec, y, y_rec, win_pos):

    guess_board_index = self.board_to_window_index.index(win_pos)
#    print ("Clicked on square ", guess_board_index)

    if (self.picked_up_from == 1):
        if (self.board[guess_board_index][1] != 0):
#            print ("Guess board square not empty...")
            pass
        else:
            GuessPut (self, x, x_rec, y, y_rec, win_pos, guess_board_index)
#            print ("Put it on the board")
    else:
        if (self.board[guess_board_index][1] == 0):
#            print ("Guess board square is empty.  Nothing to move or remove...")
            pass
        else:
            GuessPick (self, x, x_rec, y, y_rec, win_pos, guess_board_index)
            self.picked_up_from = 1
#            print ("Moving or Removing...")


def DoLeftClickControlAction (self, x, x_rec, y, y_rec, win_pos):

    # lets do all of this in the dialog module
    DoDialogControlAction (self, x, x_rec, y, y_rec, win_pos)


def ActiveAreaLeftMouseClickAction (self, x, x_rec, y, y_rec, win_pos):

    cfg.square = win_pos
    if (cfg.show_board == 1):
        if (win_pos in self.white_active_squares):
#            print ("selected ", win_pos, " which is an active White square.")
            DoLeftClickWhiteAction (self, x, x_rec, y, y_rec, win_pos)
        elif (win_pos in self.widget_active_squares):
#            print ("selected ", win_pos, " which is an active Widget square.")
            DoLeftClickWidgetAction (self, x, x_rec, y, y_rec, win_pos)
        elif (win_pos in self.guess_active_squares):
#            print ("selected ", win_pos, " which is an active Guess square.")
            DoLeftClickGuessAction (self, x, x_rec, y, y_rec, win_pos)
        elif (win_pos in self.control_active_squares):
#            print ("selected ", win_pos, " which is an active Control square.")
            DoLeftClickControlAction (self, x, x_rec, y, y_rec, win_pos)
        else:
            pass


def DoGuessRotateWidgetAction (self, x, x_rec, y, y_rec, win_pos):

    board_index = self.board_to_window_index.index(win_pos)
    picked_widget = self.board[board_index][1]
    if (picked_widget == 0):
#        print ("Nothing there to rotate...")
        pass
    else:
        widget_lut = self.widget_lookup_table[picked_widget]
        widget_base = self.widget_pile_list[widget_lut-1]
        ft_wrm = self.widget_rotate_modulus[widget_lut]

#        print ("Before ==>\nboard_index ", board_index,
#               "widget_base", widget_base,
#               "picked_widget ", picked_widget,
#               "widget_lut ", widget_lut,
#               "ft_wrm ", ft_wrm
#              )
        if (ft_wrm == 0):
#            print ("Can't rotate that one...")
            return
        elif ((picked_widget + 1) >= (widget_base + ft_wrm)):
#            print ("roll around ")
            picked_widget = widget_base
        else:
#            print ("show next in sequence ")
            picked_widget += 1

#        print ("After ==>\nboard_index ", board_index,
#               "widget_base", widget_base,
#               "picked_widget ", picked_widget,
#               "widget_lut ", widget_lut,
#               "ft_wrm ", ft_wrm
#              )

        self.board[board_index][1] = picked_widget
        self.guess_sprites[board_index].image = self.spr_mv_list[picked_widget][1]
#        print ("lut ", self.widget_lookup_table)
#        print ("wpl ", self.widget_pile_list)
#        print ("wrm ", self.widget_rotate_modulus)


def ActiveAreaRightMouseClickAction (self, x, x_rec, y, y_rec, win_pos):

    cfg.square = win_pos
    if (cfg.show_board == 1):
        if (win_pos in self.white_active_squares):
#            print ("selected ", win_pos, " which is an active White square.")
            pass
        elif (win_pos in self.widget_active_squares):
#            print ("selected ", win_pos, " which is an active Widget square.")
            pass
        elif (win_pos in self.guess_active_squares):
#            print ("selected ", win_pos, " which is an active Guess square.")
            DoGuessRotateWidgetAction (self, x, x_rec, y, y_rec, win_pos)
        else:
            pass


def ActiveAreaMouseMoveAction (self, x, x_rec, y, y_rec, win_pos):

    if (cfg.show_board == 1):
        if (win_pos in self.widget_active_squares):
            if (cfg.square != win_pos):
#                print ("moved over ", win_pos, " which is an active Widget square.")
                cfg.square = win_pos
            self.picked_up_sprite.x = x - cfg.half_img_pix - 4
            self.picked_up_sprite.y = y - cfg.half_img_pix - 4
            self.picked_up_sprite.visible = True
        elif (win_pos in self.guess_active_squares):
            if (cfg.square != win_pos):
#                print ("moved over ", win_pos, " which is an active Guess square.")
                cfg.square = win_pos
            self.picked_up_sprite.x = x - cfg.half_img_pix - 4
            self.picked_up_sprite.y = y - cfg.half_img_pix - 4
            self.picked_up_sprite.visible = True
        else:
            self.picked_up_sprite.x = x_rec
            self.picked_up_sprite.y = y_rec
            self.picked_up_sprite.visible = False
    else:
        pass


