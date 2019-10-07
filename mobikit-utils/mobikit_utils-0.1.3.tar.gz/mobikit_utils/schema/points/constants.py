#
# Copyright (c) 2019 Mobikit, Inc.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
#

from mobikit_utils.schema.meta.meta import get_name

base_name = get_name(__name__)
pk = "id"
primary_spatial = "point"
trip_id = "trip_id"
timestamp = "tm"
hexbin_lg_id = "hexbin_6_id"
hexbin_md_id = "hexbin_7_id"
columns = [pk, trip_id, primary_spatial, timestamp, hexbin_lg_id, hexbin_md_id]
