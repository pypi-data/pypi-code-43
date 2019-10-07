
from healer.resource.provider import *
from healer.config import CONFIG


def test_resource_path():
    print()

    device_section_list = [
        'device/usb/dummy_hcd',
        'device/usb/innovo_cms50f',
        'device/usb/ionhealth_ih02',
        'device/usb/bayer_contour_next_usb',
        'device/usb/ketonix_usb',
    ]

    for device_section in device_section_list:
        udev_file = CONFIG[device_section]['udev_file']
        print(f"udev_file: {udev_file}")
        resource_path = resource_provider_path(udev_file)
        assert os.path.exists(resource_path)
