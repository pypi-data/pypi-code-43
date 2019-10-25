import json
from datetime import timedelta

import requests

from quandoo.Customer import Customer
from quandoo.Error import PoorResponse
from quandoo.QuandooModel import QuandooModel, QuandooDatetime, urljoin
from quandoo.Reservation import Reservation, NewReservation
from quandoo.ReservationEnquiry import NewReservationEnquiry


class Merchant(QuandooModel):

    def __init__(self, data, agent):
        self.id = data["id"]
        self.name = data["name"]
        address_vals = [i if i in data["location"]["address"].keys() else "" for i in ['number', 'street', 'city', 'country']]
        address_vals[1] = " ".join(address_vals[:1])
        address_vals = address_vals[1:]
        self.address = ", ".join(address_vals)

        self.agent = agent

        super().__init__(data)

    def get_customers(self, offset=0, limit=100, modified_since: QuandooDatetime=None, modified_until: QuandooDatetime=None):
        params = {
            "offset": offset,
            "limit": limit
        }
        if modified_since is not None:
            params["modifiedSince"] = modified_since.get_urldt()
        if modified_until is not None:
            params["modifiedUntil"] = modified_until.get_urldt()

        request = urljoin(self.agent.url, "merchants", self.id, "customer")
        response = requests.get(request, headers=self.agent.headers, params=params)

        if response.status_code == 200:
            return [Customer(i, self.agent) for i in json.loads(response.text)["result"]]

        raise PoorResponse(response.status_code, json.loads(response.text), request)

    def get_reservations(self, offset=0, limit=100, earliest=None, latest=None):
        params = {
            "offset": offset,
            "limit": limit
        }
        if earliest is not None:
            params["earliest"] = earliest.get_urldt()
        if latest is not None:
            params["latest"] = latest.get_urldt()

        request = urljoin(self.agent.url, "merchants", self.id, "reservations")
        response = requests.get(request, headers=self.agent.headers, params=params)

        if response.status_code == 200:
            return [Reservation(i, self.agent) for i in json.loads(response.text)["reservations"]]

        raise PoorResponse(response.status_code, json.loads(response.text), request)

    def get_available_times(self, pax: int, qdt: QuandooDatetime, duration=2, area_id=None):
        params = {
            "agentId": self.agent.agent_id,
            "capacity": pax,
            "fromTime": qdt.datetime.strftime("%H:%M"),
            "toTime": (qdt.datetime + timedelta(hours=duration)).strftime("%H:%M")
        }
        if area_id is not None:
            params["areaId"] = area_id

        request = urljoin(self.agent.url, "merchants", self.id, "availabilities", qdt.datetime.strftime("%Y-%m-%d"), "times")
        response = requests.get(request, headers=self.agent.headers, params=params)

        if response.status_code == 200:
            return [QuandooDatetime.parse_str_qdt(i["dateTime"]) for i in json.loads(response.text)["timeSlots"]]

        raise PoorResponse(response.status_code, json.loads(response.text), request)

    def is_available(self, pax: int, qdt: QuandooDatetime, duration=2, area_id=None):
        return qdt in self.get_available_times(pax, qdt, duration, area_id)

    def get_reviews(self, offset=0, limit=10):
        params = {
            "offset": offset,
            "limit": limit
        }

        request = urljoin(self.agent.url, "merchants", self.id, "reviews")
        response = requests.get(request, headers=self.agent.headers, params=params)

        if response.status_code == 200:
            return json.dumps(json.loads(response.text), indent=2)

        raise PoorResponse(response.status_code, json.loads(response.text), request)

    def create_reservation(self, customer, pax: int, qdt: QuandooDatetime, area_id=None, order_id=None, extra_info=None):
        data = {
            "reservation": {
                "merchantId": self.id,
                "capacity": pax,
                "dateTime": qdt.get_qdt()
            },
            "customer": customer.to_json(),
            "tracking": {
                "agent": {
                    "id": self.agent.agent_id
                }
            }
        }
        if area_id is not None:
            data["reservation"]["areaId"] = area_id
        if order_id is not None:
            data["reservation"]["orderId"] = order_id
        if extra_info is not None:
            data["reservation"]["extraInfo"] = json.dumps(extra_info)

        request = urljoin(self.agent.url, "reservations")
        response = requests.put(request, headers=self.agent.headers, json=data)

        if response.status_code == 200:
            return NewReservation(json.loads(response.text), self.agent)

        raise PoorResponse(response.status_code, json.loads(response.text), request)

    def create_reservation_enquiry(self, customer, pax: int, start_qdt: QuandooDatetime, end_qdt: QuandooDatetime, message: str):
        data = {
            "reservationEnquiry": {
                "merchantId": self.id,
                "capacity": pax,
                "startDateTime": start_qdt.get_qdt(),
                "endDateTime": end_qdt.get_qdt(),
                "message": message
            },
            "customer": customer.to_json(),
            "tracking": {
                "agent": {
                    "id": self.agent.agent_id
                }
            }
        }

        request = urljoin(self.agent.url, "reservation-enquiries")
        response = requests.put(request, headers=self.agent.headers, json=data)

        if response.status_code == 201:
            return NewReservationEnquiry(json.loads(response.text), self.agent)

        raise PoorResponse(response.status_code, json.loads(response.text), request)
