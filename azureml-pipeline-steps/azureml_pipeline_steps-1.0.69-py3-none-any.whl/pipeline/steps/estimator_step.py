# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains functionality to create a pipeline step that runs an Estimator for Machine Learning model training."""
from azureml.pipeline.steps import PythonScriptStep


class EstimatorStep(PythonScriptStep):
    """Creates an Azure ML Pipeline step to run Estimator for Machine Learning model training.

    For an example of using EstimatorStep, see the notebook https://aka.ms/pl-estimator.

    .. remarks::

        Note that the arguments to the entry script used in the :class:`azureml.train.estimator.Estimator` object
        must be specified as *list* using the ``estimator_entry_script_arguments`` parameter when instantiating
        an EstimatorStep. The Estimator parameter ``script_params`` accepts a dictionary. However,
        ``estimator_entry_script_argument`` parameter expects arguments as a list.

        The EstimatorStep initialization involves specifying a list of
        :class:`azureml.data.data_reference.DataReference` objects with the ``inputs`` parameter. In Azure ML
        Pipelines, a pipeline step can take another step's output or DataReference objects as input. Therefore,
        when creating an EstimatorStep, the ``inputs`` and ``outputs`` parameters must be set explicitly, which
        overrides ``inputs`` parameter specified in the Estimator object.

        The best practice for working with EstimatorStep is to use a separate folder for scripts and any dependent
        files associated with the step, and specify that folder as the :class:`azureml.train.estimator.Estimator`
        object's ``source_directory``. Doing so has two benefits. First, it helps reduce the size of the snapshot
        created for the step because only what is needed for the step is snapshotted. Second, the step's output
        from a previous run can be reused if there are  no changes to the ``source_directory`` that would trigger
        a re-upload of the snaphot.

        The following example shows how to use EstimatorStep in an Azure Machine Learning Pipeline.

        .. code-block:: python

            from azureml.pipeline.steps import EstimatorStep

            est_step = EstimatorStep(name="Estimator_Train",
                                     estimator=est,
                                     estimator_entry_script_arguments=["--datadir", input_data, "--output", output],
                                     runconfig_pipeline_params=None,
                                     inputs=[input_data],
                                     outputs=[output],
                                     compute_target=cpu_cluster)

        Full sample is available from
        https://github.com/Azure/MachineLearningNotebooks/blob/master/how-to-use-azureml/machine-learning-pipelines/intro-to-pipelines/aml-pipelines-how-to-use-estimatorstep.ipynb


    :param name: The name of the step.
    :type name: str
    :param estimator: The associated estimator object for this step. Can be a pre-configured estimator such as
        :class:`azureml.train.dnn.Chainer`, :class:`azureml.train.dnn.PyTorch`,
        :class:`azureml.train.dnn.TensorFlow`, or :class:`azureml.train.sklearn.SKLearn`.
    :type estimator: azureml.train.estimator.Estimator
    :param estimator_entry_script_arguments: [Required] A list of command-line arguments.
        If the Estimator's entry script does not accept commandline arguments,
        set this parameter value to an empty list.
    :type estimator_entry_script_arguments: list[str]
    :param runconfig_pipeline_params: An override of runconfig properties at runtime using key-value pairs,
                            each with name of the runconfig property and PipelineParameter for that property.
    :type runconfig_pipeline_params: dict({(str) : (azureml.pipeline.core.PipelineParameter)})
    :param inputs: A list of inputs to use.
    :type inputs: list[azureml.pipeline.core.builder.PipelineData
                    or azureml.pipeline.core.pipeline_output_dataset.PipelineOutputDataset
                    or azureml.data.data_reference.DataReference
                    or azureml.core.Dataset
                    or azureml.data.dataset_definition.DatasetDefinition
                    or azureml.data.dataset_consumption_config.DatasetConsumptionConfig
                    or azureml.pipeline.core.PipelineDataset]
    :param outputs: A list of PipelineData objects.
    :type outputs: list[azureml.pipeline.core.builder.PipelineData
                or azureml.pipeline.core.pipeline_output_dataset.PipelineOutputDataset]
    :param compute_target: [Required] The compute target to use.
    :type compute_target: azureml.core.compute.DsvmCompute
                        or azureml.core.compute.AmlCompute
                        or azureml.core.compute.RemoteCompute
                        or str
    :param allow_reuse: Indicates whether the step should reuse previous results when re-run with the same
        settings. Reuse is enabled by default. If the step contents (scripts/dependencies) as well as inputs and
        parameters remain unchanged, the output from the previous run of this step is reused. When reusing
        the step, instead of submitting the job to compute, the results from the previous run are immediately
        made available to any subsequent steps.
    :type allow_reuse: bool
    :param version: An optional version tag to denote a change in functionality for the module.
    :type version: str
    """

    def __init__(self, name=None, estimator=None, estimator_entry_script_arguments=None,
                 runconfig_pipeline_params=None, inputs=None, outputs=None,
                 compute_target=None, allow_reuse=True, version=None):
        """
        Create an Azure ML Pipeline step to run Estimator for Machine Learning model training.

        :param name: The name of the step.
        :type name: str
        :param estimator: The associated estimator object for this step. Can be a pre-configured estimator such as
            :class:`azureml.train.dnn.Chainer`, :class:`azureml.train.dnn.PyTorch`,
            :class:`azureml.train.dnn.TensorFlow`, or :class:`azureml.train.sklearn.SKLearn`.
        :type estimator: Estimator
        :param estimator_entry_script_arguments: [Required] A list of command-line arguments.
            If the Estimator's entry script does not accept commandline arguments,
            set this parameter value to an empty list.
        :type estimator_entry_script_arguments: [str]
        :param runconfig_pipeline_params: An override of runconfig properties at runtime using key-value pairs,
                                each with name of the runconfig property and PipelineParameter for that property.
        :type runconfig_pipeline_params: dict({(str) : (azureml.pipeline.core.PipelineParameter)})
        :param inputs: A list of inputs to use.
        :type inputs: list[azureml.pipeline.core.builder.PipelineData
                    or azureml.pipeline.core.pipeline_output_dataset.PipelineOutputDataset
                    or azureml.data.data_reference.DataReference
                    or azureml.core.Dataset
                    or azureml.data.dataset_definition.DatasetDefinition
                    or azureml.data.dataset_consumption_config.DatasetConsumptionConfig
                    or azureml.pipeline.core.pipeline_output_dataset.PipelineOutputDataset
                    or azureml.pipeline.core.PipelineDataset]
        :param outputs: A list of PipelineData objects.
        :type outputs: list[azureml.pipeline.core.builder.PipelineData,
                    or azureml.pipeline.core.pipeline_output_dataset.PipelineOutputDataset]
        :param compute_target: [Required] The compute target to use.
        :type compute_target: azureml.core.compute.DsvmCompute
                        or azureml.core.compute.AmlCompute
                        or azureml.core.compute.RemoteCompute
                        or str
        :param allow_reuse: Indicates whether the step should reuse previous results when re-run with the same
            settings. Reuse is enabled by default. If the step contents (scripts/dependencies) as well as inputs
            and parameters remain unchanged, the output from the previous run of this step is reused. When reusing
            the step, instead of submitting the job to compute, the results from the previous run are immediately
            made available to any subsequent steps.
        :type allow_reuse: bool
        :param version: version
        :type version: str
        """
        # the following args are required
        if None in [estimator, compute_target]:
            raise ValueError("Estimator, compute_target parameters are required")

        if estimator.run_config.arguments:
            raise ValueError('script_params in Estimator should not be provided to EstimatorStep. '
                             'Please use estimator_entry_script_arguments instead.')

        if estimator_entry_script_arguments is None:
            raise ValueError('estimator_entry_script_arguments is a required parameter. If the Estimator''s entry'
                             'script does not accept commandline arguments, set the parameter value to empty list')

        from azureml.train.estimator import MMLBaseEstimator
        if not isinstance(estimator, MMLBaseEstimator):
            raise Exception("Estimator parameter is not of valid type")

        # resetting compute_target, arguments and data refs as they will not be used in EstimatorStep
        estimator.run_config._target = None
        estimator.run_config.arguments = []
        estimator.run_config.data_references = []

        run_config = estimator.run_config
        source_directory = estimator.source_directory
        script_name = run_config.script

        super(EstimatorStep, self).__init__(name=name, script_name=script_name,
                                            arguments=estimator_entry_script_arguments, compute_target=compute_target,
                                            runconfig=run_config, runconfig_pipeline_params=runconfig_pipeline_params,
                                            inputs=inputs, outputs=outputs,
                                            source_directory=source_directory, allow_reuse=allow_reuse,
                                            version=version)

    def create_node(self, graph, default_datastore, context):
        """
        Create a node from the Estimator step and add it to the specified graph.

        This method is not intended to be used directly. When a pipeline is instantiated with this step,
        Azure ML automatically passes the parameters required through this method so that step can be added to a
        pipeline graph that represents the workflow.

        :param graph: The graph object to add the node to.
        :type graph: azureml.pipeline.core.graph.Graph
        :param default_datastore: The default datastore.
        :type default_datastore:  azureml.data.azure_storage_datastore.AbstractAzureStorageDatastore
                            or azureml.data.azure_data_lake_datastore.AzureDataLakeDatastore
        :param context: The graph context.
        :type context: _GraphContext

        :return: The created node.
        :rtype: azureml.pipeline.core.graph.Node
        """
        return super(EstimatorStep, self).create_node(graph, default_datastore, context)
