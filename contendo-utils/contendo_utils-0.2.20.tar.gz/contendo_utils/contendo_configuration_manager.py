import os
import pandas as pd
from datetime import datetime as dt
import logging

from contendo_utils import *
#from contendo_logging import *

class ContendoConfigurationManager:

    def __init__(self):
        #
        # create the cache directory if required
        ProUtils.create_path_directories('cache/a')

        self.configsheet_url_template = 'https://docs.google.com/spreadsheets/d/{docId}/export?format=csv&gid={gid}&run=1'
        __main_configuration_doc_id = '1OHAkPPMtURUWu1d8BlZqcTX1iVnPeuZ1SdFLsGrgIDY'
        self._cacheConfigs = dict()

        _domains_df = self.get_configuration_pd(__main_configuration_doc_id, 0)
        self.domainsDict = ProUtils.pandas_df_to_dict(_domains_df, 'Domain')
        _templates_df = self.get_configuration_pd(__main_configuration_doc_id, 1672371224)
        self.templateDefsDict = ProUtils.pandas_df_to_dict(_templates_df, 'TemplateName')

    @contendo_classfunction_logger
    def get_configuration_pd(self, documentId, gid, domain='Contendo.config'):
        if (documentId, gid) not in self._cacheConfigs:
            try:
                _cachefile = 'cache/{}-{}.csv'.format(domain, gid)
                if not os.path.exists(_cachefile):
                    _url = self.configsheet_url_template.format(docId = documentId, gid=gid)
                    _config_df = pd.read_csv(_url).fillna('')
                    _config_df.to_csv(_cachefile, index=False)
                else:
                    _config_df = pd.read_csv(_cachefile).fillna('')

            except Exception as e:
                logger.error('Error reading document {}'.format(_url))
                raise e

            self._cacheConfigs[(documentId, gid)] = _config_df

        return self._cacheConfigs[(documentId, gid)]


    def get_configuration_dict(self, domain, gid, key):
        assert (domain in self.domainsDict)
        _config_df = self.get_configuration_pd(self.domainsDict[domain]['DocumentId'], gid, domain)
        _config_dict = ProUtils.pandas_df_to_dict(_config_df, key)

        return _config_dict

    def get_configuration_df(self, domain, gid):
        assert (domain in self.domainsDict)
        _config_df = self.get_configuration_pd(self.domainsDict[domain]['DocumentId'], gid, domain)

        return _config_df

    def get_domain_docid(self, domain):
        return self.domainsDict[domain]['DocumentId']

@contendo_function_logger
def test():
    startTime = dt.now()
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "{}/sportsight-tests.json".format(os.environ["HOME"])
    ccm = ContendoConfigurationManager()
    configDict = ccm.get_configuration_dict('Football.NFL', '1564699495', 'StatName')
    logger.info('Config dict: %s, len: %s', configDict, len(configDict.keys()))
    logger.info ('NFL document id: %s', ccm.get_domain_docid('Football.NFL'))

if __name__ == '__main__':
    contendo_logging_setup(default_level=logging.DEBUG)
    test()