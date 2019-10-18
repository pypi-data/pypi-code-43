from typing import Callable

import rx3
from rx3.core import Observable


def _on_error_resume_next(second: Observable) -> Callable[[Observable], Observable]:
    def on_error_resume_next(source: Observable) -> Observable:
        return rx3.on_error_resume_next(source, second)
    return on_error_resume_next
