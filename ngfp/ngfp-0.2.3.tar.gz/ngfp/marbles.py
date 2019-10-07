#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) Ant <ant@anthive.com>

import pyglet
import sys
import copy
from time import sleep

import ngfp.config as cfg

from ngfp.history import UpdateAndShowArrow, HideBothArrows, HideOutArrow, HistoryNext, HistoryAndMarbleShift, MarbleShift


def MoveLeft (self):

    return (-1)


def MovingLeft (self, dir):

    return (dir == MoveLeft(self))


def MoveRight (self):

    return (1)


def MovingRight (self, dir):

    return (dir == MoveRight(self))


def MoveUp (self):

    return (self.window_cols)


def MovingUp (self, dir):

    return (dir == MoveUp(self))


def MoveDown (self):

    return (-self.window_cols)


def MovingDown (self, dir):

    return (dir == MoveDown(self))


def ReverseDir (self, dir):
    return (-dir)


def ChangeBoard (self, which_board, board_index, widget):

#    print ("ChangeBoard which_board ", which_board, "board_index ", board_index, " widget ", widget)
    self.board[board_index][which_board] = self.widget_next_widget[widget]
    if (which_board == 0):
        self.board_sprites[board_index].image = self.spr_mv_list[self.widget_next_widget[widget]][1]
    elif (which_board == 1):
        self.guess_sprites[board_index].image = self.spr_mv_list[self.widget_next_widget[widget]][1]
    else:
        pass


def MovingWidget (self, which_board, cur_pos, board_index, widget, dir):

#    print ("MovingWidget which_board ", which_board, "cur_pos ", cur_pos, " board_index ", board_index, 
#        " widget ", widget, " direction", dir)
    try:
        new_board_index = self.board_to_window_index.index(cur_pos + dir)
#        print ("    new_board_index ", new_board_index)
        if (((cur_pos + dir) in self.guess_active_squares) and 
           (self.board[new_board_index][which_board] == 0)):
#            print ("    Found a space in square ", new_board_index)
            if (which_board == 0):
                self.board_sprites[board_index].image = self.game_bg_image
                self.board_sprites[board_index].visible = False
                self.board[board_index][0] = 0
                self.board_sprites[new_board_index].image = self.spr_mv_list[widget][1]
                self.board_sprites[new_board_index].visible = True
                self.board[new_board_index][0] = widget
            elif (which_board == 1):
                self.guess_sprites[board_index].image = self.game_bg_image
                self.guess_sprites[board_index].visible = False
                self.board[board_index][1] = 0
                self.guess_sprites[new_board_index].image = self.spr_mv_list[widget][1]
                self.guess_sprites[new_board_index].visible = True
                self.board[new_board_index][1] = widget
            else:
                pass
        else:
#            print ("    No space found, didn't move widget")
            pass
    except:
        pass


def MirrorMagic (self, which_board, cur_pos, cur_dir):

    board_index = self.board_to_window_index.index(cur_pos)
    widget = self.board[board_index][which_board]
    if (which_board == 1):
#        print ("MirrorMagic board ", which_board," board index ", board_index, " widget ", widget)
        pass
    if (widget == 0):   # nothing to do here move along...
#        print ("  MirrorMagic nothing to do here...")
        return (cur_dir)
    elif (widget == 1):   # simple mirrors: left: \
        if (MovingLeft (self, cur_dir)):
            return (MoveUp (self))
        elif (MovingRight (self, cur_dir)):
            return (MoveDown (self))
        elif (MovingUp (self, cur_dir)):
            return (MoveLeft (self))
        else:
            return (MoveRight (self))
    elif (widget == 2):   # simple mirrors: right: /
        if (MovingLeft (self, cur_dir)):
            return (MoveDown (self))
        elif (MovingRight (self, cur_dir)):
            return (MoveUp (self))
        elif (MovingUp (self, cur_dir)):
            return (MoveRight (self))
        else:
            return (MoveLeft (self))
    elif (widget == 3):   # simple flipping mirrors: left: \
        ChangeBoard (self, which_board, board_index, widget)
        if (MovingLeft (self, cur_dir)):
            return (MoveUp (self))
        elif (MovingRight (self, cur_dir)):
            return (MoveDown (self))
        elif (MovingUp (self, cur_dir)):
            return (MoveLeft (self))
        else:
            return (MoveRight (self))
    elif (widget == 4):   # simple flipping mirrors: right: / 
        ChangeBoard (self, which_board, board_index, widget)
        if (MovingLeft (self, cur_dir)):
            return (MoveDown (self))
        elif (MovingRight (self, cur_dir)):
            return (MoveUp (self))
        elif (MovingUp (self, cur_dir)):
            return (MoveRight (self))
        else:
            return (MoveLeft (self))
    elif (widget == 5):   # quad flipping mirrors: left: \
        ChangeBoard (self, which_board, board_index, widget)
        if (MovingLeft (self, cur_dir)):
            return (MoveUp (self))
        elif (MovingRight (self, cur_dir)):
            return (MoveDown (self))
        elif (MovingUp (self, cur_dir)):
            return (MoveLeft (self))
        else:
            return (MoveRight (self))
    elif ((widget == 6) or (widget == 8)):   # flipping mirrors: bounce: o
        ChangeBoard (self, which_board, board_index, widget)
        return (ReverseDir (self, cur_dir))
    elif (widget == 7):   # flipping mirrors: right: /
        ChangeBoard (self, which_board, board_index, widget)
        if (MovingLeft (self, cur_dir)):
            return (MoveDown (self))
        elif (MovingRight (self, cur_dir)):
            return (MoveUp (self))
        elif (MovingUp (self, cur_dir)):
            return (MoveRight (self))
        else:
            return (MoveLeft (self))
    elif (widget == 9):  # box and sink: box: bounce: o  (reflect all)
        return (ReverseDir (self, cur_dir))
    elif (widget == 10):  # box and sink: sink: grab: x  (absorb all)
        return (None)
    elif (widget == 11):  # axial mirrors: simple vertical: |
        if (MovingLeft (self, cur_dir)):
            return (MoveRight (self))
        elif (MovingRight (self, cur_dir)):
            return (MoveLeft (self))
        else:
            return (cur_dir)
    elif (widget == 12):  # axial mirrors: simple horizontal: -
        if (MovingUp (self, cur_dir)):
            return (MoveDown (self))
        elif (MovingDown (self, cur_dir)):
            return (MoveUp (self))
        else:
            return (cur_dir)
    elif (widget == 13):   # axial mirrors: flipping vertical: ||
        ChangeBoard (self, which_board, board_index, widget)
        if (MovingLeft (self, cur_dir)):
            return (ReverseDir (self, cur_dir))
        elif (MovingRight (self, cur_dir)):
            return (ReverseDir (self, cur_dir))
        else:
            return (cur_dir)
    elif (widget == 14):   # axial mirrors: flipping horizontal: =
        ChangeBoard (self, which_board, board_index, widget)
        if (MovingUp (self, cur_dir)):
            return (ReverseDir (self, cur_dir))
        elif (MovingDown (self, cur_dir)):
            return (ReverseDir (self, cur_dir))
        else:
            return (cur_dir)
    elif (widget == 15):  # rotators simple counterclockwise: left: \\
        if (MovingLeft (self, cur_dir)):
            return (MoveUp (self))
        elif (MovingRight (self, cur_dir)):
            return (MoveDown (self))
        elif (MovingUp (self, cur_dir)):
            return (MoveRight (self))
        else:
            return (MoveLeft (self))
    elif (widget == 16):  # rotators simple clockwise: right: //
        if (MovingLeft (self, cur_dir)):
            return (MoveDown (self))
        elif (MovingRight (self, cur_dir)):
            return (MoveUp (self))
        elif (MovingUp (self, cur_dir)):
            return (MoveLeft (self))
        else:
            return (MoveRight (self))
    elif (widget == 17):  # rotators flipper clockwise: left: []
        ChangeBoard (self, which_board, board_index, widget)
        if (MovingLeft (self, cur_dir)):
            return (MoveUp (self))
        elif (MovingRight (self, cur_dir)):
            return (MoveDown (self))
        elif (MovingUp (self, cur_dir)):
            return (MoveRight (self))
        else:
            return (MoveLeft (self))
    elif (widget == 18):  # rotators flipper counterclockwise: right: ][
        ChangeBoard (self, which_board, board_index, widget)
        if (MovingLeft (self, cur_dir)):
            return (MoveDown (self))
        elif (MovingRight (self, cur_dir)):
            return (MoveUp (self))
        elif (MovingUp (self, cur_dir)):
            return (MoveLeft (self))
        else:
            return (MoveRight (self))
    elif (widget == 19):   # 1-way mirrors: left: lower reflects: \<-
        if (MovingRight (self, cur_dir)):
            return (MoveDown (self))
        elif (MovingUp (self, cur_dir)):
            return (MoveLeft (self))
        else:
            return (cur_dir)
    elif (widget == 20):   # 1-way mirrors: left: upper reflects: ->\
        if (MovingLeft (self, cur_dir)):
            return (MoveUp (self))
        elif (MovingDown (self, cur_dir)):
            return (MoveRight (self))
        else:
            return (cur_dir)
    elif (widget == 21):   # 1-way mirrors: right: lower reflects: ->/
        if (MovingLeft (self, cur_dir)):
            return (MoveDown (self))
        elif (MovingUp (self, cur_dir)):
            return (MoveRight (self))
        else:
            return (cur_dir)
    elif (widget == 22):   # 1-way mirrors: right: upper reflects: /<-
        if (MovingRight (self, cur_dir)):
            return (MoveUp (self))
        elif (MovingDown (self, cur_dir)):
            return (MoveLeft (self))
        else:
            return (cur_dir)
    elif (widget == 23):  # flipping 1-way mirrors: left: lower reflects: rotates clockwise: \\\<-
        ChangeBoard (self, which_board, board_index, widget)
        if (MovingRight (self, cur_dir)):
            return (MoveDown (self))
        elif (MovingUp (self, cur_dir)):
            return (MoveLeft (self))
        else:
            return (cur_dir)
    elif (widget == 24):  # flipping 1-way mirrors: right: upper reflects: rotates clockwise: ///<-
        ChangeBoard (self, which_board, board_index, widget)
        if (MovingRight (self, cur_dir)):
            return (MoveUp (self))
        elif (MovingDown (self, cur_dir)):
            return (MoveLeft (self))
        else:
            return (cur_dir)
    elif (widget == 25):  # flipping 1-way mirrors: left: upper reflects: rotates clockwise: ->\\\
        ChangeBoard (self, which_board, board_index, widget)
        if (MovingLeft (self, cur_dir)):
            return (MoveUp (self))
        elif (MovingDown (self, cur_dir)):
            return (MoveRight (self))
        else:
            return (cur_dir)
    elif (widget == 26):  # flipping 1-way mirrors: right: lower reflects: rotates clockwise: ->///
        ChangeBoard (self, which_board, board_index, widget)
        if (MovingLeft (self, cur_dir)):
            return (MoveDown (self))
        elif (MovingUp (self, cur_dir)):
            return (MoveRight (self))
        else:
            return (cur_dir)
    elif (widget == 27): # flipping 1-way mirrors: left: upper reflects: rotates counterclockwise: ->\\\
        ChangeBoard (self, which_board, board_index, widget)
        if (MovingLeft (self, cur_dir)):
            return (MoveUp (self))
        elif (MovingDown (self, cur_dir)):
            return (MoveRight (self))
        else:
            return (cur_dir)
    elif (widget == 28): # flipping 1-way mirrors: right: upper reflects: rotates counterclockwise: ///<-
        ChangeBoard (self, which_board, board_index, widget)
        if (MovingRight (self, cur_dir)):
            return (MoveUp (self))
        elif (MovingDown (self, cur_dir)):
            return (MoveLeft (self))
        else:
            return (cur_dir)
    elif (widget == 29): # flipping 1-way mirrors: left: lower reflects: rotates counterclockwise: \\\<-
        ChangeBoard (self, which_board, board_index, widget)
        if (MovingRight (self, cur_dir)):
            return (MoveDown (self))
        elif (MovingUp (self, cur_dir)):
            return (MoveLeft (self))
        else:
            return (cur_dir)
    elif (widget == 30): # flipping 1-way mirrors: right: lower reflects: rotates counterclockwise: ->///
        ChangeBoard (self, which_board, board_index, widget)
        if (MovingLeft (self, cur_dir)):
            return (MoveDown (self))
        elif (MovingUp (self, cur_dir)):
            return (MoveRight (self))
        else:
            return (cur_dir)
    elif (widget == 31): # moving mirror: left: -->\X\--> ---->\X\
        MovingWidget (self, which_board, cur_pos, board_index, widget, cur_dir)
        if (MovingLeft (self, cur_dir)):
            return (MoveUp (self))
        elif (MovingRight (self, cur_dir)):
            return (MoveDown (self))
        elif (MovingUp (self, cur_dir)):
            return (MoveLeft (self))
        else:
            return (MoveRight (self))
    elif (widget == 32): # moving mirror: right: <--/X/<-- /X/<----
        MovingWidget (self, which_board, cur_pos, board_index, widget, cur_dir)
        if (MovingLeft (self, cur_dir)):
            return (MoveDown (self))
        elif (MovingRight (self, cur_dir)):
            return (MoveUp (self))
        elif (MovingUp (self, cur_dir)):
            return (MoveRight (self))
        else:
            return (MoveLeft (self))
    else:
        print ("  MirrorMagic fell through with widget (there shouldn't be any left)???", widget, " widget_next_widget ", self.widget_next_widget[widget])
        return (cur_dir)


def ShowWhiteInArrow (self, win_pos, visible):

    win_pos_index = self.white_active_squares.index(win_pos)
    SWI_xy_coordinates = copy.deepcopy(self.white_active_squares_position[win_pos_index])
#    print ("SW In Arrow XY coordinates", SWI_xy_coordinates)
    rotate = 0.0
    self.kept_start_pos = win_pos
    self.kept_start_pos_x = SWI_xy_coordinates[0]
    self.kept_start_pos_y = SWI_xy_coordinates[1]
    if (win_pos in self.dir_left):             # if we've clicked on the left side it
        self.start_direction = MoveRight(self) # means we're going right
        self.kept_start_dx = 1
        self.kept_start_dy = 0
        self.kept_start_pos_x += cfg.img_pix - cfg.tic_pix
        SWI_xy_coordinates[0] += cfg.half_img_pix
        image = self.arrow_images[1]
    elif (win_pos in self.dir_right):          # if we've clicked on the right side it
        self.start_direction = MoveLeft(self)  # means we're going left
        self.kept_start_dx = -1
        self.kept_start_dy = 0
        self.kept_start_pos_x -= cfg.tic_pix
        image = self.arrow_images[0]
    elif (win_pos in self.dir_up):             #  etc.
        self.start_direction = MoveDown(self)
        self.kept_start_dx = 0
        self.kept_start_dy = -1
        self.kept_start_pos_y -= cfg.img_pix - cfg.tic_pix
        image = self.arrow_images[3]
        rotate = 90.0
    else:
        self.start_direction = MoveUp(self)
        self.kept_start_dx = 0
        self.kept_start_dy = 1
        self.kept_start_pos_y += cfg.img_pix - cfg.tic_pix
        SWI_xy_coordinates[1] += cfg.half_img_pix
        image = self.arrow_images[2]
        rotate = 90.0
    self.kept_start_direction = self.start_direction
    UpdateAndShowArrow(self, image, 0, SWI_xy_coordinates, rotate, visible)


def ShowWhiteOutArrow (self, win_pos, visible):

    if (self.stop_direction == None):
#        print ("SW Out Arrow __No__ Arrow Out")
        pass
    else:
        win_pos_index = self.white_active_squares.index(win_pos)
        SWO_xy_coordinates = copy.deepcopy(self.white_active_squares_position[win_pos_index])
#        print ("SW Out Arrow XY coordinates", SWO_xy_coordinates)
        rotate = 0.0
        if (win_pos in self.dir_left):             # if on the left side it
            self.stop_direction = MoveLeft(self)   # means we're going left
            image = self.arrow_images[0]
        elif (win_pos in self.dir_right):          # if on the right side it
            self.stop_direction = MoveRight(self)  # means we're going right
            SWO_xy_coordinates[0] += cfg.half_img_pix
            image = self.arrow_images[1]
        elif (win_pos in self.dir_up):             #  etc.
            self.stop_direction = MoveUp(self)
            SWO_xy_coordinates[1] += cfg.half_img_pix
            image = self.arrow_images[2]
            rotate = 90.0
        else:
            self.stop_direction = MoveDown(self)
            image = self.arrow_images[3]
            rotate = 90.0
        UpdateAndShowArrow(self, image, 1, SWO_xy_coordinates, rotate, visible)


def StartMarble (self, win_pos, visible):

    self.marble_current_pos = self.kept_start_pos + self.kept_start_direction
    self.marble_current_direction = self.kept_start_direction

#    print ("Start Marble CP, CD ", self.marble_current_pos, self.marble_current_direction)

    self.marble_sprites[0].x = self.kept_start_pos_x
    self.marble_sprites[0].y = self.kept_start_pos_y
    self.marble_sprites[0].dx = self.kept_start_dx
    self.marble_sprites[0].dy = self.kept_start_dy
    self.marble_sprites[0].visible = visible
    for i in range (len (self.marble_sprites) - 1):
        self.marble_sprites[i+1].x = 0
        self.marble_sprites[i+1].y = 0
        self.marble_sprites[i+1].dx = 0
        self.marble_sprites[i+1].dy = 0
        self.marble_sprites[i+1].visible = False

#    print ("Start Marble CP, CD,  x,y with dx,dy ", 
#        self.marble_current_pos,
#        self.marble_current_direction,
#        self.marble_sprites[0].x,
#        self.marble_sprites[0].y,
#        self.marble_sprites[0].dx,
#        self.marble_sprites[0].dy)


def StopMarble (self, pos):

#    print ("StopMarble Pre Shift  : ", self.marble_sprites[pos].x, self.marble_sprites[pos].y)
    self.marble_sprites[pos].visible = False
    MarbleShift(self)
    self.marble_sprites[pos].x = self.marble_sprites[pos-1].x
    self.marble_sprites[pos].y = self.marble_sprites[pos-1].y
    self.marble_sprites[pos].visible = True
    cfg.no_user_actions = False
#    print ("StopMarble Post Shift : ", self.marble_sprites[pos].x, self.marble_sprites[pos].y)


def MarbleInMotion (self, which_board, x_rec, y_rec, win_pos, visible):

    cfg.no_user_actions = True
    HideBothArrows (self)
    start_pos = win_pos
    self.start_direction = None
    self.stop_direction = None
    self.cube.x = 0
    self.cube.y = 0
    self.cube.visible = False
    self.pointer_top_batch.draw()
    self.variable_guess_batch.draw()
    self.flip()
    ShowWhiteInArrow (self, win_pos, visible)
    for i in range(self.history_limit):
        self.color_batch_list[i].draw()
    self.marble_tick_count = 0
    StartMarble(self, win_pos, visible)
    self.marble_batch.draw()
    self.arrow_batch.draw()
    self.flip()
    self.cube.visible = True
#    print ("Starting to move game marble from ", start_pos, "in direction ", self.start_direction)

    tick_count = 0  #  we better have some limit just in case of long loops
    current_pos = start_pos + self.start_direction
    current_direction = self.start_direction
#    print ("First move game marble from ", current_pos, "in direction ", current_direction)
    while (
        (current_pos in self.guess_active_squares) and 
        (tick_count < self.tick_limit) and 
        (current_pos != None)):
        tick_count += 1
        new_dir = MirrorMagic (self, which_board, current_pos, current_direction)
        if (new_dir != None):
#            if (current_pos in self.guess_active_squares):
#                cube_xy = self.guess_active_squares_position[self.guess_active_squares.index(current_pos)]
#                print ("   Cube xy ", cube_xy)
#                self.cube.visible = True
#                self.cube.x = cube_xy[0]
#                self.cube.y = cube_xy[1]
#                self.pointer_top_batch.draw()
#                self.flip()
#            print ("Moved: game marble Tick, CP, CD ", tick_count, current_pos, current_direction)
#            sleep (0.08)
            current_pos += new_dir
            current_direction = new_dir
            self.stop_direction = current_direction
        else:
#            print ("Didn't Move: game marble Tick, CP, CD ", tick_count, current_pos, current_direction)
            self.stop_direction = None
            break

#    print ("Last moved game marble at ", current_pos, "in direction ", current_direction)
    if (tick_count >= self.tick_limit):
#        print ("Exceeded game marble tick_count of ", self.tick_limit)
        return_value = -1
    elif (self.stop_direction == None):
#        print ("No game marble Arrow Out...")
        HideOutArrow (self)
        return_value = None
    else:
        ShowWhiteOutArrow (self, current_pos, visible)
        return_value  = current_pos
    HistoryNext (self)
    HistoryAndMarbleShift (self)
    return (return_value)


def DoLeftClickWhiteAction (self, x, x_rec, y, y_rec, win_pos):

    value = MarbleInMotion (self, 0, x_rec, y_rec, win_pos, True)
#    print ("MIM 0 T ret_val ", value)


def CheckMarbleChangeDirection (self, sprite_index, x, y):

#    print ("Check Marble Change Direction at x,y ", x, y)
    self.marble_tick_count += 1
    if (self.marble_current_pos not in self.guess_active_squares): 
#        print ("Check Marble Tick, CP, CD Not in guess active squares ", self.marble_tick_count, self.marble_current_pos, self.marble_current_direction)
        pass
    else:
#        print ("Check Marble Tick, CP, CD ", self.marble_tick_count, self.marble_current_pos, self.marble_current_direction)
        old_dir = self.marble_current_direction
        new_dir = MirrorMagic (self, 1, self.marble_current_pos, self.marble_current_direction)
        if (new_dir != None):
            self.marble_current_pos += new_dir
            self.marble_current_direction = new_dir
            self.marble_stop_direction = self.marble_current_direction
            if (old_dir == new_dir):
#               print ("Check Marble didn't change direction... ")
                pass
            elif (old_dir == -new_dir):
#                print ("Check Marble reversed direction... ")
                self.marble_sprites[sprite_index].dx *= -1
                self.marble_sprites[sprite_index].x +=  cfg.tic_pix * self.marble_sprites[sprite_index].dx
                self.marble_sprites[sprite_index].dy *= -1
                self.marble_sprites[sprite_index].y +=  cfg.tic_pix * self.marble_sprites[sprite_index].dy
            elif ((MovingLeft (self, old_dir) or MovingRight (self, old_dir)) and
                  (MovingUp (self, new_dir) or MovingDown (self, new_dir))):
#                print ("Check Marble reflected Up or Down... ")
                self.marble_sprites[sprite_index].dx = 0
                self.marble_sprites[sprite_index].dy = new_dir//abs(new_dir)
                self.marble_sprites[sprite_index].y +=  cfg.tic_pix * self.marble_sprites[sprite_index].dy
            elif ((MovingUp (self, old_dir) or MovingDown (self, old_dir)) and
                  (MovingLeft (self, new_dir) or MovingRight (self, new_dir))):
#                print ("Check Marble reflected Left or Right... ")
                self.marble_sprites[sprite_index].dy = 0
                self.marble_sprites[sprite_index].dx = new_dir//abs(new_dir)
                self.marble_sprites[sprite_index].x +=  cfg.tic_pix * self.marble_sprites[sprite_index].dx
            else:
                pass
        else:
#            print ("Didn't Move: Check Marble Tick, CP, CD ", self.marble_tick_count, self.marble_current_pos, self.marble_current_direction)
            self.marble_sprites[sprite_index].dx = 0
            self.marble_sprites[sprite_index].dy = 0
            self.marble_stop_direction = None
            self.marble_tick_count = self.tick_limit
            StopMarble(self, sprite_index)

    if (self.marble_tick_count > self.tick_limit):
#        print ("Check Marble Exceeded tick_count of ", self.tick_limit)
        StopMarble(self, sprite_index)
        pass


