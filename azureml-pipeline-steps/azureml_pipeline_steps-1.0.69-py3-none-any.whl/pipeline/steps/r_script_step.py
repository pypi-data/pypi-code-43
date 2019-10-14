# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains functionality to create an Azure ML Pipeline step that runs R script."""
import os

from azureml.core import RunConfiguration
from azureml.pipeline.core._python_script_step_base import _PythonScriptStepBase


class RScriptStep(_PythonScriptStepBase):
    r"""Creates an Azure ML Pipeline step that runs R script.

    .. remarks::

        An RScriptStep is a basic, built-in step to run R script on a compute target. It takes
        a script name and other optional parameters like arguments for the script, compute target, inputs
        and outputs. If no compute target is specified, the default compute target for the workspace is
        used. You can also use a :class:`azureml.core.RunConfiguration` to specify requirements for the
        RScriptStep, such as conda dependencies and docker image.

        The best practice for working with RScriptStep is to use a separate folder for scripts and any dependent
        files associated with the step, and specify that folder with the ``source_directory`` parameter.
        Following this best practice has two benefits. First, it helps reduce the size of the snapshot
        created for the step because only what is needed for the step is snapshotted. Second, the step's output
        from a previous run can be reused if there are  no changes to the ``source_directory`` that would trigger
        a re-upload of the snapshot.

        The following code example shows using a RScriptStep in a machine learning training scenario.

        .. code-block:: python

            from azureml.pipeline.steps import RScriptStep

            trainStep = RScriptStep(
                script_name="train.R",
                arguments=["--input", blob_input_data, "--output", output_data1],
                inputs=[blob_input_data],
                outputs=[output_data1],
                compute_target=compute_target,
                source_directory=project_folder,
                cran_packages=['ggplot2', 'dplyr']
            )

        For more details on creating pipelines in general, see https://aka.ms/pl-first-pipeline.

    :param script_name: [Required] The name of a R script relative to ``source_directory``.
    :type script_name: str
    :param name: The name of the step. If unspecified, ``script_name`` is used.
    :type name: str
    :param arguments: Command line arguments for the R script file. The arguments will be passed
                      to compute via the ``arguments`` parameter in RunConfiguration.
                      For more details how to handle arguments such as special symbols, see
                      the :class:`azureml.core.RunConfiguration`.
    :type arguments: list
    :param compute_target: [Required] The compute target to use. If unspecified, the target from
        the ``runconfig`` is used. This parameter may be specified as
        a compute target object or the string name of a compute target on the workspace.
        Optionally if the compute target is not available at pipeline creation time, you may specify a tuple of
        ('compute target name', 'compute target type') to avoid fetching the compute target object (AmlCompute
        type is 'AmlCompute' and RemoteCompute type is 'VirtualMachine').
    :type compute_target: azureml.core.compute.DsvmCompute
                        or azureml.core.compute.AmlCompute
                        or azureml.core.compute.RemoteCompute
                        or azureml.core.compute.HDInsightCompute
                        or str
                        or tuple
    :param runconfig: The optional RunConfiguration to use. A RunConfiguration can be used to specify additional
                    requirements for the run, such as conda dependencies and a docker image. If unspecified, a
                    default runconfig will be created.
    :type runconfig: azureml.core.runconfig.RunConfiguration
    :param runconfig_pipeline_params: Overrides of runconfig properties at runtime using key-value pairs
                    each with name of the runconfig property and PipelineParameter for that property.
    :type runconfig_pipeline_params: {str: PipelineParameter}
    :param inputs: A list of input port bindings.
    :type inputs: list[azureml.pipeline.core.graph.InputPortBinding
                    or azureml.data.data_reference.DataReference
                    or azureml.pipeline.core.PortDataReference
                    or azureml.pipeline.core.builder.PipelineData
                    or azureml.pipeline.core.pipeline_output_dataset.PipelineOutputDataset
                    or azureml.core.Dataset
                    or azureml.data.dataset_definition.DatasetDefinition
                    or azureml.data.dataset_consumption_config.DatasetConsumptionConfig
                    or azureml.pipeline.core.PipelineDataset]
    :param outputs: A list of output port bindings.
    :type outputs: list[azureml.pipeline.core.builder.PipelineData
                        or azureml.pipeline.core.pipeline_output_dataset.PipelineOutputDataset
                        or azureml.pipeline.core.graph.OutputPortBinding]
    :param params: A dictionary of name-value pairs registered as environment variables with "AML_PARAMETER\_".
    :type params: dict
    :param source_directory: A folder that contains R script, conda env, and other resources used in
        the step.
    :type source_directory: str
    :param use_gpu: Indicates whether the environment to run the experiment should support GPUs.
        If True, a GPU-based default Docker image will be used in the environment. If False, a CPU-based
        image will be used. Default docker images (CPU or GPU) will be used only if the ``custom_docker_image``
        parameter is not set. This setting is used only in Docker-enabled compute targets.
    :type use_gpu: bool
    :param custom_docker_image: The name of the Docker image from which the image to use for training
        will be built. If not set, a default CPU-based image will be used as the base image.
    :type custom_docker_image: str
    :param cran_packages: CRAN packages to be installed.
    :type cran_packages: list
    :param github_packages: GitHub packages to be installed.
    :type github_packages: list
    :param custom_url_packages: Packages to be installed from local, directory or custom URL.
    :type custom_url_packages: list
    :param allow_reuse: Indicates whether the step should reuse previous results when re-run with the same
        settings. Reuse is enabled by default. If the step contents (scripts/dependencies) as well as inputs and
        parameters remain unchanged, the output from the previous run of this step is reused. When reusing
        the step, instead of submitting the job to compute, the results from the previous run are immediately
        made available to any subsequent steps.
    :type allow_reuse: bool
    :param version: An optional version tag to denote a change in functionality for the step.
    :type version: str

    """

    def __init__(self, script_name, name=None, arguments=None, compute_target=None, runconfig=None,
                 runconfig_pipeline_params=None, inputs=None, outputs=None, params=None, source_directory=None,
                 use_gpu=False, custom_docker_image=None, cran_packages=None, github_packages=None,
                 custom_url_packages=None, allow_reuse=True, version=None):
        r"""Create an Azure ML Pipeline step that runs R script.

        :param script_name: [Required] The name of a R script relative to ``source_directory``.
        :type script_name: str
        :param name: The name of the step. If unspecified, ``script_name`` is used.
        :type name: str
        :param arguments: Command line arguments for the R script file. The arguments will be passed
                          to compute via the ``arguments`` parameter in RunConfiguration.
                          For more details how to handle arguments such as special symbols, see
                          the :class:`azureml.core.RunConfiguration`.
        :type arguments: list
        :param compute_target: [Required] The compute target to use. If unspecified, the target from
            the ``runconfig`` will be used. This parameter may be specified as
            a compute target object or the string name of a compute target on the workspace.
            Optionally if the compute target is not available at pipeline creation time, you may specify a tuple of
            ('compute target name', 'compute target type') to avoid fetching the compute target object (AmlCompute
            type is 'AmlCompute' and RemoteCompute type is 'VirtualMachine').
        :type compute_target: azureml.core.compute.DsvmCompute
                            or azureml.core.compute.AmlCompute
                            or azureml.core.compute.RemoteCompute
                            or azureml.core.compute.HDInsightCompute
                            or str
                            or tuple
        :param runconfig: The optional RunConfiguration to use. A RunConfiguration can be used to specify additional
                        requirements for the run, such as conda dependencies and a docker image. If unspecified, a
                        default runconfig will be created.
        :type runconfig: azureml.core.runconfig.RunConfiguration
        :param runconfig_pipeline_params: Overrides of runconfig properties at runtime using key-value pairs
                        each with name of the runconfig property and PipelineParameter for that property.
        :type runconfig_pipeline_params: {str: PipelineParameter}
        :param inputs: A list of input port bindings.
        :type inputs: list[azureml.pipeline.core.graph.InputPortBinding
                        or azureml.data.data_reference.DataReference
                        or azureml.pipeline.core.PortDataReference
                        or azureml.pipeline.core.builder.PipelineData
                        or azureml.pipeline.core.pipeline_output_dataset.PipelineOutputDataset
                        or azureml.core.Dataset
                        or azureml.data.dataset_definition.DatasetDefinition
                        or azureml.data.dataset_consumption_config.DatasetConsumptionConfig
                        or azureml.pipeline.core.PipelineDataset]
        :param outputs: A list of output port bindings.
        :type outputs: list[azureml.pipeline.core.builder.PipelineData
                            or azureml.pipeline.core.pipeline_output_dataset.PipelineOutputDataset
                            or azureml.pipeline.core.graph.OutputPortBinding]
        :param params: A dictionary of name-value pairs registered as environment variables with "AML_PARAMETER\_".
        :type params: dict
        :param source_directory: A folder that contains R script, conda env, and other resources used in
            the step.
        :type source_directory: str
        :param use_gpu: Indicates whether the environment to run the experiment should support GPUs.
            If True, a GPU-based default Docker image will be used in the environment. If False, a CPU-based
            image will be used. Default docker images (CPU or GPU) will be used only if the ``custom_docker_image``
            parameter is not set. This setting is used only in Docker-enabled compute targets.
        :type use_gpu: bool
        :param custom_docker_image: The name of the Docker image from which the image to use for training
            will be built. If not set, a default CPU-based image will be used as the base image.
        :type custom_docker_image: str
        :param cran_packages: CRAN packages to be installed.
        :type cran_packages: list
        :param github_packages: GitHub packages to be installed.
        :type github_packages: list
        :param custom_url_packages: Packages to be installed from local, directory or custom url.
        :type custom_url_packages: list
        :param allow_reuse: Indicates whether the step should reuse previous results when re-run with the same
            settings. Reuse is enabled by default. If the step contents (scripts/dependencies) as well as inputs and
            parameters remain unchanged, the output from the previous run of this step is reused. When reusing
            the step, instead of submitting the job to compute, the results from the previous run are immediately
            made available to any subsequent steps.
        :type allow_reuse: bool
        :param version: An optional version tag to denote a change in functionality for the step.
        :type version: str
        """
        self._docker_image = custom_docker_image
        if self._docker_image is None:
            if use_gpu:
                self._docker_image = 'r-base:gpu'
            else:
                self._docker_image = 'r-base:cpu'

        self._launch_script_name = self._create_launch_script(script_name, source_directory, cran_packages,
                                                              github_packages, custom_url_packages)

        if runconfig is None:
            runconfig = RunConfiguration()

        runconfig.target = compute_target
        runconfig.environment.docker.enabled = True
        runconfig.script = self._launch_script_name
        runconfig.framework = 'R'
        runconfig.environment.docker.base_image = self._docker_image
        runconfig.environment.docker.base_image_registry.address = 'viennaprivate.azurecr.io'
        runconfig.environment.python.conda_dependencies.add_channel('r')
        runconfig.environment.python.user_managed_dependencies = True

        super(RScriptStep, self).__init__(
            script_name=self._launch_script_name, name=name, arguments=arguments, compute_target=compute_target,
            runconfig=runconfig, runconfig_pipeline_params=runconfig_pipeline_params, inputs=inputs, outputs=outputs,
            params=params, source_directory=source_directory, allow_reuse=allow_reuse, version=version)

    @staticmethod
    def _create_launch_script(script_name, source_directory, cran_packages, github_packages, custom_url_packages):
        """
        Create a R launch script which contains all the packages to be installed.

        :param script_name: [Required] The name of a R script relative to ``source_directory``.
        :type script_name: str
        :param source_directory: A folder that contains R script, conda env, and other resources used in
            the step.
        :type source_directory: str
        :param cran_packages: cran packages to be installed.
        :type cran_packages: list
        :param github_packages: github packages to be installed.
        :type github_packages: list
        :param custom_url_packages: packages to be installed from local, directory or custom url.
        :type custom_url_packages: list
        :return:
        """
        launch_script_name = 'launcher.R'
        if script_name == launch_script_name:
            launch_script_name = 'auto-generated-launcher.R'

        lines = ['# This is the auto-generated launcher file.\n',
                 '# It installs the packages specified in the step.\n'
                 '# Once all the packages are successfully installed, it will execute the R script.\n\n']

        if cran_packages is not None:
            for package in cran_packages:
                lines.append('install.packages(\"{}\", repos = \"http://cran.us.r-project.org\")\n'.format(package))
            lines.append('\n')

        if github_packages is not None:
            for package in github_packages:
                lines.append('devtools::install_github(\"{}\")\n'.format(package))
            lines.append('\n')

        if custom_url_packages is not None:
            for package in custom_url_packages:
                lines.append('install.packages(\"{}\", repos = NULL)\n'.format(package))
            lines.append('\n')

        lines.append('source(\"{}\")'.format(script_name))

        with open(os.path.join(source_directory, launch_script_name), "w") as launch_file:
            launch_file.writelines(lines)

        return launch_script_name

    def create_node(self, graph, default_datastore, context):
        """
        Create a node for RScriptStep and add it to the specified graph.

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
        return super(RScriptStep, self).create_node(
            graph=graph, default_datastore=default_datastore, context=context)
