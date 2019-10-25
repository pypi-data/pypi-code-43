# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Backwards compatible pass through during package migration."""
try:
    from automl.client.core.runtime import forecasting_verify
    from automl.client.core.runtime.forecasting_verify import \
        (ALLOWED_TIME_COLUMN_TYPES, check_cols_exist, data_frame_properties_are_equal,
         data_frame_properties_intersection, equals, is_collection, is_list_oftype, is_iterable_but_not_string,
         is_datetime_like, type_is_numeric, type_is_one_of, Messages)
except ImportError:
    pass
