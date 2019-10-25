# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Backwards compatible pass through during package migration."""
try:
    from automl.client.core.runtime import metrics
    from automl.client.core.runtime.metrics import \
        (minimize_or_maximize, is_better, compute_metrics_regression, compute_metrics, compute_metrics_classification)
except ImportError:
    pass
