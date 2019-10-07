import io
import os
import re
import shutil
import urllib.request
import zipfile
from typing import List, Tuple, Union
import h5py
import numpy as np

from pyus.utils import ui


PICMUS17_DATA_URL = (
    'https://www.creatis.insa-lyon.fr/EvaluationPlatform/picmus/dataset/'
)
PICMUS16_DATA_URL = (
    'https://www.creatis.insa-lyon.fr/Challenge/IEEE_IUS_2016/download/'
)


def download_2017(
        export_path: str,
        signal_selection: Union[str, List[str], Tuple[str, ...]],
        pht_selection: Union[str, List[str], Tuple[str, ...]],
        transmission_selection: Union[str, List[str], Tuple[str, ...]],
        pw_number_selection: Union[str, List[int], Tuple[int, ...]],
        scanning_region: bool = False
) -> None:

    # TODO(@dperdios): check proper iterables for the selections
    # TODO(@dperdios): check `export_path`

    # Valid optional input parameters and default parameters
    _val_sig_sel = ('rf', 'iq')
    _val_pht_sel = (
        'numerical', 'in_vitro_type1', 'in_vitro_type2', 'in_vitro_type3'
    )
    _val_trans_sel = ('transmission_1', 'transmission_2')
    _val_pwnb_sel = range(1, 76, 2)

    if signal_selection == 'all':
        signal_selection = _val_sig_sel
    if pht_selection == 'all':
        pht_selection = _val_pht_sel
    if transmission_selection == 'all':
        transmission_selection = _val_trans_sel
    if pw_number_selection == 'all':
        pw_number_selection = _val_pwnb_sel

    if not all([s in _val_sig_sel for s in signal_selection]):
        raise ValueError(
            'Invalid signal selection. Valid selection: '
            '{}'.format(', '.join(_val_sig_sel))
        )
    if not all([s in _val_pht_sel for s in pht_selection]):
        raise ValueError(
            'Invalid phantom selection. '
            'Valid selection: {}'.format(', '.join(_val_pht_sel))
        )
    if not all([s in _val_trans_sel for s in transmission_selection]):
        raise ValueError(
            'Invalid transmission selection. Valid selection: '
            '{}'.format(', '.join(_val_trans_sel))
        )
    if not all([s in _val_pwnb_sel for s in pw_number_selection]):
        raise ValueError(
            'Invalid signal selection. Valid selection: '
            '{}'.format(', '.join(map(str, _val_pwnb_sel)))
        )

    # Get all valid data file list
    #   Data files start with `dataset` and end with `.hdf5`
    data_list = _online_2017_dataset_list()

    # Set download list
    reg_signal = re.compile('\w*_(' + '|'.join(signal_selection) + ')_\w*')
    reg_pht = re.compile('\w*_(' + '|'.join(pht_selection) + ')_\w*')
    reg_transmission = re.compile(
        '\w*_(' + '|'.join(transmission_selection) + ')_\w*'
    )
    reg_pw_number = re.compile(
        '\w*_nbPW_('+ '|'.join(map(str, pw_number_selection)) + ')\.hdf5'
    )
    data_wish_list = [f for f in data_list if reg_signal.search(f) is not None
                      and reg_pht.search(f) is not None
                      and reg_transmission.search(f) is not None
                      and reg_pw_number.search(f) is not None]
    data_wish_list.sort(key=ui.natural_keys)

    # Get scanning region file
    scan_list = []
    if scanning_region:
        scan_list = _online_2017_scan_list()

    # Already existing data
    exist_list = []
    if os.path.exists(export_path):
        exist_list = [f for f in os.listdir(export_path) if f in data_list]

    # Data summary
    data_down_list = []
    print('Data download list:')
    for f in data_wish_list:
        if f not in exist_list:
            print('  {}'.format(f))
            data_down_list.append(f)
        else:
            print('  {} already exists (ignored)'.format(f))

    # Download all files and save
    down_list = [*data_down_list, *scan_list]
    url_list = [PICMUS17_DATA_URL + f for f in down_list]
    if url_list:  # check if url_list is not empty
        ui.download_url_list(url_list=url_list, path=export_path)


def load_data(
        path: str,
        indexes: Union[List[int], Tuple[int, ...]] = None,
        dtype=None
) -> Tuple[np.ndarray, dict]:
    # TODO: type hint for `dtype` (not so trivial, see NumPy doc)
    # TODO: add `slice` support
    #   Note: NumPy type hint is Union[str, object]
    # TODO: check np.ndarray.astype -> seems to return a copy of the array

    # Check if file exist and suggest to download
    abspath = os.path.abspath(path=path)
    if not os.path.exists(abspath):
        filename = os.path.basename(abspath)
        data_list = _online_2017_dataset_list()
        if filename in data_list:
            usr_in = input(
                '{file} does not exist but can be downloaded.'
                ' Do you want to download it ([y]/n)? '.format(
                    file=os.path.abspath(path)
                )
            )
            usr_in = usr_in.lower() if usr_in else 'y'  # default: 'y'
            if usr_in.lower() == 'y':
                # Download and save file in proper folder
                url = PICMUS17_DATA_URL + filename
                ui.download_url_list(
                    url_list=[url], path=os.path.dirname(abspath)
                )
            else:
                raise InterruptedError
        else:
            raise FileNotFoundError(
                '{file} does not exist'.format(file=os.path.abspath(path))
            )

    # Open HDF5 file
    with h5py.File(path, 'r') as h5_file:
        # Extract sequence information
        #   Everything lies below the h5 Group ['US']['US_DATASET0000']
        #       - ['PRF']
        #       - ['angles']
        #       - ['data']: ['data']['real'] and ['data']['imag']
        #       - ['initial_time']
        #       - ['modulation_frequency']
        #       - ['probe_geometry'] (not used since always L11)
        #       - ['sampling_frequency']
        #       - ['sound_speed']
        h5_group = h5_file['US']['US_DATASET0000']

        # Check `selected_indexes`
        if indexes is None:
            indexes = slice(None)

        # Check dtype
        if dtype is None:
            dtype = h5_group['data']['real'].dtype

        # TODO: check if we should import strings as bytes (i.e. u'')
        # TODO: check if `float` should be np.float like
        #   see numpy.core.numerictypes for the numpy type-hierarchy
        name = os.path.splitext(os.path.basename(path))[0]
        angles = h5_group['angles'][indexes].astype(dtype=dtype)
        sampling_frequency = float(h5_group['sampling_frequency'][()])
        transmit_frequency = 5.208e6  # according to PICMUS website
        # Note: according to Verasonics specifications in the PICMUS case
        #   - sampling_frequency: 250e6/12 (200% bandwidth)
        #   - transmit_frequency: sampling_frequency / 4 (200% bandwidth)
        #   - demodulation_frequency: sampling_frequency / 4 (200% bandwidth)
        # Note: when using IQ, the sampling frequency is reduced but of course
        #   does not affect the transmit frequency
        demodulation_frequency = float(h5_group['modulation_frequency'][()])
        initial_time = float(h5_group['initial_time'][()])
        mean_sound_speed = float(h5_group['sound_speed'][()])
        # Pulse repetition frequency:
        #   Time interval between consecutive transmit events (Hz)
        prf = float(h5_group['PRF'][()])

        # PICMUS raw data storage
        #   Access of RF and IQ data:
        #       ['US']['US_DATASET0000']['data']['real']: for both RF and IQ
        #       ['US']['US_DATASET0000']['data']['imag']: only zeros if RF
        #   Shape:
        #       shape=(angle_number, transducer_number, sample_number)
        #       shape=(transducer_number, sample_number) if a single angle

        # If only 1 angle in dataset (i.e. single PW) need to check indexes
        # since not entirely consistent in PICMUS dataset
        if h5_group['angles'].shape[0] is 1 and indexes != slice(None):
            # Check the only valid provided indexes for single PW case
            # TODO: to check when `slice` support is added
            if len(indexes) == 1 and indexes[0] == 0:
                indexes = slice(None)
            else:
                raise ValueError('Invalid `indexes` for 1 PW case')

        # Extract PICMUS raw data
        #   Check if RF or IQ. `modulation_frequency` is 0 in case of RF
        if demodulation_frequency == 0:  # RF
            raw_data = h5_group['data']['real'][indexes].astype(dtype=dtype)
        else:  # IQ
            # Defining a complex from two np.float32 results in a np.complex64
            raw_data = (
                    h5_group['data']['real'][indexes].astype(dtype=dtype)
                    + 1j
                    * h5_group['data']['imag'][indexes].astype(dtype=dtype)
            )

        # If only 1 angle in dataset (i.e. single PW) need to expand dimension
        # since not entirely consistent in PICMUS dataset
        if h5_group['angles'].shape[0] is 1:
            data = np.expand_dims(raw_data, axis=0)
            # Note: this does not copy the numpy array. It can be checked with
            # raw_data.__array_interface__['data'] to get the memory address
        else:
            data = raw_data

        # Expand dimension 0, the `frame_number` dimension since PICMUS only
        # provides a single frame
        data = np.expand_dims(data, axis=0)

        # Temporary stack in settings dictionary
        # TODO: remove this dict
        settings = dict()
        settings['name'] = name
        settings['sampling_frequency'] = sampling_frequency
        settings['transmit_frequency'] = transmit_frequency
        settings['demodulation_frequency'] = demodulation_frequency
        settings['initial_time'] = initial_time
        settings['angles'] = angles
        settings['prf'] = prf
        settings['mean_sound_speed'] = mean_sound_speed
        #   Additional PICMUS information
        settings['transmit_wave'] = 'square'  # (see PICMUS website)
        settings['transmit_cycles'] = 2.5  # (see PICMUS website)
        settings['medium_attenuation'] = 0.5  # (see PICMUS website)

    return data, settings


def _online_2017_dataset_list() -> List[str]:

    response = urllib.request.urlopen(PICMUS17_DATA_URL)
    index = response.read().decode('utf-8')
    reg_data = re.compile(r'(?<=<a href=")dataset\w*\.hdf5(?=">)')
    data_list = reg_data.findall(index)

    return data_list


def _online_2017_scan_list() -> List[str]:

    response = urllib.request.urlopen(PICMUS17_DATA_URL)
    index = response.read().decode('utf-8')
    reg_scan = re.compile(r'(?<=<a href=")scanning\w*.hdf5(?=">)')
    reg_list = reg_scan.findall(index)

    return reg_list


# def download_in_vivo_2016(
#         export_path: str,
#         scanning_region: bool = False
# ) -> None:
#     # Base download url
#     base_url = PICMUS16_DATA_URL
#
#     # Exported in vivo file names
#     file_check_list_2016 = ['carotid_cross_expe_dataset_rf.hdf5',
#                             'carotid_long_expe_dataset_rf.hdf5']
#     file_check_list = file_check_list_2016
#     if scanning_region:
#         file_check_list += ['carotid_cross_expe_scan.hdf5',
#                             'carotid_long_expe_scan.hdf5']
#
#     # In vivo data
#     # <a href="https://www.creatis.insa-lyon.fr/Challenge/IEEE_IUS_2016/sites/www.creatis.insa-lyon.fr.Challenge.IEEE_IUS_2016/files/in_vivo.zip">
#     response = urllib.request.urlopen(base_url)
#     index = response.read().decode('utf-8')
#     reg_data = re.compile(r'(?<=<a href=").*in_vivo\.zip(?=">)')
#     data_url = reg_data.findall(index)[0]
#
#     # Check if files already exist
#     if all([os.path.exists(os.path.join(export_path, f)) for f in file_check_list]):
#         print('PICMUS 2016 in-vivo data already exist in {}'.format(export_path))
#         return
#
#     # Create directories if required
#     if not os.path.exists(export_path):
#         os.makedirs(export_path)
#
#     # Download, extract and save files
#     with io.BytesIO() as dlbuf:
#         ui.download_file(data_url, dlbuf)
#         with zipfile.ZipFile(dlbuf, mode='r') as myzip:
#             # Only extract files from `file_check_list`
#             data_namelist = [nm for nm in myzip.namelist()
#                              if os.path.basename(nm) in file_check_list]
#             # Extract .zip in export_path (without keeping directory structure)
#             for file in data_namelist:
#                 filename = os.path.basename(file)
#                 export_file = os.path.join(export_path, filename)
#                 with myzip.open(file) as zf, open(export_file, 'wb') as fdst:
#                     shutil.copyfileobj(zf, fdst)


# def import_sequence(
#         path: str,
#         remove_tgc: bool = False,
#         selected_indexes: Union[List[int], Tuple[int, ...]] = None,
#         dtype=None,
#     ) -> PWSequence:
#
#     # Load PICMUS dataset and extract dict
#     data, settings = load_data(
#         path=path, indexes=selected_indexes, dtype=dtype
#     )
#     name = settings['name']
#     sampling_frequency = settings['sampling_frequency']
#     transmit_frequency = settings['transmit_frequency']
#     demodulation_frequency = settings['demodulation_frequency']
#     prf = settings['prf']
#     # TODO: initial_time and initial_times cannot really be 0...
#     initial_time = settings['initial_time']
#     angles = settings['angles']
#     mean_sound_speed = settings['mean_sound_speed']
#
#     # Create standard configuration L11 probe
#     probe = L11Probe()
#
#     # Additional required information for PWSequence
#     transmit_wave = 'square'  # (see PICMUS website)
#     transmit_cycles = 2.5  # (see PICMUS website)
#     medium_attenuation = 0.5  # (see PICMUS website)
#
#     # Check for compatibility
#     if demodulation_frequency != 0:
#         raise NotImplementedError('IQ data not yet supported')
#
#     # Create PWSequence object
#     sequence = PWSequence(name=name,
#                           probe=probe,
#                           sampling_frequency=sampling_frequency,
#                           demodulation_frequency=demodulation_frequency,
#                           prf=prf,
#                           initial_time=initial_time,
#                           transmit_frequency=transmit_frequency,
#                           transmit_wave=transmit_wave,
#                           transmit_cycles=transmit_cycles,
#                           mean_sound_speed=mean_sound_speed,
#                           medium_attenuation=medium_attenuation,
#                           angles=angles,
#                           data=data)
#
#     # Remove Time Gain Compensation (depends on the name)
#     if remove_tgc:
#         # TODO: maybe should remove exp TGC on the PICMUS16 and numerical
#         if not (name == 'carotid_cross_expe_dataset_rf'
#                 or name == 'carotid_long_expe_dataset_rf'
#                 or 'numerical_' in name):
#             # Remove PICMUS 2017 TGC
#             tgc_factor = _tgc_factor_2017(sequence)
#             data /= tgc_factor
#
#     return sequence


# def _tgc_factor_2017(sequence: PWSequence) -> np.ndarray:
#     """Time Gain Compensation (TGC) factor as provided by PICMUS creators
#     :return: gain
#     """
#     if isinstance(sequence, PWSequence):
#         pass
#     else:
#         raise TypeError(
#             '`sequence` must be an instance of class {name}'.format(
#                 name=PWSequence.__name__
#             )
#         )
#
#     # Reference depth and gain
#     wavelengths = np.array(
#         [0, 54.8571, 109.7143, 164.5714, 219.4286, 274.2857, 329.1429, 384],
#         dtype=np.float32
#     )
#     depth_dp = wavelengths * sequence.wavelength
#     gain_dp = np.array(
#         [139, 535, 650, 710, 770, 932, 992, 1012], dtype=np.float32
#     )
#
#     # Interpolation on data depth axis
#     depth = sequence.data_depth_axis
#
#     gain = np.interp(
#         depth, depth_dp, gain_dp, left=gain_dp[0], right=gain_dp[-1]
#     )
#
#     return gain
#
#
# def _tgc_factor_2016(self):
#     """Apply Time Gain Compensation (TGC) as provided by PICMUS creators
#     :return: gain
#     """
#     # TGC seems a bit overestimated at low depth
#     depth_dp = np.array(
#         [0.00500000000000000, 0.00507392473118280, 0.00514784946236559,
#          0.00522177419354839, 0.00529569892473118, 0.00536962365591398,
#          0.00544354838709677, 0.00551747311827957, 0.00559139784946237,
#          0.00566532258064516, 0.00573924731182796, 0.00581317204301075,
#          0.00588709677419355, 0.00596102150537634, 0.00603494623655914,
#          0.00699596774193548, 0.00803091397849462, 0.00899193548387097,
#          0.00995295698924731, 0.0110618279569892, 0.0208198924731183,
#          0.0305040322580645, 0.0402620967741936, 0.0499462365591398,
#          0.0510551075268817, 0.0633266129032258, 0.0755241935483871,
#          0.0877956989247312, 0.0999932795698925, 0.101028225806452,
#          0.105759408602151, 0.110490591397849, 0.115221774193548,
#          0.119952956989247],
#         dtype=np.float32
#     )
#
#     gain_dp = np.array(
#         [3954.02303201854, 1971.98573698770, 1504.88968200362,
#          1272.25246622229, 1127.64349036577, 1027.14137651379,
#          952.379074111648, 894.129676138251, 847.189190811593,
#          808.395032675326, 775.704038071821, 747.703195130510,
#          723.359625141767, 701.911930184349, 682.816801364510,
#          546.110607887509, 486.272697217059, 455.640798716392,
#          437.766530914643, 429.052416765706, 494.192563770543,
#          712.252920702294, 919.258740935713, 1010.94727336475,
#          1014.41491897915, 1090.37480204627, 1360.67559283420,
#          1712.33121957893, 1874.53797664298, 1926.89774411711,
#          2412.18711971837, 3117.39487759709, 4097.18247260613,
#          5171.13361080945],
#         dtype=np.float32
#     )
#
#     # Effective depth
#     depth = (self.initial_time * self.mean_sound_speed / 2
#              + np.arange(self.sample_number) * self.mean_sound_speed
#              / (2 * self.sampling_frequency))
#
#     gain = np.interp(depth, depth_dp, gain_dp, left=gain_dp[0], right=gain_dp[-1])
#
#     return gain
