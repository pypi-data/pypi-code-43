#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# It script it publish under GNU GENERAL PUBLIC LICENSE
# http://www.gnu.org/licenses/gpl-3.0.en.html
# Author: the Galaxie Viewer Team, all rights reserved


class Colors:
    green = "\033[92m"
    yellow = "\033[93m"
    normal = "\033[36m"
    red = "\033[31m"
    end = "\033[0m"
    BOLD = "\033[1m"
    CEND = "\33[0m"
    CBOLD = "\33[1m"
    CITALIC = "\33[3m"
    CURL = "\33[4m"
    CBLINK = "\33[5m"
    CBLINK2 = "\33[6m"
    CSELECTED = "\33[7m"

    CBLACK = "\33[30m"
    CRED = "\33[31m"
    CGREEN = "\33[32m"
    CYELLOW = "\33[33m"
    CBLUE = "\33[34m"
    CVIOLET = "\33[35m"
    CBEIGE = "\33[36m"
    CWHITE = "\33[37m"

    CBLACKBG = "\33[40m"
    CREDBG = "\33[41m"
    CGREENBG = "\33[42m"
    CYELLOWBG = "\33[43m"
    CBLUEBG = "\33[44m"
    CVIOLETBG = "\33[45m"
    CBEIGEBG = "\33[46m"
    CWHITEBG = "\33[47m"

    CGREY = "\33[90m"
    CRED2 = "\33[91m"
    CGREEN2 = "\33[92m"
    CYELLOW2 = "\33[93m"
    CBLUE2 = "\33[94m"
    CVIOLET2 = "\33[95m"
    CBEIGE2 = "\33[96m"
    CWHITE2 = "\33[97m"

    CGREYBG = "\33[100m"
    CREDBG2 = "\33[101m"
    CGREENBG2 = "\33[102m"
    CYELLOWBG2 = "\33[103m"
    CBLUEBG2 = "\33[104m"
    CVIOLETBG2 = "\33[105m"
    CBEIGEBG2 = "\33[106m"
    CWHITEBG2 = "\33[107m"


def convert_color_text_to_colors(status_text_color):
    if status_text_color.upper() == "ORANGE":
        status_text_color = Colors.CYELLOW
    elif status_text_color.upper() == "RED":
        status_text_color = Colors.CRED
    elif status_text_color.upper() == "RED2":
        status_text_color = Colors.CRED2
    elif status_text_color.upper() == "YELLOW":
        status_text_color = Colors.CYELLOW2
    elif status_text_color.upper() == "YELLOW2":
        status_text_color = Colors.CYELLOW
    elif status_text_color.upper() == "WHITE":
        status_text_color = Colors.CWHITE
    elif status_text_color.upper() == "WHITE2":
        status_text_color = Colors.CWHITE2
    elif status_text_color.upper() == "CYAN":
        status_text_color = Colors.CBEIGE
    elif status_text_color.upper() == "GREEN":
        status_text_color = Colors.CGREEN2
    elif status_text_color.upper() == "GREEN2":
        status_text_color = Colors.CGREEN

    return status_text_color
