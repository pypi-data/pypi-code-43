import pytest

import pandas as pd
import numpy as np

from seeq import spy
from seeq.sdk43 import *
from seeq.sdk43.rest import ApiException

from . import test_common, test_assets

from .._common import Status


def setup_module():
    test_common.login()


@pytest.mark.system
def test_pull_signal_with_grid():
    search_results = spy.search({
        "Path": "Example >> Cooling Tower 1 >> Area A"
    })

    search_results = search_results.loc[
        search_results['Name'].isin(['Compressor Power', 'Compressor Stage'])]

    df = spy.pull(search_results, start='2019-01-01', end='2019-03-07', grid='5min', header='Name',
                  tz_convert='US/Central')

    # We assert an exact value here to draw attention to any changes. The only reason this number should change is if
    # the Example Data changes in some way or there is a (possibly unexpected) change to Spy.
    assert len(df) == 18721

    # Note that the canonical timezone for US/Central appears to be CST
    assert df.index[0].tzname() == 'CST'

    assert isinstance(df.iloc[0]['Compressor Power'], np.float64)
    assert isinstance(df.iloc[0]['Compressor Stage'], np.str)


@pytest.mark.system
def test_pull_signal_no_grid():
    # This test ensures that time series with non-matching timestamps are returned
    # in a DataFrame with index entries properly interleaved and NaNs where one
    # series has a value and one doesn't.

    data1_df = spy.push(pd.DataFrame({'test_pull_signal_no_grid_1': [1, 2, 3]},
                                     index=[
                                         pd.to_datetime('2019-01-01T00:00:00.000Z'),
                                         pd.to_datetime('2019-01-01T01:00:00.000Z'),
                                         pd.to_datetime('2019-01-01T02:00:00.000Z'),
                                     ]))

    data2_df = spy.push(pd.DataFrame({'test_pull_signal_no_grid_2': [10, 20, 30]},
                                     index=[
                                         pd.to_datetime('2019-01-01T00:10:00.000Z'),
                                         pd.to_datetime('2019-01-01T01:10:00.000Z'),
                                         pd.to_datetime('2019-01-01T02:10:00.000Z'),
                                     ]))

    data3_df = spy.push(pd.DataFrame({'test_pull_signal_no_grid_3': [100, 200, 300]},
                                     index=[
                                         pd.to_datetime('2019-01-01T00:20:00.000Z'),
                                         pd.to_datetime('2019-01-01T01:20:00.000Z'),
                                         pd.to_datetime('2019-01-01T02:20:00.000Z'),
                                     ]))

    all_df = data1_df.append(data2_df).append(data3_df)

    pull_df = spy.pull(all_df, start='2018-12-01', end='2019-12-01', grid=None)

    expected_df = pd.DataFrame({
        'test_pull_signal_no_grid_1': [1, np.nan, np.nan, 2, np.nan, np.nan, 3, np.nan, np.nan],
        'test_pull_signal_no_grid_2': [np.nan, 10, np.nan, np.nan, 20, np.nan, np.nan, 30, np.nan],
        'test_pull_signal_no_grid_3': [np.nan, np.nan, 100, np.nan, np.nan, 200, np.nan, np.nan, 300]
    }, index=[
        pd.to_datetime('2019-01-01T00:00:00.000Z'),
        pd.to_datetime('2019-01-01T00:10:00.000Z'),
        pd.to_datetime('2019-01-01T00:20:00.000Z'),
        pd.to_datetime('2019-01-01T01:00:00.000Z'),
        pd.to_datetime('2019-01-01T01:10:00.000Z'),
        pd.to_datetime('2019-01-01T01:20:00.000Z'),
        pd.to_datetime('2019-01-01T02:00:00.000Z'),
        pd.to_datetime('2019-01-01T02:10:00.000Z'),
        pd.to_datetime('2019-01-01T02:20:00.000Z')
    ])

    assert pull_df.equals(expected_df)


@pytest.mark.system()
def test_pull_empty_results():
    push_df = spy.push(metadata=pd.DataFrame([{'Name': 'No Data Signal',
                                               'Type': 'Signal'}]))

    pull_df = spy.pull(push_df, start='2019-01-01T00:00:00.000Z', end='2019-01-01T01:00:00.000Z', grid=None)

    assert len(pull_df) == 0

    pull_df = spy.pull(push_df, start='2019-01-01T00:00:00.000Z', end='2019-01-01T01:00:00.000Z')

    assert len(pull_df) == 5
    assert len(pull_df.drop_duplicates()) == 1
    assert pull_df.drop_duplicates().iloc[0]['No Data Signal'] is None


@pytest.mark.system
def test_pull_across_assets():
    search_results = spy.search({
        "Path": "Example >> Cooling Tower 2",
        "Name": "Temperature"
    })

    with pytest.raises(RuntimeError):
        # This will throw an error because header='Name' results in non-unique headers
        spy.pull(search_results, start='2019-01-01', end='2019-01-02', grid='5min', header='Name')

    with pytest.raises(RuntimeError):
        # This will throw an error because there's not column named 'Stuff'
        spy.pull(search_results, start='2019-01-01', end='2019-01-02', grid='5min', tz_convert='US/Central',
                 group_by='Stuff')

    # Pull data twice-- once by pulling Area D Temperature directly, then again by pulling all Cooling Tower 2
    # Temperature signals with a group_by argument
    pull_df1 = spy.pull(search_results[search_results['Asset'] == 'Area D'], start='2019-01-01', end='2019-01-02',
                        grid='5min', tz_convert='US/Central', header='Name')

    pull_df2 = spy.pull(search_results, start='2019-01-01', end='2019-01-02', grid='5min', tz_convert='US/Central',
                        header='Name', group_by=['Path', 'Asset'])

    # Now select only Area D from the second pull, using MultiIndex manipulation
    assert len(pull_df2.columns) == 1
    assert pull_df2.columns[0] == 'Temperature'
    subset = pull_df2.xs('Area D', level='Asset').droplevel('Path')

    # They should be equal!
    assert pull_df1.equals(subset)


@pytest.mark.system
def test_group_by_with_scalars_and_conditions():
    test_assets.build_and_push_hvac_tree()

    search_results = spy.search({
        "Path": "My HVAC Units >> Facility #1 >> Area A",
    }).append(spy.search({
        "Path": "My HVAC Units >> Facility #1 >> Area B",
    })).reset_index(drop=True)

    search_results = search_results[search_results['Type'] != 'Asset']

    pull_df = spy.pull(search_results, start='2019-01-01', end='2019-01-02', grid='5min', tz_convert='US/Central',
                       header='Name', group_by=['Path', 'Asset'])

    # Make sure the Equipment ID string scalar is correct for the individual assets
    area_a_df = pull_df.query("Asset == 'Area A'")
    unique_equipment_id = area_a_df['Equipment ID'].drop_duplicates()
    assert len(unique_equipment_id) == 1
    assert unique_equipment_id.iloc[0] == 'Area A'

    area_b_df = pull_df.query("Asset == 'Area B'")
    unique_equipment_id = area_b_df['Equipment ID'].drop_duplicates()
    assert len(unique_equipment_id) == 1
    assert unique_equipment_id.iloc[0] == 'Area B'

    # The Too Hot condition for Area A and Area B should be different, if we did our bookkeeping correctly.
    too_hot_a = area_a_df['Too Hot'].reset_index(['Path', 'Asset'], drop=True)
    too_hot_b = area_b_df['Too Hot'].reset_index(['Path', 'Asset'], drop=True)
    assert not too_hot_a.equals(too_hot_b)


@pytest.mark.system
def test_bad_timezone():
    with pytest.raises(RuntimeError):
        spy.pull(pd.DataFrame(), tz_convert='CDT')


@pytest.mark.system
def test_no_end_date():
    search_results = spy.search({
        "Name": "Area A_Temperature"
    })

    start = pd.datetime.now() - pd.Timedelta(hours=1)
    df = spy.pull(search_results, start=start, grid=None)

    assert 28 <= len(df) <= 32


@pytest.mark.system
def test_bounding_values():
    metadata_df = pd.DataFrame([{
        'Name': 'test_bounding_values',
        'Type': 'Signal',
        'Interpolation Method': 'step'
    }], index=['test_bounding_values'])

    data_df = pd.DataFrame({'test_bounding_values': [1, 2, 3]},
                           index=[
                               pd.to_datetime('2019-01-01T00:00:00.000Z'),
                               pd.to_datetime('2019-01-01T00:01:00.000Z'),
                               pd.to_datetime('2019-01-01T00:02:00.000Z'),
                           ])

    push_df = spy.push(data=data_df, metadata=metadata_df)

    pull_df = spy.pull(push_df, start=pd.to_datetime('2019-01-01T00:00:50.000Z'),
                       end=pd.to_datetime('2019-01-01T00:01:50.000Z'), grid=None)

    expected_df = pd.DataFrame({
        'test_bounding_values': [2]
    }, index=[
        pd.to_datetime('2019-01-01T00:01:00.000Z')
    ])

    assert pull_df.equals(expected_df)

    pull_df = spy.pull(push_df, start=pd.to_datetime('2019-01-01T00:00:50.000Z'),
                       end=pd.to_datetime('2019-01-01T00:01:50.000Z'), grid=None, bounding_values=True)

    expected_df = pd.DataFrame({
        'test_bounding_values': [1, 2, 3]
    }, index=[
        pd.to_datetime('2019-01-01T00:00:00.000Z'),
        pd.to_datetime('2019-01-01T00:01:00.000Z'),
        pd.to_datetime('2019-01-01T00:02:00.000Z')
    ])

    assert pull_df.equals(expected_df)


@pytest.mark.system
def test_pull_condition_as_capsules():
    search_results = spy.search({
        'Name': 'Area A_Temperature'
    })

    push_df = spy.push(metadata=pd.DataFrame([{
        'Type': 'Condition',
        'Name': 'Hot',
        'Formula': '$a.validValues().valueSearch(isGreaterThan(80))',
        'Formula Parameters': {
            '$a': search_results.iloc[0]
        }
    }]))

    # Some capsules
    pull_df = spy.pull(push_df.iloc[0], start='2019-01-01T00:00:00.000Z', end='2019-06-01T00:00:00.000Z')
    assert 200 <= len(pull_df) <= 230

    # No capsules
    pull_df = spy.pull(push_df.iloc[0], start='2019-01-02T10:00:00.000Z', end='2019-01-02T11:00:00.000Z')
    assert len(pull_df) == 0


@pytest.mark.system
def test_pull_bad_id():
    # Error
    bad_df = pd.DataFrame([{
        'ID': 'BAD!'
    }])
    with pytest.raises(RuntimeError):
        spy.pull(bad_df, start='2019-01-02T10:00:00.000Z', end='2019-01-02T11:00:00.000Z', errors='catalog')

    status = Status()
    pull_df = spy.pull(bad_df,
                       start='2019-01-02T10:00:00.000Z', end='2019-01-02T11:00:00.000Z',
                       errors='catalog', status=status)

    assert len(pull_df) == 0
    assert len(status.df) == 1


@pytest.mark.system
def test_pull_condition_as_signal():
    search_results = spy.search({
        'Name': 'Area A_Temperature'
    })

    push_result = spy.push(metadata=pd.DataFrame([{
        'Type': 'Condition',
        'Name': 'Hot',
        'Formula': '$a.validValues().valueSearch(isGreaterThan(80))',
        'Formula Parameters': {
            '$a': search_results.iloc[0]
        }
    }]))

    pull_result = spy.pull(push_result, start='2019-01-01T00:00:00.000Z', end='2019-01-02T00:00:00.000Z',
                           capsules_as='signals')

    assert len(pull_result) == 97
    assert len(pull_result['Hot'].drop_duplicates()) == 2
    assert pull_result.loc[pd.to_datetime('2019-01-01T00:00:00.000Z')]['Hot'] == 1
    assert pull_result.loc[pd.to_datetime('2019-01-01T12:45:00.000Z')]['Hot'] == 1
    assert pull_result.loc[pd.to_datetime('2019-01-01T13:00:00.000Z')]['Hot'] == 0
    assert pull_result.loc[pd.to_datetime('2019-01-01T19:30:00.000Z')]['Hot'] == 0
    assert pull_result.loc[pd.to_datetime('2019-01-01T19:45:00.000Z')]['Hot'] == 1
    assert pull_result.loc[pd.to_datetime('2019-01-01T20:00:00.000Z')]['Hot'] == 0
    assert pull_result.loc[pd.to_datetime('2019-01-01T20:15:00.000Z')]['Hot'] == 1
    assert pull_result.loc[pd.to_datetime('2019-01-01T22:00:00.000Z')]['Hot'] == 1
    assert pull_result.loc[pd.to_datetime('2019-01-02T00:00:00.000Z')]['Hot'] == 0

    pull_df = search_results.append(push_result, ignore_index=True, sort=True)

    pull_result = spy.pull(pull_df, start='2019-01-01T00:00:00.000Z', end='2019-02-01T00:00:00.000Z',
                           capsules_as='signals')

    for ts, row in pull_result.iterrows():
        if row['Area A_Temperature'] > 80:
            assert row['Hot'] == 1
        else:
            assert row['Hot'] == 0


@pytest.mark.system
def test_pull_swapped_condition():
    search_results = spy.search({
        'Name': 'Temperature',
        'Path': 'Example >> Cooling Tower 1 >> Area A'
    })

    push_result = spy.push(metadata=pd.DataFrame([{
        'Type': 'Signal',
        'Name': 'Temperature Minus 5',
        'Formula': '$a - 5',
        'Formula Parameters': {
            '$a': search_results.iloc[0]
        }
    }]))

    push_result = spy.push(metadata=pd.DataFrame([{
        'Type': 'Condition',
        'Name': 'Cold',
        'Formula': '$a.validValues().valueSearch(isLessThan(80))',
        'Formula Parameters': {
            '$a': push_result.iloc[0]
        }
    }]))

    pull_df = spy.search({
        'Type': 'Asset',
        'Path': 'Example >> Cooling Tower 2'
    })

    # There will be an error related to trying to swap in Area F
    with pytest.raises(ApiException):
        spy.pull(pull_df, start='2019-01-01T00:00:00.000Z', end='2019-06-01T00:00:00.000Z',
                 calculation=push_result)

    status = Status()
    df = spy.pull(pull_df, start='2019-01-01T00:00:00.000Z', end='2019-06-01T00:00:00.000Z',
                  calculation=push_result, capsules_as='capsules', errors='catalog', status=status)

    assert len(df) > 800

    conditions = df['Condition'].drop_duplicates().tolist()

    assert len(conditions) == 2
    assert 'Example >> Cooling Tower 2 >> Area D' in conditions
    assert 'Example >> Cooling Tower 2 >> Area E' in conditions

    errors_df = status.df[status.df['Result'] != 'Success']

    assert len(errors_df) == 1
    assert 'unable to swap out Area A and swap in Area F' in errors_df.iloc[0]['Result']

    df = spy.pull(pull_df, start='2019-01-01T00:00:00.000Z', end='2019-06-01T00:00:00.000Z',
                  calculation=push_result, capsules_as='signals', errors='catalog', status=status)

    assert 'Example >> Cooling Tower 2 >> Area D' in df.columns
    assert 'Example >> Cooling Tower 2 >> Area E' in df.columns
    assert len(df['Example >> Cooling Tower 2 >> Area D'].drop_duplicates().tolist()) == 2
    assert len(df['Example >> Cooling Tower 2 >> Area E'].drop_duplicates().tolist()) == 2


@pytest.mark.system
def test_seeq_server_error():
    datasources_api = DatasourcesApi(test_common.get_client())
    signals_api = SignalsApi(test_common.get_client())

    datasource_input = DatasourceInputV1()
    datasource_input.name = 'Spy Tests'
    datasource_input.description = 'Signals, conditions and scalars from Seeq Data Lab.'
    datasource_input.datasource_class = 'Spy Tests'
    datasource_input.datasource_id = 'Spy Tests'
    datasource_input.stored_in_seeq = False
    datasource_input.additional_properties = [ScalarPropertyV1(name='Expect Duplicates During Indexing', value=True)]
    datasource_output = datasources_api.create_datasource(body=datasource_input)  # type: DatasourceOutputV1

    signals_api.put_signal_by_data_id(datasource_class=datasource_output.datasource_class,
                                      datasource_id=datasource_output.datasource_id,
                                      data_id='A Signal With No Home',
                                      body=SignalInputV1(name='A Signal With No Home'))

    search_results = spy.search({
        'Name': 'A Signal With No Home'
    })

    # noinspection PyBroadException
    try:
        spy.pull(search_results, start='2019-01-01', end='2019-03-07')
    except BaseException as e:
        assert 'The target datasource is disconnected or no longer exists' in str(e)

    status = Status()
    spy.pull(search_results, start='2019-01-01', end='2019-03-07', errors='catalog', status=status)

    assert len(status.df) == 1
    assert 'The target datasource is disconnected or no longer exists' in status.df.iloc[0]['Result']
