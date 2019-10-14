# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""SDK utilities dealing with the runtime environment."""
from typing import Optional
from pkg_resources import Requirement, RequirementParseError  # type: ignore
import re
import json
import logging

from automl.client.core.common.exceptions import ClientException
from automl.client.core.common import constants
from azureml.automl.core import package_utilities
from azureml.automl.core.automl_base_settings import AutoMLBaseSettings
from azureml.core import RunConfiguration

from ._azureautomlsettings import AzureAutoMLSettings
from .run import AutoMLRun


class _Package:
    """A class to identify packages."""

    def __init__(self, name: str, regex: str, is_conda: bool, required_version: Optional[str] = None):
        """
        Create a package representation.

        :param name: The name of the package.
        :type name: str
        :param regex: The regex to search for in conda dependencies.
        :type regex: str
        :param is_conda: The flag to determine if package should be a conda package.
        :type is_conda: bool
        :param required_version: The version specifier. Should follow PEP 440.
        :type required_version: str
        """
        self.name = name
        self.regex = regex
        self.is_conda = is_conda

        if required_version is not None:
            try:
                specifier = Requirement.parse(name + required_version).specifier  # type: ignore
                if len(specifier) < 1:
                    # ensure version specifier is complete. If length is 0 then only a number was provided
                    raise ClientException("Invalid version specifier. Ensure version follows PEP 440 standards.")
            except RequirementParseError:
                # allow conda's '=' version matching clause, different from pip's '=='
                conda_version_matching_regex = r"^\=[\.0-9]+$"
                is_conda_double_equals = is_conda and re.search(conda_version_matching_regex, required_version)
                if not is_conda_double_equals:
                    raise ClientException("Invalid version specifier. Ensure version follows PEP 440 standards.")
        self.required_version = required_version


def modify_run_configuration(settings: AzureAutoMLSettings,
                             run_config: RunConfiguration,
                             logger: logging.Logger) -> RunConfiguration:
    """
    Modify the run configuration with the correct version of AutoML and pip feed.
    Install pytorch, pytorch-transformer and cudatoolkit=9.0 in remote environment.
    GPU support enabled for CUDA driver version >= 384.81.
    Currently supports Linux which is the OS for remote compute, though Windows should work too.
    """
    from azureml.core.conda_dependencies import CondaDependencies, DEFAULT_SDK_ORIGIN

    installed_packages = package_utilities._all_dependencies()

    automl_pkg = "azureml-train-automl"
    automl_regex = r"azureml\S*automl\S*"

    # For now we will add dataprep to ensure we pin to the locally installed version
    # in case the release does not match the azureml-core release cadence
    dataprep_pkg = "azureml-dataprep"
    dataprep_regex = r"azureml\S*dataprep\S*"

    explain_pkg = "azureml-explain-model"
    explain_regex = r"azureml-explain-model([\=\<\>\~0-9\.\s]+|\Z)"

    fbprophet_pkg = "fbprophet"
    fbprophet_regex = "fbprophet"

    git_setuptools_pkg = "setuptools-git"
    git_setuptools_regex = r"setuptools-git==1.2"

    numpy_pkg = "numpy"
    numpy_regex = r"numpy([\=\<\>\~0-9\.\s]+|\Z)"

    pytorch_pkg = "pytorch"
    pytorch_regex = r"pytorch=1\.1"

    cudatoolkit_pkg = "cudatoolkit"
    cudatoolkit_regex = r"cudatoolkit=9\.0"

    xgboost_pkg = "py-xgboost"
    xgboost_regex = r"py-xgboost<=0\.80"

    # Adding inference schema generation package so we can reuse same env for inferencing as well
    inference_schema_pkg = "inference-schema"
    inference_schema_regex = r"inference-schema([\=\<\>\~0-9\.\s]+|\Z)"

    pytorch_transformers_pkg = "pytorch-transformers"  # includes BERT, XLNet, GPT-2 etc.
    pytorch_transformers_regex = r"pytorch-transformers==1.0.0"

    spacy_pkg = "spacy"  # tokenizer required by BiLSTM text DNN model
    spacy_regex = r"spacy==2.1.8"

    # download english tokenizer model
    spacy_english_model_url = "https://aka.ms/automl-resources/packages/en_core_web_sm-2.1.0.tar.gz"
    spacy_english_model_regex = "en_core_web_sm"

    # tar ball from github.com/NVIDIA/apex for half-precision floating point arithmetic
    # apex_url = "https://aka.ms/automl-resources/packages/apex.tar.gz"
    # apex_regex = "apex"

    automl_version = installed_packages[automl_pkg]     # type: Optional[str]
    if automl_version and ("dev" in automl_version or automl_version == "0.1.0.0"):
        automl_version = None
        logger.warning("You are running a developer or editable installation of required packages. Your "
                       "changes will not be run on your remote compute. Latest versions of "
                       "azureml-core and azureml-train-automl will be used unless you have "
                       "specified an alternative index or version to use.")

    explain_version = installed_packages.get(explain_pkg)
    if explain_version and ("dev" in explain_version or explain_version == "0.1.0.0"):
        explain_version = None

    required_package_list = [
        _Package(automl_pkg, automl_regex, False),
        _Package(explain_pkg, explain_regex, False),
        _Package(dataprep_pkg, dataprep_regex, False),
        _Package(numpy_pkg, numpy_regex, True),
        _Package(xgboost_pkg, xgboost_regex, True, "<=0.80"),
        _Package(pytorch_pkg, pytorch_regex, True, "=1.1.0"),  # supported for Linux - OS for remote compute
        _Package(cudatoolkit_pkg, cudatoolkit_regex, True, "=9.0"),  # 9.0 has broadest driver compatibility
        _Package(pytorch_transformers_pkg, pytorch_transformers_regex, False, "==1.0.0"),
        _Package(inference_schema_pkg, inference_schema_regex, False),
        _Package(fbprophet_pkg, fbprophet_regex, True),
        _Package(git_setuptools_pkg, git_setuptools_regex, True),
        _Package(spacy_pkg, spacy_regex, False, "==2.1.8"),
        _Package(spacy_english_model_url, spacy_english_model_regex, False),
        # _Package(apex_url, apex_regex, False),  # disabled until fix for fused kernels available
    ]

    dependencies = run_config.environment.python.conda_dependencies
    dependencies.add_channel("pytorch")
    # dependencies.set_pip_option('--global-option="--cpp_ext" --global-option="--cuda_ext"')

    # if debug flag sets an sdk_url use it
    if settings.sdk_url is not None:
        dependencies.set_pip_option("--index-url " + settings.sdk_url)
        dependencies.set_pip_option("--extra-index-url " + DEFAULT_SDK_ORIGIN)

    # if debug_flag sets packages, use those in remote run
    if settings.sdk_packages is not None:
        for package in settings.sdk_packages:
            dependencies.add_pip_package(package)

    all_pkgs_str = " ".join(dependencies.pip_packages) + " " + " ".join(dependencies.conda_packages)

    # include required packages
    for p in required_package_list:
        if not re.findall(p.regex, all_pkgs_str):
            logger.info("Package {} missing from dependencies file.".format(p.name))
            # when picking version - check if we require a specific version first
            # if not, then use what is installed. If the package doesn't require a version
            # and doesnt have an installed version don't pin.
            if p.required_version is not None:
                version_str = p.required_version
                logger.info("Using pinned version: {}{}".format(p.name, version_str))
            elif p.name in installed_packages:
                ver = installed_packages[p.name]
                version_str = "=={}".format(ver)
                logger.info("Using installed version: {}{}".format(p.name, version_str))
            else:
                version_str = ""

            if p.is_conda:
                dependencies.add_conda_package(p.name + version_str)
            else:
                dependencies.add_pip_package(p.name + version_str)

            # If azureml-train-automl is added by the SDK, we need to ensure we do not pin to an editable installtion.
            # If automl_version is none we will reset the version to not pin.
            if p.name == automl_pkg:
                if automl_version is None:
                    dependencies.add_pip_package(p.name)

            # If azureml-explain-model is added by the SDK, we need to ensure we do not pin to an editable installtion.
            # If explain_version is none we will reset the version to not pin.
            if p.name == explain_pkg:
                if explain_version is None:
                    dependencies.add_pip_package(p.name)

    # If we installed from a channel that isn't pypi we'll need to pick up the index. We'll assume
    # if the user added an index to their dependencies they know what they are doing and we won't modify anything.
    source_url = CondaDependencies.sdk_origin_url()
    if source_url != DEFAULT_SDK_ORIGIN and 'index-url' not in dependencies.serialize_to_string():
        dependencies.set_pip_option("--index-url " + source_url)
        dependencies.set_pip_option("--extra-index-url " + DEFAULT_SDK_ORIGIN)

    # this is required to ensure we do not end up with mismatched versions of core and automl packages.
    dependencies.remove_pip_package('azureml-defaults')

    run_config.environment.python.conda_dependencies = dependencies
    return run_config


def log_user_sdk_dependencies(run: AutoMLRun, logger: logging.Logger) -> None:
    """
    Log the AzureML packages currently installed on the local machine to the given run.

    :param run: The run to log user depenencies.
    :param logger: The logger to write user dependencies.
    :return:
    :type: None
    """
    dependencies = {'dependencies_versions': json.dumps(package_utilities.get_sdk_dependencies())}
    logger.info("[RunId:{}]SDK dependencies versions:{}."
                .format(run.id, dependencies['dependencies_versions']))
    run.add_properties(dependencies)
