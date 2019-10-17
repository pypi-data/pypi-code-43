"""
Authors:     David Huber, Science Systems and Applications, Inc. (SSAI)
             Carter Hulsey, Science Systems and Applications, Inc. (SSAI)
E-mail:      david.b.huber@nasa.gov
Date:        10/27/2017
             08/24/2018: Updated for v5.1 compatability and enabling of hdf5
             reading (Carter Hulsey)               

Description: This library houses functions that read in SAGE III solar L1 and L2
             product files and return a data object containing the metadata and
             products for the given file type.  The functions are described
             below.

             *******************************************************************
             **** Note for data product versions 5.1 and onward hdf4 files  ****
             **** have been disconinued and replaced with hdf5. For hdf     ****
             **** users switch to using sol_l2_hdf5 for Level 2 hdf files   ****
             **** and sol_l1_hdf5 for L1 hdf files                          ****
             *******************************************************************

Notes:       This library has two dependencies:
             NumPy (mandatory) - Provides numerical functions and array creation
             
             h5py(optional) - Library needed for reading hdf5 file formats
             Can be found at:
               https://github.com/h5py/h5py

             Python-HDF4 or PyHDF (optional) - A wrapper library for HDF4
                functions; Python-HDF4 is a fork of PyHDF that adds
                compatibility with Python 3.x while PyHDF only works with
                Python 2.x.

             SciPy (including NumPy) installation instructions can be found at
               https://scipy.org/install.html
             Python-HDF4 installation instructions can be found at
               http://fhs.github.io/python-hdf4/install.html

             If you wish to work with HDF4 files, then you must have the HDF4
             library installed as well as either Python-HDF4 or PyHDF.  The
             instructions for installing the HDF4 library can be found at
               https://support.hdfgroup.org/release4/obtain.html

             Please report any bugs to david.b.huber@nasa.gov.

Examples:    Reading a level 2 HDF file
             from read_solar import sol_l2_hdf5
             (data, stat) = sol_l2_hdf5("g3b.ssp.00612620v05.10")

             Reading a level 2 binary file
             from read_solar import sol_l2_bin
             (data, stat) = sol_l2_bin("g3b.sspb.00612620v05.10")

             Reading a level 1 HDF file
             from read_solar import sol_l1_hdf5
             (data, stat) = sol_l1_hdf5("g3b.t.00612620v05.10")

             Reading a level 1 binary file
             from read_solar import sol_l1_bin
             (data, stat) = sol_l1_bin("g3b.tb.00612620v05.10")

__________________________________________________________________________________
sol_l2_hdf4  ***** For Version 5.0 and prior******
Inputs:      The filename of a solar level 2 HDF4 product file
Outputs:     1) A data object of type SolL2Data containing the product data
             2) A status flag indicating whether the read was successful or not
Description: This function reads the data from an HDF4 level 2 product file
             and returns a data object containing the data from the file.
             A status flag is also returned and should be checked before
             attempting to access the structure after function completion.  A
             status value of 0 indicates a success while a value of -1
             indicates that an error occurred.

__________________________________________________________________________________
sol_l2_bin
Inputs:      Filename of a solar level 2 binary product file
Outputs:     1) A data object of type SolL2Data containing the product data
             2) A status flag indicating whether the read was successful or not
Description: This function reads the data from a binary level 2 product file
             and returns a data object containing the data from the file.
             A status flag is also returned and should be checked before
             attempting to access the structure after function completion.  A
             status value of 0 indicates a success while a value of -1
             indicates that an error occurred.

__________________________________________________________________________________
sol_l1_hdf4  ****** For Version 5.0 and prior  *****
Author:      David Huber <david.b.huber@nasa.gov>
Inputs:      The filename of a solar level 1 HDF4 product file
Outputs:     1) A data object of type SolTranData containing the product data
             2) A status flag indicating whether the read was successful or not
Description: This function reads the data from an HDF4 level 1 product file
             and returns a data object containing the data from the file.
             A status flag is also returned and should be checked before
             attempting to access the structure after function completion.  A
             status value of 0 indicates a success while a value of -1
             indicates that an error occurred.

__________________________________________________________________________________
sol_l1_bin
Author:      David Huber <david.b.huber@nasa.gov>
Inputs:      Filename of a solar level 1 binary product file
Outputs:     1) A data object of type SolTranData containing the product data
             2) A status flag indicating whether the read was successful or not
Description: This function reads the data from a binary level 1 product file
             and returns a data object containing the data from the file.
             A status flag is also returned and should be checked before
             attempting to access the structure after function completion.  A
             status value of 0 indicates a success while a value of -1
             indicates that an error occurred.

__________________________________________________________________________________
sol_l2_hdf5  ******For Version 5.1 and newer *******
Inputs:      Filename of a solar level 2 HDF5 product file
Outputs:     1) A data object of type SolTranData containing the product data
             2) A status flag indicating whether the read was successful or not
Description: This function reads the data from an HDF5 level 2 product file
             and returns a data object containing the data from the file.
             A status flag is also returned and should be checked before
             attempting to access the structure after function completion.  A
             status value of 0 indicates a successful read while a value of -1
             indicates that an error occurred.

__________________________________________________________________________________
sol_l1_hdf5  ******For Version 5.1 and newer ******
Inputs:      Filename of a solar level 1 HDF5 product file
Outputs:     1) A data object of type SolTranData containing the product data
             2) A status flag indicating whether the read was successful or not
Description: This function reads the data from an HDF5 level 1 product file
             and returns a data object containing the data from the file.
             A status flag is also returned and should be checked before
             attempting to access the structure after function completion.  A
             status value of 0 indicates a successful read while a value of -1
             indicates that an error occurred.

"""

import numpy as np
from sys import version_info
import sys

#Declare which symbols to import
__all__ = ["AeroExt", "SolL2Data", "TranProfile", "SolTranData","sol_l2_hdf5", "sol_l2_hdf4", 
           "sol_l2_bin","sol_l1_hdf5" ,"sol_l1_hdf4", "sol_l1_bin"]

#Set global constants
__c_MaxIndex = 20

class AeroExt:
   """
   Class Name: AeroExt
   Purpose:    Contains the data for aerosol extinction
   """
   def __init__(self, num_aer_bins, num_aer_channels):
      """
      Required inputs: Number of aerosol altitude bins, number of aerosol
                       channels used
      """
      self.aerext = np.zeros((num_aer_bins, num_aer_channels), dtype = np.float)
      self.aerext_uncert = np.zeros((num_aer_bins, num_aer_channels), dtype = np.float)
      self.aerQA = np.zeros((num_aer_bins, num_aer_channels), dtype = np.int)

class SolL2Data(object):
   """
   Class Name: SolL2Data
   Purpose:    The class contains the information from a given level 2 SAGE III
               data file.  This structure is the same for binary,HDF4, and HDF5 files.
   """
   def __init__(self,vers, num_grnd_trk, num_bins, num_aer_channels,
                num_aer_bins,num_met_grid):
      #Structure for v5.1 and greater
      if vers >= 5.1:
        #Event information
        self.event_id = 0
        self.date = 0
        self.year_fraction = 0.
        self.latitude = 0.
        self.longitude = 0.
        self.time = 0
        #Fill values
        self.int_fill_value = 0
        self.flt_fill_value = 0.
        #Mission ID
        self.mission_id = 0
        #Software and data versions
        self.L0DO_Version = 0.
        self.CCDTable_Version = 0
        self.L0_Version = 0.
        self.Spectroscopic_DataBase_Version = 0.
        self.GRAM95_Version = 0.
        self.Met_Version = 0.
        self.Software_Version = 0.
        self.Dataproduct_Version = 0.
        #Bin height
        self.bin_height = 0.
        #Dimensions
        self.num_bins = num_bins
        self.num_met_grid = num_met_grid
        self.num_aer_channels = num_aer_channels
        self.num_grnd_trk = num_grnd_trk
        self.num_aer_bins = num_aer_bins
        #Event type
        self.sc_evt_type = 0
        self.gnd_evt_type = 0
        #Solar beta angle
        self.BetaAngle_Solar = 0.
        #Status flag
        self.Aurora_Flag = 0
        self.Ephemeris_Source = 0
        #Ground track information
        self.gt_date = np.zeros((num_grnd_trk), dtype = np.int)
        self.gt_time = np.zeros((num_grnd_trk), dtype = np.int)
        self.gt_latitude = np.zeros((num_grnd_trk), dtype = np.float)
        self.gt_longitude = np.zeros((num_grnd_trk), dtype = np.float)
        self.gt_ray_dir = np.zeros((num_grnd_trk), dtype = np.float)
        #Space Craft Information
        self.Space_Craft_Lat = np.zeros((num_grnd_trk),dtype = np.float)
        self.Space_Craft_Lon = np.zeros((num_grnd_trk),dtype = np.float)
        self.Space_Craft_Alt = np.zeros((num_grnd_trk),dtype = np.float)
        #Altitude registration
        self.Homogeneity = np.zeros((num_bins), dtype = np.int)
        self.Altitude  = np.zeros((num_bins), dtype = np.float)
        self.geopotential_alt = np.zeros((num_bins), dtype = np.float)
        #Temperature/pressure profiles used for retrieval
        self.Temperature = np.zeros((num_bins), dtype = np.float)
        self.Temperature_uncert = np.zeros((num_bins), dtype = np.float)
        self.Pressure = np.zeros((num_bins), dtype = np.float)
        self.Pressure_uncert = np.zeros((num_bins), dtype = np.float)
        self.Neutral_Density = np.zeros((num_bins), dtype = np.float)
        self.Neutral_Density_uncert = np.zeros((num_bins), dtype = np.float)
        self.Temp_Pressure_Source = np.zeros((num_bins), dtype = np.int)
        #Tropopause temperature/altitude
        self.trop_temp = 0.
        self.trop_alt = 0.
        self.trop_press = 0.
        #Met temp/press
        self.met_pressure = np.zeros((num_met_grid), dtype = np.float)
        self.met_temp = np.zeros((num_met_grid), dtype = np.float)
        self.met_temp_unc = np.zeros((num_met_grid), dtype = np.float)
        self.met_altitude = np.zeros((num_met_grid), dtype = np.float)
        self.met_source = 0
        #CCD info and flags
        self.CCD_Temperature = 0.
        self.Spectrometer_Zenith_Temperature = 0.
        self.CCD_Temperature_minus_TEC = 0.
        self.Ephemeris_Quality = 0
        self.QAFlag = 0
        self.QAFlag_Altitude = np.zeros((num_bins), dtype = np.int)
        self.SpecCalStretch = 0.
        self.SpecCalShift = 0.
        self.HexErrFlag = 0
        self.ContWindowClosedFlag = 0
        self.DMPExoFlag = 0
        self.BlockExoFlag = 0
        self.TimeQualFlag = 0
        self.SpectralCalFlag = 0
        self.SolarEclipseFlag = 0
        self.DMPAltFlag = np.zeros((num_bins), dtype = np.int)
        #Composite derived ozone products
        self.Ozone_Composite = np.zeros((num_bins), dtype = np.float)
        self.Ozone_Composite_uncert = np.zeros((num_bins), dtype = np.float)
        self.Ozone_Composite_QA = np.zeros((num_bins), dtype = np.int)
        #Mesospheric ozone products
        self.Ozone_Mes = np.zeros((num_bins), dtype = np.float)
        self.Ozone_Mes_uncert = np.zeros((num_bins), dtype = np.float)
        self.Ozone_Mes_QA = np.zeros((num_bins), dtype = np.int)
        #Chappuis (MLR) derived ozone products
        self.Ozone_MLR = np.zeros((num_bins), dtype = np.float)
        self.Ozone_MLR_uncert = np.zeros((num_bins), dtype = np.float)
        self.Ozone_MLR_QA = np.zeros((num_bins), dtype = np.int)
        #Aerosol/Ozone (ao3) derived ozone products
        self.Ozone_ao3 = np.zeros((num_bins), dtype = np.float)
        self.Ozone_ao3_uncert = np.zeros((num_bins), dtype = np.float)
        self.Ozone_ao3_QA = np.zeros((num_bins), dtype = np.int)
        #Water vapor product
        self.H2O = np.zeros((num_bins), dtype = np.float)
        self.H2O_uncert = np.zeros((num_bins), dtype = np.float)
        self.H2O_QA = np.zeros((num_bins), dtype = np.int)
        #Nitrogen dioxide products
        self.NO2 = np.zeros((num_bins), dtype = np.float)
        self.NO2_uncert = np.zeros((num_bins), dtype = np.float)
        self.NO2_QA = np.zeros((num_bins), dtype = np.int)
        #Retrieved temperature/pressure products
        self.RetTemp = np.zeros((num_bins), dtype = np.float)
        self.RetTemp_uncert = np.zeros((num_bins), dtype = np.float)
        self.RetPress = np.zeros((num_bins), dtype = np.float)
        self.RetPress_uncert = np.zeros((num_bins), dtype = np.float)
        self.RetTP_QA = np.zeros((num_bins), dtype = np.int)
        #Aerosol product information
        self.Aer_wavelength = np.zeros((num_aer_channels), dtype = np.float)
        self.Aer_width = np.zeros((num_aer_channels), dtype = np.float)
        self.Molecular_SCT = np.zeros((num_aer_channels), dtype = np.float)
        self.Molecular_SCT_uncert = np.zeros((num_aer_channels), dtype = np.float)
        self.Strat_Aer_OD = np.zeros((num_aer_channels), dtype = np.float)
        self.Strat_Aer_OD_uncert = np.zeros((num_aer_channels), dtype = np.float)
        self.Strat_Aer_OD_QA = np.zeros((num_aer_channels), dtype = np.int)
        #Aerosol extinction products
        self.AerosolExt = AeroExt(num_aer_bins,num_aer_channels)

      #Structure for versions 5.0 and previous
      else:
        #Event information
        self.event_id = 0
        self.yr_day_tag = 0
        self.mission_time = 0
        #Fill values
        self.int_fill_value = 0
        self.flt_fill_value = 0.
        #Mission ID
        self.mission_id = 0
        #Software and data versions
        self.L0DO_Version = 0.
        self.L0_Version = 0.
        self.DB_Version = 0.
        self.GRAM95_Version = 0.
        self.Met_Version = 0.
        self.Software_Version = 0.
        self.Dataproduct_Version = 0.
        #Bin height
        self.bin_height = 0.
        #Dimensions
        self.num_bins = num_bins
        self.num_ao3_channels = num_aer_channels
        self.num_grnd_trk = num_grnd_trk
        self.num_aer_bins = num_aer_bins
        #Event type
        self.sc_evt_type = 0
        self.gnd_evt_type = 0
        #Solar beta angle
        self.BetaAngle = 0.
        #Status flag
        self.EvtStatusFlag = 0
        #Starting time/location
        self.st_date = 0
        self.st_time = 0
        self.st_latitude = 0.
        self.st_longitude = 0.
        self.st_altitude = 0.
        #Ending time/location
        self.end_date = 0
        self.end_time = 0
        self.end_latitude = 0.
        self.end_longitude = 0.
        self.end_altitude = 0.
        #Ground track information
        self.gt_date = np.zeros((num_grnd_trk), dtype = np.int)
        self.gt_time = np.zeros((num_grnd_trk), dtype = np.int)
        self.gt_latitude = np.zeros((num_grnd_trk), dtype = np.float)
        self.gt_longitude = np.zeros((num_grnd_trk), dtype = np.float)
        self.gt_ray_dir = np.zeros((num_grnd_trk), dtype = np.float)
        #Altitude registration
        self.Homogeneity = np.zeros((num_bins), dtype = np.int)
        self.geom_alt = np.zeros((num_bins), dtype = np.float)
        self.potential_alt = np.zeros((num_bins), dtype = np.float)
        #Temperature/pressure profiles used for retrieval
        self.CurrentTemp = np.zeros((num_bins), dtype = np.float)
        self.CurrentTemp_uncert = np.zeros((num_bins), dtype = np.float)
        self.CurrentPress = np.zeros((num_bins), dtype = np.float)
        self.CurrentPress_uncert = np.zeros((num_bins), dtype = np.float)
        self.TPSource = np.zeros((num_bins), dtype = np.int)
        #Tropopause temperature/altitude
        self.trop_temp = 0.
        self.trop_alt = 0.
        #Composite derived ozone products
        self.CompositeO3 = np.zeros((num_bins), dtype = np.float)
        self.CompositeO3_uncert = np.zeros((num_bins), dtype = np.float)
        self.SPOzone = np.zeros((num_bins), dtype = np.float)
        self.SPOzone_uncert = np.zeros((num_bins), dtype = np.float)
        self.CompO3QA = np.zeros((num_bins), dtype = np.int)
        #Mesospheric ozone products
        self.MesO3 = np.zeros((num_bins), dtype = np.float)
        self.MesO3_uncert = np.zeros((num_bins), dtype = np.float)
        self.MesSPOzone = np.zeros((num_bins), dtype = np.float)
        self.MesSPOzone_uncert = np.zeros((num_bins), dtype = np.float)
        self.MesO3QA = np.zeros((num_bins), dtype = np.int)
        #Chappuis (MLR) derived ozone products
        self.ChapO3 = np.zeros((num_bins), dtype = np.float)
        self.ChapO3_uncert = np.zeros((num_bins), dtype = np.float)
        self.ChapSPOzone = np.zeros((num_bins), dtype = np.float)
        self.ChapSPOzone_uncert = np.zeros((num_bins), dtype = np.float)
        self.MLRO3QA = np.zeros((num_bins), dtype = np.int)
        #Aerosol/Ozone (ao3) derived ozone products
        self.Ozone_ao3 = np.zeros((num_bins), dtype = np.float)
        self.Ozone_ao3_uncert = np.zeros((num_bins), dtype = np.float)
        self.aO3SPOzone = np.zeros((num_bins), dtype = np.float)
        self.aO3SPOzone_uncert = np.zeros((num_bins), dtype = np.float)
        self.Ozone_aO3QA = np.zeros((num_bins), dtype = np.int)
        #Water vapor product
        self.WaterVaporNDP = np.zeros((num_bins), dtype = np.float)
        self.WaterVaporNDP_uncert = np.zeros((num_bins), dtype = np.float)
        self.H2OQA = np.zeros((num_bins), dtype = np.int)
        #Nitrogen dioxide products
        self.NO2NDP = np.zeros((num_bins), dtype = np.float)
        self.NO2NDP_uncert = np.zeros((num_bins), dtype = np.float)
        self.SPNO2 = np.zeros((num_bins), dtype = np.float)
        self.SPNO2_uncert = np.zeros((num_bins), dtype = np.float)
        self.NO2QA = np.zeros((num_bins), dtype = np.int)
        #Retrieved temperature/pressure products
        self.RetTemp = np.zeros((num_bins), dtype = np.float)
        self.RetTemp_uncert = np.zeros((num_bins), dtype = np.float)
        self.RetPress = np.zeros((num_bins), dtype = np.float)
        self.RetPress_uncert = np.zeros((num_bins), dtype = np.float)
        self.RetTPQA = np.zeros((num_bins), dtype = np.int)
        #Aerosol product information
        self.Aer_wavelength = np.zeros((num_aer_channels), dtype = np.float)
        self.Aer_width = np.zeros((num_aer_channels), dtype = np.float)
        self.StratOD = np.zeros((num_aer_channels), dtype = np.float)
        self.StratOD_uncert = np.zeros((num_aer_channels), dtype = np.float)
        self.StratODQA = np.zeros((num_aer_channels), dtype = np.int)
        #Aerosol extinction products
        self.AerosolExt = AeroExt(num_aer_bins,num_aer_channels)
        #Aerosol extinction ratio products
        self.Aerosol1020 = np.zeros((num_aer_bins), dtype = np.float)
        self.Aerosol1020_uncert = np.zeros((num_aer_bins), dtype = np.float)
        self.Aero1020QA = np.zeros((num_aer_bins), dtype = np.int)
        self.asd_flag = np.zeros((num_aer_bins), dtype = np.int)

class TranProfile:
   """
   Class Name: TranProfile
   Author:     David Huber <david.b.huber@nasa.gov>
   Purpose:    The class contains profiles of transmission data.
   """
   def __init__(self,vers, num_alt_bins, profile_count):
      """
      Required inputs: number of altitude bins and the number of profiles (PG
                       count + 1 photodiode)
      """
      if vers <= 5.0:
        self.GeometricAltitude = np.zeros((num_alt_bins, profile_count), dtype = np.float)
        self.Transmission = np.zeros((num_alt_bins, profile_count), dtype = np.float)
        self.Transmission_unc = np.zeros((num_alt_bins, profile_count), dtype = np.float)
        self.TransQA = np.zeros((num_alt_bins, profile_count), dtype = np.int)
      else:
        self.Transmission = np.zeros((num_alt_bins, profile_count), dtype = np.float)
        self.Transmission_unc = np.zeros((num_alt_bins, profile_count), dtype = np.float)
        self.TransQA = np.zeros((num_alt_bins, profile_count), dtype = np.int)
class SolTranData:
   """
   Class Name: SolTranData
   Author:     David Huber <david.b.huber@nasa.gov>
   Purpose:    This class contains the information available in any given
               level 1 SAGE III product data file.  This data is the same for
               any given binary or HDF4 file.
   """
   def __init__(self,vers, num_grnd_trk, num_press_grid, num_alt_bins, profile_count, num_CCDPxlGrps):
      """
      Required inputs: 1)number of ground track points, 2)number of altitudes
                       at which meteorological data is available, 3)number of
                       altitude bins for transmission, 4)number of transmission
                       profiles (including the photodiode), and 5)number of pixel
                       groups
      """
      #Structure for v5.1 and greater
      if vers >= 5.1:
        #Event information
        self.event_id = 0
        self.date = 0
        self.Year_Fraction = 0.
        self.latitude = 0.
        self.longitude = 0.
        self.time = 0
        #Fill values
        self.int_fill_value = 0
        self.flt_fill_value = 0.
        #Mission ID
        self.mission_id = 0
        #Software and data versions
        self.L0DO_Version = 0.
        self.CCDVersion = 0
        self.L0_Version = 0.
        self.Spectroscopic_DataBase_Version = 0.
        self.GRAM95_Version = 0.
        self.Met_Version = 0.
        self.Software_Version = 0.
        self.Dataproduct_Version = 0.
        #Bin height
        self.bin_height = 0.
        #Dimensions
        self.profile_count = profile_count
        self.num_grnd_trk = num_grnd_trk
        self.num_press_grid = num_press_grid
        self.num_CCDPxlGrps = num_CCDPxlGrps
        self.num_alt_bins = num_alt_bins
        #Event type
        self.sc_evt_type = 0
        self.gnd_evt_type = 0
        #Solar beta angle
        self.BetaAngle_Solar = 0.
        #Aurora Flag
        self.Aurora_Flag = 0
        #Event status flag
        self.Ephemeris_Source = 0
        #Ground track information
        self.gt_date = np.zeros((num_grnd_trk), dtype = np.int)
        self.gt_time = np.zeros((num_grnd_trk), dtype = np.int)
        self.gt_latitude = np.zeros((num_grnd_trk), dtype = np.float)
        self.gt_longitude = np.zeros((num_grnd_trk), dtype = np.float)
        self.gt_ray_dir = np.zeros((num_grnd_trk), dtype = np.float)
        #Space Craft Information
        self.Space_Craft_Lat = np.zeros((num_grnd_trk), dtype = np.float)
        self.Space_Craft_Lon = np.zeros((num_grnd_trk), dtype = np.float)
        self.Space_Craft_Alt = np.zeros((num_grnd_trk), dtype = np.float)
        #Altitude info 
        self.Altitude = np.zeros((num_alt_bins), dtype = np.float)
        self.Geopotential_Alt = np.zeros((num_alt_bins), dtype = np.float)
        #Temperature/Pressure Profiles 
        self.Temperature = np.zeros((num_alt_bins), dtype = np.float)
        self.Temperature_uncert = np.zeros((num_alt_bins), dtype = np.float)
        self.Pressure = np.zeros((num_alt_bins), dtype = np.float)
        self.Pressure_uncert = np.zeros((num_alt_bins), dtype = np.float)
        self.Neutral_Density = np.zeros((num_alt_bins), dtype = np.float)
        self.Neutral_Density_uncert = np.zeros((num_alt_bins), dtype = np.float)
        self.Temp_Pressure_Source = np.zeros((num_alt_bins), dtype = np.int)
        #Tropopause temperature/altitude
        self.trop_temp = 0.
        self.trop_alt = 0.
        self.trop_press = 0.
        #Meteorological data
        self.met_pressure = np.zeros((num_press_grid), dtype = np.float)
        self.met_temp = np.zeros((num_press_grid), dtype = np.float)
        self.met_temp_unc = np.zeros((num_press_grid), dtype = np.float)
        self.met_altitude = np.zeros((num_press_grid), dtype = np.float)
        #Meteorological data source
        self.met_source = 0
        #CCD and flag info
        self.CCD_Temperature = 0.
        self.Spectrometer_Zenith_Temperature = 0.
        self.CCD_Temperature_minus_TEC = 0.
        self.Ephemeris_Quality = 0
        self.QAFlag = 0
        self.QAFlag_Altitude = np.zeros((num_alt_bins), dtype = np.int)
        self.SpecCalStretch = 0.
        self.SpecCalShift = 0.
        self.HexErrFlag = 0
        self.ContWindowClosedFlag = 0
        self.DMPExoFlag = 0
        self.BlockExoFlag = 0
        self.TimeQualFlag = 0
        self.SpectralCalFlag = 0
        self.SolarEclipseFlag = 0
        self.DMPAltFlag = np.zeros((num_alt_bins), dtype = np.int)
        #Pixel group information
        self.start_pixel_num = np.zeros((num_CCDPxlGrps), dtype = np.int)
        self.end_pixel_num = np.zeros((num_CCDPxlGrps), dtype = np.int)
        self.central_wavelength = np.zeros((num_CCDPxlGrps), dtype = np.float)
        self.half_bandwidth = np.zeros((num_CCDPxlGrps), dtype = np.float)
        #Transmission profiles for each pixel group
        self.pg_trans_profiles = TranProfile(vers,num_alt_bins, profile_count)
      #Structure for versions 5.0 and previous
      else:
        #Event information
        self.event_id = 0
        self.yr_day_tag = 0
        self.mission_time = 0
        #Fill values
        self.int_fill_value = 0
        self.flt_fill_value = 0.
        #Mission ID
        self.mission_id = 0
        #Software and data versions
        self.L0DO_Version = 0.
        self.L0_Version = 0.
        self.DB_Version = 0.
        self.GRAM95_Version = 0.
        self.Met_Version = 0.
        self.Software_Version = 0.
        self.Dataproduct_Version = 0.
        #Bin height
        self.bin_height = 0.
        #Dimensions
        self.profile_count = profile_count
        self.num_grnd_trk = num_grnd_trk
        self.num_press_grid = num_press_grid
        self.num_CCDPxlGrps = num_CCDPxlGrps
        self.num_alt_bins = num_alt_bins
        #Event type
        self.sc_evt_type = 0
        self.gnd_evt_type = 0
        #Solar beta angle
        self.BetaAngle = 0.
        #Event status flag
        self.EvtStatusFlag = 0
        #Starting time/position
        self.st_date = 0
        self.st_time = 0
        self.st_latitude = 0.
        self.st_longitude = 0.
        self.st_altitude = 0.
        #Ending time/position
        self.end_date = 0
        self.end_time = 0
        self.end_latitude = 0.
        self.end_longitude = 0.
        self.end_altitude = 0.
        #Ground track information
        self.gt_date = np.zeros((num_grnd_trk), dtype = np.int)
        self.gt_time = np.zeros((num_grnd_trk), dtype = np.int)
        self.gt_latitude = np.zeros((num_grnd_trk), dtype = np.float)
        self.gt_longitude = np.zeros((num_grnd_trk), dtype = np.float)
        self.gt_ray_dir = np.zeros((num_grnd_trk), dtype = np.float)
        #Tropopause temperature/altitude
        self.trop_temp = 0.
        self.trop_alt = 0.
        #Meteorological data source
        self.met_Source = 0
        #Meteorological data
        self.met_pressure = np.zeros((num_press_grid), dtype = np.float)
        self.met_temp = np.zeros((num_press_grid), dtype = np.float)
        self.met_temp_unc = np.zeros((num_press_grid), dtype = np.float)
        self.met_altitude = np.zeros((num_press_grid), dtype = np.float)
        #Pixel group information
        self.start_pixel_num = np.zeros((num_CCDPxlGrps), dtype = np.int)
        self.end_pixel_num = np.zeros((num_CCDPxlGrps), dtype = np.int)
        self.central_wavelength = np.zeros((num_CCDPxlGrps), dtype = np.float)
        self.half_bandwidth = np.zeros((num_CCDPxlGrps), dtype = np.float)
        #Altitude for each bin
        self.Altitude = np.zeros((num_alt_bins), dtype = np.float)
        #Temperature/pressure used for retrieval
        self.CurrentPress = np.zeros((num_alt_bins), dtype = np.float)
        self.CurrentTemp = np.zeros((num_alt_bins), dtype = np.float)
        self.CurrentTemp_uncert = np.zeros((num_alt_bins), dtype = np.float)
        self.TPSource = np.zeros((num_alt_bins), dtype = np.int)
        #Transmission profiles for each pixel group
        self.pg_trans_profiles = TranProfile(vers,num_alt_bins, profile_count)

##############################################################
def get_version(filename):
  """
  Name: get_version 
  Author: Carter Hulsey <carter.b.hulsey@nasa.gov>
  Inputs: Filename 
  Output: Version of the data product
  Description: Reads in filename and get version of data from 
          filename. Returns Version as float.
  """
  splt_file = filename.split('v')
  vers = float(splt_file[-1])

  return(vers)

##############################################################


def __l_read_int32(File, Count):
   """
   Name:        __l_read_int32
   Author:      David Huber <david.b.huber@nasa.gov>
   Inputs:      1) File handle or filename, 2) number of bytes to read in
                3) number of times to read
   Output:      The integer or integer array read in from the file
   Description: Reads in a 4-byte integer from a specified binary file on a
                little-endian system.
   """

   return np.fromfile(File, dtype=np.int32, count = Count).newbyteorder()


##############################################################


def __l_read_float32(File, Count):
   """
   Name:        __l_read_float32
   Author:      David Huber <david.b.huber@nasa.gov>
   Inputs:      1) File handle or filename, 2) size of 1-d array
   Output:      The integer or integer array read in from the file
   Description: Reads in a 4-byte floating point array from a specified binary
                file on a little-endian system.
   """

   return np.fromfile(File, dtype=np.float32, count = Count).newbyteorder()


##############################################################


def __b_read_int32(File, Count):
   """
   Name:        __b_read_int32
   Author:      David Huber <david.b.huber@nasa.gov>
   Inputs:      1) File handle or filename, 2) number of bytes to read in
                3) number of times to read
   Output:      The integer or integer array read in from the file
   Description: Reads in a 4-byte integer from a specified binary file on a
                big-endian system.
   """

   return np.fromfile(File, dtype=np.int32, count = Count).newbyteorder()


##############################################################


def __b_read_float32(File, Count):
   """
   Name:        __b_read_float32
   Author:      David Huber <david.b.huber@nasa.gov>
   Inputs:      1) File handle or filename, 2) size of 1-d array
   Output:      The integer or integer array read in from the file
   Description: Reads in a 4-byte floating point array from a specified binary
                file on a big-endian system.
   """

   return np.fromfile(File, dtype=np.float32, count = Count).newbyteorder()


##############################################################


def sol_l2_hdf5(Filename):
   """
   Name:        sol_l2_hdf5
   Author:      David Huber <david.b.huber@nasa.gov>
   Inputs:      Filename of a solar level 2 HDF5 product file
   Outputs:     1) A data object of type SolTranData containing the product data
                2) A status flag indicating whether the read was successful or not
   Description: This function reads the data from an HDF5 level 2 product file
                and returns a data object containing the data from the file.
                A status flag is also returned and should be checked before
                attempting to access the structure after function completion.  A
                status value of 0 indicates a successful read while a value of -1
                indicates that an error occurred.
   """

   #Import h5py for interaction with HDF5 files
   import h5py

   #Get Version
   vers = get_version(Filename)

   #Determine if the input file exists
   try:
      File = h5py.File(Filename, "r")
   except OSError:
      print(Filename, "is not an HDF5 file. Exiting...\n")
      return(SolL2Data(1,1,1,1), -1)

   #Go ahead and declare the section names to avoid confusion later on when
   #reading in the file contents.
   Section1 = "Section 1.0 - File Header/Section 1.0 - File Header"
   Section2 = "Section 2.0 - Product Identification/Section 2.0 - Product Identification"
   Section3 = "Section 3.0 - File Description/File Description"
   Section4Root = "Section 4.0 - Event Identification"
   Section4 = Section4Root + "/Event Identification"
   Section41 = (Section4Root + "/Section 4.1 - Ground Track Data Over This Event" + 
                "/Section 4.1 - Ground Track Data Over This Event")
   Section42 = (Section4Root + "/Section 4.2 - Spacecraft Data Over This Event" +
                "/Section 4.2 - Spacecraft Data Over This Event")
   Section43 = (Section4Root + "/Section 4.3 - Instrument Performance Data and Quality Flags For This Event" +
                "/Section 4.3 - Instrument Performance Data and Quality Flags For This Event")
   Section44 = (Section4Root + "/Section 4.4 - Altitude Based BitFlags For This Event" +
                "/Section 4.4 - Altitude Based BitFlags For This Event")
   Section5Root = "Section 5.0 - Altitude-based Data"
   Section5 = Section5Root + "/Altitude Data"
   Section51 = (Section5Root + "/Section 5.1 - Temperature pressure profiles" +
                "/Temperature pressure profiles")
   Section51A = (Section5Root + "/Section 5.1A - Derived Tropopause Data from section 5.1" +
                 "/Derived Tropopause Data from section 5.1")
   Section51B = (Section5Root + "/Section 5.1B - Meteorological Data from section 5.1" + 
                 "/Meterological Data from section 5.1")
   Section52 = (Section5Root + "/Section 5.2 - Composite Ozone profiles" +
                 "/Ozone profiles")
   Section52A = (Section5Root + "/Section 5.2A - Mesospheric Ozone profiles" +
                 "/Ozone profiles")
   Section52B = (Section5Root + "/Section 5.2B - MLR Ozone profiles" +
                 "/Ozone profiles")
   Section52C = (Section5Root + "/Section 5.2C - Aerosol Ozone profiles" +
                 "/Ozone profiles")
   Section53 = (Section5Root + "/Section 5.3 - Water Vapor profiles" +
                 "/Water Vapor profiles")
   Section54 = (Section5Root + "/Section 5.4 - Nitrogen Dioxide profiles" +
                 "/Nitrogen Dioxide profiles")
   Section55 = (Section5Root + "/Section 5.5 - Temperature pressure profiles retrieved" +
                 "/Temperature pressure profiles retrieved")
   Section6 = "Section 6.0 - Aerosol Information/Aerosol Information"
   Section61 = "Section 6.1 - Aerosol Extinction profiles/Aerosol Extinction profiles"

   #Make sure that we have the correct file type by checking whether all datasets exist
   e1 = Section1 in File
   e2 = Section2 in File
   e3 = Section3 in File
   e4 = Section4 in File
   e41 = Section41 in File
   e42 = Section42 in File
   e43 = Section43 in File
   e44 = Section44 in File
   e5 = Section5 in File
   e51 = Section51 in File
   e51a = Section51A in File
   e51b = Section51B in File
   e52 = Section52 in File
   e52a = Section52A in File
   e52b = Section52B in File
   e52c = Section52C in File
   e53 = Section53 in File
   e54 = Section54 in File
   e55 = Section55 in File
   e6 = Section6 in File
   e61 = Section61 in File

   #print(e1,e2,e3,e4,e41,e42,e43,e44,e5,e51,e51a,e51b,e52,e52a, e52b, e52c, e53, e54,e55,e6,e61)
   if(not(e1 & e2 & e3 & e4 & e41 & e42 & e43 & e44 & e5 & e51 & e51a & e51b & e52 & e52a & e52b &
        e52c & e53 & e54 & e55 & e6 & e61)):
      print("Error reading " + str(Filename) + ": Unable to locate all SAGE datasets. Exiting...\n")
      errsol = SolL2Data(1, 1, 1, 1, 1,1)
      return(SolL2Data(1, 1, 1, 1,1,1), -1)

   #Get the file description handle
   DataFile = File[Section3][0]
   num_bins = DataFile[1]
   num_met_grid = DataFile[2]
   num_aer_channels = DataFile[3]
   num_grnd_trk = DataFile[4]
   num_aer_bins = DataFile[5]

   #Declare the output data object
   solar = SolL2Data(vers,num_grnd_trk, num_bins, num_aer_channels, num_aer_bins,num_met_grid)

   #Get the height of each bin
   solar.bin_height = DataFile[0]

   #Get the header information handle
   DataHeader = File[Section1][0]
   solar.event_id = DataHeader[0]
   solar.year_fraction = DataHeader[1]
   solar.date = DataHeader[2]
   solar.latitude = DataHeader[3]
   solar.longitude = DataHeader[4]
   solar.time = DataHeader[5]
   solar.int_fill_value = DataHeader[6]
   solar.flt_fill_value = DataHeader[7]
   solar.mission_id = DataHeader[8]

   #Get the product information handle
   DataProduct = File[Section2][0]
   solar.L0DO_Version = DataProduct[0]
   solar.CCDTable_Version = DataProduct[1]
   solar.L0_Version = DataProduct[2]
   solar.Spectroscopic_DataBase_Version = DataProduct[3]
   solar.GRAM95_Version = DataProduct[4]
   solar.Met_Version = DataProduct[5]
   solar.Software_Version = DataProduct[6]
   solar.Dataproduct_Version = DataProduct[7]

   #Get the event identification handle
   DataEvent = File[Section4][0]
   solar.sc_evt_type = DataEvent[0]
   solar.gnd_evt_type = DataEvent[1]
   solar.BetaAngle_Solar = DataEvent[2]
   solar.Aurora_Flag = DataEvent[3]
   solar.Ephemeris_Source = DataEvent[4]

   #Get the event ground track information handle
   DataEventGround = np.asarray(File[Section41])
   solar.gt_date = DataEventGround["Date (YYYYMMDD)"]
   solar.gt_time = DataEventGround["Time (HHMMSS)"]
   solar.gt_latitude = DataEventGround["Subtangent Latitude (0.0 +/- 90.0 deg)"]
   solar.gt_longitude = DataEventGround["Subtangent Longitude (0.0 +/- 180.0 deg)"]
   solar.gt_ray_dir = DataEventGround["Ray Path Direction @ Subtan. Pt. (0.0 - 359.99 deg)"]

   #Get the event spacecraft information handle
   DataSpaceCraft = np.asarray(File[Section42])
   solar.Space_Craft_Lat = DataSpaceCraft["Spacecraft Subtangent Latitude (0.0 +/- 90.0 deg)"]
   solar.Space_Craft_Lon = DataSpaceCraft["Spacecraft Subtangent Longitude (0.0 +/- 180.0 deg)"]
   solar.Space_Craft_Alt = DataSpaceCraft["Spacecraft Subtangent Altitude above Earth   (KM)"]
   
   #Get Performance Data and Qual Flags
   DataQualFlag = File[Section43][0]
   solar.CCD_Temperature = DataQualFlag[0]
   solar.Spectrometer_Zenith_Temperature = DataQualFlag[1]
   solar.CCD_Temperature_minus_TEC= DataQualFlag[2]
   solar.Ephemeris_Quality = DataQualFlag[3]
   solar.SpecCalShift = DataQualFlag[4]
   solar.SpecCalStretch = DataQualFlag[5]
   solar.QAFlag = DataQualFlag[6]

   #Get Alt Bases Bit Flags 
   DataAltFlag = np.asarray(File[Section44])
   solar.QAFlag_Altitude = DataAltFlag["Altitude Based Bit Flags"]

   #Get the tropopause data handle
   DataTrop = np.asarray(File[Section5])

   #Get the T/P profiles handle
   DataTP = np.asarray(File[Section51])

   #Get the derived tropopause data handle
   DataTropDeriv = File[Section51A][0]
   solar.trop_alt = DataTropDeriv[0]
   solar.trop_temp = DataTropDeriv[1]
   solar.trop_press = DataTropDeriv[2]
   solar.met_source = DataTropDeriv[3]

   #Get the met Data
   DataMet = np.asarray(File[Section51B])

   #Get the composite ozone product handle
   DataCompO3 = np.asarray(File[Section52])

   #Get the mesospheric ozone product handle
   DataMesO3 = np.asarray(File[Section52A])

   #Get the Chappuis ozone product handle
   DataMLRO3 = np.asarray(File[Section52B])

   #Get the aerosol ozone product handle
   DataAO3 = np.asarray(File[Section52C])

   #Get the water vapor product handle
   DataH2O = np.asarray(File[Section53])

   #Get the NO2 product handle
   DataNO2 = np.asarray(File[Section54])

   #Get the retrieved T/P product handle
   DataRetTP = np.asarray(File[Section55])

   #Get the aerosol product information handle
   DataAero = np.asarray(File[Section6])

   #Get the aerosol extinction profiles product handle
   DataAeroExt = np.asarray(File[Section61])

   #Populate the output data object
   #Section 5
   solar.Homogeneity = DataTrop['Homogeneity Flags']
   solar.Altitude  = DataTrop['Geometric Altitude (km)']
   solar.geopotential_alt = DataTrop['Geopotential Altitude (km)']

   #Section 5.1
   solar.Temperature = DataTP['Temperature (K)']
   solar.Temperature_uncert = DataTP['Temperature Unc (K)']
   solar.Pressure = DataTP['Pressure (hPa)']
   solar.Pressure_uncert = DataTP['Pressure Unc (hPa)']
   solar.Neutral_Density = DataTP['Neutral Density (cm-3)']
   solar.Neutral_Density_uncert = DataTP['Neutral Density Unc (cm-3)']
   solar.Temp_Pressure_Source = DataTP['PT Array Source Flags (0-4)']

   #Section 5.1B
   solar.met_altitude = DataMet['Met Altitude (km)']
   solar.met_temp = DataMet['Met Temperature (K)']
   solar.met_temp_unc = DataMet['Met Temperature Unc (K)']
   solar.met_pressure = DataMet['Met Pressure (hPa)']

   #Section 5.2
   solar.Ozone_Composite = DataCompO3['Ozone Concentration (cm-3)']
   solar.Ozone_Composite_uncert = DataCompO3['Ozone Concentration Unc (cm-3)']
   solar.Ozone_Composite_QA = DataCompO3['Ozone QA bit flags']

   #Section 5.2a
   solar.Ozone_Mes = DataMesO3['Mes Ozone Concentration (cm-3)']
   solar.Ozone_Mes_uncert = DataMesO3['Mes Ozone Concentration Unc (cm-3)']
   solar.Ozone_Mes_QA = DataMesO3['Ozone QA bit flags']

   #Section 5.2b
   solar.Ozone_MLR = DataMLRO3['Ozone Concentration (cm-3)']
   solar.Ozone_MLR_uncert = DataMLRO3['Ozone Concentration Unc (cm-3)']
   solar.Ozone_MLR_QA = DataMLRO3['Ozone QA bit flags']

   #Section 5.2c
   solar.Ozone_ao3 = DataAO3['Ozone Concentration (cm-3)']
   solar.Ozone_ao3_uncert = DataAO3['Ozone Concentration Unc (cm-3)']
   solar.Ozone_ao3_QA = DataAO3['Ozone QA bit flags']

   #Seciont 5.3
   solar.H2O = DataH2O['Water Vapor Concentration (cm-3)']
   solar.H2O_uncert = DataH2O['Water Vapor Concentration Unc (cm-3)']
   solar.H2O_QA = DataH2O['Water Vapor QA bit flags']

   #Section 5.4
   solar.NO2 = DataNO2['Nitrogen Dioxide Concentration (cm-3)']
   solar.NO2_uncert = DataNO2['Nitrogen Dioxide Concentration Unc (cm-3)']
   solar.NO2_QA = DataNO2['Nitrogen Dioxide QA bit flags']

   #Section 5.5 
   solar.RetTemp = DataRetTP['Temperature (K)']
   solar.RetTemp_uncert = DataRetTP['Temperature Uncertainty (K)']
   solar.RetPress = DataRetTP['Pressure (hPa)']
   solar.RetPress_uncert = DataRetTP['Pressure Uncertainty (hPa)']
   solar.RetTP_QA = DataRetTP['Pressure/Temp QA bit flags']

   #Section 6
   solar.Aer_wavelength = DataAero['Aerosol Channels Centerline Wavelengths (nm)']
   solar.Aer_width = DataAero['Aerosol Channels Half-Bandwidths (nm)']
   solar.Molecular_SCT = DataAero['Aerosol Channels Molecular Cross Section (cm^2)']
   solar.Molecular_SCT_uncert = DataAero['Aerosol Channels Molecular Cross Section Uncert (cm^2)'] 
   solar.Strat_Aer_OD = DataAero['Stratospheric Optical Depth']
   solar.Strat_Aer_OD_uncert = DataAero['Stratospheric Optical Depth Uncertainty']
   solar.Strat_Aer_OD_QA = DataAero['Stratospheric Optical Depth QA bit flags']

   for ch in range(solar.num_aer_channels):
      chan = str(ch + 1)
      solar.AerosolExt.aerext[:,ch] = np.asarray(DataAeroExt['Aerosol Extinction Channel ' + chan + ' (km-1)'])
      solar.AerosolExt.aerext_uncert[:,ch] = np.asarray(DataAeroExt['Aerosol Ext. Uncert. Channel ' + chan + ' (km-1)'])
      solar.AerosolExt.aerQA[:,ch] = np.asarray(DataAeroExt['Aerosol Ext. QA bit flags Chan ' + chan])

   #Close the HDF5 file
   File.close()
   
   #Decode Bits 
   if (solar.QAFlag & 2**0) != 0:
     solar.HexErrFlag = 1
   if (solar.QAFlag & 2**1) != 0:      
     solar.ContWindowClosedFlag = 1
   if (solar.QAFlag & 2**2) != 0:
     solar.TimeQualFlag = 1
   if (solar.QAFlag & 2**3) != 0:
     solar.DMPExoFlag = 1
   if (solar.QAFlag & 2**4) != 0:
     solar.BlockExoFlag = 1
   if (solar.QAFlag & 2**5) !=0:
     solar.SpectralCalFlag = 1
   if (solar.QAFlag & 2**6) !=0:
     solar.SolarEclipseFlag =1

   for i in range(0,solar.num_bins):
     if (solar.QAFlag_Altitude[i] & 2**0) != 0:
       solar.DMPAltFlag[i] = 1

   return (solar, 0)


########################################################################


#Read HDF4 level 2 product files
def sol_l2_hdf4(Filename):
   """
   Name:        sol_l2_hdf4
   Author:      David Huber <david.b.huber@nasa.gov>
   Inputs:      The filename of a solar level 2 HDF4 product file
   Outputs:     1) A data object of type SolL2Data containing the product data
                2) A status flag indicating whether the read was successful or not
   Description: This function reads the data from an HDF4 level 2 product file
                and returns a data object containing the data from the file.
                A status flag is also returned and should be checked before
                attempting to access the structure after function completion.  A
                status value of 0 indicates a success while a value of -1
                indicates that an error occurred.
   """
   #Import pyhdf or python-hdf4 for interaction with HDF4 files.
   #pyhdf is only available for Python 2.x
   #python-hdf4 is a fork of pyhdf (hence the library name is pyhdf) and is
   #available for both Python 2.x and 3.x.

   #See installation instructions for python-hdf4 at
   #  http://fhs.github.io/python-hdf4/install.html

   #Get Version
   vers = get_version(Filename)
   if vers >= 5.1:
     sys.exit('HDF4 files do not exist for v5.1 and higher. Use HDF5 reader')
 
   try:
      from pyhdf import HDF, VS
   except ImportError:
      if(version_info[0] == 3):
         raise ImportError('Unable to locate the python-hdf4 library.' +
                           '  Please ensure version 0.9 or better is installed')
      elif(version_info[0] == 2):
         raise ImportError('Unable to locate the pyhdf or python-hdf4 library.' +
                           '  Please ensure version 0.9 (or higher) of either is installed.')

   #Open the file
   FileHandle = HDF.HDF(Filename)
   DataInterface = FileHandle.vstart()

   #Find the starting index
   for Index in range(__c_MaxIndex+1):
      try:
         TestVD = DataInterface.attach(Index)
         TestVD.detach()
         break
      except HDF.HDF4Error:
         continue

   if(Index == __c_MaxIndex):
      print("Failed to locate the starting VData index for ", Filename)
      return(-1,-1)

   #Get "Header" vdata information (Not actually the file header)
   VDataHeader = DataInterface.attach(Index)
   Index += 2
   try:
      HeaderData = VDataHeader.read()
   except HDF.HDF4Error:
      VDataHeader.detach()
      print("Failed to read header data from the HDF file")
      return(-1,-1)
   VDataHeader.detach()

   #Get product identification vdata information
   VDataProdId = DataInterface.attach(Index)
   Index += 2
   try:
      ProdIdData = VDataProdId.read()
   except HDF.HDF4Error:
      VDataProdId.detach()
      print("Failed to read product information from the HDF file")
      return(-1,-1)
   VDataProdId.detach()

   #Get file information
   VDataFileInfo = DataInterface.attach(Index)
   Index += 2
   try:
      ProdFileInfo = VDataFileInfo.read()
   except HDF.HDF4Error:
      VDataFileInfo.detach()
      print("Failed to read file information from the HDF file")
      return(-1,-1)
   VDataFileInfo.detach()

   #Get event information
   VDataEvent = DataInterface.attach(Index)
   Index += 2
   try:
      ProdEvent = VDataEvent.read()
   except HDF.HDF4Error:
      VDataEvent.detach()
      print("Failed to read event information from the HDF file")
      return(-1,-1)
   VDataEvent.detach()

   #Get information on the start of science data
   VDataSciStart = DataInterface.attach(Index)
   Index += 2
   try:
      ProdSciStart = VDataSciStart.read()
   except HDF.HDF4Error:
      VDataSciStart.detach()
      print("Failed to read science starting information from the HDF file")
      return(-1,-1)
   VDataSciStart.detach()

   #Get information on the end of the event
   VDataSciEnd = DataInterface.attach(Index)
   Index += 2
   try:
      ProdSciEnd = VDataSciEnd.read()
   except HDF.HDF4Error:
      VDataSciEnd.detach()
      print("Failed to read science ending information from the HDF file")
      return(-1,-1)
   VDataSciEnd.detach()


   #Collect array size information to initiate the output solar object
   num_bins = ProdFileInfo[0][1]
   num_ao3_channels = ProdFileInfo[0][2]
   num_grnd_trk = ProdFileInfo[0][3]
   num_aer_bins = ProdFileInfo[0][4]

   #Instantiate the solar object
   solar = SolL2Data(vers, num_grnd_trk, num_bins, num_ao3_channels, num_aer_bins)

   #Finish collecting from ProdFileInfo
   solar.bin_height = ProdFileInfo[0][0]

   #Begin populating the object attributes
   #Populate header data
   solar.event_id = HeaderData[0][0]
   solar.yr_day_tag = HeaderData[0][1]
   solar.mission_time = HeaderData[0][2]
   solar.int_fill_value = HeaderData[0][3]
   solar.flt_fill_value = HeaderData[0][4]
   solar.mission_id = HeaderData[0][5]
   #General product information
   solar.L0DO_Version = ProdIdData[0][0]
   solar.L0_Version = ProdIdData[0][1]
   solar.DB_Version = ProdIdData[0][2]
   solar.GRAM95_Version = ProdIdData[0][3]
   solar.Met_Version = ProdIdData[0][4]
   solar.Software_Version = ProdIdData[0][5]
   solar.Dataproduct_Version = ProdIdData[0][6]
   #Event information
   solar.sc_evt_type = ProdEvent[0][0]
   solar.gnd_evt_type = ProdEvent[0][1]
   solar.BetaAngle = ProdEvent[0][2]
   solar.EvtStatusFlag = ProdEvent[0][3]
   #Event starting information
   solar.st_date = ProdSciStart[0][0]
   solar.st_time = ProdSciStart[0][1]
   solar.st_latitude = ProdSciStart[0][2]
   solar.st_longitude = ProdSciStart[0][3]
   solar.st_altitude = ProdSciStart[0][4]
   #Event ending information
   solar.end_date = ProdSciEnd[0][0]
   solar.end_time = ProdSciEnd[0][1]
   solar.end_latitude = ProdSciEnd[0][2]
   solar.end_longitude = ProdSciEnd[0][3]
   solar.end_altitude = ProdSciEnd[0][4]

   #Get information on the ground track during the event
   VDataGround = DataInterface.attach(Index)
   Index += 2
   for trk in range(solar.num_grnd_trk):

      try:
         ProdGround = VDataGround.read()
      except HDF.HDF4Error:
         VDataGround.detach()
         print("Failed to read ground track information from the HDF file")
         return(-1,-1)

      solar.gt_date[trk] = ProdGround[0][0]
      solar.gt_time[trk] = ProdGround[0][1]
      solar.gt_latitude[trk] = ProdGround[0][2]
      solar.gt_longitude[trk] = ProdGround[0][3]
      solar.gt_ray_dir[trk] = ProdGround[0][4]

   VDataGround.detach()


   #Get science altitude data
   VDataSciData = DataInterface.attach(Index)
   Index += 2

   for alt in range(solar.num_bins):

      try:
         ProdSciData = VDataSciData.read()
      except HDF.HDF4Error:
         VDataSciData.detach()
         print("Failed to read science altitude data from the HDF file")
         return(-1,-1)

      solar.Homogeneity[alt] = ProdSciData[0][0]
      solar.geom_alt[alt] = ProdSciData[0][1]
      solar.potential_alt[alt] = ProdSciData[0][2]

   VDataSciData.detach()


   #Get the temperature/pressure profiles used during processing
   VDataTempPres = DataInterface.attach(Index)
   Index += 2

   for alt in range(solar.num_bins):

      try:
         ProdTempPres = VDataTempPres.read()
      except HDF.HDF4Error:
         VDataTempPres.detach()
         print("Failed to read T/P profiles used during processing from the HDF file")
         return(-1,-1)

      solar.CurrentTemp[alt] = ProdTempPres[0][0]
      solar.CurrentTemp_uncert[alt] = ProdTempPres[0][1]
      solar.CurrentPress[alt] = ProdTempPres[0][2]
      solar.CurrentPress_uncert[alt] = ProdTempPres[0][3]
      solar.TPSource[alt] = ProdTempPres[0][4]

   VDataTempPres.detach()


   #Get the temperature/pressure profiles used during processing
   VDataTrop = DataInterface.attach(Index)
   Index += 2
   try:
      ProdTrop = VDataTrop.read()
   except HDF.HDF4Error:
      VDataTrop.detach()
      print("Failed to read T/P profiles used during processing from the HDF file")
      return(-1,-1)

   solar.trop_temp = ProdTrop[0][0]
   solar.trop_alt = ProdTrop[0][1]

   VDataTrop.detach()


   #Get the composite ozone product
   VDataO3Comp = DataInterface.attach(Index)
   Index += 2
   for alt in range(solar.num_bins):

      try:
         ProdO3Comp = VDataO3Comp.read()
      except HDF.HDF4Error:
         VDataO3Comp.detach()
         print("Failed to read the ozone profile from the HDF file")
         return(-1,-1)

      solar.CompositeO3[alt] = ProdO3Comp[0][0]
      solar.CompositeO3_uncert[alt] = ProdO3Comp[0][1]
      solar.SPOzone[alt] = ProdO3Comp[0][2]
      solar.SPOzone_uncert[alt] = ProdO3Comp[0][3]
      solar.CompO3QA[alt] = ProdO3Comp[0][4]

   VDataO3Comp.detach()


   #Get the mesospheric ozone product
   VDataMesO3 = DataInterface.attach(Index)
   Index += 2
   for alt in range(solar.num_bins):

      try:
         ProdMesO3Comp = VDataMesO3.read()
      except HDF.HDF4Error:
         VDataMesO3.detach()
         print("Failed to read the ozone profile from the HDF file")
         return(-1,-1)

      solar.MesO3[alt] = ProdMesO3Comp[0][0]
      solar.MesO3_uncert[alt] = ProdMesO3Comp[0][1]
      solar.MesSPOzone[alt] = ProdMesO3Comp[0][2]
      solar.MesSPOzone_uncert[alt] = ProdMesO3Comp[0][3]
      solar.MesO3QA[alt] = ProdMesO3Comp[0][4]

   VDataMesO3.detach()


   #Get the Chappuis band ozone product
   VDataO3Chap = DataInterface.attach(Index)
   Index += 2
   for alt in range(solar.num_bins):

      try:
         ProdO3Chap = VDataO3Chap.read()
      except HDF.HDF4Error:
         VDataO3Chap.detach()
         print("Failed to read the Chappuis ozone product from the HDF file")
         return(-1,-1)

      solar.ChapO3[alt] = ProdO3Chap[0][0]
      solar.ChapO3_uncert[alt] = ProdO3Chap[0][1]
      solar.ChapSPOzone[alt] = ProdO3Chap[0][2]
      solar.ChapSPOzone_uncert[alt] = ProdO3Chap[0][3]
      solar.MLRO3QA[alt] = ProdO3Chap[0][4]

   VDataO3Chap.detach()


   #Get the aerosol ozone product
   VDataO3Aero = DataInterface.attach(Index)
   Index += 2
   for alt in range(solar.num_bins):

      try:
         ProdO3Aero = VDataO3Aero.read()
      except HDF.HDF4Error:
         VDataO3Aero.detach()
         print("Failed to read the aerosol ozone product from the HDF file")
         return(-1,-1)

      solar.Ozone_ao3[alt] = ProdO3Aero[0][0]
      solar.Ozone_ao3_uncert[alt] = ProdO3Aero[0][1]
      solar.aO3SPOzone[alt] = ProdO3Aero[0][2]
      solar.aO3SPOzone_uncert[alt] = ProdO3Aero[0][3]
      solar.Ozone_aO3QA[alt] = ProdO3Aero[0][4]

   VDataO3Aero.detach()


   #Get the water vapor product
   VDataH2O = DataInterface.attach(Index)
   Index += 2

   for alt in range(solar.num_bins):

      try:
         ProdH2O = VDataH2O.read()
      except HDF.HDF4Error:
         VDataH2O.detach()
         print("Failed to read the water vapor product from the HDF file")
         return(-1,-1)

      solar.WaterVaporNDP[alt] = ProdH2O[0][0]
      solar.WaterVaporNDP_uncert[alt] = ProdH2O[0][1]
      solar.H2OQA[alt] = ProdH2O[0][2]

   VDataH2O.detach()


   #Get the nitrogen dioxide product
   VDataNO2 = DataInterface.attach(Index)
   Index += 2
   for alt in range(solar.num_bins):

      try:
         ProdNO2 = VDataNO2.read()
      except HDF.HDF4Error:
         VDataNO2.detach()
         print("Failed to read the NO2 product from the HDF file")
         return(-1,-1)

      solar.NO2NDP[alt] = ProdNO2[0][0]
      solar.NO2NDP_uncert[alt] = ProdNO2[0][1]
      solar.SPNO2[alt] = ProdNO2[0][2]
      solar.SPNO2_uncert[alt] = ProdNO2[0][3]
      solar.NO2QA[alt] = ProdNO2[0][4]

   VDataNO2.detach()


   #Get the retrieved temperature/pressure product
   VDataTempPresRet = DataInterface.attach(Index)
   Index += 2
   for alt in range(solar.num_bins):

      try:
         ProdTempPresRet = VDataTempPresRet.read()
      except HDF.HDF4Error:
         VDataTempPresRet.detach()
         print("Failed to read the retrieved T/P profiles from the HDF file")
         return(-1,-1)

      solar.RetTemp[alt] = ProdTempPresRet[0][0]
      solar.RetTemp_uncert[alt] = ProdTempPresRet[0][1]
      solar.RetPress[alt] = ProdTempPresRet[0][2]
      solar.RetPress_uncert[alt] = ProdTempPresRet[0][3]
      solar.RetTPQA[alt] = ProdTempPresRet[0][4]

   VDataTempPresRet.detach()


   #Get information on the aerosol product
   VDataAeroInfo = DataInterface.attach(Index)
   Index += 2
   for chan in range(solar.num_ao3_channels):
      try:
         ProdAeroInfo = VDataAeroInfo.read()
      except HDF.HDF4Error:
         VDataFileInfo.detach()
         print("Failed to read the aerosol metadata from the HDF file")
         return(-1,-1)

      solar.Aer_wavelength[chan] = ProdAeroInfo[0][0]
      solar.Aer_width[chan] = ProdAeroInfo[0][1]
      solar.StratOD[chan] = ProdAeroInfo[0][2]
      solar.StratOD_uncert[chan] = ProdAeroInfo[0][3]
      solar.StratODQA[chan] = ProdAeroInfo[0][4]

   VDataAeroInfo.detach()


   #Get the aerosol extinction product
   VDataAeroExt = DataInterface.attach(Index)
   Index += 2
   for alt in range(solar.num_aer_bins):

      try:
         ProdAeroExt = VDataAeroExt.read()
      except HDF.HDF4Error:
         VDataAeroExt.detach()
         print("Failed to read the aerosol extinction product from the HDF file")
         return(-1,-1)

      for chan in range(num_ao3_channels):

         solar.AerosolExt.aerext[alt][chan] = ProdAeroExt[0][chan*3]
         solar.AerosolExt.aerext_uncert[alt][chan] = ProdAeroExt[0][chan*3+1]
         solar.AerosolExt.aerQA[alt][chan] = ProdAeroExt[0][chan*3+2]

   VDataAeroExt.detach()


   #Get the aerosol extinction ratio product
   VDataAeroRat = DataInterface.attach(Index)
   Index += 2
   for alt in range(solar.num_aer_bins):

      try:
         ProdAeroRat = VDataAeroRat.read()
      except HDF.HDF4Error:
         VDataAeroRat.detach()
         print("Failed to read the aerosol extinction ratio product from the HDF file")
         return (-1,-1)

      solar.Aerosol1020[alt] = ProdAeroRat[0][0]
      solar.Aerosol1020_uncert[alt] = ProdAeroRat[0][1]
      solar.Aero1020QA[alt] = ProdAeroRat[0][2]
      solar.asd_flag[alt] = ProdAeroRat[0][3]

   VDataAeroRat.detach()


   DataInterface.end()
   FileHandle.close()

   return (solar, 0)


##############################################################


def sol_l2_bin(Filename):
   """
   Name:        sol_l2_bin
   Author:      David Huber <david.b.huber@nasa.gov>
   Inputs:      Filename of a solar level 2 binary product file
   Outputs:     1) A data object of type SolL2Data containing the product data
                2) A status flag indicating whether the read was successful or not
   Description: This function reads the data from a binary level 2 product file
                and returns a data object containing the data from the file.
                A status flag is also returned and should be checked before
                attempting to access the structure after function completion.  A
                status value of 0 indicates a success while a value of -1
                indicates that an error occurred.
   """

   #Import byteorder from sys to determine system endianness
   from sys import byteorder

   EndianFlag = -1
   order = byteorder

   if(order == "big"):
      EndianFlag = 0
      read_int32 = __b_read_int32
      read_float32 = __b_read_float32
   elif(order == "little"):
      EndianFlag = 1
      read_int32 = __l_read_int32
      read_float32 = __l_read_float32
   else:
      print("Unable to determine endianness of this machine\n")
      return (-1, -1)
    
   #Get Version
   vers = get_version(Filename)

   #Open the file
   File = open(Filename, "r")

   if vers <= 5.0:
     #Retrieve scalar information from the product file
     event_id = read_int32(File, 1)[0]
     yr_day_tag = read_int32(File, 1)[0]
     mission_time = read_float32(File, 1)[0]
     int_fill_value = read_int32(File, 1)[0]
     flt_fill_value = read_float32(File, 1)[0]
     mission_id = read_int32(File, 1)[0]
     L0DO_Version = read_float32(File, 1)[0]
     L0_Version = read_float32(File, 1)[0]
     Software_Version = read_float32(File, 1)[0]
     Dataproduct_Version = read_float32(File, 1)[0]
     DB_Version = read_float32(File, 1)[0]
     GRAM95_Version = read_float32(File, 1)[0]
     Met_Version = read_float32(File, 1)[0]
     bin_height = read_float32(File, 1)[0]
     num_bins = read_int32(File, 1)[0]
     num_ao3_channels = read_int32(File, 1)[0]
     num_grnd_trk = read_int32(File, 1)[0]
     num_aer_bins = read_int32(File, 1)[0]

     #Initialize the solar object
     solar = SolL2Data(vers,num_grnd_trk, num_bins, num_ao3_channels, num_aer_bins, 0)
      
     #Fill the solar object with the scalar data
     solar.event_id = event_id
     solar.yr_day_tag = yr_day_tag
     solar.mission_time = mission_time
     solar.int_fill_value = int_fill_value
     solar.flt_fill_value = flt_fill_value
     solar.mission_id = mission_id
     solar.L0DO_Version = L0DO_Version
     solar.L0_Version = L0_Version
     solar.DB_Version = DB_Version
     solar.GRAM95_Version = GRAM95_Version
     solar.Met_Version = Met_Version
     solar.Software_Version = Software_Version
     solar.Dataproduct_Version = Dataproduct_Version
     solar.bin_height = bin_height

     #Read the remainder of the data
     #Event type
     solar.sc_evt_type = read_int32(File,1)[0]
     solar.gnd_evt_type = read_int32(File,1)[0]
     #Beta angle
     solar.BetaAngle = read_float32(File,1)[0]
     #Event status flag
     solar.EvtStatusFlag = read_int32(File,1)[0]
     #Starting time/position
     solar.st_date = read_int32(File,1)[0]
     solar.st_time = read_int32(File,1)[0]
     solar.st_latitude = read_float32(File,1)[0]
     solar.st_longitude = read_float32(File,1)[0]
     solar.st_altitude = read_float32(File,1)[0]
     #Ending time/position
     solar.end_date = read_int32(File,1)[0]
     solar.end_time = read_int32(File,1)[0]
     solar.end_latitude = read_float32(File,1)[0]
     solar.end_longitude = read_float32(File,1)[0]
     solar.end_altitude = read_float32(File,1)[0]
     #Ground track information
     solar.gt_date = read_int32(File,solar.num_grnd_trk)
     solar.gt_time = read_int32(File,solar.num_grnd_trk)
     solar.gt_latitude = read_float32(File,solar.num_grnd_trk)
     solar.gt_longitude = read_float32(File,solar.num_grnd_trk)
     solar.gt_ray_dir = read_float32(File,solar.num_grnd_trk)
     #Altitude registration
     solar.Homogeneity = read_int32(File,solar.num_bins)
     solar.geom_alt = read_float32(File,solar.num_bins)
     solar.potential_alt = read_float32(File,solar.num_bins)
     #Temperature/pressure profiles
     solar.CurrentTemp = read_float32(File,solar.num_bins)
     solar.CurrentTemp_uncert = read_float32(File,solar.num_bins)
     solar.CurrentPress = read_float32(File,solar.num_bins)
     solar.CurrentPress_uncert = read_float32(File,solar.num_bins)
     solar.TPSource = read_int32(File,solar.num_bins)
     #Tropopause temperature/altitude
     solar.trop_temp = read_float32(File,1)[0]
     solar.trop_alt = read_float32(File,1)[0]
     #Composite O3 products
     solar.CompositeO3 = read_float32(File,solar.num_bins)
     solar.CompositeO3_uncert = read_float32(File,solar.num_bins)
     solar.SPOzone = read_float32(File,solar.num_bins)
     solar.SPOzone_uncert = read_float32(File,solar.num_bins)
     solar.CompO3QA = read_int32(File,solar.num_bins)
     #Mesospheric O3 products
     solar.MesO3 = read_float32(File,solar.num_bins)
     solar.MesO3_uncert = read_float32(File,solar.num_bins)
     solar.MesSPOzone = read_float32(File,solar.num_bins)
     solar.MesSPOzone_uncert = read_float32(File,solar.num_bins)
     solar.MesO3QA = read_int32(File,solar.num_bins)
     #Chappuis O3 products
     solar.ChapO3 = read_float32(File,solar.num_bins)
     solar.ChapO3_uncert = read_float32(File,num_bins)
     solar.ChapSPOzone = read_float32(File,solar.num_bins)
     solar.ChapSPOzone_uncert = read_float32(File,solar.num_bins)
     solar.MLRO3QA = read_int32(File,solar.num_bins)
     #Aerosol-ozone O3 products
     solar.Ozone_ao3 = read_float32(File,solar.num_bins)
     solar.Ozone_ao3_uncert = read_float32(File,solar.num_bins)
     solar.aO3SPOzone = read_float32(File,solar.num_bins)
     solar.aO3SPOzone_uncert = read_float32(File,solar.num_bins)
     solar.Ozone_aO3QA = read_int32(File,solar.num_bins)
     #Water vapor product
     solar.WaterVaporNDP = read_float32(File,solar.num_bins)
     solar.WaterVaporNDP_uncert = read_float32(File,solar.num_bins)
     solar.H2OQA = read_int32(File,solar.num_bins)
     #NO2 products
     solar.NO2NDP = read_float32(File,solar.num_bins)
     solar.NO2NDP_uncert = read_float32(File,solar.num_bins)
     solar.SPNO2 = read_float32(File,solar.num_bins)
     solar.SPNO2_uncert = read_float32(File,solar.num_bins)
     solar.NO2QA = read_int32(File,solar.num_bins)
     #Retrieved temperature/pressure
     solar.RetTemp = read_float32(File,solar.num_bins)
     solar.RetTemp_uncert = read_float32(File,solar.num_bins)
     solar.RetPress = read_float32(File,solar.num_bins)
     solar.RetPress_uncert = read_float32(File,solar.num_bins)
     solar.RetTPQA = read_int32(File,solar.num_bins)
     #Aerosol product information
     solar.Aer_wavelength = read_float32(File,solar.num_ao3_channels)
     solar.Aer_width = read_float32(File,solar.num_ao3_channels)
     solar.StratOD = read_float32(File,solar.num_ao3_channels)
     solar.StratOD_uncert = read_float32(File,solar.num_ao3_channels)
     solar.StratODQA = read_int32(File,solar.num_ao3_channels)
     #Aerosol extinction data
     for chan in range(num_ao3_channels):
        solar.AerosolExt.aerext[:,chan] = read_float32(File, solar.num_aer_bins)
        solar.AerosolExt.aerext_uncert[:,chan] = read_float32(File, solar.num_aer_bins)
        solar.AerosolExt.aerQA[:,chan] = read_int32(File, solar.num_aer_bins)
     solar.asd_flag = read_int32(File, solar.num_aer_bins)
     #Aerosol extinction ratio data
     solar.Aerosol1020 = read_float32(File, solar.num_aer_bins)
     solar.Aerosol1020_uncert = read_float32(File, solar.num_aer_bins)
     solar.Aero1020QA = read_int32(File, solar.num_aer_bins)

     File.close()
     return(solar,0)

   else:
     #Retrieve scalar information from the product file
     event_id = read_int32(File, 1)[0]
     date = read_int32(File, 1)[0]
     fraction_time = read_float32(File, 1)[0]
     latitude = read_float32(File, 1)[0]
     longitude = read_float32(File, 1)[0]
     time = read_int32(File, 1)[0]
     int_fill_value = read_int32(File, 1)[0]
     flt_fill_value = read_float32(File, 1)[0]
     mission_id = read_int32(File, 1)[0]
     L0DO_Version = read_float32(File, 1)[0]
     CCDVersion = read_int32(File, 1)[0]
     L0_Version = read_float32(File, 1)[0]
     Software_Version = read_float32(File, 1)[0]
     Dataproduct_Version = read_float32(File, 1)[0]
     Spectroscopic_DataBase_Version = read_float32(File, 1)[0]
     GRAM95_Version = read_float32(File, 1)[0]
     Met_Version = read_float32(File, 1)[0]
     bin_height = read_float32(File, 1)[0]
     num_bins = read_int32(File, 1)[0]
     num_met_grid = read_int32(File, 1)[0]
     num_aer_channels = read_int32(File, 1)[0]
     num_grnd_trk = read_int32(File, 1)[0]
     num_aer_bins = read_int32(File, 1)[0]

     #Initialize the solar object
     solar = SolL2Data(vers,num_grnd_trk, num_bins, num_aer_channels, num_aer_bins,num_met_grid)

     #Fill the solar object with the scalar data
     solar.event_id = event_id
     solar.date = date
     solar.year_fraction = fraction_time
     solar.latitude = latitude 
     solar.longitude = longitude 
     solar.time = time
     solar.int_fill_value = int_fill_value
     solar.flt_fill_value = flt_fill_value
     solar.mission_id = mission_id
     solar.L0DO_Version = L0DO_Version
     solar.CCDTable_Version = CCDVersion 
     solar.L0_Version = L0_Version
     solar.Spectroscopic_DataBase_Version = Spectroscopic_DataBase_Version
     solar.GRAM95_Version = GRAM95_Version
     solar.Met_Version = Met_Version
     solar.Software_Version = Software_Version
     solar.Dataproduct_Version = Dataproduct_Version
     solar.bin_height = bin_height
     
     #Event type
     solar.sc_evt_type = read_int32(File,1)[0]
     solar.gnd_evt_type = read_int32(File,1)[0]
     #Beta angle
     solar.BetaAngle_Solar = read_float32(File,1)[0]
     #Aurora_Flag
     solar.Aurora_Flag = read_int32(File, 1)[0]
     #Event status flag
     solar.Ephemeris_Source = read_int32(File,1)[0]
     #Ground track information
     solar.gt_date = read_int32(File,solar.num_grnd_trk)
     solar.gt_time = read_int32(File,solar.num_grnd_trk)
     solar.gt_latitude = read_float32(File,solar.num_grnd_trk)
     solar.gt_longitude = read_float32(File,solar.num_grnd_trk)
     solar.gt_ray_dir = read_float32(File,solar.num_grnd_trk)
     #Space Craft Information 
     solar.Space_Craft_Lat = read_float32(File,solar.num_grnd_trk)
     solar.Space_Craft_Lon = read_float32(File,solar.num_grnd_trk)
     solar.Space_Craft_Alt = read_float32(File,solar.num_grnd_trk)
     #Altitude registration
     solar.Homogeneity = read_int32(File,solar.num_bins)
     solar.Altitude = read_float32(File,solar.num_bins)
     solar.geopotential_alt = read_float32(File,solar.num_bins)
     #Temperature/pressure profiles
     solar.Temperature = read_float32(File,solar.num_bins)
     solar.Temperature_uncert = read_float32(File,solar.num_bins)
     solar.Pressure = read_float32(File,solar.num_bins)
     solar.Pressure_uncert = read_float32(File,solar.num_bins)
     solar.Neutral_Density = read_float32(File,solar.num_bins)
     solar.Neutral_Density_uncert = read_float32(File,solar.num_bins)
     solar.Temp_Pressure_Source = read_int32(File,solar.num_bins)
     #Tropopause temperature/altitude
     solar.trop_temp = read_float32(File,1)[0]
     solar.trop_alt = read_float32(File,1)[0]
     solar.trop_press = read_float32(File,1)[0]
     #Met Temp/Press profiles 
     solar.met_pressure = read_float32(File, solar.num_met_grid)
     solar.met_temp = read_float32(File, solar.num_met_grid)
     solar.met_temp_unc = read_float32(File, solar.num_met_grid)
     solar.met_altitude = read_float32(File, solar.num_met_grid)
     solar.met_source = read_int32(File, 1)[0]
     #CCD and Bit flags
     solar.CCD_Temperature = read_float32(File,1)[0]
     solar.Spectrometer_Zenith_Temperature = read_float32(File, 1)[0]
     solar.CCD_Temperature_minus_TEC = read_float32(File, 1)[0]
     solar.Ephemeris_Quality = read_int32(File, 1)[0]
     solar.SpecCalShift = read_float32(File, 1)[0]
     solar.SpecCalStretch = read_float32(File, 1)[0]
     solar.QAFlag = read_int32(File, 1)[0]
     solar.QAFlag_Altitude = read_int32(File, solar.num_bins)
     #Comp Ozone 
     solar.Ozone_Composite = read_float32(File, solar.num_bins)
     solar.Ozone_Composite_uncert = read_float32(File, solar.num_bins)
     solar.Ozone_Composite_QA = read_int32(File, solar.num_bins) 
     #Mes Ozone
     solar.Ozone_Mes = read_float32(File, solar.num_bins)
     solar.Ozone_Mes_uncert = read_float32(File, solar.num_bins)
     solar.Ozone_Mes_QA = read_int32(File, solar.num_bins) 
     #MLR Ozone
     solar.Ozone_MLR = read_float32(File, solar.num_bins)
     solar.Ozone_MLR_uncert = read_float32(File, solar.num_bins)
     solar.Ozone_MLR_QA = read_int32(File, solar.num_bins)
     #Aero Ozone
     solar.Ozone_ao3 = read_float32(File, solar.num_bins)
     solar.Ozone_ao3_uncert = read_float32(File, solar.num_bins)
     solar.Ozone_ao3_QA = read_int32(File, solar.num_bins) 
     #H20
     solar.H2O = read_float32(File, solar.num_bins)
     solar.H2O_uncert = read_float32(File, solar.num_bins)
     solar.H2O_QA = read_int32(File, solar.num_bins)
     #NO2
     solar.NO2 = read_float32(File, solar.num_bins)
     solar.NO2_uncert = read_float32(File, solar.num_bins)
     solar.NO2_QA = read_int32(File, solar.num_bins)
     #Retrieved Temp/Press
     solar.RetTemp = read_float32(File, solar.num_bins) 
     solar.RetTemp_uncert = read_float32(File, solar.num_bins)
     solar.RetPress = read_float32(File, solar.num_bins)
     solar.RetPress_uncert = read_float32(File, solar.num_bins)
     solar.RetTP_QA = read_int32(File, solar.num_bins)
     #Aerosol product information
     solar.Aer_wavelength = read_float32(File,solar.num_aer_channels)
     solar.Aer_width = read_float32(File,solar.num_aer_channels)
     solar.Molecular_SCT = read_float32(File, solar.num_aer_channels)
     solar.Molecular_SCT_uncert = read_float32(File, solar.num_aer_channels)
     solar.Strat_Aer_OD = read_float32(File,solar.num_aer_channels)
     solar.Strat_Aer_OD_uncert = read_float32(File,solar.num_aer_channels)
     solar.Strat_Aer_OD_QA = read_int32(File,solar.num_aer_channels)
     #Aerosol extinction data
     for chan in range(num_aer_channels):
        solar.AerosolExt.aerext[:,chan] = read_float32(File, solar.num_aer_bins)
        solar.AerosolExt.aerext_uncert[:,chan] = read_float32(File, solar.num_aer_bins)
        solar.AerosolExt.aerQA[:,chan] = read_int32(File, solar.num_aer_bins)

     File.close()
     #Decode Bits 
     if (solar.QAFlag & 2**0) != 0:
       solar.HexErrFlag = 1
     if (solar.QAFlag & 2**1) != 0:
       solar.ContWindowClosedFlag = 1
     if (solar.QAFlag & 2**2) != 0:
       solar.TimeQualFlag = 1
     if (solar.QAFlag & 2**3) != 0:
       solar.DMPExoFlag = 1
     if (solar.QAFlag & 2**4) != 0:
       solar.BlockExoFlag = 1
     if (solar.QAFlag & 2**5) != 0:
       solar.SpectralCalFlag =1 
     if (solar.QAFlag & 2**6) != 0:
       solar.SolarEclipseFlag =1

     for i in range(0,solar.num_bins):
       if (solar.QAFlag_Altitude[i] & 2**0) != 0:
         solar.DMPAltFlag[i] = 1


     return(solar,0)


##############################################################


def sol_l1_hdf5(Filename):
   """
   Name:        sol_l1_hdf5
   Author:      David Huber <david.b.huber@nasa.gov>
   Inputs:      Filename of a solar level 1 HDF5 product file
   Outputs:     1) A data object of type SolTranData containing the product data
                2) A status flag indicating whether the read was successful or not
   Description: This function reads the data from an HDF5 level 1 product file
                and returns a data object containing the data from the file.
                A status flag is also returned and should be checked before
                attempting to access the structure after function completion.  A
                status value of 0 indicates a successful read while a value of -1
                indicates that an error occurred.
   """

   #Import h5py for interaction with HDF5 files
   import h5py

   #Get Version
   vers = get_version(Filename)
   #Check that the input file exists and is an HDF5 file
   try:
      File = h5py.File(Filename, "r")
   except OSError:
      print(Filename, "is not an HDF5 file. Exiting...\n")
      return(SolL2Data(1,1,1,1), -1)

   #Declare the section names to take up less space when actually reading them in
   Section1 = "Section 1.0 - File Header/Section 1.0 - File Header"
   Section2 = "Section 2.0 - Product Identification/Section 2.0 - Product Identification"
   Section3 = "Section 3.0 - File Description/Section 3.0 - File Description"
   Section4Root = "Section 4.0 - Event Identification"
   Section4 = Section4Root + "/Event Identification"
   Section41 = (Section4Root + "/Section 4.1 - Ground Track Data Over This Event" +
                "/Section 4.1 - Ground Track Data Over This Event")
   Section42 = (Section4Root + "/Section 4.2 - Spacecraft Data Over This Event" +
                "/Section 4.2 - Spacecraft Data Over This Event")
   Section43 = (Section4Root + "/Section 4.3 - Instrument Performance Data and Quality Flags For This Event" +
                "/Section 4.3 - Instrument Performance Data and Quality Flags For This Event")
   Section44 = (Section4Root + "/Section 4.4 - Altitude Based BitFlags For This Event" +
                "/Section 4.4 - Altitude Based BitFlags For This Event")
   Section5Root = "Section 5.0 - Pressure Surface-based Met Data"
   Section51 = Section5Root + "/Pressure Data"
   Section52 = Section5Root + "/Tropopause Data"
   Section6 = "Section 6.0 - CCD Information/Section 6.0 - CCD Information"
   Section7Root = "Section 7.0 - Altitude-based Profiles"
   Section7 = Section7Root + "/Section 7.0 - Altitude-based Profiles"
   Section71 = (Section7Root + "/Section 7.01 - Transmission Profile for Pixel Group  1" +
              "/Section 7.01 - Transmission Profile for Pixel Group  1")

   #Make sure that we have the correct file type by checking whether all datasets exist
   e1 = Section1 in File
   e2 = Section2 in File
   e3 = Section3 in File
   e4 = Section4 in File
   e41 = Section41 in File
   e42 = Section42 in File
   e43 = Section43 in File
   e44 = Section44 in File
   e51 = Section51 in File
   e52 = Section52 in File
   e6 = Section6 in File
   e7 = Section7 in File
   e71 = Section71 in File

   #print(e1, e2, e3, e4, e41, e42, e43, e44, e51, e52, e6, e7, e71)
   if(not(e1 & e2 & e3 & e4 & e41 & e42 & e43 & e44 & e51 & e52 & e6 & e7 & e71)):
      print("Error reading " + str(Filename) + ": Unable to locate all SAGE datasets. Exiting...\n")
      errsol = SolL2Data(1, 1, 1, 1,1,1)
      return(SolL2Data(1, 1, 1, 1,1,1), -1)

   #Get the file description handle
   DataFile = File[Section3][0]
   profile_count = DataFile[1]
   num_grnd_trk = DataFile[2]
   num_press_grid = DataFile[3]
   num_CCDPxlGrps = DataFile[4]
   num_alt_bins = DataFile[5]

   #Declare the output data object
   solar = SolTranData(vers,num_grnd_trk, num_press_grid, num_alt_bins, profile_count, num_CCDPxlGrps)

   #Get the altitude bin height
   solar.bin_height = DataFile[0]

   #Get the header information handle
   DataHeader = File[Section1][0]
   solar.event_id = DataHeader[0]
   solar.Year_Fraction = DataHeader[1]
   solar.date = DataHeader[2]
   solar.latitude = DataHeader[3]
   solar.longitude = DataHeader[4]
   solar.time = DataHeader[5]
   solar.int_fill_value = DataHeader[6]
   solar.flt_fill_value = DataHeader[7]
   solar.mission_id = DataHeader[8]

   #Get the product information handle
   DataProduct = File[Section2][0]
   solar.L0DO_Version = DataProduct[0]
   solar.CCDVersion = DataProduct[1]
   solar.L0_Version = DataProduct[2]
   solar.Spectroscopic_DataBase_Version = DataProduct[3]
   solar.GRAM95_Version = DataProduct[4]
   solar.Met_Version = DataProduct[5]
   solar.Software_Version = DataProduct[6]
   solar.Dataproduct_Version = DataProduct[7]

   #Get the event identification handle
   DataEvent = File[Section4][0]
   solar.sc_evt_type = DataEvent[0]
   solar.gnd_evt_type = DataEvent[1]
   solar.BetaAngle_Solar = DataEvent[2]
   solar.Aurora_Flag = DataEvent[3]
   solar.Ephemeris_Source = DataEvent[4]

   #Get the event ground track information handle
   DataEventGround = np.asarray(File[Section41])
   solar.gt_date = DataEventGround["Date (YYYYMMDD)"]
   solar.gt_time = DataEventGround["Time (HHMMSS)"]
   solar.gt_latitude = DataEventGround["Subtangent Latitude (0.0 +/- 90.0 deg)"]
   solar.gt_longitude = DataEventGround["Subtangent Longitude (0.0 +/- 180.0 deg)"]
   solar.gt_ray_dir = DataEventGround["Ray Path Direction @ Subtan. Pt. (0.0 - 359.99 deg)"]

   #Get the Space Craft information handle
   DataSpaceCraft = np.asarray(File[Section42])
   solar.Space_Craft_Lat = DataSpaceCraft["Spacecraft Subtangent Latitude (0.0 +/- 90.0 deg)"]
   solar.Space_Craft_Lon = DataSpaceCraft["Spacecraft Subtangent Longitude (0.0 +/- 180.0 deg)"]
   solar.Space_Craft_Alt = DataSpaceCraft["Spacecraft Subtangent Altitude above Earth   (KM)"]

   #Get Performance Data and Qual Flags
   DataQualFlag = File[Section43][0]
   solar.CCD_Temperature = DataQualFlag[0]
   solar.Spectrometer_Zenith_Temperature = DataQualFlag[1]
   solar.CCD_Temperature_minus_TEC= DataQualFlag[2]
   solar.Ephemeris_Quality = DataQualFlag[3]
   solar.SpecCalShift = DataQualFlag[4]
   solar.SpecCalStretch = DataQualFlag[5]
   solar.QAFlag = DataQualFlag[6]

   #Get Alt Bases Bit Flags 
   DataAltFlag = np.asarray(File[Section44])
   solar.QAFlag_Altitude = DataAltFlag["Altitude Based Bit Flags"]

   #Get the T/P profiles handle
   DataTP = np.asarray(File[Section51])

   solar.met_altitude = DataTP['Met Altitude (km)']
   solar.met_temp = DataTP['Met Temperature (K)']
   solar.met_temp_unc = DataTP['Met Temperature Unc (K)']
   solar.met_pressure = DataTP['Met Pressure (hPa)']

   #Get the tropopause data handle
   DataTrop = File[Section52][0]
   solar.trop_alt = DataTrop[0]
   solar.trop_temp = DataTrop[1]
   solar.trop_press = DataTrop[2]
   solar.met_source = DataTrop[3]

   #Get the pixel group information
   DataCCD = np.asarray(File[Section6])
   solar.start_pixel_num = DataCCD["Starting CCD Pixel Number"]
   solar.end_pixel_num = DataCCD["Ending CCD Pixel Number"]
   solar.central_wavelength = DataCCD["Central Wavelength PG n (nm)"]
   solar.half_bandwidth = DataCCD["Half-Bandwidth of PG n (nm)"]

   #Get the input meteorological data for processing
   DataMet = np.asarray(File[Section7])
   solar.Altitude = DataMet["Geometric Altitude (km)"]
   solar.Geopotential_Alt = DataMet["Geopotential Altitude (km)"]
   solar.Pressure = DataMet["Pressure (hPa)"]
   solar.Pressure_uncert = DataMet["Pressure Uncertainty (hPa)"]
   solar.Temperature = DataMet["Temperature (K)"]
   solar.Temperature_uncert = DataMet["Temperature Uncertainty (K)"]
   solar.Neutral_Density = DataMet["Density (cm-3)"]
   solar.Neutral_Density_uncert = DataMet["Density Uncertainty (cm-3)"]
   solar.Temp_Pressure_Source = DataMet["P/T Array Source Flag (0-4)"]

   #Get the transmission data for every pixel group
   for pg in range(solar.num_CCDPxlGrps):
      if(pg < 9):
         SubSec = ("/Section 7.0" + str(pg+1) +
               " - Transmission Profile for Pixel Group  " + str(pg+1))
      else:
         SubSec = ("/Section 7." + str(pg+1) +
               " - Transmission Profile for Pixel Group " + str(pg+1))
      
      SecName = Section7Root + SubSec + SubSec
      DataTran = np.asarray(File[SecName])

      solar.pg_trans_profiles.Transmission[:,pg] = (
         DataTran["Transmission Profile"])
      solar.pg_trans_profiles.Transmission_unc[:,pg] = (
         DataTran["Transmission Profile standard deviation"])
      solar.pg_trans_profiles.TransQA[:,pg] = (
         DataTran["Transmission Profile QA bit flags"])

   #Get the transmission data for the photodiode
   SubSec = "/Section 7.87 - Transmission Profile for Photodiode"
   SecName = Section7Root + SubSec + SubSec
   DataTran = np.asarray(File[SecName])

   solar.pg_trans_profiles.Transmission[:,86] = (
      DataTran["Transmission Profile"])
   solar.pg_trans_profiles.Transmission_unc[:,86] = (
         DataTran["Transmission Profile standard deviation"])
   solar.pg_trans_profiles.TransQA[:,86] = (
      DataTran["Transmission Profile QA bit flags"])

   File.close()

   #Decode Bits 
   if (solar.QAFlag & 2**0) != 0:
     solar.HexErrFlag = 1
   if (solar.QAFlag & 2**1) != 0:
     solar.ContWindowClosedFlag = 1
   if (solar.QAFlag & 2**2) != 0:
     solar.TimeQualFlag = 1
   if (solar.QAFlag & 2**3) != 0:
     solar.DMPExoFlag = 1
   if (solar.QAFlag & 2**4) != 0:
     solar.BlockExoFlag = 1
   if (solar.QAFlag & 2**5) !=0:
     solar.SpectralCalFlag = 1
   if (solar.QAFlag & 2**6) !=0:
     solar.SolarEclipseFlag =1

   for i in range(0,solar.num_alt_bins):
     if (solar.QAFlag_Altitude[i] & 2**0) != 0:
       solar.DMPAltFlag[i] = 1


   return (solar, 0)


########################################################################


#Read HDF4 level 1 product files
def sol_l1_hdf4(Filename):
   """
   Name:        sol_l1_hdf4
   Author:      David Huber <david.b.huber@nasa.gov>
   Inputs:      The filename of a solar level 1 HDF4 product file
   Outputs:     1) A data object of type SolTranData containing the product data
                2) A status flag indicating whether the read was successful or not
   Description: This function reads the data from an HDF4 level 1 product file
                and returns a data object containing the data from the file.
                A status flag is also returned and should be checked before
                attempting to access the structure after function completion.  A
                status value of 0 indicates a success while a value of -1
                indicates that an error occurred.
   """
   #Import pyhdf or python-hdf4 for interaction with HDF4 files.
   #PyHDF is only available for Python 2.x
   #Python-HDF4 is a fork of PyHDF (hence the library name is pyhdf) and is
   #available for both Python 2.x and 3.x.

   #See installation instructions for Python-HDF4 at
   #  http://fhs.github.io/python-hdf4/install.html
   #Get Version
   vers = get_version(Filename)
   if vers >= 5.1:
     sys.exit('HDF4 files do not exist for v5.1 and higher. Use HDF5 reader')

   try:
      from pyhdf import HDF, VS
   except ImportError:
      if(version_info[0] == 3):
         raise ImportError('Unable to locate the python-hdf4 library.' +
                           '  Please ensure version 0.9 or better is installed')
      elif(version_info[0] == 2):
         raise ImportError('Unable to locate the pyhdf or python-hdf4 library.' +
                           '  Please ensure version 0.9 (or higher) of either is installed.')

   #Open the file
   FileHandle = HDF.HDF(Filename)
   DataInterface = FileHandle.vstart()

   #Find the starting index
   for Index in range(__c_MaxIndex+1):
      try:
         TestVD = DataInterface.attach(Index)
         TestVD.detach()
         break
      except HDF.HDF4Error:
         continue

   if(Index == __c_MaxIndex):
      print("Failed to locate the starting VData index for ", Filename)
      return(-1,-1)

   #Get "Header" vdata information (Not actually the file header)
   VDataHeader = DataInterface.attach(Index)
   Index += 2
   try:
      HeaderData = VDataHeader.read()
   except HDF.HDF4Error:
      VDataHeader.detach()
      print("Failed to read header data from the HDF file")
      return(-1,-1)
   VDataHeader.detach()

   #Get product identification vdata information
   VDataProdId = DataInterface.attach(Index)
   Index += 2
   try:
      ProdIdData = VDataProdId.read()
   except HDF.HDF4Error:
      VDataProdId.detach()
      print("Failed to read product information from the HDF file")
      return(-1,-1)
   VDataProdId.detach()

   #Get file information
   VDataFileInfo = DataInterface.attach(Index)
   Index += 2
   try:
      ProdFileInfo = VDataFileInfo.read()
   except HDF.HDF4Error:
      VDataFileInfo.detach()
      print("Failed to read file information from the HDF file")
      return(-1,-1)
   VDataFileInfo.detach()

   #Get event information
   VDataEvent = DataInterface.attach(Index)
   Index += 2
   try:
      ProdEvent = VDataEvent.read()
   except HDF.HDF4Error:
      VDataEvent.detach()
      print("Failed to read event information from the HDF file")
      return(-1,-1)
   VDataEvent.detach()

   #Get information on the start of science data
   VDataSciStart = DataInterface.attach(Index)
   Index += 2
   try:
      ProdSciStart = VDataSciStart.read()
   except HDF.HDF4Error:
      VDataSciStart.detach()
      print("Failed to read science starting information from the HDF file")
      return(-1,-1)
   VDataSciStart.detach()

   #Get information on the end of the event
   VDataSciEnd = DataInterface.attach(Index)
   Index += 2
   try:
      ProdSciEnd = VDataSciEnd.read()
   except HDF.HDF4Error:
      VDataSciEnd.detach()
      print("Failed to read science ending information from the HDF file")
      return(-1,-1)
   VDataSciEnd.detach()


   #Collect array size information to initiate the output solar object
   profile_count = ProdFileInfo[0][1]
   num_grnd_trk = ProdFileInfo[0][2]
   num_press_grid = ProdFileInfo[0][3]
   num_CCDPxlGrps = ProdFileInfo[0][4]
   num_alt_bins = ProdFileInfo[0][5]

   #Instantiate the solar object
   solar = SolTranData(num_grnd_trk, num_press_grid, num_alt_bins, profile_count, num_CCDPxlGrps)

   #Begin populating the object attributes
   #Populate header data
   solar.event_id = HeaderData[0][0]
   solar.yr_day_tag = HeaderData[0][1]
   solar.mission_time = HeaderData[0][2]
   solar.int_fill_value = HeaderData[0][3]
   solar.flt_fill_value = HeaderData[0][4]
   solar.mission_id = HeaderData[0][5]
   #General product information
   solar.L0DO_Version = ProdIdData[0][0]
   solar.L0_Version = ProdIdData[0][1]
   solar.DB_Version = ProdIdData[0][2]
   solar.GRAM95_Version = ProdIdData[0][3]
   solar.Met_Version = ProdIdData[0][4]
   solar.Software_Version = ProdIdData[0][5]
   solar.Dataproduct_Version = ProdIdData[0][6]
   #Array sizes
   solar.bin_height = ProdFileInfo[0][0]
   #Event information
   solar.sc_evt_type = ProdEvent[0][0]
   solar.gnd_evt_type = ProdEvent[0][1]
   solar.BetaAngle = ProdEvent[0][2]
   solar.EvtStatusFlag = ProdEvent[0][3]
   #Event starting information
   solar.st_date = ProdSciStart[0][0]
   solar.st_time = ProdSciStart[0][1]
   solar.st_latitude = ProdSciStart[0][2]
   solar.st_longitude = ProdSciStart[0][3]
   solar.st_altitude = ProdSciStart[0][4]
   #Event ending information
   solar.end_date = ProdSciEnd[0][0]
   solar.end_time = ProdSciEnd[0][1]
   solar.end_latitude = ProdSciEnd[0][2]
   solar.end_longitude = ProdSciEnd[0][3]
   solar.end_altitude = ProdSciEnd[0][4]

   #Get information on the ground track during the event
   VDataGround = DataInterface.attach(Index)
   Index += 2
   for trk in range(solar.num_grnd_trk):

      try:
         ProdGround = VDataGround.read()
      except HDF.HDF4Error:
         VDataGround.detach()
         print("Failed to read ground track information from the HDF file")
         return(-1,-1)

      solar.gt_date[trk] = ProdGround[0][0]
      solar.gt_time[trk] = ProdGround[0][1]
      solar.gt_latitude[trk] = ProdGround[0][2]
      solar.gt_longitude[trk] = ProdGround[0][3]
      solar.gt_ray_dir[trk] = ProdGround[0][4]

   VDataGround.detach()


   #Get the tropopause information
   VDataTrop = DataInterface.attach(Index)
   Index += 1
   try:
      ProdTrop = VDataTrop.read()
   except HDF.HDF4Error:
      VDataTrop.detach()
      print("Failed to read troppause data from the HDF file")
      return(-1,-1)

   solar.trop_temp = ProdTrop[0][0]
   solar.trop_alt = ProdTrop[0][1]
   solar.met_Source = ProdTrop[0][2]

   VDataTrop.detach()


   #Get the temperature/pressure profiles used during processing
   VDataTempPres = DataInterface.attach(Index)
   Index += 2

   for alt in range(solar.num_press_grid):

      try:
         ProdTempPres = VDataTempPres.read()
      except HDF.HDF4Error:
         VDataTempPres.detach()
         print("Failed to read T/P profiles used during processing from the HDF file")
         return(-1,-1)

      solar.met_pressure[alt] = ProdTempPres[0][0]
      solar.met_temp[alt] = ProdTempPres[0][1]
      solar.met_temp_unc[alt] = ProdTempPres[0][2]
      solar.met_altitude[alt] = ProdTempPres[0][3]

   VDataTempPres.detach()


   #Get each pixel group's information
   VDataPGInfo = DataInterface.attach(Index)
   Index += 2

   for pg in range(solar.num_CCDPxlGrps):

      try:
         ProdPGInfo = VDataPGInfo.read()
      except HDF.HDF4Error:
         VDataPGInfo.detach()
         print("Failed to read pixel group data from the HDF file")
         return(-1,-1)

      solar.start_pixel_num[pg] = ProdPGInfo[0][0]
      solar.end_pixel_num[pg] = ProdPGInfo[0][1]
      solar.central_wavelength[pg] = ProdPGInfo[0][2]
      solar.half_bandwidth[pg] = ProdPGInfo[0][3]

   VDataPGInfo.detach()


   #Gather the temperature/pressure profile used for the retrieval
   VDataTPProf = DataInterface.attach(Index)
   Index += 2

   for alt in range(solar.num_alt_bins):

      try:
         ProdTPProf = VDataTPProf.read()
      except HDF.HDF4Error:
         VDataTPProf.detach()
         print("Failed to read T/P profiles used during retrieval from the HDF file")
         return(-1,-1)

      solar.Altitude[alt] = ProdTPProf[0][0]
      solar.CurrentPress[alt] = ProdTPProf[0][1]
      solar.CurrentTemp[alt] = ProdTPProf[0][2]
      solar.CurrentTemp_uncert[alt] = ProdTPProf[0][3]
      solar.TPSource[alt] = ProdTPProf[0][4]

   VDataTPProf.detach()


   #Get the transmission profiles
   for pg in range(solar.profile_count):
      VDataTrans = DataInterface.attach(Index)
      Index += 2

      for alt in range(solar.num_alt_bins):

         try:
            ProdTrans = VDataTrans.read()
         except HDF.HDF4Error:
            VDataTrans.detach()
            print("Failed to read transmission profiles from the HDF file")
            return(-1,-1)

         solar.pg_trans_profiles.GeometricAltitude[alt][pg] = ProdTrans[0][0]
         solar.pg_trans_profiles.Transmission[alt][pg] = ProdTrans[0][1]
         solar.pg_trans_profiles.Transmission_unc[alt][pg] = ProdTrans[0][2]
         solar.pg_trans_profiles.TransQA[alt][pg] = ProdTrans[0][3]

      VDataTrans.detach()


   DataInterface.end()
   FileHandle.close()

   return (solar, 0)


##############################################################


def sol_l1_bin(Filename):
   """
   Name:        sol_l1_bin
   Author:      David Huber <david.b.huber@nasa.gov>
   Inputs:      Filename of a solar level 1 binary product file
   Outputs:     1) A data object of type SolTranData containing the product data
                2) A status flag indicating whether the read was successful or not
   Description: This function reads the data from a binary level 1 product file
                and returns a data object containing the data from the file.
                A status flag is also returned and should be checked before
                attempting to access the structure after function completion.  A
                status value of 0 indicates a success while a value of -1
                indicates that an error occurred.
   """

   #Import byteorder from sys to determine endianness of the current machine
   from sys import byteorder

   EndianFlag = -1
   order = byteorder

   if(order == "big"):
      EndianFlag = 0
      read_int32 = __b_read_int32
      read_float32 = __b_read_float32
   elif(order == "little"):
      EndianFlag = 1
      read_int32 = __l_read_int32
      read_float32 = __l_read_float32
   else:
      print("Unable to determine endianness of this machine\n")
      return (-1, -1)

   #Get Version
   vers = get_version(Filename)

   #Open the file
   File = open(Filename, "r")

   if vers <= 5.0:
     #Retrieve scalar information from the product file
     event_id = read_int32(File, 1)[0]
     yr_day_tag = read_int32(File, 1)[0]
     mission_time = read_float32(File, 1)[0]
     int_fill_value = read_int32(File, 1)[0]
     flt_fill_value = read_float32(File, 1)[0]
     mission_id = read_int32(File, 1)[0]
     L0DO_Version = read_float32(File, 1)[0]
     L0_Version = read_float32(File, 1)[0]
     Software_Version = read_float32(File, 1)[0]
     Dataproduct_Version = read_float32(File, 1)[0]
     DB_Version = read_float32(File, 1)[0]
     GRAM95_Version = read_float32(File, 1)[0]
     Met_Version = read_float32(File, 1)[0]
     bin_height = read_float32(File, 1)[0]

     profile_count = read_int32(File, 1)[0]
     num_grnd_trk = read_int32(File, 1)[0]
     num_press_grid = read_int32(File, 1)[0]
     num_CCDPxlGrps = read_int32(File, 1)[0]
     num_alt_bins = read_int32(File, 1)[0]

     #Initialize the solar object
     solar = SolTranData(vers,num_grnd_trk, num_press_grid, num_alt_bins, profile_count,
        num_CCDPxlGrps)

     #Copy scalar information to the solar object
     solar.event_id = event_id
     solar.yr_day_tag = yr_day_tag
     solar.mission_time = mission_time
     solar.int_fill_value = int_fill_value
     solar.flt_fill_value = flt_fill_value
     solar.mission_id = mission_id
     solar.L0DO_Version = L0DO_Version
     solar.L0_Version = L0_Version
     solar.DB_Version = DB_Version
     solar.GRAM95_Version = GRAM95_Version
     solar.Met_Version = Met_Version
     solar.Software_Version = Software_Version
     solar.Dataproduct_Version = Dataproduct_Version
     solar.bin_height = bin_height
     solar.profile_count = profile_count
     solar.num_grnd_trk = num_grnd_trk
     solar.num_press_grid = num_press_grid
     solar.num_CCDPxlGrps = num_CCDPxlGrps
     solar.num_alt_bins = num_alt_bins

     #Read in the rest of the binary file
     #Event type
     solar.sc_evt_type = read_int32(File,1)[0]
     solar.gnd_evt_type = read_int32(File,1)[0]
     #sol beta angle
     solar.BetaAngle = read_float32(File,1)[0]
     #Event status flag
     solar.EvtStatusFlag = read_int32(File,1)[0]
     #Starting time/position
     solar.st_date = read_int32(File,1)[0]
     solar.st_time = read_int32(File,1)[0]
     solar.st_latitude = read_float32(File,1)[0]
     solar.st_longitude = read_float32(File,1)[0]
     solar.st_altitude = read_float32(File,1)[0]
     #Ending time/position
     solar.end_date = read_int32(File,1)[0]
     solar.end_time = read_int32(File,1)[0]
     solar.end_latitude = read_float32(File,1)[0]
     solar.end_longitude = read_float32(File,1)[0]
     solar.end_altitude = read_float32(File,1)[0]
     #Ground track information
     solar.gt_date = read_int32(File,solar.num_grnd_trk)
     solar.gt_time = read_int32(File,solar.num_grnd_trk)
     solar.gt_latitude = read_float32(File,solar.num_grnd_trk)
     solar.gt_longitude = read_float32(File,solar.num_grnd_trk)
     solar.gt_ray_dir = read_float32(File,solar.num_grnd_trk)
     #Tropopause temperature/altitude
     solar.trop_temp = read_float32(File,1)[0]
     solar.trop_alt = read_float32(File,1)[0]
     #Meteorological data
     solar.met_pressure = read_float32(File,solar.num_press_grid)
     solar.met_temp = read_float32(File,solar.num_press_grid)
     solar.met_temp_unc = read_float32(File,solar.num_press_grid)
     solar.met_altitude = read_float32(File,solar.num_press_grid)
     #Meteorological data source
     solar.met_Source = read_int32(File,1)[0]
     #Pixel group information
     solar.start_pixel_num = read_int32(File,solar.num_CCDPxlGrps)
     solar.end_pixel_num = read_int32(File,solar.num_CCDPxlGrps)
     solar.central_wavelength = read_float32(File,solar.num_CCDPxlGrps)
     solar.half_bandwidth = read_float32(File,solar.num_CCDPxlGrps)
     #Binned altitude
     solar.Altitude = read_float32(File,solar.num_alt_bins)
     #Temperature/pressure profiles used for the retrieval
     solar.CurrentPress = read_float32(File,solar.num_alt_bins)
     solar.CurrentTemp = read_float32(File,solar.num_alt_bins)
     solar.CurrentTemp_uncert = read_float32(File,solar.num_alt_bins)
     #Source of temperature/pressure data
     solar.TPSource = read_int32(File,solar.num_alt_bins)
     #Transmission data
     pg = solar.profile_count-1
     solar.pg_trans_profiles.GeometricAltitude[:,pg] = solar.Altitude[0:]
     solar.pg_trans_profiles.Transmission[:,pg] = read_float32(File, solar.num_alt_bins)
     solar.pg_trans_profiles.Transmission_unc[:,pg] = read_float32(File, solar.num_alt_bins)
     solar.pg_trans_profiles.TransQA[:,pg] = read_float32(File, solar.num_alt_bins)
     for pg in range(solar.num_CCDPxlGrps):
        solar.pg_trans_profiles.GeometricAltitude[:,pg] = solar.Altitude[0:]
        solar.pg_trans_profiles.Transmission[:,pg] = read_float32(File, solar.num_alt_bins)
        solar.pg_trans_profiles.Transmission_unc[:,pg] = read_float32(File, solar.num_alt_bins)
        solar.pg_trans_profiles.TransQA[:,pg] = read_float32(File, solar.num_alt_bins)

     File.close()
     return(solar,0)
   
   else:
     #Retrieve scalar information from the product file
     event_id = read_int32(File, 1)[0]
     date = read_int32(File, 1)[0]
     fraction_time = read_float32(File, 1)[0]
     latitude = read_float32(File, 1)[0]
     longitude = read_float32(File, 1)[0]
     time = read_int32(File, 1)[0]
     int_fill_value = read_int32(File, 1)[0]
     flt_fill_value = read_float32(File, 1)[0]
     mission_id = read_int32(File, 1)[0]
     L0DO_Version = read_float32(File, 1)[0]
     CCDVersion = read_int32(File, 1)[0]
     L0_Version = read_float32(File, 1)[0]
     Software_Version = read_float32(File, 1)[0]
     Dataproduct_Version = read_float32(File, 1)[0]
     Spectroscopic_DataBase_Version = read_float32(File, 1)[0]
     GRAM95_Version = read_float32(File, 1)[0]
     Met_Version = read_float32(File, 1)[0]
     bin_height = read_float32(File, 1)[0]

     profile_count = read_int32(File, 1)[0]
     num_grnd_trk = read_int32(File, 1)[0]
     num_press_grid = read_int32(File, 1)[0]
     num_CCDPxlGrps = read_int32(File, 1)[0]
     num_alt_bins = read_int32(File, 1)[0]

     #Initialize the solar object
     solar = SolTranData(vers, num_grnd_trk, num_press_grid, num_alt_bins, profile_count,
        num_CCDPxlGrps)

     #Copy scalar information to the solar object
     solar.event_id = event_id
     solar.date = date
     solar.Year_Fraction = fraction_time
     solar.latitude = latitude 
     solar.longitude = longitude 
     solar.time = time
     solar.int_fill_value = int_fill_value
     solar.flt_fill_value = flt_fill_value
     solar.mission_id = mission_id
     solar.L0DO_Version = L0DO_Version
     solar.CCDVersion = CCDVersion 
     solar.L0_Version = L0_Version
     solar.Spectroscopic_DataBase_Version = Spectroscopic_DataBase_Version
     solar.GRAM95_Version = GRAM95_Version
     solar.Met_Version = Met_Version
     solar.Software_Version = Software_Version
     solar.Dataproduct_Version = Dataproduct_Version
     solar.bin_height = bin_height
     solar.profile_count = profile_count
     solar.num_grnd_trk = num_grnd_trk
     solar.num_press_grid = num_press_grid
     solar.num_CCDPxlGrps = num_CCDPxlGrps
     solar.num_alt_bins = num_alt_bins
     #Read in the rest of the binary file
     #Event type
     solar.sc_evt_type = read_int32(File,1)[0]
     solar.gnd_evt_type = read_int32(File,1)[0]
     #sol beta angle
     solar.BetaAngle_Solar = read_float32(File,1)[0]
     #Aurora Flag
     solar.Aurora_Flag = read_int32(File,1)[0]
     #Event status flag
     solar.Ephemeris_Source = read_int32(File,1)[0]
     #Ground track information
     solar.gt_date = read_int32(File,solar.num_grnd_trk)
     solar.gt_time = read_int32(File,solar.num_grnd_trk)
     solar.gt_latitude = read_float32(File,solar.num_grnd_trk)
     solar.gt_longitude = read_float32(File,solar.num_grnd_trk)
     solar.gt_ray_dir = read_float32(File,solar.num_grnd_trk)
     #Space Craft Information
     solar.Space_Craft_Lat = read_float32(File, solar.num_grnd_trk)
     solar.Space_Craft_Lon = read_float32(File, solar.num_grnd_trk)
     solar.Space_Craft_Alt = read_float32(File, solar.num_grnd_trk)
     #Altitude Infotmation
     solar.Altitude = read_float32(File, solar.num_alt_bins)
     solar.Geopotential_Alt = read_float32(File, solar.num_alt_bins)
     #Temp/Press profile Information
     solar.Pressure= read_float32(File, solar.num_alt_bins)
     solar.Pressure_uncert = read_float32(File, solar.num_alt_bins)
     solar.Temperature = read_float32(File, solar.num_alt_bins)
     solar.Temperature_uncert = read_float32(File, solar.num_alt_bins)
     solar.Neutral_Density = read_float32(File, solar.num_alt_bins)
     solar.Neutral_Density_uncert = read_float32(File, solar.num_alt_bins)
     solar.Temp_Pressure_Source = read_int32(File, solar.num_alt_bins)
     #Tropopause temperature/altitude
     solar.trop_temp = read_float32(File,1)[0]
     solar.trop_alt = read_float32(File,1)[0]
     solar.trop_press = read_float32(File, 1)[0]
     #Met Temp/Press Information
     solar.met_pressure = read_float32(File,solar.num_press_grid)
     solar.met_temp = read_float32(File,solar.num_press_grid)
     solar.met_temp_unc = read_float32(File,solar.num_press_grid)
     solar.met_altitude = read_float32(File,solar.num_press_grid)
     #Meteorological data source
     solar.met_source = read_int32(File,1)[0]
     #CCD and Bit Flag Info
     solar.CCD_Temperature = read_float32(File, 1)[0]
     solar.Spectrometer_Zenith_Temperature = read_float32(File, 1)[0]
     solar.CCD_Temperature_minus_TEC = read_float32(File, 1)[0]
     solar.Ephemeris_Quality = read_int32(File, 1)[0]
     solar.SpecCalShift = read_float32(File, 1)[0]
     solar.SpecCalStretch = read_float32(File, 1)[0]
     solar.QAFlag = read_int32(File, 1)[0]
     solar.QAFlag_Altitude = read_int32(File, solar.num_alt_bins)
     #Pixel group information
     solar.start_pixel_num = read_int32(File,solar.num_CCDPxlGrps)
     solar.end_pixel_num = read_int32(File,solar.num_CCDPxlGrps)
     solar.central_wavelength = read_float32(File,solar.num_CCDPxlGrps)
     solar.half_bandwidth = read_float32(File,solar.num_CCDPxlGrps)
     #Transmission data
     pg = solar.profile_count-1
     solar.pg_trans_profiles.Transmission[:,pg] = read_float32(File, solar.num_alt_bins)
     solar.pg_trans_profiles.Transmission_unc[:,pg] = read_float32(File, solar.num_alt_bins)
     solar.pg_trans_profiles.TransQA[:,pg] = read_int32(File, solar.num_alt_bins)
     for pg in range(solar.num_CCDPxlGrps):
        solar.pg_trans_profiles.Transmission[:,pg] = read_float32(File, solar.num_alt_bins)
        solar.pg_trans_profiles.Transmission_unc[:,pg] = read_float32(File, solar.num_alt_bins)
        solar.pg_trans_profiles.TransQA[:,pg] = read_int32(File, solar.num_alt_bins)

     File.close()
     #Decode Bits 
     if (solar.QAFlag & 2**0) != 0:
       solar.HexErrFlag = 1
     if (solar.QAFlag & 2**1) != 0:
       solar.ContWindowClosedFlag = 1
     if (solar.QAFlag & 2**2) != 0:
       solar.TimeQualFlag = 1
     if (solar.QAFlag & 2**3) != 0:
       solar.DMPExoFlag = 1
     if (solar.QAFlag & 2**4) != 0:
       solar.BlockExoFlag = 1
     if (solar.QAFlag & 2**5) !=0:
       solar.SpectralCalFlag = 1
     if (solar.QAFlag & 2**6) !=0:
       solar.SolarEclipseFlag =1 

     for i in range(0,solar.num_alt_bins):
       if (solar.QAFlag_Altitude[i] & 2**0) != 0:
         solar.DMPAltFlag[i] = 1

     return(solar,0)












