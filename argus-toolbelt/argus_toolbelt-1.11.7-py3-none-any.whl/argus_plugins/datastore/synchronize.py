import csv

from argus_api.api.datastores.v1.store.store import put_data_store_entries, \
    delete_data_store_entries, get_entries_from_store

from argus_cli.helpers.log import log
from argus_cli.plugin import register_command
from argus_plugins import argus_cli_module
from argus_plugins.cases.utils import get_customer_id


def get_buffered_data(func):
    """

    :param func: The getter function for the data to be buffered
    :return: a generator with the data, the data is the ["data"] parameter of the response.
    """
    def ann(*args, **kwargs):

        buffer_size = 200

        offset = 0
        response = func(*args, limit=buffer_size, offset=offset, **kwargs)
        while offset < response["count"]:

            yield from response["data"]
            offset += buffer_size

            response = func(*args, limit=buffer_size, offset=offset, **kwargs)

    return ann


def set_data_with_buffer(func: callable, buffered_argument: str):
    """
    Decorator to send data in multiple batches
    :param func: the function to buffer
    :param buffered_argument: the keyword of the argument of func to actually buffer. Needs to be an iterable.
    :return: The new function
    """
    def buffered_function(*args, **kwargs):

        buffer = kwargs.pop(buffered_argument)

        sent_data = 0
        response = None

        buffer_size = 200
        for start in range(0, len(buffer), buffer_size):
            kwargs[buffered_argument] = buffer[start:start + buffer_size]
            response = func(*args, **kwargs)

        return response

    return buffered_function


def datastore_data(data: str) -> dict:
    """Turns a CSV string into key:value pairs"""
    try:
        with open(data, 'r') as fp:
            data = fp.readlines()
    except IOError:
        data = data.split("\n")

    # Remove any comments
    data = filter(lambda line: not line.startswith('#') and len(line) and not line.isspace(), data)
    csv_reader = csv.reader(data)

    entries = {}
    for row in csv_reader:
        key = row[0].strip()
        value = row[1].strip() if len(row) > 1 else None

        if key in entries:
            log.warn("The key \"{key}\" exists multiple times in the data. Overriding with new value")

        entries[key] = value

    return entries


@register_command(extending="datastores", module=argus_cli_module)
def delete(datastore: str, keys: list, customer: get_customer_id = None):
    """Deletes given entries from the datastore.

    :param datastore: The datastore to modify
    :param customer: The customer to affect
    :param keys: Keys to delete. A file can be provided with the @-prefix (eg. @/tmp/datastore_delete.txt).
    """
    buffered_delete = set_data_with_buffer(delete_data_store_entries,buffered_argument="key")
    result = buffered_delete(dataStore=datastore, customerID=customer, key=keys)

    print("Successfully deleted {amount} entries".format(amount=result["count"]))


@register_command(extending="datastores", module=argus_cli_module)
def update(datastore: str, data: datastore_data, customer: get_customer_id = None, default_value: str = "N/A"):
    """Adds or update entries from the data"""
    entries = [{"key": key, "value": value or default_value} for key, value in data.items()]
    buffered_put = set_data_with_buffer(put_data_store_entries, buffered_argument="entries")
    response = buffered_put(dataStore=datastore, entries=entries, customerID=customer)

    print("Successfully updated {amount} entries".format(amount=response["size"]))


@register_command(extending="datastores", module=argus_cli_module)
def sync(datastore: str, data: datastore_data, customer: get_customer_id = None, default_value: str = "N/A"):
    """Makes sure the datastore is a 1:1 match with the given data (for a given customer, if any).

    """
    delete_entries = []  # Items to delete
    update_entries = {}  # Items to update/add
    existing_entries = {}  # Entries that already exist

    fetched_entries = get_buffered_data(get_entries_from_store)(datastore)

    for entry in fetched_entries:
        if customer and entry["customer"]["shortName"] != customer:
            continue

        key = entry["key"]
        value = entry["value"] or default_value

        existing_entries[key] = value
        if key not in data:
            delete_entries.append(key)

    for key, value in data.items():
        if value != existing_entries.get(key):
            update_entries[key] = value

    if update_entries:
        update(datastore, update_entries, customer)
    if delete_entries:
        delete(datastore, delete_entries, customer)
