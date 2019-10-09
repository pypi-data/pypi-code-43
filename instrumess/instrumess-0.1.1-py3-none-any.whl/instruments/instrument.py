# -*- coding: utf-8 -*-
"""
Created on Thu Jun 28 19:27:05 2018

@author: Rastko
"""
from abc import ABC, abstractmethod, abstractproperty

class Instrument(ABC):
    """Class for all instrument drivers that requires suclasses to implement three basic methods:
    init
    close 
    reset

    """
    def __init__(self, online=True, address=None, name=None):
        self.online = online
        self._address = address
        self._name = name
        
    def _is_offline(self):
        """A method for checking if the instrument is online,
        for easy debugging it prints a warning if the instrument is offline.
        """
        if not self.online:
            print('Warning: {:16s} is offline.'.format(self._name))
            return True
        else:
            return False
    
    @abstractmethod
    def init(self):
        pass
    
    @abstractmethod
    def reset(self):
        pass

    @abstractmethod
    def close(self):
        pass