"""
    PyJAMAS is Just A More Awesome Siesta
    Copyright (C) 2018  Rodrigo Fernandez-Gonzalez (rodrigo.fernandez.gonzalez@utoronto.ca)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import os

from PyQt5 import QtWidgets

from pyjamas.rcallbacks.rcallback import RCallback


class RCBOptions(RCallback):
    def cbSetBrushSize(self, sz: int=None) -> bool:
        '''
        Sets the size of the brush used to paint polygons.
        :return: int (selected brush size or -1 if cancelled)
        '''

        brush_size: int = 0
        ok_flag: bool = None

        if sz != None and sz != False:
            brush_size = sz
            ok_flag = True
        else:
            # Read user input for brush size.
            brush_size, ok_flag = QtWidgets.QInputDialog.getInt(None, 'Set brush size: ', 'Enter new size: ',
                    self.pjs.brush_size, 1)

        
        if ok_flag and brush_size > 0:
            self.pjs.brush_size = brush_size
            self.pjs.repaint()

            return True

        else:
            return False

    def cbDisplayFiducialIDs(self):
        if self.pjs.display_fiducial_ids:
            self.pjs.display_fiducial_ids = False
        else:
            self.pjs.display_fiducial_ids = True

        self.pjs.repaint()

        return True

    def cbFramesPerSec(self, fps: int = None) -> int:
        '''
        Sets the size of the brush used to paint polygons.
        :return: int (selected brush size or -1 if cancelled)
        '''

        thefps: int = 0
        ok_flag: bool = None

        if fps is not None and fps is not False:
            thefps = fps
            ok_flag = True
        else:
            # Read user input for fps.
            thefps, ok_flag = QtWidgets.QInputDialog.getInt(None, 'Set frames per second: ',
                                                            'Enter frames per second: ',
                                                            self.pjs.fps, 1)

        if ok_flag and thefps > 0:
            self.pjs.fps = thefps

            return True

        else:
            return False

    def cbSetCWD(self, folder_name: str = '') -> bool:
        if folder_name == '' or folder_name is False: # When the menu option is clicked on, for some reason that I do not understand, the function is called with filename = False, which causes a bunch of problems.
            folder_name = QtWidgets.QFileDialog.getExistingDirectory(None, 'Save files to folder ...', self.pjs.cwd)  # fname[0] is the full filename, fname[1] is the filter used.

            # If cancel ...
            if folder_name == '':
                return False

        if os.path.exists(folder_name):
            self.pjs.cwd = os.path.abspath(folder_name)
            self.pjs.statusbar.showMessage(f"Working folder set to {self.pjs.cwd}.")

            return True

        else:
            return False