from datetime import datetime, timedelta
from .airport_time_zone import airport_to_timezone
import time
import pytz

def parse_prev_flight(flight):
    prev_f_number = prev_f_iata = None
    if flight.find('.//AircraftPreviousFlightLeg'):
        prev_f_number = flight.find('.//AircraftPreviousFlightLeg//FlightNumber').text
        prev_f_iata = flight.find('.//AircraftPreviousFlightLeg//AirlineCode').text

    return prev_f_number, prev_f_iata

def parse_flight_codeshares(flight):
    codeshares = None
    if flight.findall('.//CodeShare'):
        codes = [
            code.find('.//AirlineCode').text + \
            code.find('FlightNumber').text \
            for code in flight.findall('.//CodeShare')
        ]
        codeshares = ", ".join(codes)

    return codeshares

def parse_gate_info(lookup_key, flight):
    terminal = flight.find(f'.//{lookup_key}//Terminal').text \
        if flight.find(f'.//{lookup_key}//Terminal') is not None else ''

    gate = flight.find(f'.//{lookup_key}//Gate').text \
        if flight.find(f'.//{lookup_key}//Gate') is not None else ''

    baggage = flight.find(f'.//{lookup_key}//Baggage').text \
        if flight.find(f'.//{lookup_key}//Baggage') is not None else ''

    print(f'terminal: {terminal}, gate: {gate}, baggage: {baggage}')
    return terminal, gate, baggage


def convert_oag_status_to_normal_form(status):
    if status in ['scheduled', 'proposed']:
        return 'scheduled'
    elif status in ['outgate', 'inair', 'notakeoffinfo']:
        return 'en route'
    elif status in ['landed', 'ingate']:
        return 'arrived'
    else:
        return status


def parse_airport_info(lookup_key, flight):
    return flight.find(f'.//{lookup_key}//AirportCode').text, \
           flight.find(f'.//{lookup_key}//AirportName').text, \
           flight.find(f'.//{lookup_key}//CountryId').text


def time_to_seconds_format(tm):
    tm = time.strptime(tm, '%H:%M:%S')
    return timedelta(
        hours=tm.tm_hour, minutes=tm.tm_min
    ).seconds


def parse_od_scheduled_timestamp(lookup_key, flight):
    sch_datetime_elem = flight.find(f'.//{lookup_key}//Scheduled/..')
    scheduled_utc_date = sch_datetime_elem.find('Date').attrib['utc']
    scheduled_local_date = sch_datetime_elem.find('Date').text
    scheduled_utc_time = sch_datetime_elem.find('Time').attrib['utc']
    scheduled_local_time = sch_datetime_elem.find('Time').text

    scheduled_utc_datetime = datetime.strptime(
        scheduled_utc_date + ' ' + scheduled_utc_time, '%Y-%m-%d %H:%M:%S'
    )
    scheduled_local_datetime = datetime.strptime(
        scheduled_local_date + ' ' + scheduled_local_time, '%Y-%m-%d %H:%M:%S'
    )

    return scheduled_utc_datetime, scheduled_local_datetime


def parse_od_actual_timestamp(lookup_key, flight):
    actual_local_gatetime, actual_local_runway, \
        actual_utc_gatetime, actual_utc_runway = None, None, None, None

    datetime_elements = flight.findall(f'.//{lookup_key}//Actual/..')

    for date in datetime_elements:
        if date.find('GateTime') is not None:
            actual_local_gatetime_date = date.find('Date').text
            actual_utc_gatetime_date = date.find('Date').attrib['utc']
            actual_local_gatetime_time = date.find('Time').text
            actual_utc_gatetime_time = date.find('Time').attrib['utc']
            actual_local_gatetime = datetime.strptime(
                actual_local_gatetime_date + ' ' + actual_local_gatetime_time, '%Y-%m-%d %H:%M:%S'
            )
            actual_utc_gatetime = datetime.strptime(
                actual_utc_gatetime_date + ' ' + actual_utc_gatetime_time, '%Y-%m-%d %H:%M:%S'
            )

        if date.find('RunwayTime') is not None:
            actual_local_runway_date = date.find('Date').text
            actual_utc_runway_date = date.find('Date').attrib['utc']
            actual_local_runway_time = date.find('Time').text
            actual_utc_runway_time = date.find('Time').attrib['utc']

            actual_local_runway = datetime.strptime(
                actual_local_runway_date + ' ' + actual_local_runway_time, '%Y-%m-%d %H:%M:%S'
            )
            actual_utc_runway = datetime.strptime(
                actual_utc_runway_date + ' ' + actual_utc_runway_time, '%Y-%m-%d %H:%M:%S'
            )

    return actual_local_runway, actual_local_gatetime, actual_utc_gatetime, actual_utc_runway


def calculate_time_zone_using_offset(utc_datetime, local_datetime, airport, country):
    if (airport in airport_to_timezone):
        return airport_to_timezone[airport]

    utc_day_int = utc_datetime.day
    local_day_int = local_datetime.day
    day_difference = local_day_int - utc_day_int

    utc_hour_int = utc_datetime.hour
    local_hour_int = local_datetime.hour
    hour_difference = local_hour_int - utc_hour_int

    utc_min_int = utc_datetime.minute
    local_min_int = local_datetime.minute
    min_difference = local_min_int - utc_min_int

    utc_offset = timedelta(days=day_difference, hours=hour_difference, minutes=min_difference)
    now = datetime.now(pytz.utc)  # current time

    return [tz.zone for tz in map(pytz.timezone, pytz.country_timezones[country.lower()])
            if now.astimezone(tz).utcoffset() == utc_offset][0]
