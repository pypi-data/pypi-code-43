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

"""Provides a class that wraps the API exposed by the braynsDTI plug-in"""


class DiffuseTensorImaging:
    """DiffuseTensorImaging is a class that wraps the API exposed by the braynsDTI plug-in"""

    def __init__(self, client):
        """
        Create a new Diffuse Tensor Imaging instance
        """
        self._client = client.rockets_client

    def add_streamlines(self, name, guids, streamlines, radius=1, opacity=1):
        """
        Adds streamlines to the scene. All streamlines are added into a single model
        :param str name: Name of the model
        :param float streamlines: Streamlines
        :param float radius: Radius of the streamlines
        :param float opacity: Opacity of the streamlines
        :return: Result of the request submission
        :rtype: str
        """
        count = 0
        indices = list()
        vertices = list()
        for points in streamlines:
            indices.append(count)
            count = count + len(points)
            for point in points:
                for coordinate in point:
                    vertices.append(float(coordinate))

        params = dict()
        params['name'] = name
        params['gids'] = guids
        params['indices'] = indices
        params['vertices'] = vertices
        params['radius'] = radius
        params['opacity'] = opacity
        return self._client.request("streamlines", params=params)

    def set_spike_simulation(self, model_id, gids, timestamps, dt, end_time, time_scale=1.0,
                             decay_speed=0.1, rest_intensity=0.25, spike_intensity=0.75):
        params = dict()
        params['modelId'] = model_id
        params['gids'] = gids
        params['timestamps'] = timestamps
        params['dt'] = dt
        params['endTime'] = end_time
        params['timeScale'] = time_scale
        params['decaySpeed'] = decay_speed
        params['restIntensity'] = rest_intensity
        params['spikeIntensity'] = spike_intensity
        return self._client.request("spikeSimulation", params=params)

    def load_streamlines(self, connection_string, sql_statement, name, radius=1.0, color_scheme=0,
                         nb_max_points=1e6):
        params = dict()
        params['connectionString'] = connection_string
        params['sqlStatement'] = sql_statement
        params['name'] = name
        params['radius'] = radius
        params['colorScheme'] = color_scheme
        params['nbMaxPoints'] = nb_max_points
        return self._client.request('loadStreamlines', params)
