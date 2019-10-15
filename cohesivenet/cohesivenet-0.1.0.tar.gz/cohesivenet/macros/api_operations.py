import time

import cohesivenet.util as pipe
import cohesivenet.data_types as data_types
from cohesivenet import ApiException, UrlLib3ConnExceptions


def retry_call(call_api, args=(), kwargs={}, attempt=0, max_attempts=10, sleep=2):
    try:
        return call_api(*args, **kwargs)
    except UrlLib3ConnExceptions as e:
        attempt = attempt + 1
        if attempt >= max_attempts:
            raise e
        time.sleep(sleep)
        return retry_call(
            call_api,
            args,
            kwargs,
            attempt=attempt,
            max_attempts=max_attempts,
            sleep=sleep,
        )


def gather_results(results):
    """Group results if by success and exception

    Arguments:
        results {List[ClientExceptionResult or Any]}

    Returns:
        Tuple[List[Any], List[ClientExceptionResult]]
    """
    succeeded = []
    failed = []
    for result in results:
        if isinstance(result, data_types.ClientExceptionResult):
            failed.append(result)
        else:
            succeeded.append(result)

    return succeeded, failed


def try_call_client(client, call, *args, **kwargs):
    """Try call method call(client, *args, **kwargs) catch exception

    Arguments:
        client {VNS3Client}
        call {Callable} - function that accepts client as first arg

    Returns:
        [OperationResult or ClientExceptionResult]
    """
    try:
        response = call(client, *args, **kwargs)
        return data_types.OperationResult(client, response)
    except ApiException as e:
        return data_types.ClientExceptionResult(client, e)


async def try_call_client_async(client, call, *args, **kwargs):
    """Async call client wrapper

    Arguments:
        client {VNS3Client}
        call {Callable} - function that accepts client as first arg

    Returns:
        [OperationResult or ClientExceptionResult]
    """
    return try_call_client(client, call, *args, **kwargs)


def try_call_api(api_call, *args, should_raise=False, **kwargs):
    """try_api_call Wrapper for api call to catch errors

    Arguments:
        api_call {callable}

    Returns:
        [OperationResult or ClientExceptionResult]
    """

    try:
        return api_call(*args, **kwargs)
    except ApiException as e:
        if should_raise:
            raise e
        return e


async def try_call_api_async(api_call, *args, **kwargs):
    """try_api_call_async Async Wrapper for api call to catch errors

    Arguments:
        api_call {callable}

    Returns:
        [Coroutine -> [OperationResult or ClientExceptionResult]]
    """
    return try_call_api(api_call, *args, **kwargs)


def __bulk_call_client_sync(
    clients, call_client_func
) -> data_types.BulkOperationResult:
    """Bulk operation for clients, call same method for all clients

    Arguments:
        clients {List[VNS3Client]}
        call_client_func {callable} - func: VNS3Client -> response

    Returns:
        data_types.BulkOperationResult -- [description]
    """
    return gather_results(
        [try_call_client(client, call_client_func) for client in clients]
    )


def __bulk_call_client_parallel(
    clients, call_client_func
) -> data_types.BulkOperationResult:
    """Bulk operation for clients, call same method for all clients

    Arguments:
        clients {List[VNS3Client]}
        call_client_func {callable} - func: VNS3Client -> response

    Returns:
        data_types.BulkOperationResult
    """
    return gather_results(
        pipe.run_parallel(
            *(try_call_client_async(client, call_client_func) for client in clients)
        )
    )


def __bulk_call_client(
    clients, call_client_func, parallelize=False
) -> data_types.BulkOperationResult:
    """Bulk operation for clients, call same method for all clients

    Arguments:
        clients {List[VNS3Client]}
        call_client_func {callable} - func: VNS3Client -> response

    Returns:
        data_types.BulkOperationResult
    """
    if parallelize:
        return __bulk_call_client_parallel(clients, call_client_func)
    else:
        return __bulk_call_client_sync(clients, call_client_func)


def __bulk_call_api_sync(bound_api_calls) -> data_types.BulkOperationResult:
    """__bulk_call_api_sync Bulk operation for bound api methods, call synchronously

    Arguments:
        bound_api_calls {List[Callable]}

    Returns:
        data_types.BulkOperationResult -- [description]
    """
    return gather_results([try_call_api(api_call) for api_call in bound_api_calls])


def __bulk_call_api_parallel(bound_api_calls) -> data_types.BulkOperationResult:
    """__bulk_call_api_parallel Bulk operation for bound api methods, called asynchronously

    Arguments:
        bound_api_calls {List[Callable]}

    Returns:
        data_types.BulkOperationResult
    """
    return gather_results(
        pipe.run_parallel(
            *(try_call_api_async(api_call) for api_call in bound_api_calls)
        )
    )


def __bulk_call_api(api_calls, parallelize=False) -> data_types.BulkOperationResult:
    """Bulk operation for bound api method interface

    Arguments:
        api_calls {callable} - bound function that accepts no args.

    Returns:
        data_types.BulkOperationResult
    """
    if parallelize:
        return __bulk_call_api_parallel(api_calls)
    else:
        return __bulk_call_api_sync(api_calls)


def bulk_operation_failed(result: data_types.BulkOperationResult):
    failures = result[1]
    return len(failures) > 1


def stringify_bulk_result_exception(result: data_types.BulkOperationResult):
    exceptions = result[1]
    return ".".join([str(e) for e in exceptions])
