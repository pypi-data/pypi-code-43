from argparse import ArgumentParser
from json import loads
from logging import getLogger
from os import environ as env

from requests import get

FAILURE = -1

logger = getLogger(__name__)

argument_parser = ArgumentParser()
argument_parser.add_argument("word",
                             action="store",
                             nargs=1)
args = argument_parser.parse_args()


def main():
    try:
        app_id = env['OXFORD_DICTIONARY_APP_KEY']
        api_key = env['OXFORD_DICTIONARY_API_KEY']
    except KeyError:
        logger.error("API variables not found, populate "
                     "OXFORD_DICTIONARY_APP_KEY and OXFORD_DICTIONARY_API_KEY with"
                     "proper values.")
        return FAILURE

    try:
        prepared_url = f"https://od-api.oxforddictionaries.com:443/api/v2/" \
                       f"entries/en-gb/{args.word[0].lower()}"
    except KeyError:
        logger.error("Argument 'word' is required.")
        return FAILURE

    with get(prepared_url,
             headers={"app_id": app_id, "app_key": api_key}) as request:
        if request.ok:
            result_text = request.text
        elif request.status_code == 404:
            print(f"Word {args.word[0]} not found in Oxford Dictionary")
            return FAILURE
        else:
            logger.error(f"{request.status_code}: {request.text}")
            return FAILURE

    result_json = loads(result_text)
    tnl = '\n\t'
    try:
        print(args.word[0])
        print(len(args.word[0]) * '_')
        for result in result_json['results'][0]['lexicalEntries']:
            for entry in result['entries']:
                print("\nEtymology:")
                try:
                    print(f"\t{entry['etymologies'][0]}")
                except KeyError:
                    print("\tNo etymology found")
                print("\nDefinition:")
                try:
                    print(f"\t{tnl.join([definition for definition in entry['senses'][0]['definitions']])}")
                except KeyError:
                    print("\tNo definition found")
                print("\nExamples:")
                try:
                    print(f"\t{tnl.join([example['text'] for example in entry['senses'][0]['examples']])}")
                except KeyError:
                    print("\tNo examples found.")
            print("\n")
    except KeyError:
        print(f"Word {args.word[0]} not found in Oxford dictionary")
        return FAILURE


if __name__ == '__main__':
    main()
