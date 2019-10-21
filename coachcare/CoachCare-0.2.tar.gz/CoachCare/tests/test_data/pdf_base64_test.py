import unittest
import base64
import logging
from CoachCare.constants import TEST_DATA_DIR

class Test_pdf_base64_test(unittest.TestCase):
    #//////// Conversion Functions ///////
    def convert_to_base64(self, filename):
        data = None
        with open(filename, "rb") as pdf_file:
            data = base64.b64encode(pdf_file.read())
        logging.info(data)
        return data

    def base64_to_pdf(self, filename, base64_data):
        with open(filename, 'wb') as fout:
            fout.write(base64.decodestring(base64_data))

    #////////// TESTS /////////////
    def test_convert_to_base64(self):
        filename = TEST_DATA_DIR + "input_doc.pdf"
        data = self.convert_to_base64(filename)

    def test_base64_to_pdf(self):
        filename = TEST_DATA_DIR + "output_doc.pdf"
        base64_data = self.convert_to_base64(filename)
        self.base64_to_pdf(filename, base64_data)
        print("DONE writing pdf")

if __name__ == '__main__':
    unittest.main(exit=False)
