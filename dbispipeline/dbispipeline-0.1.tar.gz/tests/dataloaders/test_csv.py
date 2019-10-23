# noqa: D100
import unittest

import dbispipeline.dataloaders.csv as csv


class TestCsvLoader(unittest.TestCase):
    """Tests for the dbispipeline csv loader."""

    def test_default_load(self):
        """Tests if the default settings work correctly."""
        file_path = 'tests/dataloaders/test_data.csv'
        loader = csv.CsvLoader(path=file_path)

        x, y = loader.load()
        self.assertEqual(y, None)

        for row in x:
            self.assertEqual(row[0] + 1, row[2])
            if row[0] % 2:
                self.assertEqual(row[1], 'b')
            else:
                self.assertEqual(row[1], 'a')

        self.assertEqual(loader.configuration, {
            'path': file_path,
            'labels': None,
        })

    def test_delimiter_load(self):
        """Tests if the delimiter settings work correctly."""
        file_path = 'tests/dataloaders/test_data_tab.csv'
        loader = csv.CsvLoader(path=file_path, delimiter='\t')

        x, y = loader.load()
        self.assertEqual(y, None)

        for row in x:
            self.assertEqual(row[0] + 1, row[2])
            if row[0] % 2:
                self.assertEqual(row[1], 'b')
            else:
                self.assertEqual(row[1], 'a')

        self.assertEqual(loader.configuration, {
            'path': file_path,
            'labels': None,
            'delimiter': '\t',
        })

    def test_column_load(self):
        """Tests if the usecols settings work correctly."""
        file_path = 'tests/dataloaders/test_data.csv'
        columns = [0, 2]
        loader = csv.CsvLoader(path=file_path, usecols=columns)

        x, y = loader.load()
        self.assertEqual(y, None)

        for row in x:
            self.assertEqual(row[0] + 1, row[1])

        self.assertEqual(loader.configuration, {
            'path': file_path,
            'labels': None,
            'usecols': columns,
        })

    def test_labels_load(self):
        """Tests if the labels settings work correctly."""
        file_path = 'tests/dataloaders/test_data.csv'
        label_columns = ['label']
        loader = csv.CsvLoader(path=file_path, labels=label_columns)

        x, y = loader.load()
        for data_row, label_row in zip(x, y):
            self.assertEqual(data_row[0] + 1, label_row[0])
            if data_row[0] % 2:
                self.assertEqual(data_row[1], 'b')
            else:
                self.assertEqual(data_row[1], 'a')

        self.assertEqual(loader.configuration, {
            'path': file_path,
            'labels': label_columns,
        })


class TestCsvTrainTestLoader(unittest.TestCase):
    """Tests for the dbispipeline csv train test loader."""

    def test_default_load(self):
        """Tests if the default settings work correctly."""
        file_path = 'tests/dataloaders/test_data.csv'
        loader = csv.CsvTrainTestLoader(
            train_path=file_path, test_path=file_path)

        train, test = loader.load()
        self.assertTrue((train[0] == test[0]).all())
        self.assertEqual(train[1], test[1])


class TestCsvTrainValidateTestLoader(unittest.TestCase):
    """Tests for the dbispipeline csv train validate test loader."""

    def test_default_load(self):
        """Tests if the default settings work correctly."""
        file_path = 'tests/dataloaders/test_data.csv'
        loader = csv.CsvTrainValidateTestLoader(
            train_path=file_path, validate_path=file_path, test_path=file_path)

        train, validate, test = loader.load()
        self.assertTrue((train[0] == validate[0]).all())
        self.assertEqual(train[1], validate[1])
        self.assertTrue((train[0] == test[0]).all())
        self.assertEqual(train[1], test[1])
