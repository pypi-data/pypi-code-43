import pytest
import sys

from seeq import spy
from seeq.spy.assets import Asset, Mixin

from . import test_common


def setup_module():
    test_common.login()


class HVAC(Asset):

    @Asset.Attribute()
    def Temperature(self, metadata):
        # We use simple Pandas syntax to select for a row in the DataFrame corresponding to our desired tag
        return metadata[metadata['Name'].str.endswith('Temperature')]

    @Asset.Attribute()
    def Relative_Humidity(self, metadata):
        # All Attribute functions must take (self, metadata) as parameters
        return metadata[metadata['Name'].str.contains('Humidity')]


class Compressor(Asset):

    @Asset.Attribute()
    def Power(self, metadata):
        return metadata[metadata['Name'].str.endswith('Power')]


class Airflow_Attributes(Mixin):
    @Asset.Attribute()
    def Airflow_Rate(self, metadata):
        return {
            'Type': 'Signal',
            'Formula': 'sinusoid()'
        }


class HVAC_With_Calcs(HVAC):

    @Asset.Attribute()
    def Temperature_Rate_Of_Change(self, metadata):
        return {
            'Type': 'Signal',

            # This formula will give us a nice derivative in F/h
            'Formula': '$temp.lowPassFilter(150min, 3min, 333).derivative() * 3600 s/h',

            'Formula Parameters': {
                # We can reference the base class' Temperature attribute here as a dependency
                '$temp': self.Temperature(metadata),
            }
        }

    @Asset.Attribute()
    def Too_Hot(self, metadata):
        return {
            'Type': 'Condition',
            'Formula': '$temp.valueSearch(isGreaterThan($threshold))',
            'Formula Parameters': {
                '$temp': self.Temperature(metadata),

                # We can also reference other attributes in this derived class
                '$threshold': self.Hot_Threshold(metadata)
            }
        }

    @Asset.Attribute()
    def Hot_Threshold(self, metadata):
        return {
            'Type': 'Scalar',
            'Formula': '80F'
        }

    @Asset.Attribute()
    def Equipment_ID(self, metadata):
        return {
            'Type': 'Scalar',
            'Formula': '"%s"' % self.asset_definition['Name']
        }

    # Designating a function as a Component allows you to include a child asset with its own set of attributes
    @Asset.Component()
    def Compressor(self, metadata):
        return Compressor(parent=self)

    @Asset.Component()
    def Pump(self, metadata):
        return [
            {
                'Name': 'Pump Volume',
                'Type': 'Scalar',
                'Formula': '1000L'
            },
            {
                'Name': 'Pump Voltage',
                'Type': 'Scalar',
                'Formula': '110V'
            }
        ]

    @Asset.Component()
    def Airflow(self, metadata):
        return Airflow_Attributes(self)


def build_and_push_hvac_tree():
    hvac_metadata_df = get_hvac_metadata_df()
    build_df = spy.assets.build(HVAC_With_Calcs, hvac_metadata_df)
    spy.push(metadata=build_df, errors='catalog')


def get_hvac_metadata_df():
    hvac_metadata_df = spy.search({
        'Name': 'Area ?_*',
        'Datasource Class': 'Time Series CSV Files'
    })

    hvac_metadata_df['Build Asset'] = hvac_metadata_df['Name'].str.extract('(Area .)_.*')

    hvac_metadata_df['Build Path'] = 'My HVAC Units >> Facility #1'

    return hvac_metadata_df


@pytest.mark.system
def test_build():
    hvac_metadata_df = get_hvac_metadata_df()

    hvac_metadata_df['Build Template'] = 'HVAC'

    # It won't like the "Build Template" column since we're specifying the HVAC class directly
    with pytest.raises(RuntimeError):
        spy.assets.build(HVAC, hvac_metadata_df)

    hvac_metadata_df = hvac_metadata_df.drop(columns=['Build Template'])
    build_df = spy.assets.build(HVAC, hvac_metadata_df)

    # We'll get an error the first time because Area F doesn't have the signals we need
    with pytest.raises(RuntimeError):
        spy.push(metadata=build_df)

    # Now we'll catalog the errors instead of stopping on them
    spy.push(metadata=build_df, errors='catalog')

    hvac_with_calcs_metadata_df = hvac_metadata_df.copy()

    build_with_calcs_df = spy.assets.build(HVAC_With_Calcs, hvac_with_calcs_metadata_df)

    push_results_df = spy.push(metadata=build_with_calcs_df, errors='catalog')

    errors_df = push_results_df[push_results_df['Push Result'] != 'Success']

    # Should only be 4 errors (associated with Area F)
    assert len(errors_df) == 4

    search_results_df = spy.search({
        'Path': 'My HVAC Units >> Facility #1'
    })

    areas = [
        'Area A',
        'Area B',
        'Area C',
        'Area D',
        'Area E',
        'Area F',
        'Area G',
        'Area H',
        'Area I',
        'Area J',
        'Area K',
        'Area Z',
    ]

    for area in areas:
        assertions = [
            ('My HVAC Units >> Facility #1', area, 'Temperature', 'CalculatedSignal'),
            ('My HVAC Units >> Facility #1', area, 'Temperature Rate Of Change', 'CalculatedSignal'),
            ('My HVAC Units >> Facility #1', area, 'Relative Humidity', 'CalculatedSignal'),
            ('My HVAC Units >> Facility #1', area, 'Too Hot', 'CalculatedCondition'),
            ('My HVAC Units >> Facility #1', area, 'Hot Threshold', 'CalculatedScalar'),
            ('My HVAC Units >> Facility #1', area, 'Pump Voltage', 'CalculatedScalar'),
            ('My HVAC Units >> Facility #1', area, 'Pump Volume', 'CalculatedScalar'),
            ('My HVAC Units >> Facility #1 >> ' + area, 'Compressor', 'Power', 'CalculatedSignal'),
            ('My HVAC Units >> Facility #1', area, 'Airflow Rate', 'CalculatedSignal'),
        ]

        # Area F is special!
        if area == 'Area F':
            assertions = [
                ('My HVAC Units >> Facility #1', area, 'Hot Threshold', 'CalculatedScalar'),
                ('My HVAC Units >> Facility #1', area, 'Pump Voltage', 'CalculatedScalar'),
                ('My HVAC Units >> Facility #1', area, 'Pump Volume', 'CalculatedScalar'),
                ('My HVAC Units >> Facility #1 >> ' + area, 'Compressor', 'Power', 'CalculatedSignal'),
            ]

        for _path, _asset, _name, _type in assertions:
            assertion_df = search_results_df[
                (search_results_df['Path'] == _path) &
                (search_results_df['Asset'] == _asset) &
                (search_results_df['Name'] == _name) &
                (search_results_df['Type'] == _type)]

            assert len(assertion_df) == 1, \
                'Instantiated item not found: %s, %s, %s, %s' % (_path, _asset, _name, _type)


@pytest.mark.system
def test_build_with_module():
    hvac_metadata_df = spy.search({
        'Name': 'Area ?_*',
        'Datasource Class': 'Time Series CSV Files'
    })

    hvac_metadata_df['Build Path'] = 'My HVAC Units >> Facility #2'

    def _template_chooser(name):
        if 'Compressor' in name:
            return 'Compressor'
        else:
            return 'HVAC'

    hvac_metadata_df['Build Template'] = hvac_metadata_df['Name'].apply(_template_chooser)

    hvac_metadata_df['Area'] = hvac_metadata_df['Name'].str.extract('(Area .)_.*')
    hvac_metadata_df['Build Asset'] = hvac_metadata_df['Area'] + ' ' + hvac_metadata_df['Build Template']

    build_df = spy.assets.build(sys.modules[__name__], hvac_metadata_df)

    spy.push(metadata=build_df)

    search_results_df = spy.search({
        'Path': 'My HVAC Units >> Facility #2'
    })

    # There should be a "Area X HVAC" and "Area X Compressor" signals
    assert len(search_results_df) == 57
