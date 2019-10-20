import argparse

from geofinder.Loc import PlaceType

from geofinder import GeoKeys


def filter(place_name):
    # Separate out arguments
    tokens = place_name.split(",")
    args = []
    for tkn in tokens:
        if '--' in tkn:
            args.append(tkn.strip(' '))

    # Parse options in place name
    parser = argparse.ArgumentParser(description="Parses command.")
    parser.add_argument("-f", "--feature", help="Feature code, PPL etc.")
    parser.add_argument("-i", "--iso", help="ISO country code.")
    options = parser.parse_args(args)

    city1 = GeoKeys.normalize(tokens[0])
    target = city1
    country_iso = options.iso.lower()
    feature = options.feature.upper()
    place_type = PlaceType.ADVANCED_SEARCH

    print(f'iso=[{country_iso}] feature=[{feature}]')

filter(place_name="Edinburgh, --feature='CH',--iso='GB'")