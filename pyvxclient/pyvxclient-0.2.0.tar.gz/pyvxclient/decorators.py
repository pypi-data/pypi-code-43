import time
import logging
from functools import wraps
from bravado.exception import HTTPNotFound, HTTPServerError, HTTPError
from bravado.response import BravadoResponse
from pyvxclient.errors import BadRequest, Forbidden, Unauthorized, ClientError, ServerError
from pyvxclient.common import ApiResponse

log = logging.getLogger(__name__)

LIMIT = 1000


def handle_response(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        try:
            data = func(*args, **kwargs)
            if isinstance(data, BravadoResponse):
                status_code = data.incoming_response.status_code
                data = data.result
                return ApiResponse(json=data,
                                   status_code=status_code)
            else:  # ApiResponse
                return data
        except HTTPNotFound as e:
            resp = None
            if hasattr(e, 'response') and e.response:
                resp = e.response.json()
            return ApiResponse(json=resp, status_code=404)
        except HTTPError as e:
            # log.error(e)
            resp = None
            # TODO: fixed vxctl version or there is anything better?
            if hasattr(e, 'swagger_result') and e.swagger_result:
                resp = e.swagger_result
            elif hasattr(e, 'response') and e.response:
                resp = e.response.json()
            # return ApiResponse(json=resp, status_code=e.status_code)
            if e.status_code == 400:
                raise BadRequest(resp)
            elif e.status_code == 403:
                raise Forbidden(resp)
            elif e.status_code == 401:
                raise Unauthorized(resp)
            elif isinstance(e, HTTPServerError):
                raise ServerError(resp)
            else:
                raise ClientError(resp, code=e.status_code)

    return wrapped


def paginate(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        result = []
        wanted_result = kwargs.get('limit', LIMIT)
        if wanted_result >= LIMIT or wanted_result == 0:
            kwargs['limit'] = LIMIT  # force this limit of 1000

        i = 0
        # always send in page
        kwargs.setdefault('page', 1)
        start = time.time()
        while True:
            i += 1
            data = func(*args, **kwargs)
            if isinstance(data, BravadoResponse):
                status_code = data.incoming_response.status_code
                data = data.result
            else:  # ApiResponse
                data = data.data
                status_code = data.status_code

            result.extend(data.get('data'))

            # clean the result to match fields.
            # TODO: fixed vxctl version
            if 'fields' in kwargs and len(kwargs['fields']) >= 1:
                new_result = []
                log.debug("fields is set (%s), strip result from all other fields" % ",".join(kwargs['fields']))
                for row in result:
                    new_row = {}
                    for n in row.keys():
                        if n in kwargs['fields']:
                            new_row[n] = row[n]
                    if row != {}:
                        new_result.append(new_row)
                result = new_result

            items_left = (wanted_result - len(result)) if wanted_result != 0 else kwargs['limit']
            if items_left <= kwargs['limit']:
                kwargs['limit'] = items_left
            per_page = data.get('pagination').get('per_page')
            page = data.get('pagination').get('page')

            # if the result is zero or not a full page (known last page)
            if len(data.get('data')) == 0 or len(data.get('data')) < kwargs['limit']:
                break
            # if the wanted result is retrieved
            if wanted_result != 0 and ((per_page * page) >= wanted_result or len(result) == wanted_result):
                break
            else:
                kwargs["page"] += 1

        # create stats for output.
        data['data'] = result
        out = {
            "data": result,
            "pagination": data['pagination'],
            "stats": {
                "api_calls": i,
                "total_rows": len(result),
                "execution_time": time.time() - start
            }
        }
        return ApiResponse(json=out if out else None,
                           status_code=status_code)

    return wrapped
