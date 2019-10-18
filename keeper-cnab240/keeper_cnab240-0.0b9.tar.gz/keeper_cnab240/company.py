from keeper_cnab240.banks.bank_account import BankAccount


class Company:
    def __init__(self, name, document):
        self.name = name
        
        self.document_type = self.get_company_document_type(document)
        self.document = document

        self.bank_account = None

        # address
        self.street = None
        self.number = None
        self.complement = None
        self.district = None
        self.city = None
        self.state = None
        self.zipcode = None
        self.country = None
    
    def set_bank_acccount(self, bank_code, agency, account, account_digit):
        self.bank_account = BankAccount(bank_code, agency, account, account_digit)
    
    def set_address(self, street, number, complement, district, city, state, zipcode=None, country='BR'):
        self.street = street
        self.number = number
        self.complement = complement
        self.district = district
        self.city = city
        self.state = state
        self.zipcode = zipcode
        self.country = country
    
    @staticmethod
    def get_company_document_type(document_number):
        return 'cnpj' if len(str(document_number)) == 14 else 'cpf'
