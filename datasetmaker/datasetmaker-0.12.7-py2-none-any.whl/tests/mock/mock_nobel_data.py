# mypy: allow-untyped-defs


class MockResponse:
    def json(self):
        return data


data = {'laureates': [
    {
        'id': '1',
        'firstname': 'Wilhelm Conrad',
        'surname': 'Röntgen',
        'born': '1845-03-27',
        'died': '1923-02-10',
        'bornCountry': 'Prussia (now Germany)',
        'bornCountryCode': 'DE',
        'bornCity': 'Lennep (now Remscheid)',
        'diedCountry': 'Germany',
        'diedCountryCode': 'DE',
        'diedCity': 'Munich',
        'gender': 'male',
        'prizes': [
            {
                'year': '1901',
                'category': 'physics',
                'share': '1',
                'motivation': '"in recognition of the extraordinary services he has rendered by the discovery of the remarkable rays subsequently named after him"',
                'affiliations': [
                    {
                        'name': 'Munich University',
                        'city': 'Munich',
                        'country': 'Germany'}]
            }]
    },
    {
        'id': '2',
        'firstname': 'Hendrik Antoon',
        'surname': 'Lorentz',
        'born': '1853-07-18',
        'died': '1928-02-04',
        'bornCountry': 'the Netherlands',
        'bornCountryCode': 'NL',
        'bornCity': 'Arnhem',
        'diedCountry': 'the Netherlands',
        'diedCountryCode': 'NL',
        'gender': 'male',
        'prizes': [
            {
                'year': '1902',
                'category': 'physics',
                'share': '2',
                'motivation': '"in recognition of the extraordinary service they rendered by their researches into the influence of magnetism upon radiation phenomena"',
                'affiliations': [
                    {
                        'name': 'Leiden University',
                        'city': 'Leiden',
                        'country': 'the Netherlands'
                    }]
            }]
    },
    {
        'id': '967',
        'firstname': 'Nadia',
        'surname': 'Murad',
        'born': '0000-00-00',
        'died': '0000-00-00',
        'gender': 'female',
        'prizes': [{
            'year': '2018',
            'category': 'peace',
            'share': '2',
            'motivation': '"for their efforts to end the use of sexual violence as a weapon of war and armed conflict"',
            'affiliations': [[]]
        }]}
]}
