from typing import Optional, TYPE_CHECKING
if TYPE_CHECKING:
    from cryptocompsdk.request import Request


class ResponseAPIBase:
    response: Optional[str]
    _request: 'Request'

    @property
    def has_error(self) -> bool:
        return self.response == 'Error'


    # The following methods need to be set for pagination

    @property
    def is_empty(self) -> bool:
        raise NotImplementedError('must implement in ResponseAPIBase subclass')

    def __add__(self, other):
        raise NotImplementedError('must implement in ResponseAPIBase subclass')

    def __radd__(self, other):
        raise NotImplementedError('must implement in ResponseAPIBase subclass')

    @property
    def time_from(self) -> int:
        raise NotImplementedError('must implement in ResponseAPIBase subclass')

    def delete_record_matching_time(self, time: int):
        raise NotImplementedError('must implement in ResponseAPIBase subclass')

    def trim_empty_records_at_beginning(self):
        raise NotImplementedError('must implement in ResponseAPIBase subclass')


class ResponseException(Exception):
    pass