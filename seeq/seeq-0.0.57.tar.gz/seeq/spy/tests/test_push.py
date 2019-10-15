import os
import pytest

import pandas as pd

from seeq import spy

from . import test_common


def setup_module():
    test_common.login()


@pytest.mark.system
def test_push_signal():
    push_df = pd.DataFrame(pd.Series([
        1,
        2,
        3
    ], index=[
        pd.to_datetime('2019-01-01'),
        pd.to_datetime('2019-01-02'),
        pd.to_datetime('2019-01-03')
    ]), columns=['My Signal'])

    spy.push(push_df)


@pytest.mark.system
def test_bad_calculation():
    with pytest.raises(RuntimeError):
        spy.push(metadata=pd.DataFrame([{
            'Type': 'Signal',
            'Name': 'Bad Calc',
            'Formula': 'hey(nothing)'
        }]))


@pytest.mark.system
def test_push_calculated_signal():
    area_a_signals = spy.search({
        'Path': 'Example >> Cooling Tower 1 >> Area A'
    })

    dew_point_calc = spy.push(metadata=pd.DataFrame([{
        'Type': 'Signal',
        'Name': 'Dew Point',
        # From https://iridl.ldeo.columbia.edu/dochelp/QA/Basic/dewpoint.html
        'Formula': "$T - ((100 - $RH.setUnits(''))/5)",
        'Formula Parameters': {
            '$T': area_a_signals[area_a_signals['Name'] == 'Temperature'],
            '$RH': area_a_signals[area_a_signals['Name'] == 'Relative Humidity']
        }
    }]))

    assert len(dew_point_calc) == 1
    assert 'ID' in dew_point_calc


@pytest.mark.system
def test_push_signal_with_metadata():
    witsml_folder = os.path.dirname(__file__)
    witsml_file = '011_02_0.csv'
    witsml_df = pd.read_csv(os.path.join(witsml_folder, witsml_file))
    timestamp_column = witsml_df.columns[0]
    witsml_df = pd.read_csv(os.path.join(witsml_folder, witsml_file), parse_dates=[timestamp_column])
    witsml_df = witsml_df.drop(list(witsml_df.filter(regex='.*Unnamed.*')), axis=1)
    witsml_df = witsml_df.dropna(axis=1, how='all')
    witsml_df = witsml_df.set_index(timestamp_column)

    metadata = pd.DataFrame({'Header': witsml_df.columns.values})
    metadata['Type'] = 'Signal'
    metadata['Tag'] = metadata['Header'].str.extract(r'(.*)\(')
    metadata['Value Unit Of Measure'] = metadata['Header'].str.extract(r'\((.*)\)')
    metadata['File'] = witsml_file
    metadata['Well Number'] = metadata['File'].str.extract(r'(\d+)_\d+_\d+\.csv')
    metadata['Wellbore ID'] = metadata['File'].str.extract(r'\d+_(\d+)_\d+\.csv')

    metadata = metadata.set_index('Header')

    # Without a Name column, we expect the push metadata to fail
    with pytest.raises(RuntimeError):
        spy.push(data=witsml_df, metadata=metadata)

    metadata['Name'] = "Well_" + metadata['Well Number'] + "_" + "Wellbore_" + \
                       metadata['Wellbore ID'] + "_" + metadata['Tag']

    push_results_df = spy.push(data=witsml_df, metadata=metadata)

    search_results_df = spy.search(push_results_df.iloc[0])

    assert len(search_results_df) == 1
    assert search_results_df.iloc[0]['Name'] == metadata.iloc[0]['Name']
    assert 'Push Result' not in search_results_df
    assert 'Push Count' not in search_results_df
    assert 'Push Time' not in search_results_df

    pull_results_df = spy.pull(search_results_df,
                               start='2016-07-25T15:00:00.000-07:00',
                               end='2019-07-25T17:00:00.000-07:00',
                               grid=None)

    assert len(pull_results_df) == 999

    # noinspection PyUnresolvedReferences
    assert (witsml_df.index == pull_results_df.index).all()

    witsml_list = witsml_df['BITDEP(ft)'].tolist()
    pull_list = pull_results_df['Well_011_Wellbore_02_BITDEP'].tolist()
    assert witsml_list == pull_list


@pytest.mark.system
def test_push_capsules():
    capsule_data = pd.DataFrame([{
        'Capsule Start': pd.to_datetime('2019-01-10T09:00:00.000Z'),
        'Capsule End': pd.to_datetime('2019-01-10T17:00:00.000Z'),
        'Operator On Duty': 'Mark'
    }, {
        'Capsule Start': pd.to_datetime('2019-01-11T09:00:00.000Z'),
        'Capsule End': pd.to_datetime('2019-01-11T17:00:00.000Z'),
        'Operator On Duty': 'Hedwig'
    }])

    try:
        spy.push(data=capsule_data,
                 metadata=pd.DataFrame([{
                     'Name': 'Operator Shifts',
                     'Type': 'Condition'
                 }]))

        assert False, 'Without a Maximum Duration, we expect the push to fail'

    except RuntimeError as e:
        assert 'Maximum Duration' in str(e)

    push_result = spy.push(data=capsule_data,
                           metadata=pd.DataFrame([{
                               'Name': 'Operator Shifts',
                               'Type': 'Condition',
                               'Maximum Duration': '2d'
                           }]))

    assert len(push_result) == 1
    assert push_result.iloc[0]['Name'] == 'Operator Shifts'
    assert push_result.iloc[0]['Push Count'] == 2

    pull_result = spy.pull(push_result, start='2019-01-01T09:00:00.000Z', end='2019-02-01T09:00:00.000Z')

    assert len(pull_result) == 2
    assert pull_result.iloc[0]['Condition'] == 'Operator Shifts'
    assert pull_result.iloc[0]['Capsule Start'] == pd.to_datetime('2019-01-10T09:00:00.000Z')
    assert pull_result.iloc[0]['Capsule End'] == pd.to_datetime('2019-01-10T17:00:00.000Z')
    assert pull_result.iloc[0]['Operator On Duty'] == 'Mark'
    assert pull_result.iloc[1]['Condition'] == 'Operator Shifts'
    assert pull_result.iloc[1]['Capsule Start'] == pd.to_datetime('2019-01-11T09:00:00.000Z')
    assert pull_result.iloc[1]['Capsule End'] == pd.to_datetime('2019-01-11T17:00:00.000Z')
    assert pull_result.iloc[1]['Operator On Duty'] == 'Hedwig'
