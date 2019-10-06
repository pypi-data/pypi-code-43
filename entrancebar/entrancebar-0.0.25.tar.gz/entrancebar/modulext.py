from types import ModuleType
from typing import Dict, Any, AnyStr

class Modulext:
    """
    用于Import的全局插入值, 也用作半加工过程载体
    """
    Original: Dict[AnyStr, ModuleType]
    EnvInfo: Dict[AnyStr, Any]

    def __init__(self, OriginalModule: Dict[AnyStr, ModuleType], EnvInfo: Dict[AnyStr, Any]):
        self.Original = OriginalModule
        self.EnvInfo = EnvInfo

    def __getattr__(self, value: str):
        result = self.Original['default']
        for i in value.split("/"):
            result = getattr(result, i)
        return result

    def __getitem__(self, value):
        if isinstance(value, slice):
            # start: namespace, stop: item, step: NO!
            # Example["default":"__file__"]

            if value.start == "$env":
                # Example["$env": "filePath"]
                return self.EnvInfo[value.stop]
            
            if value.start == "$mixinBody":
                # 当然, 你要搞到这里的东西也挺简单.
                return getattr(self, value)

            return getattr(self.Original[value.start][value.end], value.stop)
        
        if isinstance(value, str):
            # 通常用于获取环境信息
            return self.EnvInfo[value]

        raise TypeError(f"{value} used a invalid type: {value.__class__}")