#
# Copyright (c) 2019 Mobikit, Inc.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
#

from types import SimpleNamespace


srid = 4326

db_table_types = SimpleNamespace(
    points="points",
    trips="trips",
    events="events",
    vehicles="vehicles",
    arbitrary="arbitrary",
)

# Metadata types
dtypes = SimpleNamespace(
    geometry=SimpleNamespace(
        prefix="geometry",
        point="geometry point",
        linestring="geometry linestring",
        polygon="geometry polygon",
    ),
    numeric=SimpleNamespace(
        integer="integer", real="real", bigint="bigint", double="double precision"
    ),
    boolean=SimpleNamespace(boolean="boolean"),
    string=SimpleNamespace(text="text"),
    time=SimpleNamespace(
        timestamp_without_timezone="timestamp without time zone",
        timestamp_with_timezone="timestamp with time zone",
        date="date",
        time_without_timezone="time without time zone",
        time_with_timezone="time with time zone",
    ),
    speed=SimpleNamespace(speed="speed"),
    json=SimpleNamespace(json="json", jsonb="jsonb"),
)

sqlalchemy_types = SimpleNamespace(
    geometry=SimpleNamespace(
        point={
            "name": "geoalchemy2.types.Geometry",
            "args": ["Point"],
            "kwargs": {"srid": 4326},
        },
        linestring={
            "name": "geoalchemy2.types.Geometry",
            "args": ["LineString"],
            "kwargs": {"srid": 4326},
        },
        polygon={
            "name": "geoalchemy2.types.Geometry",
            "args": ["Polygon"],
            "kwargs": {"srid": 4326},
        },
    ),
    numeric=SimpleNamespace(
        integer="sqlalchemy.sql.sqltypes.INTEGER",
        decimal="sqlalchemy.sql.sqltypes.REAL",
        bigint="sqlalchemy.sql.sqltypes.BIGINT",
    ),
    boolean="sqlalchemy.sql.sqltypes.BOOLEAN",
    time=SimpleNamespace(
        timestamp_with_timezone={
            "name": "sqlalchemy.sql.sqltypes.TIMESTAMP",
            "kwargs": {"timezone": True},
        },
        timestamp_without_timezone="sqlalchemy.sql.sqltypes.TIMESTAMP",
    ),
    text="sqlalchemy.sql.sqltypes.TEXT",
)

# SQLAlchemy types map
dtype_to_sqlalchemy_type_map = {
    dtypes.geometry.point: sqlalchemy_types.geometry.point,
    dtypes.geometry.linestring: sqlalchemy_types.geometry.linestring,
    dtypes.geometry.polygon: sqlalchemy_types.geometry.polygon,
    dtypes.numeric.integer: sqlalchemy_types.numeric.integer,
    dtypes.numeric.real: sqlalchemy_types.numeric.decimal,
    dtypes.numeric.bigint: sqlalchemy_types.numeric.bigint,
    dtypes.numeric.double: sqlalchemy_types.numeric.decimal,
    dtypes.boolean.boolean: sqlalchemy_types.boolean,
    dtypes.string.text: sqlalchemy_types.text,
    dtypes.time.timestamp_without_timezone: sqlalchemy_types.time.timestamp_with_timezone,
    dtypes.time.timestamp_with_timezone: sqlalchemy_types.time.timestamp_with_timezone,
    dtypes.speed.speed: sqlalchemy_types.numeric.decimal,
}
