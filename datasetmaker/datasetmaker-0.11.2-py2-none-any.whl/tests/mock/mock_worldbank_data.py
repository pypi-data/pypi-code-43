# type: ignore


class MockResponse:
    def json(self):
        return mortality_rate


mortality_rate = [{
    'page': 2,
    'pages': 6,
    'per_page': 50,
    'total': 264,
    'sourceid': '2',
    'lastupdated': '2019-06-28'
},
    [{
        'indicator': {
            'id': 'SP.DYN.IMRT.IN',
            'value': 'Mortality rate, infant (per 1,000 live births)'
        },
        'country': {
            'id': 'AS',
            'value': 'American Samoa'
        },
        'countryiso3code': 'ASM',
        'date': '2017',
        'value': None,
        'unit': '',
        'obs_status': '',
        'decimal': 0
    },
        {
            'indicator': {
                'id': 'SP.DYN.IMRT.IN',
                'value': 'Mortality rate, infant (per 1,000 live births)'
            },
            'country': {
                'id': 'AD',
                'value': 'Andorra'
            },
            'countryiso3code': 'AND',
            'date': '2017',
            'value': 3.2,
            'unit': '',
            'obs_status': '',
            'decimal': 0
    },
        {
            'indicator': {
                'id': 'SP.DYN.IMRT.IN',
                'value': 'Mortality rate, infant (per 1,000 live births)'
            },
            'country': {
                'id': 'AO',
                'value': 'Angola'
            },
            'countryiso3code': 'AGO',
            'date': '2017',
            'value': 53.8,
            'unit': '',
            'obs_status': '',
            'decimal': 0
    },
        {
            'indicator': {
                'id': 'SP.DYN.IMRT.IN',
                'value': 'Mortality rate, infant (per 1,000 live births)'
            },
            'country': {
                'id': 'AG',
                'value': 'Antigua and Barbuda'
            },
            'countryiso3code': 'ATG',
            'date': '2017',
            'value': 5.4,
            'unit': '',
            'obs_status': '',
            'decimal': 0
    },
        {
            'indicator': {
                'id': 'SP.DYN.IMRT.IN',
                'value': 'Mortality rate, infant (per 1,000 live births)'
            },
            'country': {
                'id': 'AR',
                'value': 'Argentina'
            },
            'countryiso3code': 'ARG',
            'date': '2017',
            'value': 9.2,
            'unit': '',
            'obs_status': '',
            'decimal': 0
    },
]]
