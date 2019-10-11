import pandas as pd
import os


def _load_data(t: int, name: str) -> pd.DataFrame:
    if t == 0:
        p = os.path.join(os.path.dirname(__file__), 'data/crowdsignal')
    elif t == 1:
        p = os.path.join(os.path.dirname(__file__), 'data/kaist')
    else:
        p = os.path.join(os.path.dirname(__file__), 'data/abc')
    p = os.path.join(p, name)
    return pd.read_pickle(p)


def load_crowdsignal_accel_phone() -> pd.DataFrame:
    return _load_data(0, 'accelerometer_phone.pkl')


def load_crowdsignal_accel_watch() -> pd.DataFrame:
    return _load_data(0, 'accelerometer_smartwatch.pkl')


def load_crowdsignal_battery_phone() -> pd.DataFrame:
    return _load_data(0, 'battery_phone.pkl')


def load_crowdsignal_battery_watch() -> pd.DataFrame:
    return _load_data(0, 'battery_smartwatch.pkl')


def load_crowdsignal_bluetooth_phone() -> pd.DataFrame:
    return _load_data(0, 'bluetooth_phone.pkl')


def load_crowdsignal_connectivity_phone() -> pd.DataFrame:
    return _load_data(0, 'connectivity_phone.pkl')


def load_crowdsignal_gsm_phone() -> pd.DataFrame:
    return _load_data(0, 'gsm_phone.pkl')


def load_crowdsignal_gyro_phone() -> pd.DataFrame:
    return _load_data(0, 'gyroscope_phone.pkl')


def load_crowdsignal_gyro_watch() -> pd.DataFrame:
    return _load_data(0, 'gyroscope_smartwatch.pkl')


def load_crowdsignal_heartrate_watch() -> pd.DataFrame:
    return _load_data(0, 'heart_rate_smartwatch.pkl')


def load_crowdsignal_label() -> pd.DataFrame:
    return _load_data(0, 'labels.pkl')


def load_crowdsignal_light_phone() -> pd.DataFrame:
    return _load_data(0, 'light_phone.pkl')


def load_crowdsignal_location_phone() -> pd.DataFrame:
    return _load_data(0, 'location_phone.pkl')


def load_crowdsignal_magnet_phone() -> pd.DataFrame:
    return _load_data(0, 'magnetometer_phone.pkl')


def load_crowdsignal_magnet_watch() -> pd.DataFrame:
    return _load_data(0, 'magnetometer_smartwatch.pkl')


def load_crowdsignal_pressure_phone() -> pd.DataFrame:
    return _load_data(0, 'pressure_phone.pkl')


def load_crowdsignal_proximity_phone() -> pd.DataFrame:
    return _load_data(0, 'proximity_phone.pkl')


def load_crowdsignal_screen_phone() -> pd.DataFrame:
    return _load_data(0, 'screen_phone.pkl')


def load_crowdsignal_sms_phone() -> pd.DataFrame:
    return _load_data(0, 'sms_phone.pkl')


def load_crowdsignal_wlan_phone() -> pd.DataFrame:
    return _load_data(0, 'wlan_phone.pkl')


def load_kaist_accel() -> pd.DataFrame:
    return _load_data(1, 'accelerometer.pkl')


def load_kaist_activity() -> pd.DataFrame:
    return _load_data(1, 'activity_event.pkl')


def load_kaist_app_usage() -> pd.DataFrame:
    return _load_data(1, 'app_usage.pkl')


def load_kaist_data_traffic() -> pd.DataFrame:
    return _load_data(1, 'data_traffic.pkl')


def load_kaist_gsr() -> pd.DataFrame:
    return _load_data(1, 'gsr.pkl')


def load_kaist_heartrate() -> pd.DataFrame:
    return _load_data(1, 'heart_rate.pkl')


def load_kaist_location() -> pd.DataFrame:
    return _load_data(1, 'location.pkl')


def load_kaist_rr_interval() -> pd.DataFrame:
    return _load_data(1, 'rr_interval.pkl')


def load_kaist_skin_temperature() -> pd.DataFrame:
    return _load_data(1, 'skin_temperature.pkl')


def load_abc_activity() -> pd.DataFrame:
    return _load_data(1, 'activity.pkl')


def load_abc_app_usage() -> pd.DataFrame:
    return _load_data(1, 'app_usage.pkl')


def load_abc_plugged() -> pd.DataFrame:
    return _load_data(1, 'plugged.pkl')


def load_abc_ringer_mode() -> pd.DataFrame:
    return _load_data(1, 'ringer_mode.pkl')


def load_abc_screen() -> pd.DataFrame:
    return _load_data(1, 'screen.pkl')


def load_abc_location() -> pd.DataFrame:
    return _load_data(1, 'location.pkl')
