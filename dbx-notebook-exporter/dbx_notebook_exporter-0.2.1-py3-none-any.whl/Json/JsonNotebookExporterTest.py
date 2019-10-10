import unittest
import os
from DbxNotebookExporter.Json.JsonNotebookExporter import JsonNotebookExporter

class JsonNotebookExporterTest(unittest.TestCase):

    def setUp(self):
        self.__exporter = JsonNotebookExporter()

    def test_multiline(self):
        testNotebookDir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))

        resources = {'libsRun': '%run {}/libs'.format('/foo/bar')}

        script, resources = self.__exporter.from_filename(testNotebookDir + '/notebook_spark.ipynb', resources)

        text_file = open(testNotebookDir + '/output.json', "w")
        text_file.write(script)
        text_file.close()

        self.assertTrue(False)

if __name__ == '__main__':
    unittest.main()
