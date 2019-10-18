
class RokuDeviceInfo():
    
    advertising_id = None
    secure_device = None
    notifications_enabled = None
    model_number = None
    model_name = None
    network_type = None
    supports_find_remote = None
    udn = None
    developer_enabled = None
    supports_wake_on_wlan = None
    software_version = None
    vendor_name = None
    supports_ecs_microphone = None
    software_build = None
    country = None
    is_tv = None
    power_mode = None
    time_zone_offset = None
    user_device_name = None
    search_enabled = None
    friendly_device_name = None
    language = None
    time_zone_tz = None
    time_zone = None
    has_play_on_roku = None
    supports_audio_guide = None
    model_region = None
    locale = None
    time_zone_name = None
    supports_ecs_text_edit = None
    time_zone_auto = None
    has_mobile_screen_saver = None
    wifi_mac = None
    notifications_first_use = None
    supports_suspend = None
    search_channels_enabled = None
    serial_number = None
    supports_private_listening = None
    friendly_model_name = None
    wifi_driver = None
    uptime = None
    voice_search_enabled = None
    supports_ethernet = None
    device_id = None
    is_stick = None
    clock_format = None
    keyed_developer_id = None
    default_device_name = None
    network_name = None
    headphones_connected = None
    support_url = None

    def __init__(self, info_json):
        device_info_obj = info_json["device-info"]
        self.advertising_id = device_info_obj["advertising-id"]
        self.secure_device = device_info_obj["secure-device"]
        self.notifications_enabled = device_info_obj["notifications-enabled"]
        self.model_number = device_info_obj["model-number"]
        self.model_name = device_info_obj["model-name"]
        self.network_type = device_info_obj["network-type"]
        self.supports_find_remote = device_info_obj["supports-find-remote"]
        self.udn = device_info_obj["udn"]
        self.developer_enabled = device_info_obj["developer-enabled"]
        self.supports_wake_on_wlan = device_info_obj["supports-wake-on-wlan"]
        self.software_version = device_info_obj["software-version"]
        self.vendor_name = device_info_obj["vendor-name"]
        self.supports_ecs_microphone = device_info_obj["supports-ecs-microphone"]
        self.software_build = device_info_obj["software-build"]
        self.country = device_info_obj["country"]
        self.is_tv = device_info_obj["is-tv"]
        self.power_mode = device_info_obj["power-mode"]
        self.time_zone_offset = device_info_obj["time-zone-offset"]
        self.user_device_name = device_info_obj["user-device-name"]
        self.search_enabled = device_info_obj["search-enabled"]
        self.friendly_device_name = device_info_obj["friendly-device-name"]
        self.language = device_info_obj["language"]
        self.time_zone_tz = device_info_obj["time-zone-tz"]
        self.time_zone = device_info_obj["time-zone"]
        self.has_play_on_roku = device_info_obj["has-play-on-roku"]
        self.supports_audio_guide = device_info_obj["supports-audio-guide"]
        self.model_region = device_info_obj["model-region"]
        self.locale = device_info_obj["locale"]
        self.time_zone_name = device_info_obj["time-zone-name"]
        self.supports_ecs_text_edit = device_info_obj["supports-ecs-textedit"]
        self.time_zone_auto = device_info_obj["time-zone-auto"]
        self.has_mobile_screen_saver = device_info_obj["has-mobile-screensaver"]
        self.wifi_mac = device_info_obj["wifi-mac"]
        self.notifications_first_use = device_info_obj["notifications-first-use"]
        self.supports_suspend = device_info_obj["supports-suspend"]
        self.search_channels_enabled = device_info_obj["search-channels-enabled"]
        self.serial_number = device_info_obj["serial-number"]
        self.supports_private_listening = device_info_obj["supports-private-listening"]
        self.friendly_model_name = device_info_obj["friendly-model-name"]
        self.wifi_driver = device_info_obj["wifi-driver"]
        self.uptime = device_info_obj["uptime"]
        self.voice_search_enabled = device_info_obj["voice-search-enabled"]
        self.supports_ethernet = device_info_obj["supports-ethernet"]
        self.device_id = device_info_obj["device-id"]
        self.is_stick = device_info_obj["is-stick"]
        self.clock_format = device_info_obj["clock-format"]
        self.keyed_developer_id = device_info_obj["keyed-developer-id"]
        self.default_device_name = device_info_obj["default-device-name"]
        self.network_name = device_info_obj["network-name"]
        self.headphones_connected = device_info_obj["headphones-connected"]
        self.support_url = device_info_obj["support-url"]

    def get_advertising_id(self):
        return self.advertising_id

    def get_secure_device(self):
        return self.secure_device

    def get_notifications_enabled(self):
        return self.notifications_enabled

    def get_model_number(self):
        return self.model_number

    def get_model_name(self):
        return self.model_name

    def get_network_type(self):
        return self.network_type

    def get_supports_find_remote(self):
        return self.supports_find_remote

    def get_udn(self):
        return self.udn

    def get_developer_enabled(self):
        return self.developer_enabled

    def get_supports_wake_on_wlan(self):
        return self.supports_wake_on_wlan

    def get_software_version(self):
        return self.software_version

    def get_vendor_name(self):
        return self.vendor_name

    def get_supports_ecs_microphone(self):
        return self.supports_ecs_microphone

    def get_software_build(self):
        return self.software_build

    def get_country(self):
        return self.country

    def get_is_tv(self):
        return self.is_tv

    def get_power_mode(self):
        return self.get_power_mode

    def get_timezone_offset(self):
        return self.get_timezone_offset

    def get_user_device_name(self):
        return self.get_user_device_name

    def get_search_enabled(self):
        return self.search_enabled

    def get_friendly_device_name(self):
        return self.friendly_device_name

    def get_language(self):
        return self.language

    def get_time_zone_tz(self):
        return self.time_zone_tz

    def get_time_zone(self):
        return self.time_zone

    def get_has_play_on_roku(self):
        return self.has_play_on_roku

    def get_supports_audio_guide(self):
        return self.supports_audio_guide

    def get_model_region(self):
        return self.model_region

    def get_locale(self):
        return self.locale

    def get_time_zone_name(self):
        return self.time_zone_name

    def get_supports_ecs_text_edit(self):
        return self.supports_ecs_text_edit

    def get_time_zone_auto(self):
        return self.time_zone_auto

    def get_has_mobile_screensaver(self):
        return self.has_mobile_screen_saver

    def get_wifi_mac(self):
        return self.wifi_mac

    def get_notifications_first_use(self):
        return self.notifications_first_use

    def get_supports_suspend(self):
        return self.supports_suspend

    def get_search_channels_enabled(self):
        return self.search_channels_enabled

    def get_serial_number(self):
        return self.serial_number

    def get_supports_private_listening(self):
        return self.supports_private_listening

    def get_friendly_model_name(self):
        return self.friendly_model_name

    def get_wifi_driver(self):
        return self.wifi_driver

    def get_uptime(self):
        return self.uptime

    def get_voice_search_enabled(self):
        return self.voice_search_enabled

    def get_supports_ethernet(self):
        return self.supports_ethernet

    def get_device_id(self):
        return self.device_id

    def get_is_stick(self):
        return self.is_stick

    def get_clock_format(self):
        return self.clock_format

    def get_keyed_developer_id(self):
        return self.keyed_developer_id

    def get_default_device_name(self):
        return self.default_device_name

    def get_network_name(self):
        return self.network_name

    def get_headphones_connected(self):
        return self.headphones_connected

    def get_support_url(self):
        return self.support_url
