from typing import Dict, AnyStr, Tuple, Optional
import re
import sys
from .modulext import Modulext
from .utilles import UniqueIDMap

namespaceMatch = r"[a-zA-z\$]([a-zA-Z0-9\._]){0,}(?=(\:\:))"
TargetMatch = r"(?<=(\:\:))(([a-zA-Z\@\$\\/]([a-zA-Z0-9\._]){0,}){0,})" # 匹配"/"后一串

cache = UniqueIDMap()

def DecodeTarget(Target):
    MatchNamespace = re.search(namespaceMatch, Target)
    if not MatchNamespace:
        raise ValueError("must specify a namespace.")
    MatchTarget = re.search(TargetMatch, Target)
    return dict(
        namespace=MatchNamespace,
        Target=MatchTarget
    )

def VisualParamsExecString(*s):
    return ";".join(["from typing import Any"] + [f"{i}: Any" for i in s])

class Import:
    requireTargets: Dict[AnyStr, AnyStr]

    def __init__(self, **targets):
        """
        Import(faq="$", faq1="$/faq_value1")(
            From
        )
        """
        self.requireTargets = targets

    def __call__(self, *sources_args: Optional, **sources_kwargs) -> Tuple:
        """
        指定导入源, 并执行真正的导入步骤.
        """
        # 解析source(导入源)
        sources = {i.namespace : i for i in sources_args}
        sourceSpec = {i: i.finder() for i in sources_args}
        # 将sources_kwargs的内容加入, 优先级较高
        sources.update(sources_kwargs)
        sourceSpec.update({k: v.finder() for k, v in sources_kwargs.items()})

        # 解析导入目标
        Targets = {k: DecodeTarget(v) for k, v in self.requireTargets.items()}

        # 判断是否有没有预料到的namespace..
        filted = [i for i in Targets.values() if i['namespace'].group(0) in sources]
        if len(filted) != len(Targets):
            # 错误分析一下吧w
            # 感觉太简单了....
            raise ValueError(f"{[i['namespace'].group(0) for i in Targets.values() if i['namespace'].group(0) not in sources]} has/have not in the sources.")

        TargetMapping = {}
        for target, item in Targets.items():
            if not item['namespace'] or not item['Target']:
                raise ValueError(f"target '{target}' has a invaild value.")
            if item['namespace'].group(0) not in sources:
                raise ValueError(f"{item['namespace']} does not exist.")
            source = sources[item['namespace'].group(0)]
            spec = sourceSpec[item['namespace'].group(0)]

            if item["Target"].group(0) == "@all": # 相当于 from xxx import *, 但是我不喜欢这样.
                raise ImportError(f"in Entrancebar, '@all' can be 'from {item['namespace'].group(0)} import *', but it's a non-except error.")

            # 读取/写入缓存
            if cache.get(spec):
                result = cache[spec] # 使用了自写的UniqueIDMap, 直接丢spec就OK了....
            else:
                result = source.render(spec)
                cache[spec] = result

            if item["Target"].group(0) == "$this": # 不访问内部, 直接返回Modulext对象
                TargetMapping[target] = result
                continue

            for i in item["Target"].group(0).split("/"):
                result = getattr(result, i)
            TargetMapping[target] = result

        sys._getframe(1).f_globals.update(TargetMapping) # 万 恶 之 源, 静态查Bug之大敌
        return tuple(TargetMapping.values())

if __name__ == "__main__":
    print(DecodeTarget("v1"))