from .pdfReader import PDFReader

import re

import logging

logger = logging.getLogger(__name__)

class PDFParser():
    def parseMatch(self, match, emisDate):
        regex = '[-]?[\s]*[0-9\.]+,'
        startValue = re.search(regex, match).start()
        endDate = 5

        date = match[0:endDate].replace(' ', '')
        desc = match[endDate:startValue]
        if str(desc).endswith('/'):
            startValue += 2
        desc = match[endDate:startValue]
        value = match[startValue:].replace(' ', '')

        emisDateMonth = emisDate[3:5]
        emisDateYear = emisDate[6:]

        dateMonth = date[3:]

        year = int(emisDateYear)
        if (int(dateMonth) > int(emisDateMonth)):
            year -= 1

        date += '/' + str(year)

        return [date, desc, value]

    def run(self, file):
        reader = PDFReader()
        pdfString = reader.run(file)

        print('run string')
        logger.info(pdfString)

        #regex = '[0-9][0-9]\/[0-9][0-9][a-zA-Z\s$-.]+[0-9]+,[0-9][0-9]'
        regex = '[0-9][0-9]\/[0-9][0-9].{1,23}[0-9]+,[0-9][0-9]'
        matches = re.findall(regex, pdfString)

        emisStart = pdfString.find('Emissão: ')
        emisDate = pdfString[emisStart+9:emisStart+19]

        results = []

        for m in matches:
            r = self.parseMatch(m, emisDate)
            logger.info(r)
            results.append(r)
        return results