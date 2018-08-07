""" Skeleton class for importing files """

import gzip

from pathlib import Path
from typing import Any, List, Tuple, Union, Dict, Hashable
from src.DGEList import DGEList
import numpy as np   # type: ignore

__all__ = [
    'GroupImporter',
    'DataImporter',
    'get_dataset_path',
    'get_open_function',
    'create_DGEList'
]


def get_open_function(filename: str) -> Tuple[Any, bool]:
    decode_required = filename.endswith("gz")
    open_function = gzip.open if decode_required else open
    return open_function, decode_required


class GroupImporter(object):

    def __init__(self, filename: Union[str, Path]) -> None:
        self.filename: str = str(filename)
        self.samples: dict = {}
        self.groups: dict = {}
        self.read_file()

    def read_file(self) -> None:
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

    def __init__(self, filename: Union[str, Path]) -> None:
        self.filename: str = str(filename)
        self.raw_data: List = []
        self.data: dict = {}
        self.samples: List = []

        self.read_file()
        self.validate()

    def read_file(self) -> None:
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
                    _, *self.samples = line
                    self.samples = self.clean_headers(self.samples)
                    header_read = True
                else:
                    self.raw_data.append(line)

    @staticmethod
    def clean_headers(samples: List[str]) -> List[str]:
        return [s.replace("\"", "").strip() for s in samples]

    def validate(self) -> None:
        columns = len(self.raw_data[1])
        for row in self.raw_data:
            if len(row) != columns:
                raise Exception("Inconsistent number of rows")

    def process_data(self) -> None:
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
    >>> from src.data_import.data_import import get_dataset_path
    >>> str(get_dataset_path("GSE49712_HTSeq.txt.gz"))  # doctest:+ELLIPSIS
    '.../src/data/GSE49712_HTSeq.txt.gz'

    """
    import src
    directory = Path(src.__file__).expanduser().resolve().parent
    return directory / 'data' / filename


def create_DGEList(sample_list: List[str],
                   data_set: Dict[Hashable, Any],   # {sample: {gene1: x, gene2: y}},
                   gene_list: List[str],
                   sample_category: Dict[Hashable, str]) -> 'DGEList':
    """ sample list and gene list must be pre-sorted
        Use this to create the DGE object for future work."""

    print("Creating DGE list object...")
    temp_data_store = np.zeros(shape=(len(gene_list), len(sample_list)))
    group = []

    for idx_s, sample in enumerate(sample_list):
        for idx_g, gene in enumerate(gene_list):
            if sample in data_set and gene in data_set[sample]:
                if data_set[sample][gene]:
                    temp_data_store[idx_g, idx_s] = data_set[sample][gene]
        group.append(sample_category[sample])

    return DGEList(counts=temp_data_store,
                   genes=np.array(gene_list),
                   samples=np.array(sample_list),
                   group=np.array(group),
                   to_remove_zeroes=False)
