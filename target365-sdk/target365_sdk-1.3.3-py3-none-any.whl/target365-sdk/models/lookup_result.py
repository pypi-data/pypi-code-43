class LookupResult:
    def fromDict(self, dict):
        """
        Covnerts json deserialized dict object into LookupResult
        :dict: dict
        """
        self.created = dict["created"]
        self.msisdn = dict["msisdn"]
        self.landline = dict["landline"]
        self.firstName = dict["firstName"]
        self.middleName = dict["middleName"]
        self.lastName = dict["lastName"]
        self.companyName = dict["companyName"]
        self.companyOrgNo = dict["companyOrgNo"]
        self.streetName = dict["streetName"]
        self.streetNumber = dict["streetNumber"]
        self.streetLetter = dict["streetLetter"]
        self.zipCode = dict["zipCode"]
        self.city = dict["city"]
        self.gender = dict["gender"]
        self.dateOfBirth = dict["dateOfBirth"]
        self.age = dict["age"]
        self.deceasedDate = dict["deceasedDate"]
