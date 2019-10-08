##################################################################################
#  SENSIML CONFIDENTIAL                                                          #
#                                                                                #
#  Copyright (c) 2017-18  SensiML Corporation.                                   #
#                                                                                #
#  The source code contained or  described  herein and all documents related     #
#  to the  source  code ("Material")  are  owned by SensiML Corporation or its   #
#  suppliers or licensors. Title to the Material remains with SensiML Corpora-   #
#  tion  or  its  suppliers  and  licensors. The Material may contain trade      #
#  secrets and proprietary and confidential information of SensiML Corporation   #
#  and its suppliers and licensors, and is protected by worldwide copyright      #
#  and trade secret laws and treaty provisions. No part of the Material may      #
#  be used,  copied,  reproduced,  modified,  published,  uploaded,  posted,     #
#  transmitted, distributed,  or disclosed in any way without SensiML's prior    #
#  express written permission.                                                   #
#                                                                                #
#  No license under any patent, copyright,trade secret or other intellectual     #
#  property  right  is  granted  to  or  conferred upon you by disclosure or     #
#  delivery of the Materials, either expressly, by implication,  inducement,     #
#  estoppel or otherwise.Any license under such intellectual property rights     #
#  must be express and approved by SensiML in writing.                           #
#                                                                                #
#  Unless otherwise agreed by SensiML in writing, you may not remove or alter    #
#  this notice or any other notice embedded in Materials by SensiML or SensiML's #
#  suppliers or licensors in any way.                                            #
#                                                                                #
##################################################################################


import os
import zipfile
from os import listdir, makedirs
from os.path import isfile, join, exists, splitext
from pathlib import Path

from ipywidgets import Layout, VBox, HBox, Button
from ipywidgets import widgets

from sensiml.device_flashing import *
from sensiml.widgets.base_widget import BaseWidget


class FlashWidget(BaseWidget):
    def __init__(self, dsk=None, folder='knowledgepacks'):
        self._dsk = dsk
        self._folder = Path(folder)
        self._flashing_file = ''
        self._selected_flasher = None
        if not exists(folder):
            makedirs(folder)

    def _refresh_platform_files(self, b=None):
        key_name = self.platform_widget.value.replace(' ', '-')
        platform_search = '{}'.format(key_name).lower()
        ext_match = '.zip'
        self.flashable_files_widget.options = []
        platform_files = [f for f in listdir(self._folder) if isfile(join(self._folder, f))
                          and platform_search in f.lower()
                          and splitext(f)[-1] == ext_match
                          and 'bin' in f.lower()]

        if len(platform_files) > 0:
            self.flashable_files_widget.options = platform_files
            self.flashable_files_widget.value = platform_files[0]

    def _refresh_flash_methods(self):
        if self._selected_flasher is None:
            return
        self.flash_methods_widget.options = self._selected_flasher.flash_methods

    def select_platform(self, platform_name):
        if isinstance(platform_name, int):
            self._selected_flasher = self._flashers[platform_name]
        elif isinstance(platform_name, str):
            for f in self._flashers:
                if platform_name in f.supported_platforms:
                    self._selected_flasher = f
                    break
        else:
            print("Unknown Platform: {}".format(str(platform_name)))
            return
        self._refresh_platform_files()
        self._refresh_flash_methods()

    def get_platform_names(self):
        flasher_boards = list()
        for j in self._flashers:
            flasher_boards.extend(j.supported_platforms)
        return flasher_boards

    def on_flash_button_clicked(self, b):
        if not self.flashable_files_widget.value:
            return
        if not self._selected_flasher:
            return
        flash_zip_file = Path(self._folder, self.flashable_files_widget.value)
        self._flashing_file = unzip_folder(flash_zip_file, self._selected_flasher.flash_file_ext)

        self._selected_flasher.flash(self._flashing_file, method=self.flash_methods_widget.value)

    def _refresh(self, b=None):
        if self._dsk is None:
            return
        self.platform_widget.options = self.get_platform_names()

    def create_widget(self):

        self._flashers = [NordicThingyFlasher(), STDeviceFlasher()]

        self.platform_widget = widgets.Dropdown(description='Platform')
        self.description_widget = widgets.Label(layout=Layout(width='66%'))
        self.flashable_files_widget = widgets.Dropdown(
            description='Binary', layout=Layout(width='85%'))
        self.flash_methods_widget = widgets.Dropdown(
            description="Flash Method")
        self.flash_button = Button(description="Flash")
        self.refresh_button = Button(
            icon='refresh', tooltip='Refresh File List', layout=Layout(width='15%'))

        self._refresh()

        self.flash_button.on_click(self.on_flash_button_clicked)
        self.refresh_button.on_click(self._refresh_platform_files)

        return VBox([
            HBox([widgets.interactive(self.select_platform,
                                      platform_name=self.platform_widget), self.description_widget]),
            HBox([self.flashable_files_widget, self.refresh_button]),
            HBox([self.flash_methods_widget, self.flash_button])
        ])


def unzip_folder(path_to_zip_file, file_ext):
    path_string = str(path_to_zip_file.absolute())
    base_name = os.path.basename(path_string[:-4])
    binary_folder = Path(path_string[:-4])
    binary_path = Path(path_string[:-4], base_name + file_ext)

    zip_ref = zipfile.ZipFile(path_to_zip_file, 'r')
    zip_ref.extractall(binary_folder)
    zip_ref.close()

    return binary_path
