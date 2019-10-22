from PyPDF2 import PdfFileReader

class PDFReader():
    def run(self, file):
        input1 = PdfFileReader(file)
        numPages = input1.getNumPages()

        pages = ''
        for i in range(0, numPages):
            page = input1.getPage(i)
            pageText = page.extractText()
            pages += pageText

        return pages