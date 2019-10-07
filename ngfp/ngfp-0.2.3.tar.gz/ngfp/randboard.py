#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) Ant <ant@anthive.com>

import pyglet
from pyglet.window import mouse
import random
from random import randrange, getrandbits
from time import sleep
import copy

import ngfp.config as cfg


def InitRandomBoardItems (self):

    # these will come from configuration file eventually...
    gridx = cfg.game_cols
    gridy = cfg.game_rows
    density = cfg.density
    densityfuzz = cfg.density_fuzz
    class_sum = sum(cfg.class_weights)

#    print ("cfg.class_weights, class_sum", cfg.class_weights, class_sum)

    self.class_list = [
                  ["ClSimple", []],
                  ["ClFlipper", []],
                  ["ClBoxSink", []],
                  ["ClAxis", []],
                  ["ClRotator", []],
                  ["ClOneWay", []],
                  ["ClEvil", []]
                 ]

    randpop = ((density * self.board_squares / 100) + 1) // 1
    randpop += ((random.getrandbits(32) % (randpop*densityfuzz*2/100 + 1)) - (randpop*densityfuzz/100)) // 1

    if (randpop > self.board_squares):
        randpop = self.board_squares

    if randpop < 0:
        randpop = 0

    while (randpop > 0):
        position = random.getrandbits(32) % self.board_squares
#            print ("randpop, position", randpop, position)

        if (self.board[position][0] == 0):
            randchance = random.getrandbits(32) % class_sum

#                print ("  randchance", randchance)
            upperbound = 0
            tempobj = 0

            for counter in range(len(cfg.class_weights)):
                upperbound += cfg.class_weights[counter]
#                    print ("    upperbound", upperbound)
                if (upperbound == 0):
                    continue                                           #  Base case

                if (randchance < upperbound):
                    if (self.class_list[counter][0] == "ClSimple"):
                        tempobj = (random.getrandbits(32) % 2) + 1     # 1-2
                        if (self.board[position][0] == 0):
                            self.widget_pile_list_counts[tempobj-1] += 1
                    elif (self.class_list[counter][0] == "ClFlipper"):
                        tempobj = (random.getrandbits(32) % 6) + 3     # 3-8
                        if (self.board[position][0] == 0):
                            if ((tempobj == 3) or (tempobj == 4)):
                                self.widget_pile_list_counts[2] += 1
                            else:
                                self.widget_pile_list_counts[3] += 1
                    elif (self.class_list[counter][0] == "ClBoxSink"):
                        tempobj = (random.getrandbits(32) % 2) + 9     # 9-10
                        if (self.board[position][0] == 0):
                            self.widget_pile_list_counts[tempobj-5] += 1
                    elif (self.class_list[counter][0] == "ClAxis"):
                        tempobj = (random.getrandbits(32) % 4) + 11    # 11-14
                        if (self.board[position][0] == 0):
                            if (tempobj == 11):
                                self.widget_pile_list_counts[6] += 1
                            elif (tempobj == 12):
                                self.widget_pile_list_counts[7] += 1
                            else:
                                self.widget_pile_list_counts[8] += 1
                    elif (self.class_list[counter][0] == "ClRotator"):
                        tempobj = (random.getrandbits(32) % 4) + 15    # 15-18
                        if (self.board[position][0] == 0):
                            if (tempobj == 15):
                                self.widget_pile_list_counts[9] += 1
                            elif (tempobj == 16):
                                self.widget_pile_list_counts[10] += 1
                            else:
                                self.widget_pile_list_counts[11] += 1
                    elif (self.class_list[counter][0] == "ClOneWay"):
                        tempobj = (random.getrandbits(32) % 4) + 19    # 19-22
                        if (self.board[position][0] == 0):
                            self.widget_pile_list_counts[tempobj-7] += 1
                    elif (self.class_list[counter][0] == "ClEvil"):
                        tempobj = (random.getrandbits(32) % 10) + 23   # 23-32
                        if (self.board[position][0] == 0):
                            if ((tempobj >= 23) and (tempobj <= 26)):
                                self.widget_pile_list_counts[16] += 1
                            elif ((tempobj >= 27) and (tempobj <= 30)):
                                self.widget_pile_list_counts[17] += 1
                            elif (tempobj == 31):
                                self.widget_pile_list_counts[18] += 1
                            else:
                                self.widget_pile_list_counts[19] += 1
                    else:
                        pass

                    if (self.board[position][0] == 0):
                        self.board[position][0] = tempobj
#                            print ("    position, tempobj", position, tempobj)
                        self.class_list[counter][1].append([position, tempobj])
                    else:
                        continue

        randpop -= 1

#    print (self.class_list)
#    print (self.widget_pile_list_counts)
#    print (self.board)


