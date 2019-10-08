'''
Export an STL
==============

Demos 307 redirects with the Onshape API
'''

from onshape_client.client import Client
from onshape_client.onshape_url import OnshapeElement, ConfiguredOnshapeElement
from onshape_client.units import u

def test_export_stl(client, cube):

    if isinstance(cube, str):
        cube = ConfiguredOnshapeElement(cube)

    # get the STL export
    stl = client.part_studios_api.export_stl1(cube.did, cube.wvm, cube.wvmid, cube.eid, _preload_content=False)

    print("Resulting STL data (unconfigured): \n" + stl.data.decode("UTF-8"))

    cube.update_current_configuration({'size': 40 * u.inch, 'edge_configuration': 'chamfered'})

    # get the STL export
    stl = client.part_studios_api.export_stl1(cube.did, cube.wvm, cube.wvmid, cube.eid, configuration=cube.get_configuration_string(), _preload_content=False)

    print("Resulting STL data (configured): \n" + stl.data.decode("UTF-8"))

if __name__ == '__main__':
    test_export_stl(Client(), "https://cad.onshape.com/documents/cca81d10f239db0db9481e6f/v/aaa25d18038e06f0b2964e2d/e/69c9eedda86512966b20bc90")