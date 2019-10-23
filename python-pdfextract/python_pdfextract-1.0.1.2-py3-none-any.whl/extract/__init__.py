from jpype import *
import chardet
import threading

lock = threading.Lock()

ByteArrayInputStream        = JClass('java.io.ByteArrayInputStream')
ByteArrayOutputStream       = JClass('java.io.ByteArrayOutputStream')


class Extractor(object):
    extractor = None
    data      = None

    def __init__(self, **kwargs):
        if 'pdf' in kwargs:
            self.data = kwargs['pdf']
        if "language" in kwargs:
            self.language = kwargs['language']
        else:
            self.language = "en"
        if "options" in kwargs:
            self.options = kwargs['options']
        else:
            self.options = ""
        if "debug" in kwargs:
            self.debug = kwargs['debug']
        else:
            self.debug = 0
        try:
            # make it thread-safe
            if threading.activeCount() > 1:
                if isThreadAttachedToJVM() == False:
                    attachThreadToJVM()
            lock.acquire()

            self.extractor = JClass("pdfextract.PDFExtract")()

        finally:
            lock.release()

    def setData(self,data):
        self.data = data

    def getHTML(self):
        self.reader = ByteArrayInputStream(self.data)
        return str(self.extractor.Extract(self.reader, JString(self.language), JString(self.options), self.debug).toString())
