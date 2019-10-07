import time

from healer.device.usb.bayer_contour_next_usb import *
from healer_test.device.invoker import invoker_bayer_contour_next


def test_parse_date_time():
    print()
    result_list = ['\x06', 'D|190626|\r\n\x06', '\x06', 'D|1103|\r\n\x06']
    print(result_list)
    clock = InvokeSupportCN.parse_clock(result_list)
    print(clock)
    assert clock.year == 2019
    assert clock.month == 6
    assert clock.day == 26
    assert clock.hour == 11
    assert clock.minute == 3
    assert clock.second == 0
    clock_date = InvokeSupportCN.make_clock_date(clock)
    clock_time = InvokeSupportCN.make_clock_time(clock)
    print(f"{clock_date} {clock_time}")
    assert clock_date == '190626'
    assert clock_time == '1103'


def test_contour_next_record():
    print()
    text = '\x021H|\\^&||7EyQm2|Bayer7410^01.10\\01.05\\10.03^7428-4293200^00000|A=1^C=03^G=en,en\\de\\fr\\it\\nl\\es\\pt\\sl\\hr\\da\\no\\fi\\sv\\el^I=0200^R=0^S=01^U=303^V=20600^X=054070054054180154154254054154^Y=360126099054120054252099^Z=1|226|||||P|1|20190621125555\r\x17F9\r\n\x05'
    frame = FrameE1381(text)
    print(frame)
    record = DeviceRecordCN(frame.data())
    print(record.field_dict())


def test_parse_instant():
    print()
    assert RecordSupportCN.parse_instant_YMD_HMS("20180910111213") == DateTime(2018, 9, 10, 11, 12, 13)


def test_contour_next_parse_data():
    print()
    text_list = [
        '\x021H|\\^&||7EyQm2|Bayer7410^01.10\\01.05\\10.03^7428-4293200^00000|A=1^C=03^G=en,en\\de\\fr\\it\\nl\\es\\pt\\sl\\hr\\da\\no\\fi\\sv\\el^I=0200^R=0^S=01^U=303^V=20600^X=054070054054180154154254054154^Y=360126099054120054252099^Z=1|226|||||P|1|20190621125555\r\x17F9\r\n\x05',
        '\x022P|1\r\x1753\r\n',
        '\x024R|2|^^^Glucose|102|mg/dL^P||M0/T1||201402052135\r\x1726\r\n',
        '\x024R|234|^^^Glucose|106|mg/dL^P||F/M0/T1||201907111026\r\x170B\r\n',
        '\x025L|1||N\r\x0384\r\n',
    ]
    for text in text_list:
        print(f"---")
        print(f"text: {text}")
        frame = FrameE1381(text)
        print(f"frame: {frame}")
        data_line = frame.data()
        record = RecordSupportCN.parse_frame_data(data_line)
        print(f"record: {record}")


def test_device():
    print()
    invoker_bayer_contour_next(verify_device_packet)
    invoker_bayer_contour_next(verify_device_clock)
    invoker_bayer_contour_next(verify_frame_stream)


def verify_device_packet(device:DeviceContourNextUSB):
    print()
    print(device.device_identity())


def verify_device_clock(device:DeviceContourNextUSB):
    print()
    clock_past = device.read_clock()
    print(f"clock_past: {clock_past}")
    device.write_clock(DateTime.now())
    clock_next = device.read_clock()
    print(f"clock_next: {clock_next}")


def verify_frame_stream(device:DeviceContourNextUSB):
    print()

#     result = device.power_on()
#     print(f"result: {result}")

    def react_frame(frame:FrameE1381) -> None:
        record = RecordSupportCN.parse_frame_data(frame.data())
        print(f"record: {record}")

    device.read_frame_stream(react_frame)
