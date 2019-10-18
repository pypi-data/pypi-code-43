from keeper_cnab240.file_section import FileSection


class SegmentSection(FileSection):
    def __init__(self, section_name, data, attributes, header_class=None, footer_class=None):
        super().__init__(section_name, data, attributes)
        if header_class:
            self.header = header_class()
        if footer_class:
            self.footer = footer_class()
        self.company = None
    
    def set_company(self, company):
        self.company = company
        self.data['company_document_type'] = self.bank.get_company_document_id(company.document_type)
        self.data['company_document_number'] = company.document
        self.data['company_agency'] = company.bank_account.agency
        self.data['company_account'] = company.bank_account.account
        self.data['company_dac'] = company.bank_account.digit
        self.data['company_name'] = company.name
        self.data['company_address_street'] = company.street
        self.data['company_address_number'] = company.number
        self.data['company_address_complement'] = company.complement
        self.data['company_address_city'] = company.city
        self.data['company_address_zipcode'] = company.zipcode
        self.data['company_address_state'] = company.state
    
    def set_header(self, header):
        self.header = header
        self.header.set_bank(self.bank)
        self.header.set_company(self.company)
        self.header.set_data(self.data)
    
    def get_header_line(self):
        if not self.header.data:
            self.set_header(self.header)
        return self.header.to_line()
    
    def set_footer(self, footer):
        self.footer = footer
        self.footer.set_bank(self.bank)
        self.footer.set_company(self.company)
        self.footer.set_data(self.data)
    
    def get_footer_line(self):
        if not self.footer.data:
            self.set_footer(self.footer)
        return self.footer.to_line()
