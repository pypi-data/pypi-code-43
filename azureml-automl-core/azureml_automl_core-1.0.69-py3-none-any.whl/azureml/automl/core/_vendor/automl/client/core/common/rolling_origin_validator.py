# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Backwards compatible pass through during package migration."""
try:
    from automl.client.core.runtime import rolling_origin_validator
    from automl.client.core.runtime.rolling_origin_validator import RollingOriginValidator
except ImportError:
    pass
