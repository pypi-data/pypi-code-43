# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Init file for azureml-explain-model/azureml/explain/model/mimic/models/linear_model."""
from interpret.ext.glassbox import LinearExplainableModel, SGDExplainableModel

__all__ = ['LinearExplainableModel', 'SGDExplainableModel']
