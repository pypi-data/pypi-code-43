import json

import requests

from quandoo.Error import PoorResponse
from quandoo.QuandooModel import PrettyClass, QuandooModel, QuandooDatetime, urljoin


class ReservationEnquiry(QuandooModel):

    def __init__(self, data, agent):
        self.id = data["id"]
        self.merchantId = data["merchantId"]
        self.customerId = data["customerId"]
        self.capacity = data["capacity"]
        self.startTime = data["startDateTime"]
        self.endTime = data["endDateTime"]
        self.status = data["status"]

        self.agent = agent

        super().__init__(data)

    def __change_status(self, new_status):
        data = {
            "status": new_status
        }
        request = urljoin(self.agent.url, "reservation-enquiries", self.id)
        response = requests.patch(request, headers=self.agent.headers, json=data)

        if response.status_code == 200:
            self.status = new_status
            return

        raise PoorResponse(response.status_code, json.loads(response.text), request)

    def get_messages(self):
        request = urljoin(self.agent.url, "reservation-enquiries", self.id, "messages")
        response = requests.get(request)

        if response.status_code == 200:
            return [Message(i) for i in json.loads(response.text)["messages"]]

        raise PoorResponse(response.status_code, json.loads(response.text), request)


class NewReservationEnquiry(QuandooModel):

    def __init__(self, data, agent):
        self.id = data["reservationEnquiry"]["id"]
        self.customerId = data["customer"]["id"]

        self.agent = agent

        super().__init__(data)

    def get_reservation_enquiry(self):
        return self.agent.get_reservation_enquiry(self.id)


class Message(PrettyClass):

    def __init__(self, data):
        self.senderType = data["senderType"]
        self.message = data["message"]
        self.creationDate = QuandooDatetime.parse_str_qdt(data["creationDate"])
