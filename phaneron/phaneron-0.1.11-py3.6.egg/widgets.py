#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2018, Cyrille Favreau <cyrille.favreau@gmail.com>
#
# This file is part of pyPhaneron
# <https://github.com/favreau/pyPhaneron>
#
# This library is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License version 3.0 as published
# by the Free Software Foundation.
#
# This library is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this library; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
# All rights reserved. Do not distribute without further notice.

"""Phaneron widgets"""

from brayns import CircuitExplorer
from ipywidgets import FloatSlider, Select, HBox, VBox, Layout, Button, SelectMultiple
import seaborn as sns
from IPython.display import display

colormaps = [
    'Accent', 'Accent_r', 'Blues', 'Blues_r', 'BrBG', 'BrBG_r', 'BuGn', 'BuGn_r',
    'BuPu', 'BuPu_r', 'CMRmap', 'CMRmap_r', 'Dark2', 'Dark2_r', 'GnBu', 'GnBu_r',
    'Greens', 'Greens_r', 'Greys', 'Greys_r', 'OrRd', 'OrRd_r', 'Oranges', 'Oranges_r',
    'PRGn', 'PRGn_r', 'Paired', 'Paired_r', 'Pastel1', 'Pastel1_r', 'Pastel2', 'Pastel2_r',
    'PiYG', 'PiYG_r', 'PuBu', 'PuBuGn', 'PuBuGn_r', 'PuBu_r', 'PuOr', 'PuOr_r',
    'PuRd', 'PuRd_r', 'Purples', 'Purples_r', 'RdBu', 'RdBu_r', 'RdGy', 'RdGy_r',
    'RdPu', 'RdPu_r', 'RdYlBu', 'RdYlBu_r', 'RdYlGn', 'RdYlGn_r', 'Reds', 'Reds_r',
    'Set1', 'Set1_r', 'Set2', 'Set2_r', 'Set3', 'Set3_r',
    'Wistia', 'Wistia_r', 'YlGn', 'YlGnBu', 'YlGnBu_r', 'YlGn_r', 'YlOrBr',
    'YlOrBr_r', 'YlOrRd', 'YlOrRd_r', 'afmhot', 'afmhot_r', 'autumn', 'autumn_r',
    'binary', 'binary_r', 'bone', 'bone_r', 'brg', 'brg_r', 'bwr', 'bwr_r', 'cool', 'cool_r',
    'coolwarm', 'coolwarm_r', 'copper', 'copper_r', 'cubehelix', 'cubehelix_r', 'flag',
    'flag_r', 'gist_earth', 'gist_earth_r', 'gist_gray', 'gist_gray_r', 'gist_heat',
    'gist_heat_r', 'gist_ncar', 'gist_ncar_r', 'gist_rainbow', 'gist_rainbow_r', 'gist_stern',
    'gist_stern_r', 'gist_yarg', 'gist_yarg_r', 'gnuplot', 'gnuplot2', 'gnuplot2_r',
    'gnuplot_r', 'gray', 'gray_r', 'hot', 'hot_r', 'hsv', 'hsv_r', 'icefire', 'icefire_r',
    'inferno', 'inferno_r', 'jet_r', 'magma', 'magma_r', 'mako', 'mako_r',
    'nipy_spectral', 'nipy_spectral_r', 'ocean', 'ocean_r', 'pink', 'pink_r', 'plasma',
    'plasma_r', 'prism', 'prism_r', 'rainbow', 'rainbow_r', 'rocket', 'rocket_r', 'seismic',
    'seismic_r', 'spring', 'spring_r', 'summer', 'summer_r',
    'tab10', 'tab10_r', 'tab20', 'tab20_r', 'tab20b', 'tab20b_r', 'tab20c', 'tab20c_r',
    'terrain', 'terrain_r', 'viridis', 'viridis_r', 'vlag', 'vlag_r', 'winter', 'winter_r'
]

shading_modes = ['none', 'diffuse', 'electron', 'cartoon', 'electron_transparency', 'perlin', 'diffuse_transparency']

default_grid_layout = Layout(border='1px solid black', margin='10px', padding='5px')


class Widgets:

    def __init__(self, client):
        """Create a new Circuit Explorer instance"""
        self._client = client.rockets_client
        self._brayns = client
        self._circuit_explorer = CircuitExplorer(client)

    def display_focal_distance(self):

        x_slider = FloatSlider(description='X', min=0, max=1, value=0.5)
        y_slider = FloatSlider(description='Y', min=0, max=1, value=0.5)
        a_slider = FloatSlider(description='Aperture', min=0, max=1, value=0)
        f_slider = FloatSlider(description='Focus radius', min=0, max=1, value=0.01)
        d_slider = FloatSlider(description='Focus distance', min=0, max=10000, value=0, disabled=True)

        class Updated:

            def __init__(self, brayns, circuit_explorer):
                self._brayns = brayns
                self._circuit_explorer = circuit_explorer
                self._widget_value = None
                self._x = 0.5
                self._y = 0.5
                self._aperture = 0.0
                self._focus_radius = 0.01
                self._focus_distance = 0.0
                self._nb_focus_points = 20

            def _update_camera(self):
                self._focus_distance = 0.0
                import random
                for n in range(self._nb_focus_points):
                    self._focus_distance = self._focus_distance + self._get_focal_distance(
                        (self._x + (random.random() - 0.5) * self._focus_radius,
                         self._y + (random.random() - 0.5) * self._focus_radius))

                self._focus_distance = self._focus_distance / self._nb_focus_points
                params = self._brayns.CircuitExplorerPerspectiveCameraParams()
                params.focus_distance = self._focus_distance
                params.aperture_radius = self._aperture
                params.enable_clipping_planes = True
                d_slider.value = self._focus_distance
                self._brayns.set_camera_params(params)

            def update_focus_radius(self, val_dict) -> None:
                self._widget_value = val_dict['new']
                self._focus_radius = self._widget_value
                self._update_camera()

            def update_aperture(self, val_dict) -> None:
                self._widget_value = val_dict['new']
                self._aperture = self._widget_value
                self._update_camera()

            def update_x(self, val_dict) -> None:
                self._widget_value = val_dict['new']
                self._x = self._widget_value
                self._update_camera()

            def update_y(self, val_dict) -> None:
                self._widget_value = val_dict['new']
                self._y = self._widget_value
                self._update_camera()

            def _get_focal_distance(self, coordinates=(0.5, 0.5)):
                """
                Return the focal distance for the specified normalized coordinates in the image

                :param list coordinates: Coordinates in the image
                :return: The focal distance
                :rtype: float
                """
                target = self._brayns.inspect(array=coordinates)['position']
                origin = self._brayns.camera.position.data
                v = [0, 0, 0]
                for k in range(3):
                    v[k] = float(target[k]) - float(origin[k])
                import math
                return math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])

        update_class = Updated(self._brayns, self._circuit_explorer)

        def update_x(v):
            update_class.update_x(v)

        def update_y(v):
            update_class.update_y(v)

        def update_aperture(v):
            update_class.update_aperture(v)

        def update_focus_radius(v):
            update_class.update_focus_radius(v)

        x_slider.observe(update_x, 'value')
        y_slider.observe(update_y, 'value')
        a_slider.observe(update_aperture, 'value')
        f_slider.observe(update_focus_radius, 'value')

        position_box = VBox([x_slider, y_slider])
        parameters_box = VBox([a_slider, f_slider, d_slider])
        horizontal_box = HBox([position_box, parameters_box], layout=default_grid_layout)
        display(horizontal_box)

    def display_palette_for_models(self):

        def set_colormap(model_id, colormap_name, shading_mode):
            material_ids = self._circuit_explorer.get_material_ids(model_id)['ids']
            nb_materials = len(material_ids)
            palette = sns.color_palette(colormap_name, nb_materials)
            self._circuit_explorer.set_material_extra_attributes(model_id=model_id)

            specular_exponents = list()
            shading_modes = list()
            colors = list()
            for c in palette:
                colors.append((c[0], c[1], c[2]))
                shading_modes.append(shading_mode)
                if shading_mode in [2, 4]:
                    specular_exponents.append(1)
                elif shading_mode == 3:
                    specular_exponents.append(3)
                else:
                    specular_exponents.append(20)

            self._circuit_explorer.set_materials(
                model_ids=[model_id], material_ids=material_ids, specular_exponents=specular_exponents,
                diffuse_colors=colors, specular_colors=colors, shading_modes=shading_modes)

        ''' Models '''
        model_names = list()
        for model in self._brayns.scene.models:
            model_names.append(model['name'])
        model_combobox = Select(options=model_names, description='Models:', disabled=False)

        ''' Shading modes '''
        shading_combobox = Select(options=shading_modes, description='Shading:', disabled=False)

        ''' Colors '''
        palette_combobox = Select(options=colormaps, description='Palette:', disabled=False)

        ''' Events '''
        def update_materials_from_palette(v):
            set_colormap(self._brayns.scene.models[model_combobox.index]['id'], v['new'], shading_combobox.index)

        def update_materials_from_shading(v):
            set_colormap(self._brayns.scene.models[model_combobox.index]['id'], palette_combobox.value,
                         shading_combobox.index)

        shading_combobox.observe(update_materials_from_shading, 'value')
        palette_combobox.observe(update_materials_from_palette, 'value')

        horizontal_box = HBox([model_combobox, shading_combobox, palette_combobox], layout=default_grid_layout)
        display(horizontal_box)

    def display_model_visibility(self):
        model_names = list()
        for model in self._brayns.scene.models:
            model_names.append(model['name'])
        model_select = SelectMultiple(options=model_names, description='Models:', disabled=False)

        show_btn = Button(description='Show')
        hide_btn = Button(description='Hide')
        vbox_params = VBox([show_btn, hide_btn])

        def update_models(visible):
            for model_id in model_select.index:
                self._brayns.update_model(
                    id=self._brayns.scene.models[model_id]['id'],
                    visible=visible)

        def show_models(event):
            update_models(True)

        def hide_models(event):
            update_models(False)

        show_btn.on_click(show_models)
        hide_btn.on_click(hide_models)

        hbox = HBox([model_select, vbox_params], layout=default_grid_layout)
        display(hbox)

    def display_palette_for_transfer_function(self):

        def update_palette(brayns, model_id, palette_name):
            nb_points = 64
            palette = sns.color_palette(palette_name, nb_points)

            btf = brayns.get_model_transfer_function(id=model_id)
            colors = list()
            points = list()

            step = 1.0 / float(nb_points - 1)
            for i in range(len(palette)):
                c = palette[i]
                colors.append((c[0], c[1], c[2]))
                points.append([i * step, 0.5])

            btf['colormap']['name'] = palette_name
            btf['colormap']['colors'] = colors
            btf['opacity_curve'] = points
            btf['range'] = [-80, -10]
            brayns.set_model_transfer_function(id=model_id, transfer_function=btf)

        ''' Models '''
        model_names = list()
        for model in self._brayns.scene.models:
            model_names.append(model['name'])
        model_combobox = Select(options=model_names, description='Models:', disabled=False)

        ''' Colors '''
        palette_combobox = Select(options=colormaps, description='Palette:', disabled=False)

        ''' Events '''
        def update_materials_from_palette(v):
            update_palette(self._brayns, self._brayns.scene.models[model_combobox.index]['id'], v['new'])

        palette_combobox.observe(update_materials_from_palette, 'value')

        horizontal_box = HBox([model_combobox, palette_combobox], layout=default_grid_layout)
        display(horizontal_box)
