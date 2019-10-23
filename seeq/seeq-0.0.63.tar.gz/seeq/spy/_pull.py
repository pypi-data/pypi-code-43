import queue
import threading

import pandas as pd
import numpy as np

from seeq.sdk43 import *

from . import _common
from . import _login

from ._common import Status


def pull(items, *, start=None, end=None, grid='15min', header='__auto__', group_by=None, capsules_as='auto',
         tz_convert=None, calculation=None, bounding_values=False, errors='raise', quiet=False, status=None):
    """
    Retrieves signal, condition or scalar data from Seeq Server and return it in a DataFrame.
    :param items: A DataFrame or Series containing ID and Type columns that can be used to identify the items to pull.
    This is usually created via a call to spy.search().
    :type items: pd.DataFrame, pd.Series
    :param start: The starting time for which to pull data. Note that Seeq will potentially return one additional
    row that is earlier than this time (if it exists), as a "bounding value" for interpolation purposes. This
    argument must be a string that pd.to_datetime() can parse, or a pd.Timestamp. If not provided, 'start' will
    default to 'end' minus 1 hour.
    :type start: str, pd.Timestamp
    :param end: The end time for which to pull data. Note that Seeq will potentially return one additional
    row that is earlier than this time (if it exists), as a "bounding value" for interpolation purposes. This
    argument must be a string that pd.to_datetime() can accept. If not provided, 'end' will default to now.
    :type end: str, pd.Timestamp
    :param grid: A period to use for interpolation such that all returned samples have the same timestamps.
    Interpolation will be applied at the server to achieve this. If grid=None is specified, no interpolation will occur
    and each signal's samples will be returned untouched. Where timestamps don't match, NaNs will be present within a
    row.
    :type grid: str, None
    :param header: The metadata property to use as the header of each column. Common values would be 'ID' or 'Name".
    Defaults to '__auto__', which concatenates Path and Name if they are present.
    :type header: str
    :param group_by: The name of a column or list of columns for which to group by. Often necessary when pulling data
    across assets: When you want header='Name', you typically need group_by=['Path', 'Asset']
    :type group_by: str, list(str)
    :param capsules_as: If 'auto' (default), returns capsules as a time series of 0 or 1 when signals are also
    present in the items argument, or returns capsules as individual rows if no signals are present. 'signals' or
    'capsules' forces the output to the former or the latter, if possible.
    :type capsules_as: str
    :param tz_convert: The time zone in which to return all timestamps. If the time zone string is not recognized,
    the list of supported time zone strings will be returned in the exception text.
    :type tz_convert: str
    :param calculation: When applying a calculation across assets, the 'calculation' argument must be a one-row
    DataFrame (or a Series) and the 'items' argument must be full of assets. When applying a calculation to a
    signal/condition/scalar, calculation must be a string with a signal variable in it: $signal, $condition or $scalar.
    :type calculation: str, pd.DataFrame
    :param bounding_values: If True, extra 'bounding values' will be returned before/after the specified query range
    for the purposes of assisting with interpolation to the edges of the range or, in the case of Step or PILinear
    interpolation methods, interpolating to 'now' when appropriate.
    :type bounding_values: bool
    :param errors: If 'raise' (default), any errors encountered will cause an exception. If 'catalog', errors will be
    added to a 'Result' column in the status.df DataFrame (errors='catalog' must be combined with status=<Status
    object>).
    :type errors: str
    :param quiet: If True, suppresses progress output.
    :type quiet: bool
    :param status: If supplied, this Status object will be updated as the command progresses.
    :type status: Status
    :return: A DataFrame with the requested data.
    :rtype: pd.DataFrame
    """
    if errors == 'catalog' and status is None:
        raise RuntimeError("status argument must be a valid Status object when errors='catalog'")

    status = Status.validate(status, quiet)
    _common.validate_timezone_arg(tz_convert)
    _common.validate_errors_arg(errors)

    if not (isinstance(items, (pd.DataFrame, pd.Series))):
        raise RuntimeError('items argument must be a pandas.DataFrame or pandas.Series')

    if not items.index.is_unique:
        raise RuntimeError("The items DataFrame's index must be unique. Use reset_index(drop=True, inplace=True) "
                           "before passing in to spy.pull().")

    if isinstance(calculation, pd.DataFrame):
        if len(calculation) != 1:
            raise RuntimeError("When applying a calculation across assets, calculation argument must be a one-row "
                               "DataFrame, or a Series. When applying a calculation to a signal/condition/scalar, "
                               'calculation must be a string with a signal variable in it: $signal, $condition or '
                               '$scalar.')

        calculation = calculation.iloc[0]

    if isinstance(items, pd.Series):
        items = pd.DataFrame().append(items)

    if capsules_as not in ['auto', 'capsules', 'signals']:
        raise RuntimeError("capsules_as must be one of 'auto', 'capsules', 'signals'")

    if group_by:
        if isinstance(group_by, str):
            group_by = [group_by]
        if not isinstance(group_by, list):
            raise RuntimeError('group_by argument must be a str or list(str)')
        if not all(col in items.columns for col in group_by):
            raise RuntimeError('group_by columns %s not present in query DataFrame' % group_by)

    # noinspection PyUnresolvedReferences
    pd_start = pd.to_datetime(start)  # type: pd.Timestamp
    # noinspection PyUnresolvedReferences
    pd_end = pd.to_datetime(end)  # type: pd.Timestamp

    if pd_end is None:
        pd_end = pd.to_datetime(pd.datetime.now())
        if pd_start is not None and pd_start > pd_end:
            pd_end = pd_start + pd.Timedelta(hours=1)

    if pd_start is None:
        pd_start = pd.to_datetime(pd.datetime.now()) if pd_end is None else pd_end
        pd_start = pd_start - pd.Timedelta(hours=1)

    status_columns = list()
    if 'ID' in items:
        status_columns.append('ID')
    if 'Path' in items:
        status_columns.append('Path')
    if 'Asset' in items:
        status_columns.append('Asset')
    if 'Name' in items:
        status_columns.append('Name')

    status.df = items[status_columns].copy()
    status.df['Count'] = 0
    status.df['Time'] = 0
    status.df['Result'] = 'Pulling'

    status.update('Pulling data from %s to %s' % (pd_start, pd_end), Status.RUNNING)

    items_api = ItemsApi(_login.client)
    formulas_api = FormulasApi(_login.client)

    query_df = items  # type: pd.DataFrame
    output_df = pd.DataFrame()
    at_least_one_signal = False
    column_names = dict()
    final_column_names = list()
    for phase in ['signals', 'conditions', 'scalars', 'final']:
        threads = list()
        try:
            pulled_series = queue.Queue()
            status_updates = queue.Queue()

            def _drain_status_updates():
                while True:
                    try:
                        _index, _message, _exception, _count, _time = status_updates.get_nowait()

                        if _exception and errors == 'raise':
                            raise _exception

                        status.df.at[_index, 'Result'] = _message
                        status.df.at[_index, 'Count'] = _count
                        status.df.at[_index, 'Time'] = _time
                    except queue.Empty:
                        break

                status.update('Pulling from <strong>%s</strong> to <strong>%s</strong>' % (pd_start, pd_end),
                              Status.RUNNING)

            for index, row in query_df.iterrows():
                # noinspection PyBroadException
                try:
                    output_df, at_least_one_signal = _process_query_row(
                        _drain_status_updates, at_least_one_signal, calculation, capsules_as,
                        column_names, final_column_names, formulas_api, grid, header, index,
                        items_api, output_df, pd_start, pd_end, phase, pulled_series, row,
                        status, status_updates, threads, tz_convert, bounding_values, group_by)

                except BaseException:
                    if errors == 'raise':
                        raise

                    status.df.at[index, 'Result'] = _common.format_exception()

            still_running = True
            while still_running:
                _drain_status_updates()

                still_running = False
                for _, thread in threads:
                    thread.join(0.1)

                    if thread.is_alive():
                        still_running = True
                        break

            _drain_status_updates()

            # noinspection PyUnresolvedReferences
            for index, item_name, series in list(pulled_series.queue):
                item_row = query_df.loc[index]
                join_df = pd.DataFrame({item_name: series})
                if group_by is None:
                    if item_name in output_df.columns:
                        raise RuntimeError('Column headers not unique. 2+ instances of "%s" found. Use header="ID" '
                                           'to guarantee uniqueness, or alternatively try group_by=["Path", "Asset"] '
                                           'if you are using an asset tree.' % item_name)
                else:
                    for group_column in group_by:
                        join_df[group_column] = item_row[group_column]

                    join_df.set_index(group_by, inplace=True, append=True)

                output_df = join_df if len(output_df) == 0 else output_df.combine_first(join_df)

        except BaseException as e:
            for stop_event, _ in threads:
                stop_event.set()

            status.exception(e)

            if isinstance(e, KeyboardInterrupt):
                return None

            raise

    status.update('Pull successful from <strong>%s</strong> to <strong>%s</strong>' % (pd_start, pd_end),
                  Status.SUCCESS)

    # Ensures that the order of the columns matches the order in the metadata
    output_df = output_df[final_column_names]

    return output_df


def _process_query_row(_drain_status_updates, at_least_one_signal, calculation, capsules_as, column_names,
                       final_column_names, formulas_api, grid, header, index, items_api, output_df, pd_start, pd_end,
                       phase, pulled_series, row, status, status_updates, threads, tz_convert, bounding_values,
                       group_by):
    if phase == 'signals' and not _common.present(row, 'ID'):
        status.df.at[index, 'Result'] = 'No "ID" column - skipping'
        return output_df, at_least_one_signal

    item_id, item_name, item_type = _get_item_details(header, items_api, row)

    index_to_use = output_df.index
    if group_by and isinstance(output_df.index, pd.MultiIndex):
        index_query = ' and '.join([("%s == '%s'" % (g, row[g])) for g in group_by])
        index_to_use = output_df.query(index_query).index.levels[0]

    calculation_to_use = calculation
    if item_type == 'Asset':
        if calculation is None:
            raise RuntimeError('To pull data for an asset, you must provide a "calculate" argument whose '
                               'value is the metadata of a calculation that is based on a single asset.')

        swap_input = SwapInputV1()
        swap_input.swap_in = item_id
        calc_item_id, _, item_type = _get_item_details(header, items_api, calculation)

        item_dependency_output = items_api.get_formula_dependencies(
            id=calc_item_id)  # type: ItemDependencyOutputV1

        unique_assets = set(dep.ancestors[-1].id
                            for dep in item_dependency_output.dependencies
                            if len(dep.ancestors) > 0)

        if len(unique_assets) != 1:
            raise RuntimeError('To pull data for an asset, the "calculate" parameter must be a calculated '
                               'item that involves only one asset.')

        swap_input.swap_out = unique_assets.pop()

        swapped_item = items_api.find_swap(id=calc_item_id, body=[swap_input])  # type: ItemPreviewV1

        item_id = swapped_item.id

        # Don't try to apply a calculation later, we've already done it via our swap activity
        calculation_to_use = None

    if phase == 'signals' and \
            'Signal' not in item_type and 'Condition' not in item_type and 'Scalar' not in item_type:
        status.df.at[index, 'Result'] = 'Not a Signal, Condition or Scalar - skipping'
        return output_df, at_least_one_signal

    if 'Signal' in item_type:
        at_least_one_signal = True

    if phase == 'signals' and 'Signal' in item_type:

        parameters = ['signal=%s' % item_id]
        if calculation_to_use is not None:
            formula = calculation_to_use
        else:
            formula = '$signal'

        if grid:
            formula = 'resample(%s, %s)' % (formula, grid)

        stop_event = threading.Event()
        thread = threading.Thread(target=_pull_signal, args=(formulas_api, formula, parameters, item_id,
                                                             item_name, pulled_series, pd_start, pd_end,
                                                             tz_convert, column_names, stop_event,
                                                             status_updates, index, bounding_values))

        thread.start()
        threads.append((stop_event, thread))

    elif phase == 'conditions' and 'Condition' in item_type:
        if capsules_as == 'capsules' and at_least_one_signal:
            raise RuntimeError('Pull cannot include signals when conditions present and "capsules_as" '
                               'parameter is "capsules"')

        if capsules_as == 'auto':
            capsules_as = 'signals' if at_least_one_signal else 'capsules'

        if capsules_as == 'signals' and not at_least_one_signal:
            if grid is None:
                raise RuntimeError(
                    "Pull cannot include conditions when no signals present with capsules_as="
                    "'capsules' and grid=None")

            placeholder_item_name = '__placeholder__'
            _pull_signal(formulas_api, '0.toSignal(%s)' % grid, list(), placeholder_item_name,
                         placeholder_item_name, pulled_series, pd_start, pd_end, tz_convert, dict(),
                         threading.Event())

            _, _, series = pulled_series.get(True, 30)
            output_df[placeholder_item_name] = series
            at_least_one_signal = True
            index_to_use = series.index

        parameters = ['condition=%s' % item_id]
        if calculation_to_use is not None:
            formula = calculation_to_use
        else:
            formula = '$condition'

        output_df = _pull_condition(capsules_as, formulas_api, formula, parameters, item_id,
                                    item_name, output_df, pulled_series, pd_start, pd_end, tz_convert,
                                    column_names, index, index_to_use, status, _drain_status_updates)

    elif phase == 'scalars' and 'Scalar' in item_type:
        parameters = ['scalar=%s' % item_id]
        if calculation_to_use is not None:
            formula = calculation_to_use
        else:
            formula = '$scalar'

        _pull_scalar(formulas_api, formula, parameters, item_id, item_name, output_df, column_names, index,
                     index_to_use, pulled_series, status, _drain_status_updates)

    elif phase == 'final':
        if item_id in column_names:
            for column_name in column_names[item_id]:
                if column_name not in final_column_names:
                    final_column_names.append(column_name)

    return output_df, at_least_one_signal


def _convert_column_timezone(ts_column, tz):
    ts_column = ts_column.tz_localize('UTC')
    return ts_column.tz_convert(tz) if tz else ts_column


def _pull_condition(capsules_as, formulas_api, formula, parameters, item_id, item_name, output_df, pulled_series,
                    pd_start, pd_end, tz, column_names, index, index_to_use, status, _drain_status_updates):
    # noinspection PyBroadException
    try:
        timer = _common.timer_start()
        capsule_count = 0
        current_start = pd_start.value
        offset = 0
        while True:
            formula_run_output, _, http_headers = formulas_api.run_formula_with_http_info(
                formula=formula,
                parameters=parameters,
                start='%d ns' % current_start,
                end='%d ns' % pd_end.value,
                offset=offset,
                limit=_common.DEFAULT_PULL_PAGE_SIZE)  # type: FormulaRunOutputV1

            next_start = current_start
            capsules_output = formula_run_output.capsules  # type: CapsulesOutputV1
            check_for_dupes = True

            columns = dict()
            if capsules_as == 'signals':
                columns[item_name] = pd.Series(0, index_to_use)
                for capsule in capsules_output.capsules:
                    pd_capsule_start = _common.convert_to_timestamp(
                        capsule.start if capsule.start is not None else 0, tz)
                    pd_capsule_end = _common.convert_to_timestamp(
                        capsule.end if capsule.end is not None else 7258118400000000000, tz)
                    columns[item_name].loc[(columns[item_name].index >= pd_capsule_start) &
                                           (columns[item_name].index <= pd_capsule_end)] = 1

                    for prop in capsule.properties:  # type: ScalarPropertyV1
                        colname = '%s - %s' % (item_name, prop.name)
                        if colname not in columns:
                            columns[colname] = pd.Series(np.nan, index_to_use)
                        columns[colname].loc[(columns[colname].index >= pd_capsule_start) &
                                             (columns[colname].index <= pd_capsule_end)] = prop.value

                column_names[item_id] = list()
                for col, series in columns.items():
                    pulled_series.put((index, col, series))
                    column_names[item_id].append(col)
            else:
                capsule_df_rows = list()

                for capsule in capsules_output.capsules:
                    column_names[item_id] = ['Condition', 'Capsule Start', 'Capsule End']
                    if check_for_dupes and \
                            'Condition' in output_df and \
                            'Capsule Start' in output_df and \
                            'Capsule End' in output_df and \
                            len(output_df.loc[(output_df['Condition'] == item_name) &
                                              (output_df['Capsule Start'] == _common.convert_to_timestamp(capsule.start,
                                                                                                          tz)) &
                                              (output_df['Capsule End'] == _common.convert_to_timestamp(capsule.end,
                                                                                                        tz))]):
                        # This can happen as a result of pagination
                        continue

                    check_for_dupes = False

                    capsule_dict = {
                        'Condition': item_name,
                        'Capsule Start': _common.convert_to_timestamp(capsule.start, tz),
                        'Capsule End': _common.convert_to_timestamp(capsule.end, tz)
                    }

                    for prop in capsule.properties:  # type: ScalarPropertyV1
                        capsule_dict[prop.name] = prop.value
                        column_names[item_id].append(prop.name)

                    capsule_df_rows.append(capsule_dict)

                    if not pd.isna(capsule.start) and capsule.start > next_start:
                        next_start = capsule.start

                output_df = output_df.append(capsule_df_rows)

            # Note that capsule_count here can diverge from the exact count in the output due to pagination
            capsule_count += len(capsules_output.capsules)

            if len(capsules_output.capsules) < _common.DEFAULT_PULL_PAGE_SIZE:
                break

            if next_start == current_start:
                # This can happen if the page is full of capsule that all have the same start time
                offset += _common.DEFAULT_PULL_PAGE_SIZE
            else:
                offset = 0

            current_start = next_start

            status.df.at[index, 'Result'] = 'Pulling %s' % _common.convert_to_timestamp(current_start, tz)
            status.df.at[index, 'Count'] = capsule_count
            status.df.at[index, 'Time'] = _common.timer_elapsed(timer)

            _drain_status_updates()

        status.df.at[index, 'Result'] = 'Success'
        status.df.at[index, 'Count'] = capsule_count
        status.df.at[index, 'Time'] = _common.timer_elapsed(timer)

    except BaseException:
        status.df.at[index, 'Result'] = _common.format_exception()

    return output_df


def _pull_signal(formulas_api, formula, parameters, item_id, item_name, pulled_series, pd_start, pd_end, tz,
                 column_names, stop_event=None, status_updates=None, index=None, bounding_values=False):
    # noinspection PyBroadException
    try:
        series = pd.Series()
        timer = _common.timer_start()
        current_start = pd_start
        last_key = 0
        while not stop_event.is_set():
            formula_run_output, _, http_headers = formulas_api.run_formula_with_http_info(
                formula=formula,
                parameters=parameters,
                start='%d ns' % current_start.value,
                end='%d ns' % pd_end.value,
                offset=0,
                limit=_common.DEFAULT_PULL_PAGE_SIZE)  # type: FormulaRunOutputV1

            series_samples_output = formula_run_output.samples  # type: SeriesSamplesOutputV1

            def _keep_sample(_sample_output):
                if _sample_output.key <= last_key:
                    return False

                if bounding_values:
                    return True

                if _sample_output.key < pd_start.value:
                    return False

                if _sample_output.key > pd_end.value:
                    return False

                return True

            time_index = _convert_column_timezone(pd.DatetimeIndex([sample_output.key for sample_output in
                                                                    series_samples_output.samples if
                                                                    _keep_sample(sample_output)]), tz)

            series = series.append(pd.Series([sample_output.value for sample_output in
                                              series_samples_output.samples if _keep_sample(sample_output)],
                                             index=time_index))

            if len(series_samples_output.samples) < _common.DEFAULT_PULL_PAGE_SIZE:
                break

            if len(series) > 0:
                last_key = series.index[-1].value

            if time_index[-1].value > current_start.value:
                current_start = time_index[-1]

            if status_updates is not None:
                status_updates.put((index, 'Pulling: %s' % str(current_start), None,
                                    len(series), _common.timer_elapsed(timer)))

        column_names[item_id] = [item_name]
        if status_updates is not None:
            status_updates.put((index, 'Success', None, len(series), _common.timer_elapsed(timer)))
        pulled_series.put((index, item_name, series))

    except BaseException as e:
        if status_updates is not None:
            status_updates.put((index, _common.format_exception(), e, None, None))


def _pull_scalar(formulas_api, formula, parameters, item_id, item_name, output_df, column_names, index,
                 index_to_use, pulled_series, status, _drain_status_updates):
    timer = _common.timer_start()

    formula_run_output, _, http_headers = formulas_api.run_formula_with_http_info(
        formula=formula,
        parameters=parameters)  # type: FormulaRunOutputV1

    if len(output_df.index) == 0:
        output_df.at[0, item_name] = formula_run_output.scalar.value
    else:
        pulled_series.put((index, item_name, pd.Series(formula_run_output.scalar.value, index_to_use)))

    column_names[item_id] = [item_name]

    status.df.at[index, 'Result'] = 'Success'
    status.df.at[index, 'Count'] = 1
    status.df.at[index, 'Time'] = _common.timer_elapsed(timer)


def _get_item_details(header, items_api, row):
    item_id = _common.get(row, 'ID')
    item = None

    if _common.present(row, 'Type'):
        item_type = _common.get(row, 'Type')
    else:
        item = items_api.get_item_and_all_properties(id=item_id)  # type: ItemOutputV1
        item_type = item.type

    if header.upper() == 'ID':
        item_name = item_id
    elif _common.present(row, header):
        item_name = _common.get(row, header)
    else:
        if not item:
            item = items_api.get_item_and_all_properties(id=item_id)  # type: ItemOutputV1

        item_name = ''
        if header == '__auto__' and _common.present(row, 'Path'):
            item_name = _common.get(row, 'Path') + ' >> '
            if _common.present(row, 'Asset'):
                item_name += _common.get(row, 'Asset') + ' >> '

        if header in ['__auto__', 'Name']:
            item_name += item.name
        elif header == 'Description':
            item_name += item.description
        else:
            prop = [p.value for p in item.properties if p.name == header]
            if len(prop) == 0:
                item_name += item_id
            else:
                item_name += prop[0]

    return item_id, item_name, item_type
