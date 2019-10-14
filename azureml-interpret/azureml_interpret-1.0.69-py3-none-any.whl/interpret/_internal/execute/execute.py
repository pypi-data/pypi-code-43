# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
from azureml.core import ScriptRunConfig, Environment
from azureml._logging import ChainedIdentity


class BaseExecuteExplainer(ChainedIdentity):
    # TODO: Implement this when implementing a 2nd child class

    def __init__(self):
        pass


class TabularExecuteExplainer(BaseExecuteExplainer):
    """Executes TabularExplainer on the given model"""
    def __init__(self,
                 model_id,
                 model_type,
                 init_data_id="init_data",
                 eval_data_id="eval_data",
                 features_id=None,
                 classes_id=None,
                 local=True):
        """Initialize TabularExecuteExplainer.
        :param model_id: The id of a model that has been registered AND deployed in MMS
        :type model: string
        :param model_type: Either 'regression' or 'classification'
        :type model_type: string
        :param init_data_id: The name of the file on Datastore where init_data is stored
            defaults to "init_data_id"
        :type init_data_id: string
        :param eval_data_id: The name of the file on Datastore where eval_data is stored
            defaults to "eval_data_id"
        :type eval_data_id: string
        :param features: The name of the file on Datastore where feature names are stored (optional)
        :type features: string
        :param classes: The name of the file on Datastore where class names are stored (optional)
        :type classes: string
        :param local: True to perform local explanation, False or omit for global explanation
        :type local: boolean
        """
        self._model_id = model_id
        self._model_type = model_type
        self._init_data_id = init_data_id
        self._eval_data_id = eval_data_id
        self._features_id = features_id
        self._classes_id = classes_id
        self._local = local

    def submit(self, experiment):
        env = get_environment(debug=False)
        arguments = [
            '--model_id', self._model_id,
            '--model_type', self._model_type,
            '--init_data', self._init_data_id,
            '--eval_data', self._eval_data_id]
        if self._local is True:
            arguments.append('--local')
        if self._features_id is not None:
            arguments.extend(['--features', self._features_id])
        if self._classes_id is not None:
            arguments.extend(['--classes', self._classes_id])
        src = ScriptRunConfig(
            source_directory=os.path.join(os.path.dirname(
                os.path.abspath(__file__)), 'execute_scripts'),
            script='tabular_execute_script.py',
            arguments=arguments
        )
        src.run_config.environment = env
        # additional steps - e.g. setup compute target
        run = experiment.submit(config=src)
        run.wait_for_completion(show_output=True)
        return run


def get_environment(debug=False):
    ENVIRONMENT_NAME = 'explain-model-execute-env'
    env = Environment(name=ENVIRONMENT_NAME)
    env.python.user_managed_dependencies = True
    return env
