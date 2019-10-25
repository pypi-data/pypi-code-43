#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
**Mapping Learning Configuration**


This class sets the configuration of Mapping Learning application. It is able 
to load the configuration from a YAML file and to (re)write a re-usable
configuration file based.

Config class checks that application will be able to run properly using given
configuration:

* input files exists?
* value of parameters belong to expected type
* ...
"""
from __future__ import print_function
from __future__ import unicode_literals

import os
import re
from datetime import datetime
from numpy import nan

from maplearn.app.static_dict import StaticDict
try:
    import configparser
except ImportError:
    import ConfigParser as configparser

from maplearn import logger


def splitter(text):
    """
    Splits a character string based on several separators and remove useless
    empty characters.

    Args:
        text (str) : character string to split

    Returns:
        list: list of stripped character strings, None elsewhere
    """
    if not isinstance(text, list):
        try:
            text = re.split("[,;|]", text)
        except TypeError:
            return None
    text = set([i.strip() for i in text])
    return list(text)


class Config(object):
    """
    This class is the medium between a configuration file and the applicaton.
    It is able to load and check a configuration file (Yaml) and rewrite a new
    configuration file (that can be re-used by Mappling Learning later).

    Args:
        config_file (str) : path to a configuration file

    The class attributes described below reflects the sections in configuration
    file.

    Properties:
        * io (dict): input/output. path to samples, dataset files and output.
          list of features to use...
        * codes (dict): label codes and corresponding names
        * preprocess (dict) : which preprocessing step(s) to apply
        * process (dict) : which processes to apply (list of algorihms...)
    """

    __METADATA = dict(
        preprocess={'scale': 'Scale',
                    'balance': 'Reequilibrage des echantillons',
                    'separability': 'Analyse de separabilite des \
                    echantillons'})

    def __init__(self, file_config):
        self.__data = StaticDict(
            metadata=StaticDict(
                title="Mapping Learning's report", description=None,
                author=None, date=datetime.today().strftime('%d/%m/%Y')),
            io=StaticDict(data=None, samples=None, features=None,
                          label=None, label_id=None, na=nan,
                          output=os.path.join(os.getcwd(), 'tmp')),
            codes=None,
            preprocess=StaticDict(scale=True, balance=False, reduce=None,
                                  ncomp=None, separability=False),
            process=StaticDict(type=None, kfold=3, optimize=False,
                               algorithm=None, predict=False, n_clusters=15,
                               distance='euclidean')
            )

        if file_config is None:
            logger.warning("Configuration file is not defined")
        elif not os.path.exists(file_config):
            str_msg = "Configuration file is missing (%s)" % file_config
            logger.critical(str_msg)
            raise configparser.Error(str_msg)
        else:
            logger.debug('Configuration file (%s) found', file_config)
            #file_config = file_config.encode('unicode-escape')
        self._file_cfg = file_config
        self.__cfg = configparser.ConfigParser()
        self.__cfg._boolean_states = {'t': True, 'true': True,
                                      'f': False, 'false':False, 'oui':True,
                                      'non': False, 'o':True, 'n':False}
        if self._file_cfg is not None:
            self.read()

    def check(self):
        """
        Check that parameters stored in attributes are correct

        Returns:
            int : number of issues detected
        """
        nb_pbs = 0
        if not os.path.exists(self.__data['io']['output']):
            os.makedirs(self.__data['io']['output'])

        # list of data sources
        self.__data['io']['features'] = splitter(self.__data['io']['features'])
        if self.__data['io']['samples'] is not None:
            if self.__data['io']['samples'] in ['iris', 'digits', 'boston']:
                logger.debug('Choosen samples : %s',
                             self.__data['io']['samples'])
            elif not os.path.exists(self.__data['io']['samples']):
                logger.critical("Missing samples source file (%s)",
                                self.__data['io']['samples'])
                nb_pbs += 1
        if self.__data['io']['data'] is not None:
            if not os.path.exists(self.__data['io']['data']):
                logger.critical("Missing data source file (%s)",
                                self.__data['io']['data'])
                nb_pbs += 1

        # list of algorithm(s)
        __algos = splitter(self.__data['process']['algorithm'])
        if isinstance(__algos, list):
            __algos.sort()
        self.__data['process']['algorithm'] = __algos
        if nb_pbs <= 0:
            logger.info('Configuration checked : OK')
        else:
            logger.critical('Configuration : %i issue(s)', nb_pbs)
        return nb_pbs

    def __set_params(self, section, nature, *params):
        """
        Sets several string parameters in a given section of the configuration

        Args:
            * section (str) : name of the section to edit with parameters
            * nature (type): type of parameters (str, int, bool)
            * *params: list of parameters to edit
        """
        for i in params:
            try:
                if nature == str:
                    param = self.__cfg.get(section, i).strip()
                elif nature == int:
                    param = self.__cfg.getint(section, i)
                elif nature == bool:
                    param = self.__cfg.getboolean(section, i)
            except configparser.NoOptionError:
                logger.debug('Parameter %s (%s) not defined', i, section)
            except ValueError:
                logger.debug('Parameter %s (%s) poorly defined', i, section)
            else:
                if param != '' and param is not None:
                    self.__data[section][i] = param
                    logger.debug('Parameter %s (%s) = %s', i, section,
                                 str(param))
                else:
                    logger.debug('Parameter %s (%s) not set', i, section)

    def read(self):
        """
        Load parameters from configuration file and put them in corresponding
        class attributes

        Returns:
            int : number of issues got when reading the file
        """
        logger.debug('Trying to read configuration...')
        self.__cfg.read(self._file_cfg)

        if self.__cfg.has_section('metadata'):
            self.__set_params('metadata', str, 'title', 'description',
                              'author')

        # input/output [io] section
        self.__set_params('io', str, 'samples', 'label_id', 'label',
                          'features', 'data', 'output')
        self.__set_params('io', int, 'na')
        for i in ['data', 'samples', 'output']:
            if self.__data['io'][i] is not None:
                self.__data['io'][i] = os.path.normpath(self.__cfg.get('io',
                                                                       i))
        # get legend of labels if given in configuration file
        if self.__cfg.has_section('codes'):
            self.__data['codes'] = dict(self.__cfg.items('codes'))
            # keys of codes are stored in a temporary list (necessary for the
            # loop below)
            __keys = list(self.__data['codes'].keys())
            for i in __keys:
                self.__data['codes'][int(i)] = self.__data['codes'].pop(i)
            logger.info('Legend read with %i classes',
                        len(self.__data['codes']))

        # preprocessing section
        self.__set_params('preprocess', str, 'reduce')
        self.__set_params('preprocess', int, 'ncomp')
        self.__set_params('preprocess', bool, 'scale', 'separability',
                          'balance')

        # processing section
        self.__set_params('process', str, 'type', 'distance', 'algorithm')
        self.__set_params('process', bool, 'optimize', 'predict')
        self.__set_params('process', int, 'kfold', 'n_clusters')

        # Check configuration
        nb_pbs = self.check()
        if nb_pbs == 0:
            logger.info('Configuration file read !')
        else:
            str_msg = '%i issue(s) when loading configuration file' % nb_pbs
            logger.critical(str_msg)
            raise configparser.Error(str_msg)
        return nb_pbs

    @property
    def io(self):
        """
        Input/Output property
        """
        return self.__data['io']

    @property
    def codes(self):
        """
        Dictionnary describing label codes and the name of classes
        """
        return self.__data['codes']

    @property
    def preprocess(self):
        """
        Dictionnary of preprocess parameters
        """
        return self.__data['preprocess']

    @property
    def process(self):
        """
        Dictionnary of process parameters
        """
        return self.__data['process']

    def write(self, fichier=None):
        """
        Write a new configuration file feeded by class attributes content.

        Args:
            fichier (str) : path to configuration file to write
        """
        if fichier is None:
            fichier = self._file_cfg

        for i in ['data', 'samples', 'output']:
            try:
                path = os.path.normpath(self.__io[i])
            except AttributeError:
                logger.debug('%s is not a path', i)
            else:
                # Needed for Windows compatibility
                self.__io[i] = path.replace('\\', '\\\\')
        __cfg = configparser.ConfigParser()
        for i in self.__data.keys():
            if self.__data[i] is not None:
                __cfg.add_section(i)
                for j in self.__data[i].keys():
                    if self.__data[i][j] is None:
                        value = ''
                    elif isinstance(self.__data[i][j], list):
                        value = ';'.join(self.__data[i][j])
                    else:
                        value = self.__data[i][j]
                    try:
                        value = str(value)
                    except AttributeError:
                        pass
                    __cfg.set(i, str(j), value)
        with open(fichier, 'w') as __file:
            __cfg.write(__file)

    def __str__(self):

        str_msg = '<a href="https://bitbucket.org/thomas_a/maplearn">![logo]'
        str_msg += u'(%s){: .logo}</a> \n\n#%s#\n' % (os.path.join('img', \
                   'logo.png'), self.__data['metadata']['title'])
        if self.__data['metadata']['description'] is not None:
            str_msg += u'\n\n##Description##\n%s\n' % self.__data['metadata']['description']
        str_msg += u'\n\n####Realisation : '
        if self.__data['metadata']['author'] is not None:
            str_msg += '%s - ' % self.__data['metadata']['author']
        str_msg += '%s####\n' % self.__data['metadata']['date']
        str_msg += '\n\n##Resume##'
        str_msg += '\n* Entree(s)\n'
        if not self.__data['io']['samples'] is None:
            str_msg += '\n\t- Echantillons : %s' % self.__data['io']['samples']
        if not self.__data['io']['data'] is None:
            str_msg += '\n\t- Donnees : %s' % self.__data['io']['data']
        if not self.__data['io']['na'] is None:
            str_msg += '\n\t- Valeur nulle (NA) : %s' % str(self.__data['io']['na'])

        str_msg += '\n\n* Pretraitement'
        for i in ['scale', 'balance', 'separability']:
            if self.__data['preprocess'][i]:
                str_msg += '\n\t- %s' % self.__METADATA['preprocess'][i]
        if self.__data['preprocess']['reduce'] is not None:
            str_msg += '\n\t- Reduction des dimensions par %s' \
                      % self.__data['preprocess']['reduce']

        str_msg += '\n* Traitement : %s' % self.__data['process']['type']
        if self.__data['process']['algorithm'] is None:
            str_msg += '\n\t- Algorithmes : Tous'
        else:
            str_msg += '\n\t- %i algorithme(s) : %s' \
                      % (len(self.__data['process']['algorithm']),
                         ', '.join(self.__data['process']['algorithm']))
        if self.__data['process']['type'] == 'clustering' and \
            self.__data['process']['n_clusters'] is not None:
            str_msg += '\n\t- %i cluster(s) souhaites' % self.__data['process']['n_clusters']
        if self.__data['process']['optimize']:
            str_msg += '\n\t- Optimisation des algorithmes'
        str_msg += '\n\t- Approche %i-fold' % self.__data['process']['kfold']
        str_msg += '\n\t- Distance : %s' % self.__data['process']['distance']
        str_msg += '\n* Sortie\n\t- Dossier : %s' % self.__data['io']['output']
        return str_msg

    def __del__(self):
        self.__cfg = None
        self.__data = None
