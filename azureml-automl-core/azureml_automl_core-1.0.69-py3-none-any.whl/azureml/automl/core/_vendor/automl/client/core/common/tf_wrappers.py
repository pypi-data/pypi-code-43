# Copyright (c) 2018 Microsoft Corporation.  All rights reserved.
"""Backwards compatible pass through during package migration."""
try:
    from automl.client.core.runtime import tf_wrappers
    from automl.client.core.runtime.tf_wrappers import \
        (TFLinearClassifierWrapper, TFDNNClassifierWrapper, TFLinearRegressorWrapper,
         TFDNNRegressorWrapper, OPTIMIZERS, ACTIVATION_FNS)
except ImportError:
    pass
