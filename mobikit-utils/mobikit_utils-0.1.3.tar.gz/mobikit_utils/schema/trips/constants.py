#
# Copyright (c) 2019 Mobikit, Inc.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
#

from mobikit_utils.schema.meta.meta import get_name

base_name = get_name(__name__)
pk = "id"
trip_id = "trip_id"
start_coords = "start_point"
start_timestamp = "start_tm"
end_coords = "end_point"
end_timestamp = "end_tm"
render_polyline = "linestring"
columns = [
    pk,
    trip_id,
    start_coords,
    start_timestamp,
    end_coords,
    end_timestamp,
    render_polyline,
]
