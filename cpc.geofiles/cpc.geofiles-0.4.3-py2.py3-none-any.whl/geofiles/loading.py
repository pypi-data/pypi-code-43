"""
Contains methods for loading larger amounts of data than a single day

For example, let's say you want to load all of the forecasts valid today's
month and day from all years between 1985 and 2010. This module is intended
to make that much simpler.
"""

# Built-ins
import os

# Third-party
import numpy as np
import jinja2
from cpc.units.units import UnitConverter
import xarray as xr
from cpc.geogrids.manipulation import interpolate

# This package
from .datasets import EnsembleForecast, DeterministicForecast, Observation, Climatology
from .reading import read_grib
from .exceptions import LoadingError, ReadingError


def all_int_to_str(input):
    if all(isinstance(x, int) for x in input):
        # Get length of longest int
        max_length = max([len(str(x)) for x in input])
        # Convert all ints to strings, zero-padding to the max length
        return ['{{:0{}.0f}}'.format(max_length).format(x) for x in input]
    elif all(isinstance(x, str) for x in input):
        return input
    else:
        raise ValueError('input must be a list of ints')


def load_ens_fcsts(issued_dates, fhrs, members, file_template, data_type, geogrid,
                   fhr_stat='mean', yrev=False, grib_var=None, grib_level=None,
                   remove_dup_grib_fhrs=False, unit_conversion=None, log=False, transform=None,
                   debug=False, accum_over_fhr=False, nc_var=None, one_spatial_dimension=False,
                   interp_grid=None):
    """
    Loads ensemble forecast data

    Data is loaded for a given list of dates, forecast hours and members. The file template can
    contain any of the following bracketed variables:

    - {yyyy}
    - {mm}
    - {dd}
    - {cc}
    - {fhr}
    - {member}

    Within a loop over the dates, fhrs and members, the bracketed variables above are replaced
    with the appropriate value.

    Parameters
    ----------

    - issued_dates (list of strings): list of issued dates in YYYYMMDD or YYYYMMDDCC format - if
      YYYYMMDD, the cycle is assumed to be 00
    - fhrs (list of numbers or strings): list of fhrs to load
    - members (list of numbers or strings): list of members to load
    - file_template (string): file template used to construct file names for each date,
      fhr and member
    - data_type (string): data type (bin, grib1 or grib2)
    - geogrid (Geogrid): Geogrid associated with the data
    - fhr_stat (string): statistic to calculate over the forecast hour dimension (mean [default]
      or sum)
    - yrev (boolean): whether fcst data is reversed in the y-direction, and should be flipped
      when loaded (default: False)
    - grib_var (string): grib variable name (for grib files only)
    - grib_level (string): grib level name (for grib files only)
    - remove_dup_grib_fhrs (boolean): whether to remove potential duplicate fhrs from the grib
      files (default: False) - sets the `grep_fhr` parameter to the current fhr when calling
      `read_grib()`, which greps for the fhr in the given grib file - this is useful for gribs
      that may for some reason have duplicate records for a given variable but with different
      fhrs. This way you can get the record for the correct fhr.
    - unit_conversion - *string* (optional) - type of unit conversion to perform. If None,
      then no unit conversion will be performed.
    - log - *boolean* (optional, deprecated - use transform='log') - take the log of the forecast
      variable before calculating an ensemble mean and/or returning the data (default: False)
    - transform - *string* (optional) - type of data transform to do (supported values: 'log',
      'sqare-root', None [default])
    - debug (boolean): if True the file data is loaded from will be printed out (default: False)
    - accum_over_fhr: if True the given field is assumed to accumulate continuously throughout
      the forecast (eg. ECENS precip is the total accumulation from the start of the forecast up
      to that given fhr) - in this case the field total from fhr1 to fhr2 is field_fhr2 - field_fhr1
    - nc_var (string): NetCDF variable name (optional)
    - interp_grid (string): Name of the Geogrid you with to interpolate to before returning

    Returns
    -------

    - EnsembleForecast object containing the forecast data and some QC data

    Examples
    --------

    Load a few days of ensemble forecast data

        >>> from cpc.geogrids import Geogrid
        >>> from cpc.geofiles.loading import load_ens_fcsts
        >>> valid_dates = ['20160101', '20160102', '20160103']
        >>> fhrs = range(0, 120, 6)
        >>> members = range(0, 21)
        >>> file_template = '/path/to/files/{yyyy}/{mm}/{dd}/{cc}/' \
                            'gefs_{yyyy}{mm}{dd}_{cc}z_f{fhr}_m{member}.grb2'
        >>> data_type = 'grib2'
        >>> geogrid = Geogrid('1deg-global')
        >>> grib_var = 'TMP'
        >>> grib_level = '2 m above ground'
        >>> dataset = load_ens_fcsts(valid_dates, fhrs, members, file_template,
        ...                          data_type, geogrid, grib_var=grib_var,
        ...                          grib_level=grib_level)
        >>> print(dataset.ens.shape)
        (3, 21, 65160)
        >>> print(dataset.ens[:, :, 0])  # doctest: +SKIP
        [[ 246.18849945  246.40299683  247.11050034  245.95850067  246.17949905
           246.91550064  247.41700134  246.53700104  247.96300125  246.05699921
           246.08150101  247.11800003  247.46500015  247.30050049  247.44899979
           245.84649963  247.8234993   246.21900101  246.45600128  245.72950058
           246.05299988]
         [ 246.11650085  245.45250092  247.54049759  246.35499878  245.56750107
           246.74899902  247.23949966  246.52750015  247.40500031  245.96500092
           245.85749969  246.07099915  247.3465004   246.61099854  245.78749771
           247.18349838  246.47999954  245.44049988  245.78899994  245.67700043
           245.87299957]
         [ 245.88300095  245.5995018   247.63799896  247.21050034  245.88849945
           246.78749847  246.15800018  246.15749969  246.41600113  246.00299988
           246.80950012  246.51200104  247.11650009  246.2659996   245.96800156
           247.20250168  246.22499924  245.72900162  245.85200043  244.81850128
           245.73949966]]
        >>> print(dataset.ens_mean.shape)
        (3, 65160)
        >>> print(dataset.ens_mean[:, 0])  # doctest: +SKIP
        [ 246.67957157  246.33497583  246.28476225]
    """
    # ----------------------------------------------------------------------------------------------
    # Create a new EnsembleForecast Dataset
    #
    dataset = EnsembleForecast()

    # ----------------------------------------------------------------------------------------------
    # Set dates loaded
    #
    dataset.dates_loaded |= set(issued_dates)

    # ----------------------------------------------------------------------------------------------
    # Create a UnitConverter object to convert the data units (if necessary) later on
    #
    if unit_conversion:
        uc = UnitConverter()

    # ----------------------------------------------------------------------------------------------
    # Initialize arrays for the EnsembleForecast Dataset the full ensemble data array
    #
    if data_type in ('grib1', 'grib2'):
        if fhr_stat is None:
            dataset.ens = np.nan * np.empty(
                (len(fhrs), len(issued_dates), len(members), geogrid.num_y * geogrid.num_x)
            )
        else:
            dataset.ens = np.nan * np.empty(
                (len(issued_dates), len(members), geogrid.num_y * geogrid.num_x)
            )
    else:
        if fhr_stat is None:
            dataset.ens = np.nan * np.empty(
                (len(fhrs), len(issued_dates), len(members), geogrid.num_y, geogrid.num_x)
            )
        else:
            dataset.ens = np.nan * np.empty(
                (len(issued_dates), len(members), geogrid.num_y, geogrid.num_x)
            )

    # ----------------------------------------------------------------------------------------------
    # Grib-specific setup
    #
    if data_type in ('grib1', 'grib2'):
        # ----------------------------------------------------------------------------------------------
        # Convert fhrs and members to strings (if necessary)
        #
        fhrs = all_int_to_str(fhrs)
        members = all_int_to_str(members)

    # ----------------------------------------------------------------------------------------------
    # Loop over date, members, and fhrs
    #
    for d, date in enumerate(issued_dates):
        # ------------------------------------------------------------------------------------------
        # Grib-specific looping and data loading
        #
        if data_type in ('grib1', 'grib2'):
            # Split date into components
            yyyy, mm, dd = date[0:4], date[4:6], date[6:8]
            if len(date) == 10:
                cc = date[8:10]
            else:
                cc = '00'
            for m, member in enumerate(members):
                # Initialize an array for a single day, single member, all fhrs
                data_f = np.nan * np.empty((len(fhrs), geogrid.num_y * geogrid.num_x))
                for f, fhr in enumerate(fhrs):
                    # Replace variables in file template
                    kwargs = {
                        'yyyy': yyyy, 'mm': mm, 'dd': dd, 'cc': cc, 'cycle': f'{cc}z', 'cycle_num': cc,
                        'fhr': fhr, 'member': member
                    }
                    file = jinja2.Template(os.path.expandvars(file_template)).render(**kwargs)
                    # Read in data from file
                    if data_type in ('grib1', 'grib2'):
                        try:
                            data_f[f] = read_grib(file, data_type, grib_var, grib_level, geogrid,
                                                  yrev=yrev, debug=debug)
                        except ReadingError:
                            # Set this day to missing
                            data_f[f] = np.full((geogrid.num_y * geogrid.num_x), np.nan)
                            # Add this date to the list of dates with files not loaded
                            dataset.dates_with_files_not_loaded.add(date)
                            # Add this file to the list of files not loaded
                            dataset.files_not_loaded.add(file)
                    elif data_type in ['bin', 'binary']:
                        try:
                            if debug:
                                print(f'Attempting to load data from {file}...')
                            data_f[f] = np.fromfile(file, dtype='float32')
                            # --------------------------------------------------------------------------
                            # Flip in the y-direction if necessary
                            if yrev:
                                # Reshape into 2 dimensions
                                data_temp = np.reshape(data_f[f], (geogrid.num_y, geogrid.num_x))
                                # Flip
                                data_temp = np.flipud(data_temp)
                                # Reshape back into 1 dimension
                                data_temp = np.reshape(data_temp, data_f[f].size)
                                # Replace data_f[f]
                                data_f[f] = data_temp
                        except Exception as e:
                            if debug:
                                print(f'Couldn\'t load data from file {file}: {e}')
                            # Set this day to missing
                            data_f[f] = np.full((geogrid.num_y * geogrid.num_x), np.nan)
                            # Add this date to the list of dates with files not loaded
                            dataset.dates_with_files_not_loaded.add(date)
                            # Add this file to the list of files not loaded
                            dataset.files_not_loaded.add(file)
                # ------------------------------------------------------------------------------------------------------
                # Take stat over fhr (don't use nanmean/nanstd, if an fhr is missing then we don't trust this mean/std
                #
                # Note: we only do this for gribs. With xarray we average/summed over fhr above for NetCDF files
                #
                if data_type in ('grib1', 'grib2'):
                    if fhr_stat == 'mean':
                        dataset.ens[d, m] = np.mean(data_f, axis=0)
                    elif fhr_stat == 'min':
                        dataset.ens[d, m] = np.min(data_f, axis=0)
                    elif fhr_stat == 'max':
                        dataset.ens[d, m] = np.max(data_f, axis=0)
                    elif fhr_stat == 'sum':
                        if accum_over_fhr:
                            dataset.ens[d, m] = data_f[-1] - data_f[0]
                        else:
                            dataset.ens[d, m] = np.sum(data_f, axis=0)
                    elif fhr_stat is None:
                        dataset.ens[:, d, m] = data_f
                    else:
                        raise LoadingError('fhr_stat must be mean, sum, or None', file)
        elif data_type == 'netcdf':
            yyyy, mm, dd = date[0:4], date[4:6], date[6:8]
            cc = date[8:10] if len(date) == 10 else '00'
            kwargs = {'yyyy': yyyy, 'mm': mm, 'dd': dd, 'cc': cc, 'cycle': f'{cc}z', 'cycle_num': cc}
            file = jinja2.Template(os.path.expandvars(file_template)).render(**kwargs)
            try:
                xr_dataset = xr.open_dataset(file, decode_times=False)
            except FileNotFoundError as e:
                print(f"Couldn't load data from file {file}: {e}")
                # Add this date to the list of dates with files not loaded
                dataset.dates_with_files_not_loaded.add(date)
                # Add this file to the list of files not loaded
                dataset.files_not_loaded.add(file)
                return dataset

            xr_dataset = xr_dataset[nc_var].sel(time=np.in1d(xr_dataset[nc_var].time, [int(f) for f in fhrs]))
            if fhr_stat == 'mean':
                xr_dataset = xr_dataset.mean(dim='time')
            elif fhr_stat == 'sum':
                if accum_over_fhr:
                    xr_dataset = xr_dataset.sel(time=int(fhrs[-1])) - xr_dataset.sel(time=int(fhrs[0]))
                else:
                    xr_dataset = xr_dataset.sum(dim='time')
            elif fhr_stat == 'min':
                xr_dataset = xr_dataset.min(dim='time')
            elif fhr_stat == 'max':
                xr_dataset = xr_dataset.max(dim='time')

            if fhr_stat is None:
                dataset.ens[:, d, :] = xr_dataset.values
            else:
                dataset.ens[d] = xr_dataset.values

            # Interpolate grid (if necessary)
            if interp_grid is not None:
                dataset.ens - interpolate(dataset.ens, geogrid, interp_grid)

        # --------------------------------------------------------------------------------------
        # Convert units (if necessary)
        #
        if unit_conversion:
            # If the unit_conversion is 'prate-to-mm' then we have to convert the data by
            # multiplying by the number of seconds between each fhr (eg. 86400 for 24-hour
            # files)
            if unit_conversion == 'prate-to-mm':
                if len(fhrs) < 2:
                    raise ValueError(f'Cannot apply a unit conversion of {unit_conversion} with'
                                     f' only a single fhr')
                else:
                    dataset.ens *= (int(fhrs[1]) - int(fhrs[0])) * 3600
            else:
                dataset.ens = uc.convert(dataset.ens, unit_conversion)

        # --------------------------------------------------------------------------------------
        # Do data transformation (if necessary)
        #
        # Assuming a minimum log value of -2, set vals of < 1mm to 0.14 (exp(-2))
        if transform == 'log' or log:
            with np.errstate(divide='ignore', invalid='ignore'):
                dataset.ens = np.log(np.where(dataset.ens < 1, np.exp(-2), dataset.ens))
        elif transform == 'square-root':
            with np.errstate(divide='ignore'):
                dataset.ens = np.sqrt(dataset.ens)

    # --------------------------------------------------------------------------------------
    # Reshape data back to 1 dimension of space
    #
    if fhr_stat is not None:
        if one_spatial_dimension and dataset.ens.ndim == 4:
            dataset.ens = dataset.ens.reshape(dataset.ens.shape[0], dataset.ens.shape[1], -1)
        elif one_spatial_dimension and dataset.ens.ndim == 5:
            dataset.ens = dataset.ens.reshape(dataset.ens.shape[0], dataset.ens.shape[1], dataset.ens.shape[2], -1)

    return dataset


def load_dtrm_fcsts(issued_dates, fhrs, file_template, data_type, geogrid, fhr_stat='mean',
                    yrev=False, grib_var=None, grib_level=None, remove_dup_grib_fhrs=False,
                    unit_conversion=None, log=False, transform=None, debug=False):
    """
    Loads deterministic forecast data

    Data is loaded for a given list of dates and forecast hours. The file template can contain
    any of the following bracketed variables:

    - {yyyy}
    - {mm}
    - {dd}
    - {cc}
    - {fhr}

    Within a loop over the dates and fhrs, the bracketed variables above are replaced with the
    appropriate value.

    Parameters
    ----------

    - issued_dates (list of strings): list of issued dates in YYYYMMDD or YYYYMMDDCC format - if
      YYYYMMDD, the cycle is assumed to be 00
    - fhrs (list of numbers or strings): list of fhrs to load
    - file_template (string): file template used to construct file names for each date,
      fhr and member
    - data_type (string): data type (bin, grib1 or grib2)
    - geogrid (Geogrid): Geogrid associated with the data
    - fhr_stat (string): statistic to calculate over the forecast hour dimension (mean [default]
      or sum)
    - yrev (boolean): whether fcst data is reversed in the y-direction, and should be flipped
      when loaded (default: False)
    - grib_var (string): grib variable name (for grib files only)
    - grib_level (string): grib level name (for grib files only)
    - remove_dup_grib_fhrs (boolean): whether to remove potential duplicate fhrs from the grib
      files (default: False) - sets the `grep_fhr` parameter to the current fhr when calling
      `read_grib()`, which greps for the fhr in the given grib file - this is useful for gribs
      that may for some reason have duplicate records for a given variable but with different
      fhrs. This way you can get the record for the correct fhr.
    - unit_conversion - *string* (optional) - type of unit conversion to perform. If None,
      then no unit conversion will be performed.
    - log - *boolean* (optional, deprecated - use transform='log') - take the log of the forecast
      variable before calculating an ensemble mean and/or returning the data (default: False)
    - transform - *string* (optional) - type of data transform to do (supported values: 'log',
      'sqare-root', None [default])
    - debug (boolean): if True the file data is loaded from will be printed out (default: False)

    Returns
    -------

    - DeterministicForecast object containing the forecast data and some QC data

    Examples
    --------

    Load a few days of deterministic forecast data

        >>> from cpc.geogrids import Geogrid
        >>> from cpc.geofiles.loading import load_dtrm_fcsts
        >>> valid_dates = ['20160101', '20160102', '20160103']
        >>> fhrs = range(0, 120, 6)
        >>> file_template = '/path/to/files/{yyyy}/{mm}/{dd}/{cc}/' \
                            'gfs_{yyyy}{mm}{dd}_{cc}z_f{fhr}.grb2'
        >>> data_type = 'grib2'
        >>> geogrid = Geogrid('0.5-deg-global-center-aligned')
        >>> grib_var = 'TMP'
        >>> grib_level = '2 m above ground'
        >>> dataset = load_dtrm_fcsts(valid_dates, fhrs, file_template,
        ...                           data_type, geogrid, grib_var=grib_var,
        ...                           grib_level=grib_level)
        >>> print(dataset.fcst.shape, dataset.fcst[:, 0])  # doctest: +SKIP
        (3, 259920) [ 246.64699936  246.50599976  245.97450104]
    """
    # ----------------------------------------------------------------------------------------------
    # Make sure grib parameters are set if data_type is grib1 or grib2
    #
    if data_type in ('grib1', 'grib2'):
        if grib_var is None or grib_level is None:
            raise LoadingError('When data_type is grib1 or grib2, grib_var and grib_level must be defined')

    # ----------------------------------------------------------------------------------------------
    # Create a new DeterministicForecast Dataset
    #
    dataset = DeterministicForecast()

    # ----------------------------------------------------------------------------------------------
    # Initialize array for the DeterministicForecast Dataset
    #
    dataset.fcst = np.nan * np.empty((len(issued_dates), geogrid.num_y * geogrid.num_x))

    # ----------------------------------------------------------------------------------------------
    # Convert fhrs to strings (if necessary)
    #
    fhrs = all_int_to_str(fhrs)

    # ----------------------------------------------------------------------------------------------
    # Set dates loaded
    #
    dataset.dates_loaded |= set(issued_dates)

    # ----------------------------------------------------------------------------------------------
    # Create a UnitConverter object to convert the data units (if necessary) later on
    #
    if unit_conversion:
        uc = UnitConverter()

    # ----------------------------------------------------------------------------------------------
    # Loop over date and fhrs
    #
    for d, date in enumerate(issued_dates):
        # Split date into components
        yyyy, mm, dd = date[0:4], date[4:6], date[6:8]
        if len(date) == 10:
            cc = date[8:10]
        else:
            cc = '00'
        # Initialize an array for a single day, all fhrs
        data_f = np.nan * np.empty((len(fhrs), geogrid.num_y * geogrid.num_x))
        for f, fhr in enumerate(fhrs):
            # Replace variables in file template
            kwargs = {'yyyy': yyyy, 'mm': mm, 'dd': dd, 'cc': cc, 'fhr': fhr}
            file = jinja2.Template(os.path.expandvars(file_template)).render(**kwargs)
            # Read in data from file
            if data_type in ('grib1', 'grib2'):
                try:
                    data_f[f] = read_grib(file, data_type, grib_var, grib_level, geogrid, yrev=yrev,
                                          debug=debug)
                except ReadingError:
                    # Set this day to missing
                    data_f[f] = np.full((geogrid.num_y * geogrid.num_x), np.nan)
                    # Add this date to the list of dates with files not loaded
                    dataset.dates_with_files_not_loaded.add(date)
                    # Add this file to the list of files not loaded
                    dataset.files_not_loaded.add(file)
        # --------------------------------------------------------------------------------------
        # Convert units (if necessary)
        #
        if unit_conversion:
            data_f = uc.convert(data_f, unit_conversion)
        # --------------------------------------------------------------------------------------
        # Do data transformation (if necessary)
        #
        # Assuming a minimum log value of -2, set vals of < 1mm to 0.14 (exp(-2))
        if transform == 'log' or log:
            with np.errstate(divide='ignore', invalid='ignore'):
                data_f = np.log(np.where(data_f < 1, np.exp(-2), data_f))
        elif transform == 'square-root':
            with np.errstate(divide='ignore'):
                dataset.ens = np.sqrt(dataset.ens)

        # Take stat over fhr (don't use nanmean/nanstd, if an fhr is missing then we
        # don't trust this mean/std
        if fhr_stat == 'mean':
            dataset.fcst[d] = np.mean(data_f, axis=0)
        elif fhr_stat == 'std':
            dataset.fcst[d] = np.std(data_f, axis=0)
        else:
            raise LoadingError('fhr_stat must be either mean or std', file)

    return dataset


def load_obs(valid_dates, file_template, data_type, geogrid, record_num=None, yrev=False,
             grib_var=None, grib_level=None, unit_conversion=None, log=False,
             transform=None, debug=False, wgrib2_new_grid=False):
    """
    Loads observation data

    Data is loaded for a given list of dates. The file template can contain any of the following
    bracketed variables:

    - {yyyy}
    - {mm}
    - {dd}
    - {hh}

    Within a loop over the dates, the bracketed variables above are replaced with the appropriate
    value.

    Parameters
    ----------

    - valid_dates (list of strings): list of valid dates in YYYYMMDD or YYYYMMDDHH format
    - file_template (string): file template used to construct file names for each date,
      fhr and member
    - data_type (string): data type (bin, grib1 or grib2)
    - geogrid (Geogrid): Geogrid associated with the data
    - record_num (int): binary record containing the desired variable - if None then the file is
      assumed to be a single record (default)
    - yrev (boolean): whether fcst data is reversed in the y-direction, and should be flipped
      when loaded (default: False)
    - grib_var (string): grib variable name (for grib files only)
    - grib_level (string): grib level name (for grib files only)
    - unit_conversion - *string* (optional) - type of unit conversion to perform. If None,
      then no unit conversion will be performed.
    - log - *boolean* (optional, deprecated - use transform='log') - take the log of the forecast
      variable before calculating an ensemble mean and/or returning the data (default: False)
    - transform - *string* (optional) - type of data transform to do (supported values: 'log',
      'sqare-root', None [default])
    - debug (boolean): if True the file data is loaded from will be printed out (default: False)

    Returns
    -------

    - Observation object containing the observation data and some QC data

    Examples
    --------

    Load a few days of observation data

        >>> from cpc.geogrids import Geogrid
        >>> from cpc.geofiles.loading import load_obs
        >>> valid_dates = ['20150101', '20150102', '20150103']
        >>> file_template = '/path/to/files/{yyyy}/{mm}/{dd}/tmean_01d_{yyyy}{mm}{dd}.bin'
        >>> data_type = 'binary'
        >>> geogrid = Geogrid('1deg-global')
        >>> dataset = load_obs(valid_dates, file_template, data_type, geogrid)
        >>> print(dataset.obs.shape, dataset.obs[:, 0])  # doctest: +SKIP
        (3, 65160) [-28.48999405 -28.04499435 -27.81749725]
    """
    # ----------------------------------------------------------------------------------------------
    # Create a new Observation Dataset
    #
    dataset = Observation()

    # ----------------------------------------------------------------------------------------------
    # Initialize array for the Observation Dataset
    #
    dataset.obs = np.nan * np.empty((len(valid_dates), geogrid.num_y * geogrid.num_x))

    # ----------------------------------------------------------------------------------------------
    # Set dates loaded
    #
    dataset.dates_loaded |= set(valid_dates)

    # ----------------------------------------------------------------------------------------------
    # Create a UnitConverter object to convert the data units (if necessary) later on
    #
    if unit_conversion:
        uc = UnitConverter()

    # ----------------------------------------------------------------------------------------------
    # Loop over date
    #
    for d, date in enumerate(valid_dates):
        # Split date into components
        yyyy, mm, dd = date[0:4], date[4:6], date[6:8]
        if len(date) == 10:
            hh = date[8:10]
        else:
            hh = '00'
        # Replace variables in file template
        kwargs = {'yyyy': yyyy, 'mm': mm, 'dd': dd, 'hh': hh}
        file = jinja2.Template(os.path.expandvars(file_template)).render(**kwargs)
        # Read in data from file
        if data_type in ('grib1', 'grib2'):
            try:
                # Read grib with read_grib()
                dataset.obs[d] = read_grib(file, data_type, grib_var, grib_level, geogrid,
                                           yrev=yrev, debug=debug, wgrib2_new_grid=wgrib2_new_grid)
            except ReadingError:
                # Set this day to missing
                dataset.obs[d] = np.full((geogrid.num_y * geogrid.num_x), np.nan)
                # Add this date to the list of dates with files not loaded
                dataset.dates_with_files_not_loaded.add(date)
                # Add this file to the list of files not loaded
                dataset.files_not_loaded.add(file)
        elif data_type in ['bin', 'binary']:
            try:
                # Load data from file
                if debug:
                    print('Binary file being read: {}'.format(file))
                tempdata = np.fromfile(file, dtype='float32')
                # Determine number of records in the binary file
                num_records = int(tempdata.size / (geogrid.num_y * geogrid.num_x))
                # Reshape data and extract the appropriate record - if record_num is specified,
                # extract that record number, otherwise just take the entire array
                if record_num is not None:
                    dataset.obs[d] = tempdata.reshape(
                        num_records, geogrid.num_y * geogrid.num_x
                    )[record_num]
                else:
                    dataset.obs[d] = tempdata.reshape(
                        num_records, geogrid.num_y * geogrid.num_x
                    )
            except:
                # Set this day to missing
                dataset.obs[d] = np.full((geogrid.num_y * geogrid.num_x), np.nan)
                # Add this date to the list of dates with files not loaded
                dataset.dates_with_files_not_loaded.add(date)
                # Add this file to the list of files not loaded
                dataset.files_not_loaded.add(file)

    # --------------------------------------------------------------------------------------
    # Convert units (if necessary)
    #
    if unit_conversion:
        dataset.obs = uc.convert(dataset.obs, unit_conversion)
    # --------------------------------------------------------------------------------------
    # Do data transformation (if necessary)
    #
    if transform == 'log' or log:
        with np.errstate(divide='ignore'):
            dataset.obs = np.log(np.where(dataset.obs < 1, np.exp(-2), dataset.obs))
    elif transform == 'square-root':
        with np.errstate(divide='ignore'):
            dataset.obs = np.sqrt(dataset.obs)

    return dataset


def load_climos(valid_days, file_template, geogrid, num_ptiles=None, debug=False):
    """
    Loads climatology data

    Data is loaded for a given range of days of the year. Currently the data must be in binary
    format with the dimensions (ptiles x grid points) when num_ptiles is an integer, and (grid
    points [1-d]) when num_ptiles is None

    - {mm}
    - {dd}

    Within a loop over the days, the bracketed variables above are replaced with the appropriate
    value.

    Parameters
    ----------

    - valid_days (list of strings): list of days of the year to load - must be formatted as MMDD
      (eg. [0501, 0502, 0503, 0504, 0505])
    - file_template (string): file template used to construct file names for each date,
      fhr and member
    - geogrid (Geogrid): Geogrid associated with the data
    - num_ptiles (int or None): number of percentiles expected in the data file - if None then
    the file is assumed to be a mean or standard deviation instead of percentiles (default: None)
    - debug (boolean): if True the file data is loaded from will be printed out (default: False)

    Returns
    -------

    - Climatology object containing the observation data and some QC data

    Examples
    --------

    Load a few days of climatology data

        >>> from cpc.geogrids import Geogrid
        >>> from cpc.geofiles.loading import load_climos
        >>> valid_days = ['0101', '0102', '0103']
        >>> file_template = '/path/to/files/tmean_clim_poe_05d_{mm}{dd}.bin'
        >>> geogrid = Geogrid('1deg-global')
        >>> num_ptiles = 19
        >>> dataset = load_climos(valid_days, file_template, geogrid,
        ...                       num_ptiles=num_ptiles, debug=True)
        >>> print(dataset.climo.shape)
        (3, 19, 65160)
        >>> print(dataset.climo[:, :, 0])
        [[ nan  nan  nan  nan  nan  nan  nan  nan  nan  nan  nan  nan  nan  nan
           nan  nan  nan  nan  nan]
         [ nan  nan  nan  nan  nan  nan  nan  nan  nan  nan  nan  nan  nan  nan
           nan  nan  nan  nan  nan]
         [ nan  nan  nan  nan  nan  nan  nan  nan  nan  nan  nan  nan  nan  nan
           nan  nan  nan  nan  nan]]
    """
    # ----------------------------------------------------------------------------------------------
    # Create a new Climatology Dataset
    #
    dataset = Climatology()

    # ----------------------------------------------------------------------------------------------
    # Initialize array for the Climatology Dataset
    #
    # If num_ptiles is an integer, add a ptile dimension to the climo array
    if num_ptiles is not None:
        try:
            dataset.climo = np.full(
                (len(valid_days), num_ptiles, geogrid.num_y * geogrid.num_x), np.nan
            )
        except:
            raise LoadingError('num_ptiles must be an integer or None')
    else:
        dataset.climo = np.nan * np.empty((len(valid_days), geogrid.num_y * geogrid.num_x))

    # ----------------------------------------------------------------------------------------------
    # Set dates loaded
    #
    dataset.dates_loaded |= set(valid_days)

    # ----------------------------------------------------------------------------------------------
    # Loop over date
    #
    for d, date in enumerate(valid_days):
        # Split date into components
        mm, dd = date[0:2], date[2:4]
        # Replace variables in file template
        kwargs = {'mm': mm, 'dd': dd}
        file = jinja2.Template(os.path.expandvars(file_template)).render(**kwargs)
        # Read in data from file
        try:
            # Load data from file
            if num_ptiles is not None:
                dataset.climo[d] = np.fromfile(file, 'float32').reshape(
                    num_ptiles, geogrid.num_y * geogrid.num_x)
            else:
                dataset.climo[d] = np.fromfile(file, 'float32').reshape(
                    geogrid.num_y * geogrid.num_x)
        except:
            # Set this day to missing
            if num_ptiles:
                dataset.climo[d] = np.full((num_ptiles, geogrid.num_y * geogrid.num_x), np.nan)
            else:
                dataset.climo[d] = np.full((geogrid.num_y * geogrid.num_x), np.nan)
            # Add this date to the list of dates with files not loaded
            dataset.dates_with_files_not_loaded.add(date)
            # Add this file to the list of files not loaded
            dataset.files_not_loaded.add(file)

    return dataset

