#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Library module related with PSD (Photoshop) operations
"""

from __future__ import print_function, division, absolute_import

import os
import tempfile
import shutil
import subprocess

try:
    import comtypes.client
    _PSD_AVAILABLE = True
except ImportError:
    print('Impossible to load comtypes library. Photoshop dependant functionality will be disabled!')
    _PSD_AVAILABLE = False
# endregion


def find_layers(layer):
    """
    Get all layers from a PSD layer
    """

    layers = list()
    is_group = False
    try:
        layer.layers
        is_group = True
    except:
        pass

    if is_group:
        for grp_layer in layer.layers:
            find_layers(grp_layer)
    else:
        layers.append(layer)
    return layers


def load_image_sequence_from_psd(psd_file):
    layers_list = list()
    files_list = list()

    if not _PSD_AVAILABLE:
        return
    if not os.path.isfile(psd_file):
        return
    ps_app = comtypes.client.CreateObject('Photoshop.Application')
    if not ps_app:
        return
    doc = ps_app.Open(psd_file)
    if not doc:
        return
    options = comtypes.client.CreateObject('Photoshop.PNGSaveOptions')
    for layer in doc.Layers:
        layers_list.extend(find_layers(layer))

    export_dir_path = tempfile.mkdtemp()

    try:
        for layer in layers_list:
            layer.Visible = False
    except Exception:
        print('Error while settings layers on file {}'.format(psd_file))
        return list()

    try:
        for i, layer in enumerate(layers_list):
            layer.Visible = True
            layer_name = 'Layer_' + str(i)
            png_file = os.path.join(export_dir_path, layer_name+'.png')
            if os.path.isfile(png_file):
                psd_time = os.state(psd_file)[8]
                png_time = os.stat(png_file)[8]
                if psd_time > png_time:
                    os.remove(png_file)
            if not os.path.exists(png_file):
                doc.SaveAs(png_file, options, True)
            layer.Visible = False
            files_list.append(png_file)
    except Exception as e:
        print('Error exporting layers. Removing temporary folder ...')
        print(e)

        shutil.rmtree(export_dir_path)
        return list()
    subprocess.Popen(r'explorer /select, "' + export_dir_path + '"')
    doc.Close(2)
    if ps_app.Documents.Count <= 0:
        ps_app.Quit()
    return files_list, export_dir_path
