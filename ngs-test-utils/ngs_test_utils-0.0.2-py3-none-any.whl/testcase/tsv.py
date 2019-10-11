"""Test utilities for .tsv files."""

import csv
import gzip


class TsvTestCaseMixin:
    """Mixin for manipulation of .tsv files in tests."""

    def tsv_to_list(self, fname, delimiter="\t", columns=None):
        """Read .tsv file to a nested list."""
        if columns and not isinstance(columns, list):
            columns = [columns]

        open_function = open
        if fname.endswith(".gz"):
            open_function = gzip.open

        content = []
        with open_function(fname, "rt") as handle:
            for line in handle:
                line = line.strip().split(delimiter)

                if columns:
                    line = [item for i, item in enumerate(line) if i in columns]

                content.append(line)
        return content

    def list_to_tsv(self, content, fname=None, delimiter="\t"):
        """Write contents of a nested list to a .tsv file."""
        if not fname:
            fname = self.get_filename(extension="tsv")

        open_function = open
        if fname.endswith(".gz"):
            open_function = gzip.open

        with open_function(fname, "wt") as handle:
            csvwriter = csv.writer(handle, delimiter=delimiter, lineterminator="\n")
            for line in content:
                csvwriter.writerow(line)

        return fname
