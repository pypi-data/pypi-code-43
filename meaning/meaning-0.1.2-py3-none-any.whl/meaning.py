import re
import pangu
import huepy
import argparse
import requests
import xmltodict

from meaning.version import __version__

def get_parser():
    parser = argparse.ArgumentParser(description="Translate words via command line")
    parser.add_argument('words', metavar='WORDS', type=str, nargs='*', help='the words to translate')
    parser.add_argument('-S', '--shell', action='store_true', help='spawn a query prompt shell')
    parser.add_argument('-R', '--reset', action='store_true', help='reset meaning configuration')
    parser.add_argument('-v', '--version', action='store_true', help='displays the current version of meaning')

    return parser

def highlight(text: str, keyword: str):
    text = pangu.spacing_text(text)
    return re.sub(
        keyword,
        "\33[0m" + "\33[93m" + keyword + "\33[0m" + "\33[37m",
        text,
        flags=re.IGNORECASE
    )

def TranslateWithAiCiBa(words: str):
    iciba_key = '47A83B5C4CBA453E752D056400733043'
    url = "http://dict-co.iciba.com/api/dictionary.php?key={key}&w={w}&type={type}"

    try:
        resp = requests.get(url.format(key=iciba_key, w=words, type="xml"))
        resp.encoding = 'utf-8'

        resp_dict = xmltodict.parse(resp.text).get('dict')
        ps = resp_dict.get('ps') or ''
        print(" " + words + "  " + huepy.lightred(ps) + '\n')

        pos = resp_dict.get("pos")
        acceptation = resp_dict.get("acceptation")

        if pos and acceptation:
            if not isinstance(pos, list) and not isinstance(acceptation, list):
                pos = [pos]
                acceptation = [acceptation]
            for p, a in zip([i for i in pos], [i for i in acceptation]):
                if a and p:
                    print(" - " + huepy.lightcyan(p + " " + a))
            print()
    
        index = 1
        sent = resp_dict.get("sent")
        if not sent:
            pass
        elif not isinstance(sent, list):
            sent = [sent]
        print(huepy.orange('Example:'))
        for item in sent:
            for key, value in item.items():
                if key == "orig":
                    print(highlight(huepy.grey("  {}. ".format(index) + value), words))
                    index += 1
                elif key == "trans":
                    print(huepy.cyan("      " + value))
        print()
    except Exception as e:
        print(" " + huepy.red(e))

def RunTerminal():
    parser = get_parser()
    args = vars(parser.parse_args())
        
    words = ' '.join(args['words'])

    if args['version']:
        print(huepy.cyan("meaning " + __version__))
        return 

    elif not args['words']:
        parser.print_help()
        return 

    TranslateWithAiCiBa(words)

if __name__ == "__main__":
    RunTerminal()