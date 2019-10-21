import requests
import xml.etree.ElementTree as ET
from cacheout import Cache
from .flight_view_helper import *


class Client:
    def __init__(self, username, password):
        self.URL = "http://xml.flightview.com/fvDemoConsOOOI/fvxml.exe?"
        self.username = username
        self.password = password
        self.cache = Cache(maxsize=256, ttl=300, timer=time.time, default=None)

    def make_request(self, oag_request_object):
        username = "" if self.username == "" else "a={}".format(self.username)
        password = "" if self.password == "" else "b={}".format(self.password)

        request_string = "{}&{}&{}".format(username, password, oag_request_object)
        response = requests.get(self.URL+request_string)

        if response.status_code == 200:
            return self.xml_to_dict(response)
        else:
            return {"error": response.status_code, "content": response.content}


    def fetch_from_cache(self, provider_id):
        flight = self.cache.get(provider_id)
        return flight

    def xml_to_dict(self, xml_response):
        root = ET.fromstring(xml_response.content)

        flights = []
        for flight in root.iter('Flight'):

            if flight.find('.//CommercialAirline') is None: continue

            provider = 'oag'
            provider_id = flight.attrib['FlightId']
            f_number = flight.find('.//FlightNumber').text
            airline_iata_code = flight.find('.//AirlineCode').text
            airline_name = flight.find('.//AirlineName').text
            origin_city = flight.find('.//Departure//CityName').text.lower()
            dest_city = flight.find('.//Arrival//CityName').text.lower()
            aircraft_type = flight.find('.//AircraftType').text
            status = flight.find('.//FlightStatus/').tag
            filed_ete = time_to_seconds_format(
                flight.find('.//FlightDuration//Time').text
            )
            tail_number = flight.find('.//TailNumber').text \
                if flight.find('.//TailNumber') is not None else ''

            prev_f_number, prev_f_iata= parse_prev_flight(flight)
            codeshares = parse_flight_codeshares(flight)

            origin_airport_code, origin_airport_name, origin_airport_country = \
                parse_airport_info('Departure', flight)

            dest_airport_code, dest_airport_name, dest_airport_country = \
                parse_airport_info('Arrival', flight)

            origin_scheduled_utc_datetime, origin_scheduled_local_datetime = \
                parse_od_scheduled_timestamp('Departure', flight)

            dest_scheduled_utc_datetime, dest_scheduled_local_datetime = \
                parse_od_scheduled_timestamp('Arrival', flight)

            origin_actual_runway_datetime, origin_actual_gatetime_datetime, \
                origin_actual_utc_gatetime_datetime, origin_actual_utc_runway_datetime = \
                parse_od_actual_timestamp('Departure', flight)

            dest_actual_runway_datetime, dest_actual_gatetime_datetime, \
                dest_actual_utc_gatetime_datetime, dest_actual_utc_runway_datetime = \
                parse_od_actual_timestamp('Arrival', flight)

            origin_terminal, origin_gate, _ = parse_gate_info('Departure', flight)
            dest_terminal, dest_gate, dest_baggage = parse_gate_info('Arrival', flight)

            origin_delay_reason = flight.find('.//Departure//DelayReason//Code').text \
                if flight.find('.//Departure//DelayReason//Code') is not None else ''
            dest_delay_reason = flight.find('.//Arrival//DelayReason//Code').text \
                if flight.find('.//Arrival//DelayReason//Code') is not None else ''

            origin_tz = calculate_time_zone_using_offset(
                origin_scheduled_utc_datetime, origin_scheduled_local_datetime,
                origin_airport_code, origin_airport_country
            )
            dest_tz = calculate_time_zone_using_offset(
                dest_scheduled_utc_datetime, dest_scheduled_local_datetime,
                dest_airport_code, dest_airport_country
            )

            formatted_resp = {
                'flight': {
                    'tail_number': tail_number,
                    'number': f_number,
                    'airline_name': airline_name,
                    'airline_iata': airline_iata_code,
                    'origin_airport_name': origin_airport_name,
                    'dest_airport_name': dest_airport_name,
                    'origin_airport_code': origin_airport_code,
                    'dest_airport_code': dest_airport_code,
                    'origin_city': origin_city,
                    'dest_city': dest_city,
                    'origin_scheduled_dep': origin_scheduled_local_datetime,
                    'origin_scheduled_dep_utc': origin_scheduled_utc_datetime,
                    'dest_scheduled_arrival': dest_scheduled_local_datetime,
                    'dest_scheduled_arrival_utc': dest_scheduled_utc_datetime,
                    'origin_tz': origin_tz,
                    'dest_tz': dest_tz,
                    'origin_actual_dep': origin_actual_gatetime_datetime,
                    'origin_actual_dep_utc': origin_actual_utc_gatetime_datetime,
                    'dest_actual_arrival': dest_actual_gatetime_datetime,
                    'dest_actual_arrival_utc': dest_actual_utc_gatetime_datetime,
                    'origin_actual_dep_runway': origin_actual_runway_datetime,
                    'origin_actual_dep_runway_utc': origin_actual_utc_runway_datetime,
                    'dest_actual_arrival_runway': dest_actual_runway_datetime,
                    'dest_actual_arrival_runway_utc': dest_actual_utc_runway_datetime,
                    'origin_country': origin_airport_country,
                    'dest_country': dest_airport_country,
                    'origin_delay_reason': origin_delay_reason,
                    'dest_delay_reason': dest_delay_reason,
                    'origin_terminal': origin_terminal,
                    'dest_terminal': dest_terminal,
                    'dest_baggage': dest_baggage,
                    'origin_gate': origin_gate,
                    'dest_gate': dest_gate,
                    'provider': provider,
                    'provider_id': provider_id,
                    'codeshares': codeshares,
                    'filed_ete': filed_ete,
                    'aircraft_type': aircraft_type,
                    'status': convert_oag_status_to_normal_form(status.lower()),
                },
                'prev_flight': {
                    'number': prev_f_number,
                    'iata': prev_f_iata,
                }
            }

            self.cache.set(formatted_resp['flight']['provider_id'], formatted_resp)

            flights.append(formatted_resp)

        return flights