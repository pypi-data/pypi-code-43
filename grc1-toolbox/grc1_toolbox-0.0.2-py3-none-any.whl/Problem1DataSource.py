import os
import numpy as np
try:
    from urllib2 import urlopen
except ImportError:
    from urllib.request import urlopen
import pandas as pd
import pickle

class Problem1DataSource():

    def __init__(self, url, instrumentId):
        self.cachedFolder = "historicalData/"
        self.instrumentId = instrumentId
        if not os.path.isfile(self.cachedFolder + instrumentId +".csv"):
            self.downloadFile(instrumentId, url)



    def downloadFile(self, instrumentId, url):
        downloadLocation = self.cachedFolder

        if not os.path.exists(downloadLocation):
            os.mkdir(downloadLocation, 0o755)

        url = '%s/%s.csv' % (url, instrumentId)
        print('Downloading from %s' % url)
        response = urlopen(url)
        status = response.getcode()
        if status == 200:
            print('Downloading %s data to file: %s' % (instrumentId, downloadLocation))
            with open(downloadLocation + instrumentId + ".csv", 'w') as f:
                f.write(response.read().decode('utf8'))
            return True
        else:
            raise ValueError('File not found. Please check settings!')

    def readData(self):
        df = pd.read_csv(self.cachedFolder + self.instrumentId + ".csv",index_col='Index')
        df = df[~df.duplicated()]
        return df