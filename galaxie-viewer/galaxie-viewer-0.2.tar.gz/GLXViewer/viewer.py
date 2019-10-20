#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# It script it publish under GNU GENERAL PUBLIC LICENSE
# http://www.gnu.org/licenses/gpl-3.0.en.html
# Author: the Galaxie Radio Team, all rights reserved

import sys
import datetime
import shutil

from GLXViewer.utils import center_text
from GLXViewer.utils import bracket_text
from GLXViewer.utils import resize_text


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


def flush_a_new_line():
    sys.stdout.write("\n")
    sys.stdout.flush()


def flush_infos(
    with_date=True,
    status_text="DEBUG",
    status_text_color="ORANGE",
    status_symbol=" ",
    column_1="",
    column_2="",
    column_3="",
    prompt=None,
):
    """
    Flush a line a bit like you want

    :param with_date:
    :param column_3:
    :param status_text:
    :param status_symbol:
    :param status_text_color:
    :param prompt: The prompt to display
    :param column_1: A Class name
    :type column_1: str or None
    :param column_2: The thing to print
    :type column_2: str or None
    """

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
    else:
        status_text_color = Colors.CYELLOW

    status_symbol_color = Colors.BOLD + Colors.CBEIGE

    # Column date
    if with_date:
        with_date = str(
            datetime.datetime.now().replace(microsecond=0).isoformat()
        )

    # Status Clean up
    status_text = resize_text(text=status_text, max_width=5)
    status_text = center_text(text=status_text, max_width=5)
    status_text = bracket_text(text=status_text)

    # Column state
    if with_date:
        string_print = "{0:} {1:<5} {2:<3} {3:<10} {4:<10}".format(
            str(Colors.CWHITEBG + Colors.CGREY + with_date + Colors.end),
            str(status_text_color + status_text + Colors.end),
            str(status_symbol_color + status_symbol + Colors.end),
            str(column_1),
            str(column_2),
        )
        string_print_size = "{0:} {1:<5} {2:<3} {3:<10} {4:<10}".format(
            str(with_date),
            str(status_text),
            str(status_symbol),
            str(column_1),
            str(column_2),
        )
    else:
        string_print = "{0:<5} {1:<3} {2:<10} {3:<10}".format(
            str(status_text_color + status_text + Colors.end),
            str(status_symbol_color + status_symbol + Colors.end),
            str(column_1),
            str(column_2),
        )

        string_print_size = "{0:<5} {1:<3} {2:<10} {3:<10}".format(
            str(status_text), str(status_symbol), str(column_1), str(column_2)
        )

    sys.stdout.write("\b" * shutil.get_terminal_size()[0])
    sys.stdout.write(string_print)

    if prompt is None:
        sys.stdout.write("\n")

    elif int(prompt) < 0:
        # sys.stdout.write("\b" * int(columns - len(string_print)))
        if with_date:
            sys.stdout.write(
                "\b" * int(len(string_print) - len(string_print_size) - 13)
            )
        else:
            sys.stdout.write(
                "\b" * int(len(string_print) - len(string_print_size) + 1)
            )
    else:
        sys.stdout.write("\b" * shutil.get_terminal_size()[0])

    # Only on final flush, that because that ultra slow
    sys.stdout.flush()

    # lines = textwrap.wrap(
    #     str(column_2),
    #     width=int(_get_terminal_width() - 30)
    # )
    # count = 1
    # for line in lines:
    #     set_prompt_type(prompt)
    #     sys.stdout.write(' ')
    #     sys.stdout.write(line)
    #     sys.stdout.write('\n')
    #     line_length = len(line)
    #     sys.stdout.write("\b" * line_length)
    #     sys.stdout.flush()
    #     count += 1
