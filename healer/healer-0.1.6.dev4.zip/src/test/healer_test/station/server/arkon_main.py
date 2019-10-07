"""
Start flask app in development mode
"""

from healer.station.server import config
from healer.station.server.arkon import FlaskBuilder
from healer.station.server.support.arkon import PackageResourceExt

if __name__ == '__main__':

    app = FlaskBuilder.produce_app(config.DevsConfig)

    # custom resource blueprint
    station_client = PackageResourceExt('client_test', 'healer_test.station.client')
    station_client.init_app(app)

    # report route rules
    for rule in list(app.url_map.iter_rules()):
        print(f"{rule}")

    # start app in development mode
    app.run(
        debug=app.config['DEBUG'],
    )
