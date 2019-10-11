__version__ = '0.9.0'

from influxdb import InfluxDBClient
import geohash2
import logging
from geolite2 import geolite2
import click
import re
from typing import List, Dict, Union
from hashlib import sha256
from base64 import b64encode
from datetime import datetime

Event = Dict[str,Union[str, Dict]]

logger = logging.getLogger('ringserverstats')
logger.setLevel(logging.INFO)
# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)

def parse_ringserver_log(filename: str) -> List[Event]:
    """
    Read a txlog file and parses information.
    Returns a list of events (dictionary)
    """
    logstart_pattern = r'START CLIENT (?P<hostname>\b(?:[0-9A-Za-z][0-9A-Za-z-]{0,62})(?:\.(?:[0-9A-Za-z][0-9A-Za-z-]{0,62}))*(\.?|\b)) \[(?P<ip>(?<![0-9])(?:(?:[0-1]?[0-9]{1,2}|2[0-4][0-9]|25[0-5])[.](?:[0-1]?[0-9]{1,2}|2[0-4][0-9]|25[0-5])[.](?:[0-1]?[0-9]{1,2}|2[0-4][0-9]|25[0-5])[.](?:[0-1]?[0-9]{1,2}|2[0-4][0-9]|25[0-5]))(?![0-9]))\] \((?P<agent>.*)\) @ (?P<timestamp>[0-9]+-[0-9]+-[0-9]+ (?:2[0123]|[01]?[0-9]):(?:[0-5][0-9]):(?:[0-5][0-9])).*'
    logevent_pattern = '(?P<network>[A-Z0-9]*)_(?P<station>[A-Z0-9]*)_(?P<location>[A-Z0-9]*)_(?P<channel>[A-Z0-9]*)/MSEED (?P<bytes>[0-9]+) (?P<packets>[0-9]+)'
    georeader = geolite2.reader()
    process_events = True

    events = []
    with open(filename, 'r', encoding='ISO-8859-1') as file:
        linecount = 0
        for log in file:
            linecount +=1
#            logger.debug(filename + ":"+str(linecount) +" "+ log)
            # log line exemple: START CLIENT 52.red-88-2-197.staticip.rima-tde.net [88.2.197.52] (SeedLink|SeedLink Client) @ 2016-11-28 00:00:00 (connected 2016-11-26 16:37:07) TX
            if log.startswith('START CLIENT'):
                events_data = re.search(logstart_pattern, log)
                if events_data == None:
                    logger.warning("Unable to parse START log at %s:%d : %s"%(filename, linecount, log))
                    process_events = False
                    continue
                events_data = events_data.groupdict()
                location = georeader.get(events_data['ip'])
                # store time as epoch
                events_data['timestamp'] = int(datetime.strptime(events_data['timestamp'], '%Y-%m-%d %H:%M:%S').timestamp())
                # hash location and get the city name
                if location != None:
                    events_data['geohash'] = geohash2.encode(location['location']['latitude'], location['location']['longitude'])
                    try:
                        events_data['countrycode'] = location['country']['iso_code']
                    except KeyError:
                        events_data['countrycode'] = ''
                    try:
                        events_data['city'] = location['city']['names']['en']
                    except KeyError:
                        events_data['city'] = ''

                else:
                    logger.warning("No location available at %s:%d : %s\nAssuming it was in Grenoble"%(filename, linecount, log))
                    events_data['geohash'] = 'u0h0fpnzj9ft'
                    events_data['city'] = 'Grenoble'
                    events_data['countrycode'] = 'FR'
                # hash hostname
                events_data['hostname'] = b64encode(sha256(events_data['hostname'].encode()).digest())[:12] # overcomplicated oneliner to hash the hostname
                logger.debug(events_data)
            elif log.startswith('END CLIENT'):
                process_events = True
            elif process_events:
                # line exemple :
                # FR_SURF_00_HHZ/MSEED 21511168 42014
                event = re.search(logevent_pattern, log)
                if event == None:
                    logger.warning("Unable to parse log at %s:%d : %s"%(filename, linecount, log))
                    continue
                event = event.groupdict()
                logger.debug(event)
                events.append({**events_data, **event})
    return(events)

def influxdb_send_data(idbclient: InfluxDBClient, data: List[Dict]) -> bool:
    """
    Sends data into influxdb
    """
    try:
        idbclient.write_points(data, time_precision='s', retention_policy='short', batch_size=10000)
    except Exception as e:
        logger.error("Unexpected error writing data to influxdb")
        logger.error(e)
        return False
    return True

@click.command()
@click.option('--influxdbhost',  'dbhost',   help='Influxdb hostname or adress.', envvar='INFLUXDB_HOST')
@click.option('--influxdbport',  'dbport',   help='Influxdb port. Default: 8086', envvar='INFLUXDB_PORT', default=8086, type=click.INT)
@click.option('--influxdbdb',    'dbname',   help='Influxdb database.', envvar='INFLUXDB_DB')
@click.option('--ssl/--no-ssl',              help='Should we connect with SSL ?', default=True, envvar='INFLUXDB_SSL')
@click.option('--verifyssl/--no-verifyssl',  help='Should the connexion do SSL check ?', default=False, envvar='INFLUXDB_VERIFY_SSL')
@click.option('--influxdbuser',  'dbuser',   help='Influxdb user', envvar='INFLUXDB_USER')
@click.option('--influxdbpass',  'password', help='Influxdb pass', envvar='INFLUXDB_PASS')
@click.option('--measurement',  'measurement', help='Influxdb measurement', envvar='INFLUXDB_MEASUREMENT', default='ringserver')
@click.argument('files', type=click.Path(exists=True), nargs=-1)
def cli(dbhost: str, dbport: int, dbname: str, verifyssl: bool, dbuser: str, password: str, ssl: bool, measurement: str, files: List):
    for f in files:
        influxdb_json_data = []
        logger.info("Opening file %s"%(f))
        # Parsing events from a logfile
        lastevent_time = 0
        firstevent_time = 0
        for event in  parse_ringserver_log(f):
            # get the first event time
            if firstevent_time == 0 or firstevent_time > event['timestamp']:
                firstevent_time = event['timestamp']
            # get the last event time
            if lastevent_time == 0 or lastevent_time < event['timestamp']:
                lastevent_time = event['timestamp']
            # Constructing an influxdb data from the event
            influxdb_json_data.append(
                {"measurement": measurement,
                 "tags": {
                     "network": event['network'],
                     "station": event['station'],
                     "location": event['location'],
                     "channel": event['channel'],
                     "city":    event['city'],
                     "country": event['countrycode'],
                     "agent":   event['agent'],
                     "client": event['hostname']
                 },
                 "time": event['timestamp'],
                 "fields": {
                     "bytes": int(event['bytes']),
                     "geohash": event['geohash']   # high cardinality, do not index
                 }
                }
            )

        if dbhost != None :
            logger.info("Sending %d metrics"%len(influxdb_json_data))

            try:
                logger.debug("host     = "+dbhost)
                logger.debug("database = "+dbname)
                logger.debug("username = "+dbuser)
                client = InfluxDBClient(host     = dbhost,
                                        port     = dbport,
                                        database = dbname,
                                        username = dbuser,
                                        password = password,
                                        ssl      = ssl,
                                        verify_ssl = verifyssl
                )
                influxdb_send_data(client, influxdb_json_data)
                client.close()
            except Exception as e:
                logger.error("Error writing to influxdb %s:%d database %s"%(dbhost,dbport,dbname))
                logger.error(e)
    client.close()
