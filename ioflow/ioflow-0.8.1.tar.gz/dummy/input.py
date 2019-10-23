from typing import Callable, Dict, List, Any, Generator


def build_input_func(
    data_generator_func: Callable[[], List[Any]], configure: Dict = None
) -> Callable[[], Generator[str, Any, None]]:
    def input_func():
        for offset_data in data_generator_func():
            yield str(offset_data)

    return input_func
