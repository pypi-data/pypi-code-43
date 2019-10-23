#! /usr/bin/env python
#coding=utf-8
class mech:
    def __init__(self,name,emiss_opt):
        self.name = name
        self.emiss_opt = emiss_opt

    def wrfchem(self):
        cbmz_mosaic = ['E_ISO',   'E_SO2',  'E_NO',      'E_CO',    'E_ETH',  'E_HC3', 'E_HC5',
                   'E_HC8',   'E_XYL','  E_OL2',     'E_OLT',   'E_OLI',  'E_TOL', 'E_CSL',
                   'E_HCHO',  'E_ALD',  'E_KET',     'E_ORA2',  'E_NH3',  'E_NO2', 'E_CH3OH',
                   'E_C2H5OH','E_PM25I','E_PM25J',   'E_ECI',   'E_ECJ',  'E_ORGI','E_ORGJ',
                   'E_SO4I',  'E_SO4J',' E_NO3I',    'E_NO3J',  'E_SO4C', 'E_NO3C','E_ORGC',
                   'E_ECC']
        radmsorg = ['E_ISO','E_SO2','E_NO','E_NO2','E_CO','E_ETH','E_HC3',
                'E_HC5','E_HC8','E_XYL','E_OL2','E_OLT','E_OLI','E_TOL',
                'E_CSL','E_HCHO','E_ALD','E_KET','E_ORA2','E_NH3','E_PM25I',
                'E_PM25J','E_PM_10','E_ECI','E_ECJ','E_ORGI','E_ORGJ','E_SO4I',
                'E_SO4J','E_NO3I','E_NO3J','E_NAAJ','E_NAAI','E_ORGI_A','E_ORGJ_A',
                'E_ORGI_BB','E_ORGJ_BB']
        mechanism = {'chmz_mosaic':{'speciate':cbmz_mosaic,'emiss_opt':4},
                 'radmsorg':{'speciate':radmsorg,'emiss_opt':3}}
        return mechanism[self.name]['speciate']