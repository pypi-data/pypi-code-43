import unittest
import os
from DbxNotebookExporter.Python.PythonNotebookExporter import PythonNotebookExporter

class PythonNotebookExporterTest(unittest.TestCase):

    def setUp(self):
        self.__exporter = PythonNotebookExporter()

    def test_multiline(self):
        testNotebookDir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))

        script, resources = self.__exporter.from_filename(testNotebookDir + '/test_notebook.ipynb')

        text_file = open(testNotebookDir + '/output.py', "w")
        text_file.write(script)
        text_file.close()

        self.assertTrue(False)

if __name__ == '__main__':
    unittest.main()
