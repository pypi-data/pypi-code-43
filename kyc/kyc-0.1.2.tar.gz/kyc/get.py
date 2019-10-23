from .model.datatable import Datatable
from .errors.tej_error import LimitExceededError
from .api_config import ApiConfig
from .message import Message
import warnings
import copy

def get(datatable_code, **options):

    if 'paginate' in options.keys():
        paginate = options.pop('paginate')
    else:
        paginate = None
        
    if 'chinese_column_name' in options.keys():
        chinese_column_name = options.pop('chinese_column_name')
    else:
        chinese_column_name = False
        
    if 'opts_filter' in options.keys():
        filters = options.pop('opts_filter')
        options.update(filters)

    data = None
    page_count = 0
    while True:
        next_options = copy.deepcopy(options)
        next_data = Datatable(datatable_code).data(params=next_options)

        if data is None:
            data = next_data
        else:
            data.extend(next_data)

        if page_count >= ApiConfig.page_limit:
            raise LimitExceededError(Message.WARN_DATA_LIMIT_EXCEEDED)

        next_cursor_id = next_data.meta['next_cursor_id']

        if next_cursor_id is None:
            break
        elif paginate is not True and next_cursor_id is not None:
            warnings.warn(Message.WARN_PAGE_LIMIT_EXCEEDED, UserWarning)
            break

        page_count = page_count + 1
        options['opts.cursor_id'] = next_cursor_id
    return data.to_pandas(chinese_column_name = chinese_column_name)