#!/usr/bin/env python3
from jdTranslationHelper import jdTranslationHelper
from optparse import OptionParser
import urllib
import wikiquote
import random
import sys
import os

translations = jdTranslationHelper()
translations.loadDirectory(os.path.join(os.path.dirname(os.path.realpath(__file__)),"translation"))

parser = OptionParser()
parser.add_option("-l", "--lang", dest="lang",help=translations.translate("options.language"),default="en")
parser.add_option("-s", "--site", dest="site",help=translations.translate("options.site"))
parser.add_option("-d", "--qotd",action="store_true", dest="day", default=False,help=translations.translate("options.qotd"))
options, args = parser.parse_args()

try:
    urllib.request.urlopen("https://www.wikiquote.org")
except:
    print(translations.translate("noInternet"))
    sys.exit(0)

if options.day:
    quote = wikiquote.quote_of_the_day(lang=options.lang)
    print(quote[0] + " -- " + quote[1])
    sys.exit(0)

if options.site:
    site = options.site
else:
    site = wikiquote.random_titles(max_titles=1,lang=options.lang)[0]

try:
    quote = random.choice(wikiquote.quotes(site,lang=options.lang,max_quotes=100))
    print(quote + " -- " + site)
except:
    print(translations.translate("quoteError"))

#This is function is just to prevent a error message with setup.py
def main():
    pass
