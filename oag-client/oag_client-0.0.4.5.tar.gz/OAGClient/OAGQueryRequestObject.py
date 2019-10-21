class OAGQueryRequestObject:
    def __init__(self):
        self.aircraft_id = ""
        self.departure_airport = ""
        self.arrival_airport = ""
        self.departure_date = ""
        self.departure_hour = ""
        self.arrival_hour = ""
        self.airline = ""

    def __str__(self):
        aircraft_id = "" if self.aircraft_id == "" else "ACID={}&".format(self.aircraft_id)
        departure_airport = "" if self.departure_airport == "" else "DEPAP={}&".format(self.departure_airport)
        arrival_airport = "" if self.arrival_airport == "" else "ARRAP={}&".format(self.arrival_airport)
        departure_date = "" if self.departure_date == "" else "DEPDATE={}&".format(self.departure_date)
        departure_hour = "" if self.departure_hour == "" else "DEPHR={}&".format(self.departure_hour)
        arrival_hour = "" if self.arrival_hour == "" else "ARRHR={}&".format(self.arrival_hour)
        airline = "" if self.airline == "" else "AL={}&".format(self.airline)

        return "{}{}{}{}{}{}{}".format(aircraft_id, departure_airport, arrival_airport, departure_date,
                                             departure_hour, arrival_hour, airline)