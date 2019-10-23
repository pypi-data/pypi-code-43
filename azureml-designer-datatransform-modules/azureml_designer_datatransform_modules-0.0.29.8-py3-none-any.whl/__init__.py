# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# try:
#     __import__('pkg_resources').declare_namespace(__name__)
# except ImportError:
__path__ = __import__('pkgutil').extend_path(__path__, __name__)
# print("---------init of azureml custom module-------------------")
# print(__path__)
# print(__name__)
