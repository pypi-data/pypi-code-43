import re
import io
import slate3k as slate
import base64


def extract_text_from_vivo_base64(arq):

    def b642Pdf(arq):
        pdfBytesFile = open(arq, 'rb')
        pdfBytes = pdfBytesFile.read()
        pdf = base64.b64decode(pdfBytes)
        txt = slate.PDF(io.BytesIO(pdf))
        return slate.PDF(io.BytesIO(pdf))

    def substring(string, txtflag):
        return string[string.find(txtflag)+len(txtflag):]

    def string2dict(string):
        string = string[:-1]
        dic = {}
        for k in string.split(','):
            a, b = k.split(':')
            dic[a] = b
        return dic

    def range_substring(str, txtStart, txtStop):
        return str[str.find(txtStart)+len(txtStart):str.find(txtStop)]
