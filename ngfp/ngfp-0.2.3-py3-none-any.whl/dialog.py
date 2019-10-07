#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) Ant <ant@anthive.com>

import os
import pyglet
import sys
import copy
import json
from pathlib import Path
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gio
from gi.repository import Gtk
from gi.repository import Gdk

import ngfp.config as cfg

from ngfp.board import ClearAndResizeBoard, DrawBoard
from ngfp.marbles import MarbleInMotion
from ngfp.version import GetVersion


setting = Gio.Settings.new("org.gtk.Settings.FileChooser")
setting.set_boolean("sort-directories-first", True)


class DialogWindow(Gtk.Window):


    def __init__(self):
        Gtk.Window.__init__(self)

        self.set_keep_above(True)
        self.set_default_size(500, 200)
        self.set_border_width (30)
#        self.set_title ("DialogWindow")

        self.set_position (Gtk.WindowPosition.CENTER)


        self.box = Gtk.Box (spacing=40, orientation=Gtk.Orientation.VERTICAL)
        self.add(self.box)

        self.label = Gtk.Label("Additional Information")
        self.box.add(self.label)

        button = Gtk.Button("Ok")
        button.connect("clicked", self.on_ok_button_clicked)

        self.box.add(button)

        self.show_all()


    def on_ok_button_clicked(self, widget):

#        print("The OK button was clicked")

        self.destroy()


def DialogWin (title, added):

    info_win = DialogWindow()
    info_win.connect("destroy", Gtk.main_quit)
    info_win.set_title(title)
    info_win.label.set_text(added)
    info_win.show_all()
    Gtk.main()


# print configuration parameters
def print_cfg ():
    print ("C ", cfg.game_cols, cfg.game_rows, cfg.density, cfg.density_fuzz, cfg.class_weights)
    print ("D ", cfg.default_game_cols, cfg.default_game_rows, cfg.default_density, cfg.default_density_fuzz, cfg.default_class_weights)


def LoadConfigOrUseCurrent ():

    if (cfg.full_config_filename.exists() == True):
        with open(cfg.full_config_filename, "r") as fn:
            loaded_config = json.load(fn)
#            print ("LoadConfigOrUseCurrent config loaded : ", loaded_config)
            cfg.default_game_cols = loaded_config[1][0]
            cfg.default_game_rows = loaded_config[1][1]
            cfg.default_density = loaded_config[1][2]
            cfg.default_density_fuzz = loaded_config[1][3]
            cfg.default_class_weights = copy.deepcopy(loaded_config[1][4])
            cfg.game_cols = loaded_config[2][0]
            cfg.game_rows = loaded_config[2][1]
            cfg.density = loaded_config[2][2]
            cfg.density_fuzz = loaded_config[2][3]
            cfg.class_weights = copy.deepcopy(loaded_config[2][4])
            if (cfg.show_board != 2):
                DialogWin (
                    "              Ngfp Configuration Loaded             ",
                    "                                                    "
                    )

    else:
        # current defaults are set in config.py
        # and we don't want to clobber or reset
        # them unless the user specifically requests it
#        print ("Use Current Parameters")
        if (cfg.show_board != 2):
            DialogWin (
                "          Ngfp Configuration File Doesn't Exist         ",
                "     The current defaults are being used instead        "
            )

#    print_cfg ()


def SaveConfigToFile ():
#    print_cfg ()
    if (cfg.config_path.exists() != True):
#        print ("Creating : ", str(cfg.config_path))
        cfg.config_path.mkdir(mode=0o700, parents=True, exist_ok=False)
        DialogWin (
            "           Ngfp No Configuration Directory Exists            ",
            "         We've created " + str(cfg.config_path) + "          "
            )

    with open(cfg.full_config_filename, mode="w") as fileout:
        json.dump([["NGFP_Config\n", 1], [cfg.default_game_cols, cfg.default_game_rows, cfg.default_density, cfg.default_density_fuzz, cfg.default_class_weights],[cfg.game_cols, cfg.game_rows, cfg.density, cfg.density_fuzz, cfg.class_weights]], fileout, indent = 4, separators=(',', ': '))

    DialogWin (
        "               Ngfp Configuration Saved                ",
        "                                                       "
        )


class MyConfigWindow(Gtk.ApplicationWindow):


    def __init__(self, app):
        Gtk.Window.__init__(self, title="Ngfp Configuration", application=app)
        self.set_default_size(600, 600)
        self.set_border_width (30)
        self.set_position (Gtk.WindowPosition.CENTER)

        # adjustments (initial value, min value, max value,
        # step increment - press cursor keys to see!,
        # page increment - click around the handle to see!,
        # page size - not used here)
        adj_width = Gtk.Adjustment(cfg.game_cols, cfg.min_cols, cfg.max_cols, 1, 1, 0)
        adj_height = Gtk.Adjustment(cfg.game_rows, cfg.min_rows, cfg.max_rows, 1, 1, 0)
        adj_density = Gtk.Adjustment(cfg.density, 0, 100, 1, 1, 0)
        adj_density_fuzz = Gtk.Adjustment(cfg.density_fuzz, 0, (100 - cfg.density), 1, 1, 0)

        # a horizontal scale
        self.h1_scale = Gtk.Scale(
            orientation=Gtk.Orientation.HORIZONTAL, adjustment=adj_width)
        # of integers (no digits)
        self.h1_scale.set_digits(0)
        # that can expand horizontally if there is space in the grid (see
        # below)
        self.h1_scale.set_hexpand(False)
        # that is aligned at the top of the space allowed in the grid (see
        # below)
        self.h1_scale.set_valign(Gtk.Align.START)

        # we connect the signal "value-changed" emitted by the scale with the callback
        # function left_h1_scale_moved
        self.h1_scale.connect("value-changed", self.left_h1_scale_moved)

        # 2nd horizontal scale
        self.h2_scale = Gtk.Scale(
            orientation=Gtk.Orientation.HORIZONTAL, adjustment=adj_height)
        # of integers (no digits)
        self.h2_scale.set_digits(0)
        # that can expand horizontally if there is space in the grid (see below)
        self.h2_scale.set_hexpand(False)

        # we connect the signal "value-changed" emitted by the scale with the callback
        # function left_h2_scale_moved
        self.h2_scale.connect("value-changed", self.left_h2_scale_moved)

        # 3rd horizontal scale
        self.h3_scale = Gtk.Scale(
            orientation=Gtk.Orientation.HORIZONTAL, adjustment=adj_density)
        # of integers (no digits)
        self.h3_scale.set_digits(0)
        # that can expand horizontally if there is space in the grid (see below)
        self.h3_scale.set_hexpand(False)

        # we connect the signal "value-changed" emitted by the scale with the callback
        # function left_h3_scale_moved
        self.h3_scale.connect("value-changed", self.left_h3_scale_moved)

        # 4th horizontal scale
        self.h4_scale = Gtk.Scale(
            orientation=Gtk.Orientation.HORIZONTAL, adjustment=adj_density_fuzz)
        # of integers (no digits)
        self.h4_scale.set_digits(0)
        # that can expand horizontally if there is space in the grid (see below)
        self.h4_scale.set_hexpand(False)

        # we connect the signal "value-changed" emitted by the scale with the callback
        # function left_h4_scale_moved
        self.h4_scale.connect("value-changed", self.left_h4_scale_moved)

        # the four labels needed on the left side
        self.l1_label = Gtk.Label()
        self.l1_label.set_text(cfg.property_labels[0])
        self.l2_label = Gtk.Label()
        self.l2_label.set_text(cfg.property_labels[1])
        self.l3_label = Gtk.Label()
        self.l3_label.set_text(cfg.property_labels[2])
        self.l4_label = Gtk.Label()
        self.l4_label.set_text(cfg.property_labels[3])

        # and then the bottom label for the left side
        self.bottom_label_left = Gtk.Label()
        self.bottom_label_left.set_text("Move the scale handles...")
        self.bottom_label_left.set_width_chars (21)

        # a grid to attach the widgets
        self.grid = Gtk.Grid ()
        self.grid.set_row_homogeneous (True)
        self.grid.set_column_spacing (2)
        self.grid.set_row_spacing (20)

        # do the left side first
        self.grid.add (self.h1_scale)
        self.grid.attach_next_to (self.l1_label, self.h1_scale, Gtk.PositionType.BOTTOM, 1, 1)
        self.grid.attach_next_to (self.h2_scale, self.l1_label, Gtk.PositionType.BOTTOM, 1, 1)
        self.grid.attach_next_to (self.l2_label, self.h2_scale, Gtk.PositionType.BOTTOM, 1, 1)
        self.grid.attach_next_to (self.h3_scale, self.l2_label, Gtk.PositionType.BOTTOM, 1, 1)
        self.grid.attach_next_to (self.l3_label, self.h3_scale, Gtk.PositionType.BOTTOM, 1, 1)
        self.grid.attach_next_to (self.h4_scale, self.l3_label, Gtk.PositionType.BOTTOM, 1, 1)
        self.grid.attach_next_to (self.l4_label, self.h4_scale, Gtk.PositionType.BOTTOM, 1, 1)
        self.grid.attach_next_to (self.bottom_label_left, self.l4_label, Gtk.PositionType.BOTTOM, 1, 1)

        class_pack = []
        class_label = []
        class_pic_pack = []
        class_pic_left = []
        class_pic_right = []
        class_adj = []
        self.class_scale = []

        # ok, now the right side
        pic_ind = 0
        j = 0
        col = 1
        for i in range(len(cfg.widget_class_labels)):
            class_pack.append (Gtk.Box (orientation=Gtk.Orientation.VERTICAL))
            class_label.append (Gtk.Label (cfg.widget_class_labels[i]))
            class_pack[i].pack_start (class_label[i], True, False, 0)
            class_label[i].set_width_chars (15)
            class_pic_pack.append (Gtk.Box (spacing=50))
            class_pic_pack[i].set_halign (Gtk.Align.CENTER)
            class_pic_left.append (Gtk.Image.new_from_file(cfg.pic_list[cfg.config_percent_list[pic_ind]]))
            pic_ind += 1
            class_pic_right.append (Gtk.Image.new_from_file(cfg.pic_list[cfg.config_percent_list[pic_ind]]))
            pic_ind += 1
            class_pic_pack[i].pack_start (class_pic_left[i], False, False, 0)
            class_pic_pack[i].pack_start (class_pic_right[i], False, False, 0)
            class_pack[i].pack_start (class_pic_pack[i], True, True, 0)
            class_adj.append (Gtk.Adjustment (cfg.class_weights[i], 1, 100, 1, 1, 0))
            self.class_scale.append (Gtk.Scale (orientation=Gtk.Orientation.HORIZONTAL, adjustment=class_adj[i]))
            self.class_scale[i].set_digits(0)
            class_pack[i].pack_start (self.class_scale[i], True, False, 0)
            self.grid.attach (class_pack[i], col, j, 1, 3)

            # we connect the signal "value-changed" emitted by the scale with the callback
            # function right_scale_moved
            self.class_scale[i].connect("value-changed", self.right_scale_moved)

            if ((i + 1) > 3):
                j = 4
                col = (i + 1) % 4 + 1
            else:
                col += 1

        new_game_button = Gtk.Button.new_with_label("New Game")
        new_game_button.connect("clicked", self.on_new_game_clicked) 
        self.grid.attach (new_game_button, 4, 4, 1, 1)

        save_button = Gtk.Button.new_with_label("Save Config")
        save_button.connect("clicked", self.on_save_clicked)
        self.grid.attach (save_button, 4, 5, 1, 1)

        load_button = Gtk.Button.new_with_label("Load Config")
        load_button.connect("clicked", self.on_load_clicked)
        self.grid.attach (load_button, 4, 6, 1, 1)

        cancel_button = Gtk.Button.new_with_label("Cancel")
        cancel_button.connect("clicked", self.on_cancel_clicked)
        self.grid.attach (cancel_button, 4, 7, 1, 1)

        restore_button = Gtk.Button.new_with_label("Defaults")
        restore_button.connect("clicked", self.on_restore_clicked)
        self.grid.attach (restore_button, 4, 8, 1, 1)

        self.add(self.grid)


    # any signal from the left property scales is signaled to the
    # bottom_label_left text of which is changed and also the
    # respective config parameters
    def left_h1_scale_moved(self, event):
        cfg.game_cols = int(self.h1_scale.get_value())
        self.bottom_label_left.set_text("W " + str(cfg.game_cols) + " H " + str(cfg.game_rows) + " D " + str(cfg.density) + " F " + str(cfg.density_fuzz))

    def left_h2_scale_moved(self, event):
        cfg.game_rows = int(self.h2_scale.get_value())
        self.bottom_label_left.set_text("W " + str(cfg.game_cols) + " H " + str(cfg.game_rows) + " D " + str(cfg.density) + " F " + str(cfg.density_fuzz))

    def left_h3_scale_moved(self, event):
        cfg.density = int(self.h3_scale.get_value())
        self.bottom_label_left.set_text("W " + str(cfg.game_cols) + " H " + str(cfg.game_rows) + " D " + str(cfg.density) + " F " + str(cfg.density_fuzz))

    def left_h4_scale_moved(self, event):
        cfg.density_fuzz = int(self.h4_scale.get_value())
        self.bottom_label_left.set_text("W " + str(cfg.game_cols) + " H " + str(cfg.game_rows) + " D " + str(cfg.density) + " F " + str(cfg.density_fuzz))


    # any signals from the right class scales is signaled to
    # update the config class_weights
    def right_scale_moved(self, event):
        for i in range(len(self.class_scale)):
            new_value = int(self.class_scale[i].get_value())
            if (new_value != cfg.class_weights[i]):
#                print ("Class Weights NV i ", i, new_value)
                cfg.class_weights[i] = new_value


    def on_new_game_clicked(self, widget):
#        print ("New Game")
        cfg.show_board = 2  # reinitialize sprites and lists
        cfg.do_random_board = True
        cfg.new_game_cols = cfg.game_cols
        cfg.new_game_rows = cfg.game_rows
        self.destroy ()
#        print_cfg ()


    def on_save_clicked(self, widget):
#        print ("Save Config")
        SaveConfigToFile ()


    def on_load_clicked(self, widget):
#        print ("Load Config")
        LoadConfigOrUseCurrent ()
        self.h1_scale.set_value(cfg.game_cols)
        self.h2_scale.set_value(cfg.game_rows)
        self.h3_scale.set_value(cfg.density)
        self.h4_scale.set_value(cfg.density_fuzz)
        for i in range(len(cfg.class_weights)):
            self.class_scale[i].set_value (cfg.class_weights[i])


    def on_cancel_clicked(self, widget):
#        print ("Cancel")
        self.destroy ()
#        print_cfg ()


    def on_restore_clicked(self, widget):
#        print ("Restore Defaults")
        cfg.game_cols = cfg.default_game_cols
        cfg.game_rows = cfg.default_game_rows
        cfg.density = cfg.default_density
        cfg.density_fuzz = cfg.default_density_fuzz
        for i in range(len(cfg.class_weights)):
            cfg.class_weights[i] = cfg.default_class_weights[i]
            self.class_scale[i].set_value (cfg.default_class_weights[i])
        self.h1_scale.set_value(cfg.game_cols)
        self.h2_scale.set_value(cfg.game_rows)
        self.h3_scale.set_value(cfg.density)
        self.h4_scale.set_value(cfg.density_fuzz)
        if (cfg.show_board != 2):
            DialogWin (
                "             Ngfp Configuration Parameters Reset           ",
                "                      Using default values                 "
            )

#        print_cfg ()


class MyConfigApplication(Gtk.Application):


    def __init__(self):
        Gtk.Application.__init__(self)


    def do_activate(self):
        win = MyConfigWindow(self)
        win.show_all()


    def do_startup(self):
        Gtk.Application.do_startup(self)


def ConfigGame (self):

#    print ("ConfigGame dialog ...")
    app = MyConfigApplication()
    app.run()


def SimpleCheck (self):

#    print ("SimpleCheck")

    for i in range(len(self.board)):
        if (self.board[i][0] != self.board[i][1]):
            return (False)
    return (True)


def ComplexCheck (self):

#    print ("ComplexCheck")

    tmp_board = copy.deepcopy (self.board)
    tmp_history_arrow_index = self.arrow_index
    tmp_arrow_history_sprites = self.arrow_history_sprites[:]
    tmp_history_color_sprites = self.history_color_sprites[:]
    tmp_color_batch_list = self.color_batch_list[:]
    tmp_marble_sprites = self.marble_sprites[:]

    board_match = True

    try:
        for eval_depth in range(8):
            for i in range(len(self.white_active_squares)):
                board_out = MarbleInMotion (self, 0, 0, 0, self.white_active_squares[i], False)
                guess_out = MarbleInMotion (self, 1, 0, 0, self.white_active_squares[i], False)

                if (board_out != guess_out):
                    board_match = False
                    raise StopIteration
#            print ("ComplexCheck : ", eval_depth)

    except StopIteration:
        pass

    # the above may change the display/sprites/etc 
    # so restore like we are starting from a new board
    # and redisplay
    
    cfg.new_game_cols = cfg.game_cols
    cfg.new_game_rows = cfg.game_rows
    cfg.new_board = copy.deepcopy(tmp_board)
    cfg.new_widget_counts = copy.deepcopy(self.widget_pile_list_counts)

    self.arrow_index = tmp_history_arrow_index
    self.arrow_history_sprites = tmp_arrow_history_sprites[:]
    self.history_color_sprites = tmp_history_color_sprites[:]
    self.color_batch_list = tmp_color_batch_list[:]
    self.marble_sprites = tmp_marble_sprites[:]

    cfg.show_board = 2  # reinitialize sprites and lists
    cfg.do_random_board = False
    DrawBoard (self)

    cfg.show_board = 1
    cfg.no_user_actions = False
    return (board_match)


def CheckBoard (self):

#    print ("CheckBoard dialog ...")

    if (sum(self.widget_pile_list_counts) != 0):
        DialogWin (
            "            You Need To Use All Of The Mirrors             ",
            "                   Sorry   Try again                       "
            )
        return

    if (SimpleCheck (self) == True):
        DialogWin (
            "           You Won!  Exact Match Found                     ",
            "     You've solved the puzzle   Congratulations!           "
            )
    elif (ComplexCheck (self) == True):
        DialogWin (
            "        You Won!  Functionally Identical Match Found          ",
            "       You've solved the puzzle   Congratulations!            "
            )
    else:
        DialogWin (
            "             You Lost   No Match Found                     ",
            "                Sorry   Try again                          "
            )


def add_load_filters(dialog):

    filter_json = Gtk.FileFilter()
    filter_json.set_name("json files")
    filter_json.add_pattern("*.json")
    dialog.add_filter(filter_json)

    filter_gfp = Gtk.FileFilter()
    filter_gfp.set_name("gfp files")
    filter_gfp.add_pattern("*.gfp")
    dialog.add_filter(filter_gfp)


def add_save_filters(dialog):

    filter_json = Gtk.FileFilter()
    filter_json.set_name("json files")
    filter_json.add_pattern("*.json")
    dialog.add_filter(filter_json)


class MyOpenWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Game File Open", has_focus=False)

        self.set_default_size (300,100)
        self.set_border_width (20)
        self.set_position (Gtk.WindowPosition.MOUSE)

        self.dialog = Gtk.FileChooserDialog("Please choose a game file to open", self,
        Gtk.FileChooserAction.OPEN,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            "Select", Gtk.ResponseType.OK))

        add_load_filters(self.dialog)
        self.dialog.set_border_width (20)
        self.dialog.set_default_size (300,100)
        self.dialog.set_position (Gtk.WindowPosition.MOUSE)

        self.dialog.show_all()
        response = self.dialog.run()
        if response == Gtk.ResponseType.OK:
#            print("Select clicked")
            cfg.dialog_cancelled = False
            cfg.this_fn_to_open = str(self.dialog.get_filename())
        elif response == Gtk.ResponseType.CANCEL:
#            print("Cancel clicked")
            cfg.dialog_cancelled = True

        self.dialog.destroy()
        self.quit(self)

    def quit (self, widget, event=None):
        #return True # prevent closing
        return False # close


class MySaveAsWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Game File Save As", has_focus=False)

        self.set_default_size (300,100)
        self.set_border_width (20)
        self.set_position (Gtk.WindowPosition.MOUSE)

        self.dialog = Gtk.FileChooserDialog("Save your game as", self,
        Gtk.FileChooserAction.SAVE,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            "Select", Gtk.ResponseType.OK))

        add_save_filters(self.dialog)
        self.dialog.set_border_width (20)
        self.dialog.set_default_size (300,100)
        self.dialog.set_position (Gtk.WindowPosition.MOUSE)

        self.dialog.set_do_overwrite_confirmation(self.dialog)

        if (cfg.this_fn_to_save == None):
            self.dialog.set_current_name(str(cfg.data_path / Path(cfg.suggested_fn)))
        else:
            self.dialog.set_filename(cfg.this_fn_to_save)

        self.dialog.show_all()
        response = self.dialog.run()
        if response == Gtk.ResponseType.OK:
#            print("Select clicked")
            cfg.dialog_cancelled = False
            cfg.this_fn_to_save = self.dialog.get_filename()
#            print("Save File selected: " + self.dialog.get_filename())
        elif response == Gtk.ResponseType.CANCEL:
#            print("Cancel clicked")
            cfg.dialog_cancelled = True

        self.dialog.destroy()
        self.quit(self)

    def quit (self, widget, event=None):
        #return True # prevent closing
        return False # close


class TextViewWindow(Gtk.Window):

    def __init__(self):

        Gtk.Window.__init__(self, title="About Ngfp")

        self.top_display = pyglet.canvas.get_display()
        self.top_screen = self.top_display.get_default_screen()
        self.full_screen_width = self.top_screen.width
        self.full_screen_height = self.top_screen.height
        self.set_default_size(self.full_screen_width, (self.full_screen_height -250))

        self.grid = Gtk.Grid()
        self.add(self.grid)

        self.create_textview()


    def create_textview(self):
        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_hexpand(True)
        scrolledwindow.set_vexpand(True)
        self.grid.attach(scrolledwindow, 0, 1, 3, 1)

        self.textview = Gtk.TextView()
        self.textbuffer = self.textview.get_buffer()
        self.textbuffer.set_text(
            "\n    Ngfp is running in directory : " + str(Path.cwd()) + "\n"
            "    Ngfp code is running from directory : " + os.path.dirname(__file__) + "\n"
            + "\n"
            + "      It saves game files to directory : " + str(cfg.data_path) + "\n"
            + "\n"
            "    Ngfp Version is : " + GetVersion() + "\n"
            + "\n"
            + "        Open file name : " + str(cfg.this_fn_to_open) + "\n"
            + "        Save file name : " + str(cfg.this_fn_to_save) + "\n"
            + "\n"
            + "      It keeps configuration settings in directory : " + str(cfg.config_path) + "\n"
            + "        Configuration file name : " + cfg.config_filename + "\n"
            + "\n"
            + "\n"
            + "    For more Game Help Press H, F1 or ?\n"
            + "      On a Linux system there should also be a man page.\n"
            + "\n"
            + "    To Quit Playing Game Press Q or ESC\n"
            + "\n"
            + "\n"
            + "    Project Location :"
            + "    https://salsa.debian.org/ant-guest/gfpoken-in-python\n"
            + "\n"
            + "    To leave this window close it..."
            )

        scrolledwindow.add(self.textview)
        self.textview.set_editable(False)
        self.textview.set_cursor_visible(False)


def ShowAbout (self):

#    print_cfg ()
    win = TextViewWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()


class HelpViewWindow(Gtk.Window):

    def __init__(self):

        Gtk.Window.__init__(self, title="Ngfp Help")

        self.top_display = pyglet.canvas.get_display()
        self.top_screen = self.top_display.get_default_screen()
        self.full_screen_width = self.top_screen.width
        self.full_screen_height = self.top_screen.height
        self.set_default_size(self.full_screen_width, (self.full_screen_height -250))

        self.grid = Gtk.Grid()
        self.add(self.grid)

        self.create_textview()


    def create_textview(self):
        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_hexpand(True)
        scrolledwindow.set_vexpand(True)
        self.grid.attach(scrolledwindow, 0, 1, 3, 1)

        self.textview = Gtk.TextView()
        self.textbuffer = self.textview.get_buffer()
        self.textbuffer.set_text(
            "\n  Ngfp is a puzzle game.  When Ngfp is first started you will be shown on the left a blank grid called the Guess grid and on the right is a selection of mirrors.  Under each mirror is the number that need to be placed on the Guess grid to solve the puzzle.  You have to use all of the mirrors.\n"
            + "\n"
            + "  To place a mirror on the Guess grid left mouse click on a mirror to select it, move the mouse over the Guess grid and then click again on the Guess grid where you want to put it down (you do not need to hold the mouse button down).  To rotate the mirror after it has been placed right mouse click on it.  To move a mirror left click on it to select it from the Guess grid and then left click again the Guess grid where you want to place it.  Note that you cannot drop mirrors any place other than on the Guess grid or on the mirrors (the mirror you are moving disappears places where it can't be dropped).\n"
            + "\n"
            + "  To discover where to put the mirrors left mouse click on any white square that borders the Guess grid and this starts a colored marble rolling through the Guess grid.  If you have already placed mirrors then the marble will be reflected or absorbed in various ways depending upon the type of mirror.  Each colored marble will have a matching colored arrow marking where it started, but not all marbles will have a matching out arrow (some mirrors capture the marble or it is possible for the game to randomly generate mirrors which can send the marble in a loop which the marble does not exit).  The marble rolls where the mirrors reflect it - the out arrows show where the marble should finish.\n"
            + "\n"
            + "  You can place up to four markers in a Guess grid location to keep track of what you think may be there.  'J', 'K', 'L' and ';' will put a mark (or turn the mark off if you've already made one) in the grid location your mouse last was over.  F3 will clear the marks from that grid location, F4 will clear all marks (there is no Undo for F3 or F4).\n"
            + "\n"
            + "  F5 will restart the game.  This clears all markers and all guesses from the board (there is no Undo for F5).\n"
            + "\n"
            + "  There are two kinds of solutions to the puzzle.  One is an exact match and the other is a functional match (where all marbles put in from the edges come out where they are supposed to, but the mirrors may not be in the exact arrangement as the Game grid puzzle) - both are considered Wins.  In a very few cases you may have an invalid solution but Ngfp does not notice it - this is because for some puzzles the complexity is more than Ngfp evaluates (in theory this is related to what is called The Halting Problem in Computer Science).\n"
            + "\n"
            + "  There are two status indicators at the bottom corners near the Guess or Game grid.  The Green button in the indicator to the right says that you are in the Guess grid where you can put down markers or mirrors which reflect what you think the puzzle might be.  The Pink button in the indicator to the left says that you are looking at the actual puzzle you are trying to solve (the Game grid).  If you seem to not be getting any response from Ngfp it is likely that you have pressed F2 or the Show Board Icon or have some other game window open.  If you have pressed F2 you can press F2 again to return to playing the game.  The Show Board Icon will also show the actual puzzle, but you cannot toggle back to the Guess grid (use F2 for that).  And if you have a help or dialog window open you have to close it before Ngfp can continue.\n"
            + "\n"
            + "  Configuration information can be changed, game checked to see if you have won and games can be loaded and saved via the icons in the green column in the center.\n"
            + "\n"
            + "\n"
            + "    On a Linux system there should be a man page.\n"
            + "\n"
            + "\n"
            + "  Mouse:\n"
            + "\n"
            + "    Left mouse click picks up and drops mirrors."
            + "    Left mouse click on a white square starts a marble."
            + "    Right mouse click rotates mirrors."
            + "\n"
            + "    Left mouse click on a green square picture to:"
            + "      - change, load, save or restore the game configuration"
            + "      - check to see if you have solved the puzzle"
            + "      - change to the Game grid"
            + "      - load a previously saved game"
            + "      - save a game"
            + "      - show quick help and some game information"
            + "\n"
            + "\n"
            + "  Keys:\n"
            + "\n"
            + "    J, K, L and ; are ways to place markers.\n"
            + "    F3 clears markers in one grid location.\n"
            + "    F4 clears all markers.\n"
            + "    F5 starts the game over.\n"
            + "\n"
            + "\n"
            + "    To Quit Playing Game Press Q or ESC.\n"
            + "\n"
            + "    H, ? or F1 should bring up this help text.\n"
            + "\n"
            + "    F2 is a way to give up and see the puzzle.\n"
            + "\n"
            + "\n"
            + "    To leave this window close it..."
            )

        scrolledwindow.add(self.textview)
        self.textview.set_editable(False)
        self.textview.set_cursor_visible(False)
        self.textview.set_wrap_mode(Gtk.WrapMode.WORD)


def ShowHelp (self):

#    print_cfg ()
    win = HelpViewWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()


def Load_GFPSave_Version_1 (self, lines_in):

    line = lines_in.pop(0)
    line = lines_in.pop(0)
    board_dimensions_strings = line.split()
    cfg.new_game_cols = int(board_dimensions_strings[0])
    cfg.new_game_rows = int(board_dimensions_strings[1])

    # remember the lists are numbered from bottom left in pyglet
    # so board[0][0] is the 1st item of the last line, which is why 
    # we reverse them
    guess_lines = lines_in[:cfg.new_game_rows]
    marker_lines = lines_in[cfg.new_game_rows:cfg.new_game_rows*2]
    board_lines = lines_in[cfg.new_game_rows*2:cfg.new_game_rows*3]

    cfg.new_board = []
    for i in reversed(range(len(board_lines))):
        line_str = board_lines[i]
        for item_ind in line_str.split():
            cfg.new_board.append([int(item_ind), 0])

    board_ind = 0
    for i in reversed(range(len(guess_lines))):
        line_str = guess_lines[i]
        for item_ind in line_str.split():
            cfg.new_board[board_ind][1] = int(item_ind)
            board_ind += 1

    counters_str = lines_in[len(lines_in)-1]
    cfg.new_widget_counts = []
    for i in counters_str.split():
        cfg.new_widget_counts.append(int(i))

    # add a zero for extra widget
    cfg.new_widget_counts.append(0)

    # we're going to have to redraw the board
    # but we aren't a random board
    cfg.show_board = 2
    cfg.do_random_board = False

#    print ("Load_GFPSave_Version_1 -> new variables NC NR NB NWC", cfg.new_game_cols, cfg.new_game_rows, cfg.new_board, cfg.new_widget_counts)


def Load_NGFPSave_Version_1 (self, lines_in):

    cfg.new_game_cols = lines_in[1][0]
    cfg.new_game_rows = lines_in[1][1]

    cfg.new_board = []
    cfg.new_board = copy.deepcopy(lines_in[2])

    cfg.new_widget_counts = []
    cfg.new_widget_counts = copy.deepcopy(lines_in[3])

    # we're going to have to redraw the board
    # but we aren't a random board
    cfg.show_board = 2
    cfg.do_random_board = False

#    print ("Load_NGFPSave_Version_1 -> new variables NC NR NB NWC", cfg.new_game_cols, cfg.new_game_rows, cfg.new_board, cfg.new_widget_counts)


def LoadSavedGameFromFile (self):

#    print ("LoadSavedGameFromFile...")

    cfg.saved_dir = str(Path.cwd())
#    print ("Keep track of current directory : ", cfg.saved_dir)

    # check for saved games directory
    if (cfg.data_path.exists() != True):
        DialogWin (
            "             Ngfp Save Game Directory Missing              ",
            "You haven't created : " + str(cfg.data_path) + " yet       "
            )
        return

    # is there anything in there?
    if (len(os.listdir(path=str(cfg.data_path))) == 0):
        DialogWin (
            "             Ngfp Save Game Directory Empty                ",
            "       There are no saved games yet                        "
            )
        return

#    print ("Changing directory to : ", str(cfg.data_path))
    os.chdir(str(cfg.data_path))
    win = MyOpenWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    win.hide()

#    print ("Going back to directory : ", cfg.saved_dir)
    os.chdir(cfg.saved_dir)

    if (cfg.dialog_cancelled == True):
#        print ("Load Dialog Cancelled")
        return

    if (cfg.this_fn_to_open == None):
#        print ("LoadSavedGameFromFile...  No file selected...")
        return

#    print ("Open File selected : ", cfg.this_fn_to_open)
    if (cfg.this_fn_to_open.endswith(".gfp") == True):
        try:
            with open(cfg.this_fn_to_open) as filein:
                lines_in = filein.readlines()
            Load_GFPSave_Version_1 (self, lines_in)
            cfg.show_board = 2  # reinitialize sprites and lists
            cfg.do_random_board = False
            cfg.this_fn_to_save = cfg.this_fn_to_open
            DrawBoard (self)
        except:
            DialogWin (
                "             Ngfp Loading A Previously Saved Game Failed   ",
                "  Not sure what isn't working with this file : " + str(cfg.this_fn_to_save)
                )
#            print ("LoadSavedGameFromFile : ", cfg.this_fn_to_open, "didn't load...")
    elif (cfg.this_fn_to_open.endswith(".json") == True):
        try:
            with open(cfg.this_fn_to_open) as filein:
                lines_in = json.load(filein)
            Load_NGFPSave_Version_1 (self, lines_in)
            cfg.show_board = 2  # reinitialize sprites and lists
            cfg.do_random_board = False
            cfg.this_fn_to_save = cfg.this_fn_to_open
            DrawBoard (self)
        except:
            DialogWin (
                "Ngfp Loading A Previously Saved Game Failed",
                "  Not sure what isn't working with this file : " + str(cfg.this_fn_to_save)
                )
#            print ("LoadSavedGameFromFile : ", cfg.this_fn_to_open, "didn't load...")


def SaveGameToFile (self):

#    print ("SaveGameToFile ...")

    cfg.saved_dir = str(Path.cwd())
#    print ("Keep track of current directory : ", cfg.saved_dir)

    if (cfg.data_path.exists() != True):
#        print ("No save directory exists.  Creating : ", str(cfg.data_path))
        cfg.data_path.mkdir(mode=0o700, parents=True, exist_ok=False)
        DialogWin (
            "             Ngfp No Save Game Directory Exists            ",
            "  We've created " + str(cfg.data_path) + " for you         "
            )

#    print ("Changing directory to : ", str(cfg.data_path))
    os.chdir(str(cfg.data_path))

    win = MySaveAsWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    win.hide()

    if (cfg.dialog_cancelled == True):
#        print ("Dialog Cancelled")
#        print ("Going back to directory : ", cfg.saved_dir)
        os.chdir(cfg.saved_dir)
        return

    if (cfg.this_fn_to_save == None):
#        print ("SaveGameToFile...  No file selected...")
#        print ("Going back to directory : ", cfg.saved_dir)
        os.chdir(cfg.saved_dir)
        return

#    print ("Saving Game to File : ", cfg.this_fn_to_save)
    with open(cfg.this_fn_to_save, mode="w") as fileout:

        json.dump([["NGFP_Save\n", 1], [cfg.game_cols, cfg.game_rows], self.board, self.widget_pile_list_counts], fileout, indent = 4, separators=(',', ': '))

    cfg.this_fn_to_open = cfg.this_fn_to_save
#    print ("Going back to directory : ", cfg.saved_dir)
    os.chdir(cfg.saved_dir)


def DoDialogControlAction (self, x, x_rec, y, y_rec, win_pos):

#    print ("DoDialogControlAction ", x, x_rec, y, y_rec, win_pos)

    menu_index = self.control_active_squares.index(win_pos)

    # simple menu selection
    if (menu_index == 0):
        # New Game Config Dialog
        ConfigGame (self)
    elif (menu_index == 1):
        # Check Board
        CheckBoard (self)
    elif (menu_index == 2):
        # Flip to Other Board
        cfg.show_board = (cfg.show_board + 1) % 2
    elif (menu_index == 3):
        # Load Saved Game
        LoadSavedGameFromFile (self)
    elif (menu_index == 4):
        # Save Current Game
        SaveGameToFile (self)
    elif (menu_index == 5):
        # About This Game
        ShowAbout (self)
    else:
        pass


