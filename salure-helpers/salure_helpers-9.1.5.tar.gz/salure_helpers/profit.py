import json
import time
from urllib import parse

import requests


class GetConnector:

    def __init__(self, environment, base64token, base_url='rest.afas.online'):
        self.environment = environment
        self.base64token = base64token
        self.base_url = base_url

    def get_metadata(self):
        url = 'https://{}.{}/profitrestservices/metainfo'.format(self.environment, self.base_url)
        authorizationHeader = {'Authorization': 'AfasToken ' + self.base64token}
        vResponse = requests.get(url, headers=authorizationHeader).json()['getConnectors']

        return vResponse
        # for key in vResponse:
        #     if len(key['id']) > 0:
        #         self.get_data(key['id'])

    def get_data(self, connector):
        start = time.time()

        total_response = []
        loop_boolean = True
        no_of_loops = 0
        no_of_results = 0

        while loop_boolean:
            url = 'https://{}.{}/profitrestservices/connectors/{}'.format(self.environment, self.base_url, connector)
            parameters = {"skip": 40000 * no_of_loops, "take": 40000}
            authorization_header = {'Authorization': 'AfasToken {}'.format(self.base64token)}
            response = requests.get(url.encode("utf-8"), parameters, headers=authorization_header)
            if response.status_code == 200:
                response_json = response.json()['rows']
                no_of_loops += 1
                no_of_results += len(response_json)
                loop_boolean = True if len(response_json) == 40000 else False

                print(time.strftime('%H:%M:%S'), 'Got next connector from profit: ', connector, ' With nr of rows: ', no_of_results)
                total_response += response_json
            else:
                return response.text

        return total_response

    def get_filtered_data(self, connector, fields=None, values=None, operators=None, orderbyfields=None):
        """
        Possible filter operators are:
        1: is gelijk aan
        2: is groter of gelijk aan
        3: is kleiner of gelijk aan
        4: is groter dan
        5: is kleiner dan
        6: tekst komt voor in veld	                                Plaats de filterwaarde tussen %..%, bijvoorbeeld %Microsoft%
        7: is niet gelijk aan / Tekst komt niet voor in veld	    Plaats de filterwaarde tussen %..%, bijvoorbeeld %Microsoft%
        8: veld is leeg	                                            Geef filterfieldid, filtervalue en operatortype op. De waarde bij filtervalue is altijd null
        9: veld is niet leeg	                                    Geef filterfieldid, filtervalue en operatortype op
        10 :veld begint met tekst	                                Plaats het teken % aan het einde van de filterwaarde, bijvoorbeeld Microsoft%
        12 :veld begint niet met tekst	                            Plaats het teken % aan het einde van de filterwaarde, bijvoorbeeld Microsoft%
        13 :veld eindigt met tekst	                                Plaats het teken % aan het begin van de filterwaarde, bijvoorbeeld %Microsoft
        14 :veld eindigt niet met tekst	                            Plaats het teken % aan het begin van de filterwaarde, bijvoorbeeld %MiMicrosoft

        If you use a skip and take, highly recommended to specify orderbyfields. This makes the requests much faster.
        You should use unique fields or combinations of most unique fields in the dataset

        Using ';' between filters is OR, ',' is AND
        """

        total_response = []
        loop_boolean = True
        no_of_loops = 0
        no_of_results = 0

        if fields != None:
            parameters = {"filterfieldids": fields, "filtervalues": values, "operatortypes": operators}
        else:
            parameters = {}

        if orderbyfields is not None:
            parameters["orderbyfieldids"] = "-{}".format(orderbyfields)

        url = 'https://{}.{}/profitrestservices/connectors/{}'.format(self.environment, self.base_url, connector)

        while loop_boolean:
            loop_parameters = {"skip": 40000 * no_of_loops, "take": 40000}
            parameters.update(loop_parameters)
            authorization_header = {'Authorization': 'AfasToken {}'.format(self.base64token)}
            response = requests.get(url.encode("utf-8"), parameters, headers=authorization_header, timeout=30000)
            if response.status_code == 200:
                response_json = response.json()['rows']
                no_of_loops += 1
                no_of_results += len(response_json)
                loop_boolean = True if len(response_json) == 40000 else False

                print(time.strftime('%H:%M:%S'), 'Got next connector from profit: ', connector, ' With nr of rows: ', no_of_results)
                total_response += response_json
            else:
                return response.text

        return total_response

    def get_json_filtered_data(self, connector: str, fields: list, values: list, operators: list, orderbyfields: str = None):
        """
        This method is meant for complex combined filters like (a and b) or (a and c)

        Possible filter operators are:
        1: is gelijk aan
        2: is groter of gelijk aan
        3: is kleiner of gelijk aan
        4: is groter dan
        5: is kleiner dan
        6: tekst komt voor in veld	                                Plaats de filterwaarde tussen %..%, bijvoorbeeld %Microsoft%
        7: is niet gelijk aan / Tekst komt niet voor in veld	    Plaats de filterwaarde tussen %..%, bijvoorbeeld %Microsoft%
        8: veld is leeg	                                            Geef filterfieldid, filtervalue en operatortype op. De waarde bij filtervalue is altijd null
        9: veld is niet leeg	                                    Geef filterfieldid, filtervalue en operatortype op
        10 :veld begint met tekst	                                Plaats het teken % aan het einde van de filterwaarde, bijvoorbeeld Microsoft%
        12 :veld begint niet met tekst	                            Plaats het teken % aan het einde van de filterwaarde, bijvoorbeeld Microsoft%
        13 :veld eindigt met tekst	                                Plaats het teken % aan het begin van de filterwaarde, bijvoorbeeld %Microsoft
        14 :veld eindigt niet met tekst	                            Plaats het teken % aan het begin van de filterwaarde, bijvoorbeeld %MiMicrosoft

        If you use a skip and take, highly recommended to specify orderbyfields. This makes the requests much faster.
        You should use unique fields or combinations of most unique fields in the dataset

        Using ';' between filters is OR, ',' is AND
        :param connector: name of connector
        :param fields: list of filters. each listitem is one filterblock. example: ['naam, woonplaats', 'achternaam, einddatum']
        :param values: list of filters. each listitem corresponds to one filterblock. example: ['Jan, Gouda', 'Janssen, 2019-01-01T00:00']
        :param operators: list of filters. each listitem corresponds to one filterblock. example: ['1, 1', '1, 3']
        :param orderbyfields: string of fields to order result by
        :return: data in json format
        """

        total_response = []
        loop_boolean = True
        no_of_loops = 0
        no_of_results = 0

        parameters = {"Filters": {"Filter": []}}

        for filter_no in range(0, len(fields)):
            filter = {"@FilterId": 'Filter {}'.format(filter_no + 1), "Field": []}
            fields_values = fields[filter_no].split(',')
            operators_values = operators[filter_no].split(',')
            values_values = values[filter_no].split(',')
            for number in range(0, len(fields_values)):
                filter["Field"].append({"@FieldId": fields_values[number],
                                        "@OperatorType": operators_values[number],
                                        "#text": values_values[number]})
            parameters['Filters']['Filter'].append(filter)

        url = 'https://{}.{}/profitrestservices/connectors/{}'.format(self.environment, self.base_url, connector)
        # Dit stukje hieronder heeft JJ een paar uur van zn leven gekost. Do not touch
        querystring = parse.quote(json.dumps(parameters, separators=(',', ':')))
        if orderbyfields is not None:
            querystring = querystring + '&orderbyfieldids={}'.format(orderbyfields)

        while loop_boolean:
            loop_parameters = "&skip={}&take={}".format(40000 * no_of_loops, 40000)
            authorization_header = {'Authorization': 'AfasToken {}'.format(self.base64token)}
            response = requests.get(url, data='', headers=authorization_header, timeout=30000, params="filterjson={}{}".format(querystring, loop_parameters))
            if response.status_code == 200:
                response_json = response.json()['rows']
                no_of_loops += 1
                no_of_results += len(response_json)
                loop_boolean = True if len(response_json) == 40000 else False

                print(time.strftime('%H:%M:%S'), 'Got next connector from profit: ', connector, ' With nr of rows: ', no_of_results)
                total_response += response_json
            else:
                return response.text

        return total_response


class UpdateConnector:

    def __init__(self, environment, base64token, base_url='rest.afas.online'):
        self.environment = environment
        self.base64token = base64token
        self.base_url = base_url

    def update(self, updateconnector, data):
        url = 'https://{}.{}/profitrestservices/connectors/{}'.format(self.environment, self.base_url, updateconnector)

        headers = {
            'authorization': "AfasToken {0}".format(self.base64token),
            'content-type': "application/json",
            'cache-control': "no-cache"
        }

        update = requests.request("PUT", url, data=data, headers=headers)

        return update

    def update_person(self, data: dict, overload_fields={}):
        """
        :param data: Fields that are allowed are listed in allowed fields array. Update this whenever necessary
        :param overload_fields: The custom fields in this dataset. Give the key of the field and the value. For example: {DFEDS8-DSF9uD-DDSA: 'Vrij veld'}
        :return: status code for request and optional error message
        """
        allowed_fields = ['employee_id', 'mail_work', 'mail_private', 'mobile_work', 'mobile_private', 'nickname', 'first_name', 'initials', 'prefix', 'last_name',
                          'birth_name', 'gender', 'nationality', 'birth_date', 'country_of_birth', 'ssn', 'marital_status', 'date_of_marriage', 'phone_work', 'phone_private', 'city_of_birth']
        required_fields = ['employee_id', 'person_id']

        for field in data.keys():
            if field not in allowed_fields and field not in required_fields:
                return 'Field {field} is not allowed. Allowed fields are: {allowed_fields}'.format(field=field, allowed_fields=tuple(allowed_fields))

        for field in required_fields:
            if field not in data.keys():
                return 'Field {field} is required. Required fields are: {required_fields}'.format(field=field, required_fields=tuple(required_fields))

        url = 'https://{}.{}/profitrestservices/connectors/{}'.format(self.environment, self.base_url, 'KnEmployee/KnPerson')
        headers = {
            'authorization': "AfasToken {0}".format(self.base64token),
            'content-type': "application/json",
            'cache-control': "no-cache"
        }
        base_body = {
            "AfasEmployee": {
                "Element": {
                    "@EmId": data['employee_id'],
                    "Objects": {
                        "KnPerson": {
                            "Element": {
                                "Fields": {
                                    "MatchPer": "0",
                                    "BcCo": data['person_id']
                                }
                            }
                        }
                    }
                }
            }
        }
        fields_to_update = {}

        # Add fields that you want to update a dict (adding to body itself is too much text)
        fields_to_update.update({"EmA": data['mail_work']}) if 'mail_work' in data else fields_to_update
        fields_to_update.update({"EmA2": data['mail_private']}) if 'mail_private' in data else fields_to_update
        fields_to_update.update({"MbNr": data['mobile_work']}) if 'mobile_work' in data else fields_to_update
        fields_to_update.update({"MbN2": data['mobile_private']}) if 'mobile_private' in data else fields_to_update
        fields_to_update.update({"CaNm": data['nickname']}) if 'nickname' in data else fields_to_update
        fields_to_update.update({"FiNm": data['first_name']}) if 'first_name' in data else fields_to_update
        fields_to_update.update({"In": data['initials']}) if 'initials' in data else fields_to_update
        fields_to_update.update({"Is": data['prefix']}) if 'prefix' in data else fields_to_update
        fields_to_update.update({"LaNm": data['last_name']}) if 'last_name' in data else fields_to_update
        fields_to_update.update({"NmBi": data['birth_name']}) if 'birth_name' in data else fields_to_update
        fields_to_update.update({"ViGe": data['gender']}) if 'gender' in data else fields_to_update
        fields_to_update.update({"PsNa": data['nationality']}) if 'nationality' in data else fields_to_update
        fields_to_update.update({"DaBi": data['birth_date']}) if 'birth_date' in data else fields_to_update
        fields_to_update.update({"RsBi": data['country_of_birth']}) if 'country_of_birth' in data else fields_to_update
        fields_to_update.update({"SoSe": data['ssn']}) if 'ssn' in data else fields_to_update
        fields_to_update.update({"ViCs": data['marital_status']}) if 'marital_status' in data else fields_to_update
        fields_to_update.update({"DaMa": data['date_of_marriage']}) if 'date_of_marriage' in data else fields_to_update
        fields_to_update.update({"TeNr": data['phone_work']}) if 'phone_work' in data else fields_to_update
        fields_to_update.update({"TeN2": data['phone_private']}) if 'phone_private' in data else fields_to_update
        fields_to_update.update({"RsBi": data['city_of_birth']}) if 'city_of_birth' in data else fields_to_update

        # Update the request body with update fields
        base_body['AfasEmployee']['Element']['Objects']['KnPerson']['Element']['Fields'].update(fields_to_update)

        update = requests.request("PUT", url, data=json.dumps(base_body), headers=headers)

        return update

    def update_organisation(self, data: dict, method: str, custom_fields={}):
        """
        This function updates organisations in CRM with the AFAS updateconnect 'KnOrganisation'.
        :param data: Deliver all the data which should be updated in list format. The data should at least contain the required_fields and can contain also the allowed fields
        :param method: Is a PUT for an update of an existing cost carrier. is a POST for an insert of a new cost carrier
        :param custom_fields: The custom fields in this dataset. Give the key of the field and the value. For example: {DFEDS8-DSF9uD-DDSA: 'Vrij veld'}
        :return: The status code from AFAS Profit
        """
        required_fields = ['organisation_id', 'name', 'blocked']
        allowed_fields = ['search_name', 'kvk_number', 'phone_number_work', 'email_work', 'vat_number', 'status']
        allowed_fields_address = ['country', 'street', 'housenumber', 'housenumber_add', 'zipcode', 'residence']
        all_fields = required_fields + allowed_fields + allowed_fields_address

        # Check if the fields in data exists in the required or allowed fields
        for field in data.keys():
            if field not in all_fields:
                raise ValueError('Field {} is not allowed. Allowed fields are: {}'.format(field, tuple(all_fields)))

        # Check if all the required_fields are present
        for field in required_fields:
            if field not in data.keys():
                raise ValueError('Field {} is required. Required fields are: {}'.format(field, tuple(required_fields)))

        if method != 'PUT' and method != 'POST' and method != 'DELETE':
            raise ValueError('Parameter method should be PUT, POST or DELETE (in uppercase)')

        if method == 'DELETE':
            url = f"https://{self.environment}.{self.base_url}/profitrestservices/connectors/KnOrganisation/KnOrganisation/MatchOga,BdIdBcCo,Nm,Bl/0,1,{data['organisation_id']},{data['name']},{data['blocked']}"
            base_body = {}
        else:
            url = 'https://{}.{}/profitrestservices/connectors/{}'.format(self.environment, self.base_url, 'KnOrganisation')

            base_body = {
                "KnOrganisation": {
                    "Element": {
                        "Fields": {
                            "MatchOga": "0",
                            "BcId": 1,
                            "BcCo": data['organisation_id'],
                            "Nm": data['name'],
                            "Bl": data['blocked']
                        },
                        "Objects": {

                        }
                    }
                }
            }

            address_body = {
                "KnBasicAddressAdr": {
                    "Element": {
                        "Fields": {
                            "PbAd": False
                        }
                    }
                }
            }

            # If one of the optional fields of a subelement is included, we need to merge the whole JSON object to the basebody
            if any(field in data.keys() for field in allowed_fields_address):
                fields_to_update = {}
                fields_to_update.update({"CoId": data['country']}) if 'country' in data else fields_to_update
                fields_to_update.update({"Ad": data['street']}) if 'street' in data else fields_to_update
                fields_to_update.update({"HmNr": data['housenumber']}) if 'housenumber' in data else fields_to_update
                fields_to_update.update({"HmAd": data['housenumber_add']}) if 'housenumber_add' in data else fields_to_update
                fields_to_update.update({"ZpCd": data['zipcode']}) if 'zipcode' in data else fields_to_update
                fields_to_update.update({"Rs": data['residence']}) if 'residence' in data else fields_to_update

                # merge subelement with basebody
                address_body['KnBasicAddressAdr']['Element']['Fields'].update(fields_to_update)
                base_body['KnOrganisation']['Element']['Objects'].update(address_body)

            # Add allowed fields to the basebody if they are available in the data. Fields that are not exists in the basebody, should not be added tot this basebody to prevent errrors.
            fields_to_update = {}
            fields_to_update.update({"SeNm": data['search_name']}) if 'search_name' in data else fields_to_update
            fields_to_update.update({"CcNr": data['kvk_number']}) if 'kvk_number' in data else fields_to_update
            fields_to_update.update({"TeNr": data['phone_number_work']}) if 'phone_number_work' in data else fields_to_update
            fields_to_update.update({"EmAd": data['email_work']}) if 'email_work' in data else fields_to_update
            fields_to_update.update({"FiNr": data['vat_number']}) if 'vat_number' in data else fields_to_update
            fields_to_update.update({"StId": data['status']}) if 'status' in data else fields_to_update

            base_body['KnOrganisation']['Element']['Fields'].update(fields_to_update)

            # Now create a dict for all the custom fields. This fields are not by default added to the base_body because they're not always present in the dataset
            fields_to_update = {}
            for key in custom_fields.keys():
                fields_to_update.update({key: custom_fields[key]})

            # Update the request body with update fields
            base_body['KnOrganisation']['Element']['Fields'].update(fields_to_update)

        headers = {
            'authorization': "AfasToken {0}".format(self.base64token),
            'content-type': "application/json",
            'cache-control': "no-cache"
        }

        update = requests.request(method, url, data=json.dumps(base_body), headers=headers)

        return update

    def update_employee(self, data: dict, overload_fields={}):
        """
        :param data: Fields that are allowed are listed in allowed fields array. Update this whenever necessary
        :return: status code for request and optional error message
        """
        allowed_fields = ['employee_id', 'city_of_birth']
        required_fields = ['employee_id']

        for field in data.keys():
            if field not in allowed_fields and field not in required_fields:
                return 'Field {field} is not allowed. Allowed fields are: {allowed_fields}'.format(field=field, allowed_fields=tuple(allowed_fields))

        for field in required_fields:
            if field not in data.keys():
                return 'Field {field} is required. Required fields are: {required_fields}'.format(field=field, required_fields=tuple(required_fields))

        url = 'https://{}.{}/profitrestservices/connectors/{}'.format(self.environment, self.base_url, 'KnEmployee')
        headers = {
            'authorization': "AfasToken {0}".format(self.base64token),
            'content-type': "application/json",
            'cache-control': "no-cache"
        }
        base_body = {
            "AfasEmployee": {
                "Element": {
                    "@EmId": data['employee_id'],
                    "Fields": {
                    }
                }
            }
        }
        fields_to_update = {}

        # Add fields that you want to update a dict (adding to body itself is too much text)
        fields_to_update.update({"LwRs": data['city_of_birth']}) if 'city_of_birth' in data else fields_to_update

        # Update the request body with update fields
        base_body['AfasEmployee']['Element']['Fields'].update(fields_to_update)

        update = requests.request("PUT", url, data=json.dumps(base_body), headers=headers)

        return update

    def update_address(self, data: dict, overload_fields={}):
        """
        :param data: Fields that are allowed are listed in allowed fields array. Update this whenever necessary
        :return: status code for request and optional error message
        """
        allowed_fields = ['street_number_add', 'city']
        required_fields = ['employee_id', 'person_id', 'country', 'street', 'street_number', 'postal_code', 'startdate']
        for field in data.keys():
            if field not in allowed_fields and field not in required_fields:
                return 'Field {field} is not allowed. Allowed fields are: {allowed_fields}'.format(field=field, allowed_fields=tuple(allowed_fields))

        for field in required_fields:
            if field not in data.keys():
                return 'Field {field} is required. Required fields are: {required_fields}'.format(field=field, required_fields=tuple(required_fields))

        url = 'https://{}.{}/profitrestservices/connectors/{}'.format(self.environment, self.base_url, 'KnEmployee/KnPerson')
        headers = {
            'authorization': "AfasToken {0}".format(self.base64token),
            'content-type': "application/json",
            'cache-control': "no-cache"
        }
        base_body = {
            "AfasEmployee": {
                "Element": {
                    "@EmId": data['employee_id'],
                    "Objects": {
                        "KnPerson": {
                            "Element": {
                                "Fields": {
                                    "MatchPer": "0",
                                    "BcCo": data['person_id']
                                },
                                "Objects": {
                                    "KnBasicAddressAdr": {
                                        "Element": {
                                            "Fields": {
                                                "CoId": data['country'],
                                                "PbAd": False,
                                                "Ad": data['street'],
                                                "HmNr": data['street_number'],
                                                "BcCo": data['employee_id'],
                                                "ZpCd": data['postal_code'],
                                                "ResZip": True,
                                                "BeginDate": data['startdate']
                                            }
                                        }
                                    },
                                    "KnBasicAddressPad": {
                                        "Element": {
                                            "Fields": {
                                                "CoId": data['country'],
                                                "PbAd": False,
                                                "Ad": data['street'],
                                                "HmNr": data['street_number'],
                                                "BcCo": data['employee_id'],
                                                "ZpCd": data['postal_code'],
                                                "ResZip": True,
                                                "BeginDate": data['startdate']
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        fields_to_update = {}

        # Add fields that you want to update a dict (adding to body itself is too much text)
        fields_to_update.update({"HmAd": data['street_number_add']}) if 'street_number_add' in data else fields_to_update
        fields_to_update.update({"Rs": data['city']}) if 'city' in data else fields_to_update

        # This is to include custom fields
        for key in overload_fields.keys():
            fields_to_update.update({key: overload_fields[key]})

        # Update the request body with update fields
        base_body['AfasEmployee']['Element']['Objects']['KnPerson']['Element']['Objects']['KnBasicAddressAdr']['Element']['Fields'].update(fields_to_update)
        base_body['AfasEmployee']['Element']['Objects']['KnPerson']['Element']['Objects']['KnBasicAddressPad']['Element']['Fields'].update(fields_to_update)

        update = requests.request("POST", url, data=json.dumps(base_body), headers=headers)

        return update

    def update_contract(self, data: dict, overload_fields={}):
        """
        :param data: Dictionary of fields that you want to update in AFAS. Only fields listed in allowed arrays are accepted. Fields listed in required fields array, are mandatory
        :return: status code for request and optional error message
        """
        allowed_fields_contract = ['employee_id', 'type_of_employment', 'enddate_contract', 'termination_reason', 'termination_initiative', 'probation_period', 'probation_enddate', 'cao', 'terms_of_employment', 'type_of_contract', 'employer_number', 'type_of_employee', 'employment']
        required_fields_contract = ['employee_id', 'startdate_contract']
        allowed_fields_function = ['costcarrier_id']
        required_fields_function = ['organizational_unit', 'function_id', 'costcenter_id']
        allowed_fields_timetable = ['changing_work_pattern']
        required_fields_timetable = ['weekly_hours', 'parttime_percentage']
        allowed_fields_salary = ['step', 'function_scale', 'salary_scale']
        required_fields_salary = ['type_of_salary', 'salary_amount', 'period_table']
        allowed_fields = allowed_fields_contract + allowed_fields_salary + allowed_fields_timetable + allowed_fields_function
        required_fields = required_fields_contract + required_fields_function + required_fields_timetable + required_fields_salary

        # Check if there are fields that are not allowed or fields missing that are required
        for field in data.keys():
            if field not in allowed_fields and field not in required_fields:
                return 'Field {field} is not allowed. Allowed fields are: {allowed_fields}'.format(field=field, allowed_fields=tuple(allowed_fields))
        for field in required_fields_contract:
            if field not in data.keys():
                return 'Field {field} is required. Required fields are: {required_fields}'.format(field=field, required_fields=tuple(required_fields))

        url = 'https://{}.{}/profitrestservices/connectors/{}'.format(self.environment, self.base_url, 'KnEmployee/AfasContract')
        headers = {
            'authorization': "AfasToken {0}".format(self.base64token),
            'content-type': "application/json",
            'cache-control': "no-cache"
        }
        base_body = {
            "AfasEmployee": {
                "Element": {
                    "@EmId": data['employee_id'],
                    "Objects": {
                        "AfasContract": {
                            "Element": {
                                "@DaBe": data['startdate_contract'],
                                "Fields": {
                                }
                            }
                        }
                    }
                }
            }
        }

        # Extra JSON objects which are optional at contract creation
        function = {
            "AfasOrgunitFunction": {
                "Element": {
                    "@DaBe": data['startdate_contract'],
                    "Fields": {
                    }
                }
            }
        }

        timetable = {
            "AfasTimeTable": {
                "Element": {
                    "@DaBg": data['startdate_contract'],
                    "Fields": {
                        "StPa": True
                    }
                }
            }
        }

        salary = {
            "AfasSalary": {
                "Element": {
                    "@DaBe": data['startdate_contract'],
                    "Fields": {
                    }
                }
            }
        }

        # If one of the optional fields of a subelement is included, we need to merge the whole JSON object to the basebody
        if any(field in data.keys() for field in allowed_fields_function):
            for field in required_fields_function:
                if field not in data.keys():
                    return 'Field {field} is required. Required fields for function are: {required_fields}'.format(field=field, required_fields=tuple(required_fields))

            fields_to_update = {}
            fields_to_update.update({"DpId": data['organizational_unit']}) if 'organizational_unit' in data else fields_to_update
            fields_to_update.update({"FuId": data['function_id']}) if 'function_id' in data else fields_to_update
            fields_to_update.update({"CcId": data['costcenter_id']}) if 'costcenter_id' in data else fields_to_update
            fields_to_update.update({"CrId": data['costcarrier_id']}) if 'costcarrier_id' in data else fields_to_update

            # merge subelement with basebody
            function['AfasOrgunitFunction']['Element']['Fields'].update(fields_to_update)
            base_body['AfasEmployee']['Element']['Objects'].update(function)

        if any(field in data.keys() for field in allowed_fields_timetable):
            for field in required_fields_timetable:
                if field not in data.keys():
                    return 'Field {field} is required. Required fields for timetable are: {required_fields}'.format(field=field, required_fields=tuple(required_fields))

            fields_to_update = {}
            fields_to_update.update({"StPa": data['changing_work_pattern']}) if 'changing_work_pattern' in data else fields_to_update
            fields_to_update.update({"HrWk": data['weekly_hours']}) if 'weekly_hours' in data else fields_to_update
            fields_to_update.update({"PcPt": data['parttime_percentage']}) if 'parttime_percentage' in data else fields_to_update

            timetable['AfasTimeTable']['Element']['Fields'].update(fields_to_update)
            base_body['AfasEmployee']['Element']['Objects'].update(timetable)

        if any(field in data.keys() for field in allowed_fields_salary):
            for field in required_fields_salary:
                if field not in data.keys():
                    return 'Field {field} is required. Required fields for salaries are: {required_fields}'.format(field=field, required_fields=tuple(required_fields))

            fields_to_update = {}
            fields_to_update.update({"SaSt": data['step']}) if 'step' in data else fields_to_update
            fields_to_update.update({"SaPe": data['type_of_salary']}) if 'type_of_salary' in data else fields_to_update
            fields_to_update.update({"EmSa": data['salary_amount']}) if 'salary_amount' in data else fields_to_update
            fields_to_update.update({"PtId": data['period_table']}) if 'period_table' in data else fields_to_update
            fields_to_update.update({"VaSc": data['salary_scale']}) if 'salary_scale' in data else fields_to_update
            fields_to_update.update({"FuSc": data['function_scale']}) if 'function_scale' in data else fields_to_update

            salary['AfasSalary']['Element']['Fields'].update(fields_to_update)
            base_body['AfasEmployee']['Element']['Objects'].update(salary)

        # Add fields that you want to update a dict (adding to body itself is too much text)
        fields_to_update = {}
        fields_to_update.update({"DaEn": data['enddate_contract']}) if 'enddate_contract' in data else fields_to_update
        fields_to_update.update({"PEmTy": data['type_of_employment']}) if 'type_of_employment' in data else fields_to_update
        fields_to_update.update({"ViIe": data['termination_initiative']}) if 'termination_initiative' in data else fields_to_update
        fields_to_update.update({"ViRe": data['termination_reason']}) if 'termination_reason' in data else fields_to_update
        fields_to_update.update({"ViTo": data['probation_period']}) if 'probation_period' in data else fields_to_update
        fields_to_update.update({"DaEt": data['probation_enddate']}) if 'probation_enddate' in data else fields_to_update
        fields_to_update.update({"ClId": data['cao']}) if 'cao' in data else fields_to_update
        fields_to_update.update({"WcId": data['terms_of_employment']}) if 'terms_of_employment' in data else fields_to_update
        fields_to_update.update({"ApCo": data['type_of_contract']}) if 'type_of_contract' in data else fields_to_update
        fields_to_update.update({"CmId": data['employer_number']}) if 'employer_number' in data else fields_to_update
        fields_to_update.update({"EmMt": data['type_of_employee']}) if 'type_of_employee' in data else fields_to_update
        fields_to_update.update({"ViEt": data['employment']}) if 'employment' in data else fields_to_update

        # This is to include custom fields
        # TODO: implement overload for subelements too (eg. salary, function etc)
        for key in overload_fields.keys():
            fields_to_update.update({key: overload_fields[key]})

        # Update the request body with update fields
        base_body['AfasEmployee']['Element']['Objects']['AfasContract']['Element']['Fields'].update(fields_to_update)

        update = requests.request("POST", url, data=json.dumps(base_body), headers=headers)

        return update

    def update_function(self, data: dict, overload_fields={}):
        """
        :param data: Fields that are allowed are listed in allowed fields array. Update this whenever necessary
        :return: status code for request and optional error message
        """
        allowed_fields = ['formation', 'costcarrier']
        required_fields = ['startdate', 'employee_id', 'organizational_unit', 'function', 'costcentre']

        for field in data.keys():
            if field not in allowed_fields and field not in required_fields:
                return 'Field {field} is not allowed. Allowed fields are: {allowed_fields}'.format(field=field, allowed_fields=tuple(allowed_fields))

        for field in required_fields:
            if field not in data.keys():
                return 'Field {field} is required. Required fields are: {required_fields}'.format(field=field, required_fields=tuple(required_fields))

        url = 'https://{}.{}/profitrestservices/connectors/{}'.format(self.environment, self.base_url, 'KnEmployee/AfasOrgunitFunction')
        headers = {
            'authorization': "AfasToken {0}".format(self.base64token),
            'content-type': "application/json",
            'cache-control': "no-cache"
        }
        base_body = {
            "AfasEmployee": {
                "Element": {
                    "@EmId": data['employee_id'],
                    "Objects": {
                        "AfasOrgunitFunction": {
                            "Element": {
                                "@DaBe": data['startdate'],
                                "Fields": {
                                    "DpId": data['organizational_unit'],
                                    "FuId": data['function'],
                                    "CrId": data['costcentre']
                                }
                            }
                        }
                    }
                }
            }
        }
        fields_to_update = {}

        # Add fields that you want to update a dict (adding to body itself is too much text)
        fields_to_update.update({"FpId": data['formation']}) if 'formation' in data else fields_to_update
        fields_to_update.update({"CcId": data['costcarrier']}) if 'costcarrier' in data else fields_to_update

        for key in overload_fields.keys():
            fields_to_update.update({key: overload_fields[key]})

        # Update the request body with update fields
        base_body['AfasEmployee']['Element']['Objects']['AfasOrgunitFunction']['Element']['Fields'].update(fields_to_update)

        update = requests.request("PUT", url, data=json.dumps(base_body), headers=headers)

        return update

    def update_salary(self, data: dict, overload_fields={}):
        """
        :param data: Fields that are allowed are listed in allowed fields array. Update this whenever necessary
        :return: status code for request and optional error message
        """
        allowed_fields = ['step', 'period_table', 'salary_year', 'function_scale', 'function_scale_type', 'salary_scale', 'salary_scale_type', 'salary_amount']
        required_fields = ['startdate', 'employee_id', 'salary_type']

        for field in data.keys():
            if field not in allowed_fields and field not in required_fields:
                return 'Field {field} is not allowed. Allowed fields are: {allowed_fields}'.format(field=field, allowed_fields=tuple(allowed_fields))

        for field in required_fields:
            if field not in data.keys():
                return 'Field {field} is required. Required fields are: {required_fields}'.format(field=field, required_fields=tuple(required_fields))

        url = 'https://{}.{}/profitrestservices/connectors/{}'.format(self.environment, self.base_url, 'KnEmployee/AfasSalary')
        headers = {
            'authorization': "AfasToken {0}".format(self.base64token),
            'content-type': "application/json",
            'cache-control': "no-cache"
        }
        base_body = {
            "AfasEmployee": {
                "Element": {
                    "@EmId": data['employee_id'],
                    "Objects": {
                        "AfasSalary": {
                            "Element": {
                                "@DaBe": data['startdate'],
                                "Fields": {
                                    "SaPe": data['salary_type'],
                                    "EmSa": data['salary_amount']
                                }
                            }
                        }
                    }
                }
            }
        }
        fields_to_update = {}

        # Add fields that you want to update a dict (adding to body itself is too much text)
        fields_to_update.update({"SaSt": data['step']}) if 'step' in data else fields_to_update
        fields_to_update.update({"SaYe": data['salary_year']}) if 'salary_year' in data else fields_to_update
        fields_to_update.update({"PtId": data['period_table']}) if 'period_table' in data else fields_to_update.update({"PtId": 5})
        fields_to_update.update({"VaSc": data['salary_scale']}) if 'salary_scale' in data else fields_to_update
        fields_to_update.update({"TaId": data['salary_scale_type']}) if 'salary_scale_type' in data else fields_to_update
        fields_to_update.update({"FuSc": data['function_scale']}) if 'function_scale' in data else fields_to_update
        fields_to_update.update({"FuTa": data['function_scale_type']}) if 'function_scale_type' in data else fields_to_update

        for key in overload_fields.keys():
            fields_to_update.update({key: overload_fields[key]})

        # Update the request body with update fields
        base_body['AfasEmployee']['Element']['Objects']['AfasSalary']['Element']['Fields'].update(fields_to_update)

        update = requests.request("PUT", url, data=json.dumps(base_body), headers=headers)

        return update

    def update_timetable(self, data: dict, overload_fields={}):
        """
        :param data: Fields that are allowed are listed in allowed fields array. Update this whenever necessary
        :return: status code for request and optional error message
        """

        allowed_fields = ['changing_work_pattern']
        required_fields = ['startdate', 'employee_id', 'weekly_hours', 'parttime_percentage']

        for field in data.keys():
            if field not in allowed_fields and field not in required_fields:
                return 'Field {field} is not allowed. Allowed fields are: {allowed_fields}'.format(field=field, allowed_fields=tuple(allowed_fields))

        for field in required_fields:
            if field not in data.keys():
                return 'Field {field} is required. Required fields are: {required_fields}'.format(field=field, required_fields=tuple(required_fields))

        url = 'https://{}.{}/profitrestservices/connectors/{}'.format(self.environment, self.base_url, 'KnEmployee/AfasTimeTable')
        headers = {
            'authorization': "AfasToken {0}".format(self.base64token),
            'content-type': "application/json",
            'cache-control': "no-cache"
        }
        base_body = {
            "AfasEmployee": {
                "Element": {
                    "@EmId": data['employee_id'],
                    "Objects": {
                        "AfasTimeTable": {
                            "Element": {
                                "@DaBe": data['startdate'],
                                "Fields": {
                                    "StPa": True,
                                    "HrWk": data['weekly_hours'],
                                    "PcPt": data['parttime_percentage']
                                }
                            }
                        }
                    }
                }
            }
        }
        fields_to_update = {}

        # Add fields that you want to update a dict (adding to body itself is too much text)
        fields_to_update.update({"StPa": data['changing_work_pattern']}) if 'changing_work_pattern' in data else fields_to_update

        for key in overload_fields.keys():
            fields_to_update.update({key: overload_fields[key]})

        # Update the request body with update fields
        base_body['AfasEmployee']['Element']['Objects']['AfasTimeTable']['Element']['Fields'].update(fields_to_update)

        update = requests.request("PUT", url, data=json.dumps(base_body), headers=headers)

        return update

    def new_wage_component(self, data: dict, overload_fields={}):
        """
        :param data: Fields that are allowed are listed in allowed fields array. Update this whenever necessary
        :return: status code for request and optional error message
        """
        allowed_fields = ['enddate', 'contract_no']
        required_fields = ['employee_id', 'parameter', 'startdate', 'value']

        for field in data.keys():
            if field not in allowed_fields and field not in required_fields:
                return 'Field {field} is not allowed. Allowed fields are: {allowed_fields}'.format(field=field, allowed_fields=tuple(allowed_fields))

        for field in required_fields:
            if field not in data.keys():
                return 'Field {field} is required. Required fields are: {required_fields}'.format(field=field, required_fields=tuple(required_fields))

        url = 'https://{}.{}/profitrestservices/connectors/{}'.format(self.environment, self.base_url, 'HrVarValue')
        headers = {
            'authorization': "AfasToken {0}".format(self.base64token),
            'content-type': "application/json",
            'cache-control': "no-cache"
        }
        base_body = {
            "HrVarValue": {
                "Element": {
                    "Fields": {
                        "VaId": data['parameter'],
                        "Va": data['value'],
                        "EmId": data['employee_id'],
                        "DaBe": data['startdate']
                    }
                }
            }
        }
        fields_to_update = {}

        # Add fields that you want to update a dict (adding to body itself is too much text)
        fields_to_update.update({"EnSe": data['contract_no']} if 'contract_no' in data else fields_to_update)
        fields_to_update.update({"DaEn": data['enddate']} if 'enddate' in data else fields_to_update)
        fields_to_update.update({"DiTp": data['apply_type']} if 'apply_type' in data else fields_to_update)

        for key in overload_fields.keys():
            fields_to_update.update({key: overload_fields[key]})

        # Update the request body with update fields
        base_body['HrVarValue']['Element']['Fields'].update(fields_to_update)

        update = requests.request("POST", url, data=json.dumps(base_body), headers=headers)

        return update

    def new_wage_mutation(self, data: dict, overload_fields={}):
        """
        :param data: Fields that are allowed are listed in allowed fields array. Update this whenever necessary
        :return: status code for request and optional error message
        """
        allowed_fields = ['period_table']
        required_fields = ['employee_id', 'year', 'month', 'employer_id', 'wage_component_id', 'value']

        for field in data.keys():
            if field not in allowed_fields and field not in required_fields:
                return 'Field {field} is not allowed. Allowed fields are: {allowed_fields}'.format(field=field, allowed_fields=tuple(allowed_fields))

        for field in required_fields:
            if field not in data.keys():
                return 'Field {field} is required. Required fields are: {required_fields}'.format(field=field, required_fields=tuple(required_fields))

        url = 'https://{}.{}/profitrestservices/connectors/{}'.format(self.environment, self.base_url, 'HrCompMut')
        headers = {
            'authorization': "AfasToken {0}".format(self.base64token),
            'content-type': "application/json",
            'cache-control': "no-cache"
        }
        base_body = {
            "HrCompMut": {
                "Element": {
                    "@Year": data['year'],
                    "@PeId": data['month'],
                    "@EmId": data['employee_id'],
                    "@ErId": data['employer_id'],
                    "@Sc02": data['wage_component_id'],
                    "Fields": {
                        "VaD1": data['value']
                    }
                }
            }
        }
        fields_to_update = {}
        selector_to_update = {}

        # Add fields that you want to update a dict (adding to body itself is too much text)
        selector_to_update.update({"@PtId": data['period_table']}) if 'period_table' in data else selector_to_update.update({"@PtId": 5})

        for key in overload_fields.keys():
            fields_to_update.update({key: overload_fields[key]})

        # Update the request body with update fields
        base_body['HrCompMut']['Element']['Fields'].update(fields_to_update)
        base_body['HrCompMut']['Element'].update(selector_to_update)

        update = requests.request("POST", url, data=json.dumps(base_body), headers=headers)

        return update

    def update_bank_account(self, data: dict, overload_fields={}):
        """
        :param data: Fields that are allowed are listed in allowed fields array. Update this whenever necessary
        :return: status code for request and optional error message
        """
        allowed_fields = ['bankname', 'country']
        required_fields = ['employee_id', 'bank_account', 'iban']

        for field in data.keys():
            if field not in allowed_fields and field not in required_fields:
                return 'Field {field} is not allowed. Allowed fields are: {allowed_fields}'.format(field=field, allowed_fields=tuple(allowed_fields))

        for field in required_fields:
            if field not in data.keys():
                return 'Field {field} is required. Required fields are: {required_fields}'.format(field=field, required_fields=tuple(required_fields))

        url = 'https://{}.{}/profitrestservices/connectors/{}'.format(self.environment, self.base_url, 'KnEmployee/AfasBankInfo')
        headers = {
            'authorization': "AfasToken {0}".format(self.base64token),
            'content-type': "application/json",
            'cache-control': "no-cache"
        }
        base_body = {
            "AfasEmployee": {
                "Element": {
                    "@EmId": data['employee_id'],
                    "Objects": {
                        "AfasBankInfo": {
                            "Element": {
                                "@AcId": data['bank_account'],  # "0417164300",
                                "@NoBk": False,  # Cash payment (old)
                                "Fields": {
                                    "IbCk": True,  # IBAN check (always true)
                                    "Iban": data['iban']  # "NL91ABNA0417164300"
                                }
                            }
                        }
                    }
                }
            }
        }

        fields_to_update = {}

        # Add fields that you want to update a dict (adding to body itself is too much text)
        fields_to_update.update({"BkIc": data['bankname']}) if 'bankname' in data else fields_to_update
        fields_to_update.update({"CoId": data['country']}) if 'country' in data else fields_to_update

        for key in overload_fields.keys():
            fields_to_update.update({key: overload_fields[key]})

        # Update the request body with update fields
        base_body['AfasEmployee']['Element']['Objects']['AfasBankInfo']['Element']['Fields'].update(fields_to_update)

        update = requests.request("PUT", url, data=json.dumps(base_body), headers=headers)

        return update

    def new_employee_with_first_contract(self, data: dict, overload_fields={}):
        """
        :param data: Fields that are allowed are listed in allowed fields array. Update this whenever necessary
        :param overload_fields: Any custom fields that are not in the allowed or required fields
        :return: status code for request and optional error message
        """

        allowed_fields_person = []
        required_fields_person = ['employee_id', 'last_name', 'gender', 'first_name', 'place_of_birth', 'date_of_birth', 'country', 'email_work', 'email_home', 'ssn']
        required_fields_contract = ['date_effective', 'type_of_contract', 'collective_agreement', 'terms_of_employment', 'employment', 'type_of_employee', 'employer']
        required_fields_address = ['house_number', 'street', 'postal_code', 'city']
        required_fields_function = ['organizational_unit', 'date_effective', 'function_id', 'costcenter']
        required_fields_schedule = ['weekly_hours', 'parttime_percentage']
        required_fields_salary = ['type_of_salary', 'amount']

        allowed_fields = allowed_fields_person
        required_fields = required_fields_contract + required_fields_function + required_fields_schedule + required_fields_salary + required_fields_address + required_fields_person

        # Check if there are fields that are not allowed or fields missing that are required
        for field in data.keys():
            if field not in allowed_fields and field not in required_fields:
                return 'Field {field} is not allowed. Allowed fields are: {allowed_fields}'.format(field=field, allowed_fields=tuple(allowed_fields))
        for field in required_fields:
            if field not in data.keys():
                return 'Field {field} is required. Required fields are: {required_fields}'.format(field=field, required_fields=tuple(required_fields))

        body = {
            "AfasEmployee": {
                "Element": {
                    "@EmId": data['employee_ID'],  # Employee selector
                    "Objects": {
                        "KnPerson": {
                            "Element": {
                                "Fields": {
                                    "PadAdr": False,  # Postbus adres
                                    "AutoNum": False,  # Autonumber
                                    # Match existing employees on BSN [{"id":"0","description":"Zoek op BcCo (Persoons-ID)"},{"id":"1","description":"Burgerservicenummer"},{"id":"2","description":"Naam + voorvoegsel + initialen + geslacht"},{"id":"3","description":"Naam + voorvoegsel + initialen + geslacht + e-mail werk"},{"id":"4","description":"Naam + voorvoegsel + initialen + geslacht + mobiel werk"},{"id":"5","description":"Naam + voorvoegsel + initialen + geslacht + telefoon werk"},{"id":"6","description":"Naam + voorvoegsel + initialen + geslacht + geboortedatum"},{"id":"7","description":"Altijd nieuw toevoegen"}]
                                    "MatchPer": "1",
                                    "BcCo": data['employee_ID'],  # Employee ID
                                    "SeNm": data['last_name'],  # Search name
                                    "FiNm": data['first_name'],  # First Name
                                    "LaNm": data['last_name'],  # Last Name
                                    "SpNm": False,  # Birthname seperately
                                    "NmBi": data['last_name'],  # Birthname
                                    # Use of name [{"id":"0","description":"Birth name"},{"id":"1","description":"Partner's birth name + Birth name"},{"id":"2","description":"Partner birth name"},{"id":"3","description":"Birth name + Partner's birth name"}]
                                    "ViUs": "0",
                                    # Gender [{"id":"M","description":"Male"},{"id":"U","description":"Unknown"},{"id":"F","description":"Female"}]
                                    "ViGe": data['gender'],
                                    "PsNa": data['country'],  # Nationality
                                    "DaBi": data['date_of_birth'],  # Birth date
                                    "CoBi": data['country_of_birth'],  # Country of birth
                                    "RsBi": data['place_of_birth'],  # Place of birth
                                    "SoSe": data['ssn'],  # SSN
                                    "EmAd": data['email_work'],  # Company emailaddress
                                    "EmA2": data['email_home']  # Private emailaddress
                                },
                                "Objects": {
                                    "KnBasicAddressAdr": {
                                        "Element": {
                                            "Fields": {
                                                "CoId": data['country'],  # Country
                                                "PbAd": True,  # Postbusadres
                                                "Ad": data['street'],  # Street
                                                "HmNr": data['house_number'],  # Streetnumber
                                                "ZpCd": data['postal_code'],  # Postal code
                                                "Rs": data['city'],  # City
                                                "ResZip": True  # Lookup city with postal code
                                            }
                                        }
                                    },
                                    "KnBasicAddressPad": {
                                        "Element": {
                                            "Fields": {
                                                "CoId": data['country'],  # Country
                                                "PbAd": True,  # Postbusadres
                                                "Ad": data['street'],  # Street
                                                "HmNr": data['house_number'],  # Streetnumber
                                                "ZpCd": data['postal_code'],  # Postal code
                                                "Rs": data['city'],  # City
                                                "ResZip": True  # Lookup city with postal code
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        "AfasContract": {
                            "Element": {
                                "@DaBe": data['date_effective'],
                                "Fields": {
                                    "ClId": data['collective_agreement'],  # Cao - fixed
                                    "WcId": data['terms_of_employment'],  # Arbeidsvoorwaarde - Fixed op zoetwarenindustrie - 36 uur
                                    "ApCo": data['type_of_contract'],  # Type of contract
                                    "CmId": data['employer'],  # employer - fixed
                                    "EmMt": data['type_of_employee'],  # Type of employee (1=personeelslid)
                                    "ViEt": data['employment']  # Dienstbetrekking
                                }
                            }
                        },
                        "AfasOrgunitFunction": {
                            "Element": {
                                "@DaBe": data['date_effective'],  # Startdate organizational unit
                                "Fields": {
                                    "DpId": data['organizational_unit'],  # OE
                                    "FuId": data['function_id'],  # Function 0232=medewerk(st)er
                                    "CcId": data['costcarrier'],  # fixed on default: Profit
                                    "CrId": data['costcenter']  # Cost center
                                }
                            }
                        },
                        "AfasTimeTable": {
                            "Element": {
                                "@DaBg": data['date_effective'],  # Startdate Timetable
                                "Fields": {
                                    "StPa": True,  # Wisselend arbeidspatroon
                                    "HrWk": data['weekly_hours'],  # Weekly hours
                                    "PcPt": data['parttime_percentage']  # Parttime percentage
                                }
                            }
                        },
                        "AfasSalary": {
                            "Element": {
                                "@DaBe": data['date_effective'],  # Startdate salary
                                "Fields": {
                                    "SaPe": ['type_of_salary'],  # Sort of salary - fixed (V=vast)
                                    "EmSa": data['amount'],  # Salary amount
                                    "PtId": 5  # Period table - fixed (periode HRM)
                                }
                            }
                        }
                    }
                }
            }
        }

    def update_cost_center(self, data: dict, method: str, custom_fields={}):
        """
        This function updates HR cost centers with the AFAS updateconnect 'HrCosteCentre'.
        :param data: Deliver all the data which should be updated in list format. The data should at least contain the required_fields and can contain also the allowed fields
        :param method: Is a PUT for an update of an existing cost center. is a POST for an insert of a new cost center
        :param custom_fields: The custom fields in this dataset. Give the key of the field and the value. For example: {DFEDS8-DSF9uD-DDSA: 'Vrij veld'}
        :return: The status code from AFAS Profit
        """
        required_fields = ['cost_center_id', 'cost_center_description', 'employer_id', 'blocked']
        allowed_fields = ['cost_center_type']
        all_fields = required_fields + allowed_fields

        # Check if the fields in data exists in the required or allowed fields
        for field in data.keys():
            if field not in all_fields:
                raise ValueError('Field {} is not allowed. Allowed fields are: {}'.format(field, tuple(all_fields)))

        # Check if all the required_fields are present
        for field in required_fields:
            if field not in data.keys():
                raise ValueError('Field {} is required. Required fields are: {}'.format(field, tuple(required_fields)))

        if method != 'PUT' and method != 'POST' and method != 'DELETE':
            raise ValueError('Parameter method should be PUT, POST or DELETE (in uppercase)')

        # Do a delete call if the method is a delete. Delete do not need a body
        if method == 'DELETE':
            url = f"https://{self.environment}.{self.base_url}/profitrestservices/connectors/HrCostCentre/HrCostCentre/CmId,CrId,CrDs,Bl/{data['employer_id']},{data['cost_center_id']},{data['cost_center_description']},{data['blocked']}"
            base_body = {}
        else:
            url = 'https://{}.{}/profitrestservices/connectors/HrCostCentre'.format(self.environment, self.base_url)

            base_body = {
                "HrCostCentre": {
                    "Element": {
                        "Fields": {
                            "CmId": data['employer_id'],
                            "CrId": data['cost_center_id'],
                            "CrDs": data['cost_center_description'],
                            "Bl": data['blocked']
                        }
                    }
                }
            }

            # Now create a dict for all the allowed fields. This fields are not by default added to the base_body because they're not always present in the dataset
            fields_to_update = {}
            fields_to_update.update({"CrTy": data['cost_center_type']}) if 'cost_center_type' in data else fields_to_update

            # Also add custom_fields to the base_body.
            for key in custom_fields.keys():
                fields_to_update.update({key: custom_fields[key]})

            # Update the request body with update fields
            base_body['HrCostCentre']['Element']['Fields'].update(fields_to_update)

        headers = {
            'authorization': "AfasToken {0}".format(self.base64token),
            'content-type': "application/json",
            'cache-control': "no-cache"
        }

        update = requests.request(method, url, data=json.dumps(base_body), headers=headers)

        return update

    def update_cost_carrier(self, data: dict, method: str, custom_fields={}):
        """
        This function updates HR cost carriers with the AFAS updateconnect 'HrCosteCarrier'.
        :param data: Deliver all the data which should be updated in list format. The data should at least contain the required_fields and can contain also the allowed fields
        :param method: Is a PUT for an update of an existing cost carrier. is a POST for an insert of a new cost carrier
        :param custom_fields: The custom fields in this dataset. Give the key of the field and the value. For example: {DFEDS8-DSF9uD-DDSA: 'Vrij veld'}
        :return: The status code from AFAS Profit
        """
        required_fields = ['cost_carrier_id', 'cost_carrier_description', 'employer_id', 'blocked']
        allowed_fields = []
        all_fields = required_fields + allowed_fields

        # Check if the fields in data exists in the required or allowed fields
        for field in data.keys():
            if field not in all_fields:
                raise ValueError('Field {} is not allowed. Allowed fields are: {}'.format(field, tuple(all_fields)))

        # Check if all the required_fields are present
        for field in required_fields:
            if field not in data.keys():
                raise ValueError('Field {} is required. Required fields are: {}'.format(field, tuple(required_fields)))

        if method != 'PUT' and method != 'POST' and method != 'DELETE':
            raise ValueError('Parameter method should be PUT, POST or DELETE (in uppercase)')

        if method == 'DELETE':
            url = f"https://{self.environment}.{self.base_url}/profitrestservices/connectors/HrCostCarrier/HrCostCarrier/CmId,CcId,CcDs,Bl/{data['employer_id']},{data['cost_carrier_id']},{data['cost_carrier_description']},{data['blocked']}"
            base_body = {}
        else:
            url = 'https://{}.{}/profitrestservices/connectors/{}'.format(self.environment, self.base_url, 'HrCostCarrier')

            base_body = {
                "HrCostCarrier": {
                    "Element": {
                        "Fields": {
                            "CmId": data['employer_id'],
                            "CcId": data['cost_carrier_id'],
                            "CcDs": data['cost_carrier_description'],
                            "Bl": data['blocked']
                        }
                    }
                }
            }

            # Now create a dict for all the custom fields. This fields are not by default added to the base_body because they're not always present in the dataset
            fields_to_update = {}
            for key in custom_fields.keys():
                fields_to_update.update({key: custom_fields[key]})

            # Update the request body with update fields
            base_body['HrCostCarrier']['Element']['Fields'].update(fields_to_update)

        headers = {
            'authorization': "AfasToken {0}".format(self.base64token),
            'content-type': "application/json",
            'cache-control': "no-cache"
        }

        update = requests.request(method, url, data=json.dumps(base_body), headers=headers)

        return update

    def post(self, rest_type, updateconnector, data):
        url = 'https://{}.{}/profitrestservices/connectors/{}'.format(self.environment, self.base_url, updateconnector)

        headers = {
            'authorization': "AfasToken {0}".format(self.base64token),
            'content-type': "application/json",
            'cache-control': "no-cache"
        }

        update = requests.request(rest_type, url, data=data, headers=headers)

        return update
