from typing import List, Any, Dict


def action(models: List[Any], body: Dict) -> List[int]:
    ans = []
    for idx, model in enumerate(models):
        func_name = body["function"]
        function = getattr(model, func_name)
        ans.append(function(body))
    return ans
