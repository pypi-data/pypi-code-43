# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Module for model interpretability, including feature and class importance for blackbox and whitebox models.

You can use model interpretability to explain why a model model makes the predictions it does and help build
confidence in the model.  For more information, see the article
https://docs.microsoft.com/en-us/azure/machine-learning/service/machine-learning-interpretability-explainability.
"""

from .mimic_wrapper import MimicWrapper

__all__ = ['MimicWrapper']
