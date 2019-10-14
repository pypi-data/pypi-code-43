# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Backwards compatible pass through during package migration."""
try:
    from automl.client.core.runtime import time_series_data_frame
    from automl.client.core.runtime.time_series_data_frame import TimeSeriesDataFrame
except ImportError:
    pass
