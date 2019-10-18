from .model import Model

class LookupResult(Model):

    def _accepted_params(self):
        return [
            'created',
            'msisdn',
            'landline',
            'firstName',
            'middleName',
            'lastName',
            'companyName',
            'companyOrgNo',
            'streetName',
            'streetNumber',
            'streetLetter',
            'zipCode',
            'city',
            'gender',
            'dateOfBirth',
            'age',
            'deceasedDate',
        ]
