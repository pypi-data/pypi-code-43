#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# It script it publish under GNU GENERAL PUBLIC LICENSE
# http://www.gnu.org/licenses/gpl-3.0.en.html
# Author: the Galaxie viewer Team, all rights reserved
import sys
import os
import time
# Require when you haven't GLXRadio as default Package
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(current_dir))
from GLXViewer.viewer import flush_infos
from GLXViewer.viewer import flush_a_new_line


def main():
    start_time = time.time()
    flush_infos(
        column_1=__file__,
        column_2='Yes that is possible'
    )
    flush_infos(
        column_1=__file__,
        column_2='it have no difficulty to make it',
        column_3='what ?'
    )
    flush_infos(
        column_1='Use you keyboard with Ctrl + c for stop the demo',
        status_text='INFO',
        status_text_color='YELLOW',
        status_symbol='!',
    )
    while True:

        flush_infos(
            column_1=__file__,
            column_2=str(time.time() - start_time),
            status_text='REC',
            status_text_color='RED',
            status_symbol='<',
            prompt=True
        )


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        flush_a_new_line()
        sys.exit()
