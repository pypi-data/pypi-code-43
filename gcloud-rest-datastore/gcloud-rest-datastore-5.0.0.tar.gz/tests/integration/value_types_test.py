"""Make sure all value types are serialized/deserialized correctly"""
import pytest
from gcloud.rest.auth import BUILD_GCLOUD_REST  # pylint:disable=no-name-in-module
from gcloud.rest.datastore import Datastore
from gcloud.rest.datastore import Key
from gcloud.rest.datastore import LatLng
from gcloud.rest.datastore import PathElement

# Selectively load libraries based on the package
if BUILD_GCLOUD_REST:
    from requests import Session
else:
    from aiohttp import ClientSession as Session


#@pytest.mark.asyncio  # type: ignore
def test_geo_point_value(creds     , kind     , project     )        :
    key = Key(project, [PathElement(kind)])

    with Session() as s:
        ds = Datastore(project=project, service_file=creds, session=s)

        allocatedKeys = ds.allocateIds([key], session=s)
        ds.reserveIds(allocatedKeys, session=s)

        props_insert = {'location': LatLng(49.2827, 123.1207)}
        ds.insert(allocatedKeys[0], props_insert, session=s)
        actual = ds.lookup([allocatedKeys[0]], session=s)
        assert actual['found'][0].entity.properties == props_insert
