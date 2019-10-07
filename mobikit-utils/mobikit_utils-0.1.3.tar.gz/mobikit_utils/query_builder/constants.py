#
# Copyright (c) 2019 Mobikit, Inc.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
#

from types import SimpleNamespace

# Query API parameters
filter_types = SimpleNamespace(
    less_than_equal="lte",
    greater_than_equal="gte",
    greater_than="gt",
    less_than="lt",
    equal="eq",
    like="like",
    is_in="in",
    between="between",
    within="within",
    intersected_by="intersectedBy",
    is_null="isNull",
)
conjunction_types = SimpleNamespace(AND="and", OR="or")
aggregation_types = SimpleNamespace(
    count="count",
    average="average",
    sum="sum",
    max="max",
    min="min",
    first="first",
    last="last",
    median="median",
    stddev="stddev",
)
sort_dirs = SimpleNamespace(ascending="ascending", descending="descending")
select_types = SimpleNamespace(simple="simple", aggregate="aggregate")
downsize_methods = SimpleNamespace(sample="sample", truncate="truncate")
spatial_formats = SimpleNamespace(
    geometry="geometry", text="text", lat="lat", lng="lng", geojson="geojson"
)

# Query API payload schema
payload_schema = SimpleNamespace(
    select=SimpleNamespace(
        name="select",
        field="field",
        function="function",
        distinct="distinct",
        alias="alias",
        format="format",
    ),
    filter_block=SimpleNamespace(conjunction="conjunction", predicates="predicates"),
    filter=SimpleNamespace(
        name="filter",
        type="type",
        field="field",
        negated="negated",
        meta="meta",
        inequality_meta=SimpleNamespace(comparand="comparand"),
        between_meta=SimpleNamespace(lb="lb", ub="ub"),
        in_meta=SimpleNamespace(comparand="comparand"),
        like_meta=SimpleNamespace(comparand="comparand"),
        within_meta=SimpleNamespace(lat="lat", lng="lng", radius="radius"),
        intersected_by_meta=SimpleNamespace(geometry="geometry", geojson="geojson"),
    ),
    group=SimpleNamespace(name="group"),
    sort=SimpleNamespace(name="sort", field="field", dir="dir"),
    sample=SimpleNamespace(name="sample"),
    limit=SimpleNamespace(name="limit"),
    offset=SimpleNamespace(name="offset"),
    meta=SimpleNamespace(
        name="meta", downsize_method="downsizeMethod", spatial_format="spatialFormat"
    ),
)

field_meta_schema = SimpleNamespace(
    type_family=SimpleNamespace(
        name="type_family", generic="generic", spatial="spatial"
    )
)
