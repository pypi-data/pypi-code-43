import sys
import os
from pip._internal.operations.freeze import freeze
import azureml
# azureml.__path__ = __import__('pkgutil').extend_path([os.path.join(os.getcwd(),'azureml')],'azureml')

# sys.path.insert(0,os.getcwd())
# print("working folder")
# print(os.getcwd())
# print("current file path")
# print(os.path.abspath(__file__))
# print("common directory")
# print(os.listdir(os.path.join(os.getcwd(), "azureml/custommodules/common")))
# print("azureml look up path")
# print(azureml.__path__)
# print("pip")
# for requirement in freeze():
#     print(requirement)

import importlib
import re
from azureml.designer.modules.datatransform.common.logger import custom_module_logger as logger
from azureml.designer.modules.datatransform.common.logger import format_obj
from azureml.designer.modules.datatransform.common.module_collection import get_all_modules_name, construct_module_by_name
from azureml.studio.internal.error_handler import error_handler
from azureml.designer.modules.datatransform import __version__

@error_handler 
def main(*rawargs):
    # construct transform custom module from args
    module_list =  get_all_modules_name()
    logger.info("Start custom modules")
    logger.info(f"Module version: {__version__}")
    logger.info("args: %s"%(', '.join(rawargs)))
    if len(rawargs) < 2:
        raise ValueError("Please specify transform module class")
    transform_module_class_name = rawargs[1]
    if not transform_module_class_name in module_list:
        raise ValueError(f"Please specify transform module class within [{','.join(module_list)}]")
    # TODO: set position variable as choices
    logger.info(format_obj("transform_module_class_name", transform_module_class_name))
    transform_module = construct_module_by_name(transform_module_class_name)
    transform_module.parse_and_insert_args(rawargs[1:], True)
    logger.info("start to run custom module: %s", transform_module_class_name)
    transform_module.train()

if __name__ == "__main__":
    main(*sys.argv)
