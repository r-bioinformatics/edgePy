""" Skeleton class for importing files """

import gzip

from pathlib import Path
from typing import Union


__all__ = [
    'GroupImporter',
    'DataImporter',
    'get_dataset_path',
    'get_open_function'
]


def get_open_function(filename):
    decode_required = False
    if filename.endswith("gz"):
        open_function = gzip.open
        decode_required = True
    else:
        open_function = open

    return open_function, decode_required


class GroupImporter(object):

    def __init__(self, filename):
        self.filename = str(filename) if filename else None
        if not self.filename:
            raise Exception("No group filename")
        self.samples = {}
        self.groups = {}
        self.read_file()

    def read_file(self):
        open_function, decode_required = get_open_function(filename=self.filename)
        with open_function(self.filename) as f:
            for line in f:
                if decode_required:
                    # this is needed if we are using gzip, which returns a
                    # binary-string.
                    line = line.decode('utf-8')
                line = line.strip().split(":")
                if len(line) < 2:
                    continue  # blank line, or does not have any samples.
                group = line[0].strip()
                samples = [x.strip() for x in line[1].split(",")]
                self.groups[group] = samples
                for sample in samples:
                    if sample in self.samples:
                        raise Exception(f"Duplicate sample detected! {sample}")
                    self.samples[sample] = group


class DataImporter(object):

    def __init__(self, filename):
        self.filename = str(filename) if filename else None
        if not self.filename:
            raise Exception("No data source filename")
        self.raw_data = []
        self.data = {}
        self.samples = None

        self.read_file()
        self.validate()

    def read_file(self):
        open_function, decode_required = get_open_function(filename=self.filename)

        header_read = False

        with open_function(self.filename) as f:
            for line in f:
                if decode_required:
                    # this is needed if we are using gzip, which returns a
                    # binary-string.
                    line = line.decode('utf-8')
                line = line.strip().split("\t")
                if not header_read:
                    self.samples = line
                    self.samples = self.clean_headers(self.samples)
                    header_read = True
                else:
                    self.raw_data.append(line)

    @staticmethod
    def clean_headers(samples):
        return [s.replace("\"", "").strip() for s in samples]

    def validate(self):
        columns = len(self.raw_data[1])
        for row in self.raw_data:
            if len(row) != columns:
                raise Exception("Inconsistent number of rows")

    def process_data(self):
        for line in self.raw_data:
            gene = line[0]
            self.data[gene] = [float(point) for point in line[1:]]

        self.raw_data.clear()


def get_dataset_path(filename: Union[str, Path]) -> Path:
    """Return the filesystem path to the packaged data file.

    Parameters
    ----------
    filename : str, pathlib.Path
        The full name of the packaged data file.

    Return
    ------
    path : pathlib.Path
        The filesystem path to the packaged data file.

    Examples
    --------
    >>> from edgePy.io import get_dataset_path
    >>> str(get_dataset_path("GSE49712_HTSeq.txt.gz"))  # doctest:+ELLIPSIS
    '.../edgePy/data/GSE49712_HTSeq.txt.gz'

    """
    import edgePy
    directory = Path(edgePy.__file__).expanduser().resolve().parent
    return directory / 'data' / filename
