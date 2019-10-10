import pandas as pd
import os


def _load_data(is_crowdsignal: bool, name: str) -> pd.DataFrame:
    if is_crowdsignal:
        p = os.path.join(os.path.dirname(__file__), 'data/crowdsignal')
    else:
        p = os.path.join(os.path.dirname(__file__), 'data/kaist')
    p = os.path.join(p, name)
    return pd.read_pickle(p)


def load_crowdsignal_accel_phone() -> pd.DataFrame:
    return _load_data(True, 'accelerometer_phone.pkl')


def load_crowdsignal_accel_watch() -> pd.DataFrame:
    return _load_data(True, 'accelerometer_smartwatch.pkl')


def load_crowdsignal_battery_phone() -> pd.DataFrame:
    return _load_data(True, 'battery_phone.pkl')


def load_crowdsignal_battery_watch() -> pd.DataFrame:
    return _load_data(True, 'battery_smartwatch.pkl')


def load_crowdsignal_bluetooth_phone() -> pd.DataFrame:
    return _load_data(True, 'bluetooth_phone.pkl')


def load_crowdsignal_connectivity_phone() -> pd.DataFrame:
    return _load_data(True, 'connectivity_phone.pkl')


def load_crowdsignal_gsm_phone() -> pd.DataFrame:
    return _load_data(True, 'gsm_phone.pkl')


def load_crowdsignal_gyro_phone() -> pd.DataFrame:
    return _load_data(True, 'gyroscope_phone.pkl')


def load_crowdsignal_gyro_watch() -> pd.DataFrame:
    return _load_data(True, 'gyroscope_smartwatch.pkl')


def load_crowdsignal_heartrate_watch() -> pd.DataFrame:
    return _load_data(True, 'heart_rate_smartwatch.pkl')


def load_crowdsignal_label() -> pd.DataFrame:
    return _load_data(True, 'labels.pkl')


def load_crowdsignal_light_phone() -> pd.DataFrame:
    return _load_data(True, 'light_phone.pkl')


def load_crowdsignal_location_phone() -> pd.DataFrame:
    return _load_data(True, 'location_phone.pkl')


def load_crowdsignal_magnet_phone() -> pd.DataFrame:
    return _load_data(True, 'magnetometer_phone.pkl')


def load_crowdsignal_magnet_watch() -> pd.DataFrame:
    return _load_data(True, 'magnetometer_smartwatch.pkl')


def load_crowdsignal_pressure_phone() -> pd.DataFrame:
    return _load_data(True, 'pressure_phone.pkl')


def load_crowdsignal_proximity_phone() -> pd.DataFrame:
    return _load_data(True, 'proximity_phone.pkl')


def load_crowdsignal_screen_phone() -> pd.DataFrame:
    return _load_data(True, 'screen_phone.pkl')


def load_crowdsignal_sms_phone() -> pd.DataFrame:
    return _load_data(True, 'sms_phone.pkl')


def load_crowdsignal_wlan_phone() -> pd.DataFrame:
    return _load_data(True, 'wlan_phone.pkl')


def load_kaist_accel() -> pd.DataFrame:
    return _load_data(False, 'accelerometer.pkl')


def load_kaist_activity() -> pd.DataFrame:
    return _load_data(False, 'activity_event.pkl')


def load_kaist_app_usage() -> pd.DataFrame:
    return _load_data(False, 'app_usage.pkl')


def load_kaist_data_traffic() -> pd.DataFrame:
    return _load_data(False, 'data_traffic.pkl')


def load_kaist_gsr() -> pd.DataFrame:
    return _load_data(False, 'gsr.pkl')


def load_kaist_heartrate() -> pd.DataFrame:
    return _load_data(False, 'heart_rate.pkl')


def load_kaist_location() -> pd.DataFrame:
    return _load_data(False, 'location.pkl')


def load_kaist_rr_interval() -> pd.DataFrame:
    return _load_data(False, 'rr_interval.pkl')


def load_kaist_skin_temperature() -> pd.DataFrame:
    return _load_data(False, 'skin_temperature.pkl')
