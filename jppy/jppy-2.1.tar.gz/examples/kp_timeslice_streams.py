import km3pipe as kp

def printer(blob):
    print(blob)
    return blob

pipe = kp.Pipeline()
pipe.attach(kp.io.jpp.TimeslicePump, filename="test.root", stream="SN")
pipe.attach(printer)
pipe.drain(10)
