import pandas as pd
import feedparser

import datetime
import time

from methods import *
from graphics import *





url_base = 'http://export.arxiv.org/api/query?search_query='
url_tail = '&max_results=10000'
#TODO choose how many MSCs and which one


"""
A class to set a specific math field, send a request through the arXiv API and
store the xml response.

The response format is in Atom 1.0, a lightweight and commonly used
xml-based format that is human readable. To parse this xml we use feedparser.
"""
class Scraper(object):

    def __init__(self, macro_field):

        try:
            self.url = url_base + url_query(macro_field) + url_tail
        except ValueError:
            print("Error!")
            print("Research field not valid!")
        else:
            self.field = macro_field
            self.query_dict = feedparser.parse(self.url)

            if query_dict.status == 404:
                raise Exception("404 - Page Not Found")
                print("The query was unsuccessful, parsing cannot begin.")
            elif query_dict.status == 400:
                raise Exception("400 - Bad Request")
                print("The query was unsuccessful, parsing cannot begin.")
            elif query_dict.status == 200:
                print("The query was successful, parsing can begin now!")




"""
The scrape method parses the feed we obtain from our request. For each preprint,
we want to retain its submision year, the list of its authors and the number of
pages of its PDF version. In case one of these data is not available, as it is
almost always the case with preprints that have been withdrawn, the code for that
iteration is simply skipped.

When the parsing is complete, the cleaned data are saved into both a pandas
DataFrame and a .csv file whose name contains the research field
and current month & year.
"""
    def scrape(self):

        years = []
        authors = []
        pages = []

        temporary_record = [0, [], 0]
        t0 = time.time()
        print("scraping started!"")
        for i in range(len(self.query_dict.entries)):

            if i%100 == 0:
                print("Total number of papers scraped: {:d}".format(i))
            record = self.query_dict.entries[i]

            temporary_record[0] = get_year(record.get('published'))
            if temporary_record[0] == None:
                continue

            temporary_record[1] = get_authors(record.get('authors'))
            if temporary_record[1] == None:
                continue

            temporary_record[2] = get_num_pages(record, i)
            if temporary_record[2] == None:
                continue

            years.append(temporary_record[0])
            authors.append(temporary_record[1])
            pages.append(temporary_record[2])

        # TODO print how many results, how many articles parsed, how many invalid

        t1 = time.time()

        records = pd.DataFrame({'years':years, 'authors':authors, 'pages': pages})
        df.index.names = self.field
        query_details = get_details(self.field)
        self.name_file = 'Arxivtrends_preprints__' + query_details + '.csv'
        records.to_csv(self.name_file,  sep='\t', index = None, header=False)

        total_time = t1 - t0
        print('fetching is completed in ' + str(datetime.timedelta(seconds = x)) + ' hours.')
        print ('Total number of papers scraped: {:d}'.format(len(records)))

        return records


"""
Getters
"""
    def getUrl(self):
        return self.url

    def getField(self):
        return self.field

    def getNameFile(self):
        return self.name_file
