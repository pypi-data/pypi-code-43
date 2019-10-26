from .base import ErConnector
from .address import add_address
from .communication import list_communication_methods, add_communication_method


class Seed(object):

    def __init__(self, seed_id, data=None):
        self.seed_id = seed_id
        self.data = None
        if not data:
            # Fetch from remote
            self.refresh()
        else:
            # Allows it to be populated by list_communication_methods without an additional fetch
            self.data = data
            self.populate_from_data()

    def refresh(self):
        self.data = get_seed_by_id(self.seed_id).data
        self.populate_from_data()

    def save(self, **kwargs):
        return update_seed(seed_id=self.seed_id, **kwargs)

    def populate_from_data(self):
        self.first_name = self.data.get('First', None)
        self.last_name = self.data.get('Last', None)
        self.full_name = '{first} {last}'.format(
            first=self.first_name,
            last=self.last_name
        )
        self.title = self.data['Title']

    def add_address(self, type_id,
                    address_line_1,
                    city,
                    state_id,
                    region_id,
                    postal_code,
                    address_line_2=None,
                    country_id=220
                    ):

        return add_address(abouttype_id='Seed', obj_id=self.seed_id, type_id=type_id, address_line_1=address_line_1, city=city, state_id=state_id,
                           region_id=region_id, postal_code=postal_code, address_line_2=address_line_2,
                           country_id=country_id, )

    def list_communication_methods(self):
        return list_communication_methods('Seed', self.seed_id)

    def add_communication_method(self,type_id, value, is_primary=False):
        return add_communication_method(abouttype_id='Seed', obj_id=self.seed_id, type_id=type_id, value=value, is_primary=is_primary )


def create_seed(
        type_id,
        expected_harvest_type,
        adsource_id,
        assign_to,
        first_name=None,
        last_name=None,
        title=None,
        company_name=None,
):
    connector = ErConnector()
    url = 'Seed/'
    data = {
        'TypeID': type_id,
        'ExpectedHarvestType': expected_harvest_type,
        'AdSourceID': adsource_id,
        'AssignTo': assign_to,
        'First': first_name,
        'Last': last_name,
        'Title': title,
        'CompanyName': company_name,
    }
    response = connector.send_request(
        path=url,
        verb='POST',
        payload=data
    )

    return Seed(seed_id=response['ID'], data=response)


def update_seed(seed_id, **kwargs):
    seed = get_seed_by_id(seed_id)
    data = seed.data
    for x in kwargs:
        if x in data.keys():
            data[x] = kwargs[x]
    connector = ErConnector()
    url = 'Seed/{seed_id}'.format(seed_id=seed_id)
    response = connector.send_request(
        path=url,
        verb='PUT',
        payload=data
    )

    return response

def list_seed_types():
    connector = ErConnector()
    url = 'Seed/Type'
    response = connector.send_request(
        path=url,
        verb='GET'
    )

    return response


def get_seed_type_id_by_name(name):
    try:
        return [x for x in list_seed_types() if x['Name'] == name][0]['ID']
    except:
        return None


def get_seed_by_id(id):
    connector = ErConnector()
    url = 'Seed/{id}'.format(id=id)
    response = connector.send_request(
        path=url,
        verb='GET'
    )

    return Seed(seed_id=id, data=response)
