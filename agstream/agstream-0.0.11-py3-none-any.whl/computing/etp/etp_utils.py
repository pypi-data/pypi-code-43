# -*- coding: utf-8 -*-
"""
    Created on 9 mai 2018
    
    @author: guill
    
    
    Etp Utilities
    ----------------    
    
    Utilities to compute various ETP stuff


"""
from __future__ import division

from builtins import object
from past.utils import old_div
import math


class EtpUtil(object):
    """ 
    
        Description
        -----------------------------------
        Class grouping necessary functions used in ETP calcultation
    
    """

    def __init__(self):
        self.GSC = 0.082
        # constante solaire
        self.LAMBDA = 2.45
        # chaleur latente de vaporisation
        self.ALPHA = 0.23
        # albédo du gazon de référence hypothétique
        self.SIGMA = 4.903e-9
        # constante de Stefan-Boltzmann (MJ.K-4.m-2.jour-1)

    def getRayonnementExtraAtmospherique(self, date, latitude):
        """
        Get the extra Atmospherique ray
        
        :param latitude : latitude chooses
        :param date: date of the day
        
        """
        dayOfYear = date.timetuple().tm_yday

        # conversion de la latitude en radion
        latitude = old_div(latitude * math.pi, 180)
        dr = 1 + 0.033 * (math.cos(old_div(2 * math.pi * dayOfYear, 365)))
        delt = 0.409 * math.sin(old_div(2 * math.pi * dayOfYear, 365) - 1.39)
        om = math.acos(-(math.tan(latitude) * math.tan(delt)))

        return (
            (old_div((24 * 60), math.pi))
            * self.GSC
            * dr
            * (
                om * math.sin(latitude) * math.sin(delt)
                + math.cos(latitude) * math.cos(delt) * math.sin(om)
            )
        )
