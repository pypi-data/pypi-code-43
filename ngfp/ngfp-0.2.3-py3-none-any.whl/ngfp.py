#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) Ant <ant@anthive.com>

import pyglet
from pyglet.window import mouse
from pyglet import clock

import ngfp.config as cfg

from ngfp.active import ActiveAreaLeftMouseClickAction, ActiveAreaRightMouseClickAction, ActiveAreaMouseMoveAction
from ngfp.board import ClearSquareMarkers, ClearAllMarkers, ToggleMarker, RestartGame, DrawBoard
from ngfp.dialog import ShowHelp
from ngfp.labels import UpdateLabels
from ngfp.marbles import CheckMarbleChangeDirection, StopMarble
from ngfp.my_init import MyInitStuff


class Window(pyglet.window.Window):

    def __init__ (
            self,
            width,
            height,
            caption,
            resizable,
            fullscreen,
            visible,
            *args,
            **kwargs):


        super(Window, self).__init__(width, height, caption, resizable, fullscreen, visible, *args, **kwargs)

        self.set_visible(False)

        MyInitStuff (self)

        # put the gcube and cube someplace.
        # i may not need these eventually so not going to make this
        # a function for now...
        x_pos = cfg.img_pix * (cfg.game_cols+1)
        y_pos = 0
        self.gcube = pyglet.sprite.Sprite( self.gcube_image, batch=self.pointer_bottom_batch, x = x_pos, y = y_pos)
        self.gcube.visible = False
        self.top_sprites.append(self.gcube)
        x_pos = 0
        y_pos = 0
        self.cube = pyglet.sprite.Sprite( self.cube_image, batch=self.pointer_top_batch, x = x_pos, y = y_pos)
        self.cube.visible = False
        self.top_sprites.append(self.cube)

        self.picked_up = False
        self.picked_up_window_square = -1
        self.picked_up_sprite = pyglet.sprite.Sprite( self.game_bg_image, batch=self.pointer_top_batch, x = 0, y = 0)
        self.picked_up_sprite.visible = False
        self.picked_up_sprite.opacity = 150


    def on_draw(self):
        self.render()


    def on_close(self):
        exit()


    def on_mouse_press(self, x, y, button, modifiers):

        # only do things when something else isn't happening
        if (cfg.no_user_actions == False):
            img_pix = cfg.img_pix
            x_win = x // img_pix
            x_rec = x_win * img_pix
            y_win = y // img_pix
            y_rec = y_win * img_pix
            win_pos = (y_win * self.window_cols) + x_win

            if button == mouse.LEFT:
#                print("The LEFT mouse button was pressed.", x, x_rec, x_win, y, y_rec, y_win, win_pos)
                ActiveAreaLeftMouseClickAction(self, x, x_rec, y, y_rec, win_pos)
            elif button == mouse.MIDDLE:
#                print("The MIDDLE mouse button was pressed.", x, x_rec, x_win, y, y_rec, y_win, win_pos)
                pass
            elif button == mouse.RIGHT:
#                print("The RIGHT mouse button was pressed.", x, x_rec, x_win, y, y_rec, y_win, win_pos)
                ActiveAreaRightMouseClickAction(self, x, x_rec, y, y_rec, win_pos)


    def on_mouse_release(self, x, y, button, modifiers):
#        print ("The mouse was released")
        pass


    def on_mouse_motion(self, x, y, dx, dy):

        # don't do anything when something else is happening
        if (cfg.no_user_actions == True):
            return ()

        img_pix = cfg.img_pix
        x_win = x // img_pix
        x_rec = x_win * img_pix
        y_win = y // img_pix
        y_rec = y_win * img_pix
        win_pos = (y_win * self.window_cols) + x_win

        if (win_pos in self.guess_active_squares):
            self.mouse_win_pos = win_pos

        if (self.picked_up):
            ActiveAreaMouseMoveAction(self, x, x_rec, y, y_rec, win_pos)
        else:
            pass


    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        pass


    def on_mouse_leave(self, x, y):
        pass


    def on_mouse_enter(self, x, y):
        pass


    def on_key_press(self, symbol, modifiers):

        self.keys_held.append(symbol)
        if ((symbol == pyglet.window.key.ESCAPE) or (symbol == pyglet.window.key.Q)): # [ESC] or [Q]
#            print ("The 'ESC' or 'Q' key was pressed")
            exit()
        elif ((symbol == pyglet.window.key.F1) or
            (symbol == pyglet.window.key.QUESTION) or
            (symbol == pyglet.window.key.H)):
            ShowHelp (self)
#            print ("The 'F1', 'H', or '?' key was pressed ")
            pass
        elif symbol == pyglet.window.key.F2:
#            print ("The 'F2' key was pressed, show board ", cfg.show_board)
            # after the initial showing of the background we
            # don't ever need to see the background again so 
            # only toggle between the game board and the guess 
            # board (0 or 1)...
            cfg.show_board = (cfg.show_board + 1) % 2

            if (cfg.show_board == 0):
                self.cube.visible = True
                self.gcube.visible = False
                if (self.picked_up == True):
                    self.picked_up_sprite.visible = False
            elif (cfg.show_board == 1):
                self.cube.visible = False
                self.gcube.visible = True
                if (self.picked_up == True):
                    self.picked_up_sprite.visible = True
#            print ("The 'F2' key was pressed, show board changed to ", cfg.show_board)
        elif ((cfg.show_board == 1) and (symbol == pyglet.window.key.F3)):
            ClearSquareMarkers(self)
        elif ((cfg.show_board == 1) and (symbol == pyglet.window.key.F4)):
            ClearAllMarkers(self)
        elif ((cfg.show_board == 1) and (symbol == pyglet.window.key.F5)):
            RestartGame(self)
        elif ((cfg.show_board == 1) and (symbol == pyglet.window.key.J)):
            ToggleMarker(self, 0)
        elif ((cfg.show_board == 1) and (symbol == pyglet.window.key.K)):
            ToggleMarker(self, 1)
        elif ((cfg.show_board == 1) and (symbol == pyglet.window.key.L)):
            ToggleMarker(self, 2)
        elif ((cfg.show_board == 1) and (symbol == pyglet.window.key.SEMICOLON)):
            ToggleMarker(self, 3)
#        elif symbol == pyglet.window.key.LEFT:
#            if self.cube.x > 0:
#                self.cube.x -= cfg.img_pix
#            print ("The 'LEFT' key was pressed")
#        elif symbol == pyglet.window.key.RIGHT:
#            if self.cube.x < self.game_board_x_limit:
#                self.cube.x += cfg.img_pix
#            print ("The 'RIGHT' key was pressed")
#        elif symbol == pyglet.window.key.UP:
#            if self.cube.y < self.game_board_y_limit:
#                self.cube.y += cfg.img_pix
#            print ("The 'UP' key was pressed")
#        elif symbol == pyglet.window.key.DOWN:
#            if self.cube.y > 0:
#                self.cube.y -= cfg.img_pix
#            print ("The 'DOWN' key was pressed")


    def on_key_release(self, symbol, modifiers):
        try:
            self.keys_held.pop(self.keys_held.index(symbol))
#            print ("The key was released")
        except:
            pass


    def update(self, dt):

        for i in range(len(self.marble_sprites)):
            if ((self.marble_sprites[i].x == 0) and
                (self.marble_sprites[i].y == 0)):
                self.marble_sprites[i].dx = 0
                self.marble_sprites[i].dy = 0
                self.marble_sprites[i].visible = False
            elif (self.marble_sprites[i].visible == True):

                if ((self.marble_sprites[i].dx != 0) and
                    (self.marble_sprites[i].x >= self.game_board_x_upper_limit)):
                    self.marble_sprites[i].x = self.game_board_x_upper_limit
                    self.marble_sprites[i].dx = 0
                    StopMarble (self, i)
                elif ((self.marble_sprites[i].dx != 0) and
                    (self.marble_sprites[i].x <= (self.game_board_x_lower_limit - cfg.img_pix))):
                    self.marble_sprites[i].x = self.game_board_x_lower_limit - cfg.img_pix
                    self.marble_sprites[i].dx = 0
                    StopMarble (self, i)
                elif (self.marble_sprites[i].dx != 0):
                    if (((self.marble_sprites[i].x % cfg.img_pix) == 0) and
                        ((self.marble_sprites[i].y % cfg.img_pix) == 0)):
                        CheckMarbleChangeDirection (self, i, self.marble_sprites[i].x, self.marble_sprites[i].y)
                    tmp_pix = cfg.tic_pix
                    self.marble_sprites[i].x += tmp_pix * self.marble_sprites[i].dx

                if ((self.marble_sprites[i].dy != 0) and
                    (self.marble_sprites[i].y >= self.game_board_y_upper_limit)):
                    self.marble_sprites[i].y = self.game_board_y_upper_limit
                    self.marble_sprites[i].dy = 0
                    StopMarble (self, i)
                elif ((self.marble_sprites[i].dy != 0) and
                    (self.marble_sprites[i].y <= (self.game_board_y_lower_limit - cfg.img_pix))):
                    self.marble_sprites[i].y = self.game_board_y_lower_limit - cfg.img_pix
                    self.marble_sprites[i].dy = 0
                    StopMarble (self, i)
                elif (self.marble_sprites[i].dy != 0):
                    if (((self.marble_sprites[i].x % cfg.img_pix) == 0) and
                        ((self.marble_sprites[i].y % cfg.img_pix) == 0)):
                        CheckMarbleChangeDirection (self, i, self.marble_sprites[i].x, self.marble_sprites[i].y)
                    tmp_pix = cfg.tic_pix
                    self.marble_sprites[i].y += tmp_pix * self.marble_sprites[i].dy


    def render(self):

        self.clear()

        DrawBoard (self)

        UpdateLabels(self)

        self.fixed_batch.draw()
        self.green_batch.draw()
        self.control_batch.draw()
        self.widget_batch.draw()
        self.fixed_board_batch.draw()
        self.variable_board_batch.draw()
        self.variable_guess_batch.draw()
        self.pointer_bottom_batch.draw()
        self.pointer_top_batch.draw()
        self.marble_batch.draw()
        for i in range(self.history_limit):
            self.color_batch_list[i].draw()
        self.arrow_batch.draw()
        self.marker_batch.draw()
        self.text_batch.draw()

#        self.fps.draw()

        self.flip()


def main():
    window = Window(width=cfg.img_pix*(cfg.game_cols+cfg.control_cols+3), height=cfg.img_pix*(cfg.game_rows+2), caption="Ngfp", resizable=False, fullscreen=False, visible=False)
    pyglet.clock.schedule_interval(window.update, 1/120.0) # update at 60Hz
    pyglet.app.run()


if __name__ == "__main__":
    main()


