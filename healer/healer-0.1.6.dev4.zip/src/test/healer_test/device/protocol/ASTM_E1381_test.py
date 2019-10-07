
import pickle

from healer.device.protocol.ASTM_E1381 import *


def test_contour_next_frame():
    print()
    text = '\x021H|\\^&||7EyQm2|Bayer7410^01.10\\01.05\\10.03^7428-4293200^00000|A=1^C=03^G=en,en\\de\\fr\\it\\nl\\es\\pt\\sl\\hr\\da\\no\\fi\\sv\\el^I=0200^R=0^S=01^U=303^V=20600^X=054070054054180154154254054154^Y=360126099054120054252099^Z=1|226|||||P|1|20190621125555\r\x17F9\r\n\x05'
    frame = FrameE1381(text)
    print(frame)


def test_contour_next_pickle():
    print()
    text = '\x021H|\\^&||7EyQm2|Bayer7410^01.10\\01.05\\10.03^7428-4293200^00000|A=1^C=03^G=en,en\\de\\fr\\it\\nl\\es\\pt\\sl\\hr\\da\\no\\fi\\sv\\el^I=0200^R=0^S=01^U=303^V=20600^X=054070054054180154154254054154^Y=360126099054120054252099^Z=1|226|||||P|1|20190621125555\r\x17F9\r\n\x05'
    source = FrameE1381(text)
    binary = pickle.dumps(source)
    target = pickle.loads(binary)
    print(f"source: {source}")
    print(f"target: {target}")
    print(f"binary: {binary}")
    assert source == target
