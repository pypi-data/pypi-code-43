from typing import List
import importlib
import re
from azureml.designer.modules.datatransform.common.module_base import ModuleBase
def get_all_modules() -> List[ModuleBase]:
    # from azureml.designer.modules.datatransform.modules.apply_math_module import ApplyMathModule
    # from azureml.designer.modules.datatransform.modules.apply_sql_trans_module import ApplySqlTransModule
    # from azureml.designer.modules.datatransform.modules.clip_values_module import ClipValuesModule
    # from azureml.designer.modules.datatransform.modules.summarize_data_module import SummarizeDataModule
    # return [
    #     ApplyMathModule(),
    #     ApplySqlTransModule(),
    #     ClipValuesModule(), 
    #     SummarizeDataModule()
    # ]
    return [ construct_module_by_name(module_name) for module_name in get_all_modules_name()]

def get_all_modules_name() -> List[str]:
    return [
        'ApplyMathModule',
        'ApplySqlTransModule',
        'ClipValuesModule',
        'SummarizeDataModule',
        'GenTestDataModule',
        # 'DoNothingModule',
        # 'WaitingModule'
    ]

def construct_module_by_name(module_name:str) -> ModuleBase:
    split_class_name = re.findall('[A-Z][^A-Z]*',module_name)
    module_file_name = '_'.join(split_class_name).lower()
    module_namespace = 'azureml.designer.modules.datatransform.modules.' + module_file_name
    module = importlib.import_module(module_namespace, module_name)
    module_class = getattr(module, module_name)
    return module_class()

