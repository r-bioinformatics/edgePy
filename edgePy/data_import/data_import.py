""" Skeleton class for importing files """

from smart_open import smart_open  # type: ignore

from io import StringIO
from pathlib import Path
from typing import Any, List, Union, Dict, Hashable, Mapping
from edgePy.DGEList import DGEList
import numpy as np  # type: ignore
import json


__all__ = ["get_dataset_path", "create_DGEList"]


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
    >>> from edgePy.data_import.data_import import get_dataset_path
    >>> str(get_dataset_path("GSE49712_HTSeq.txt.gz"))  # doctest:+ELLIPSIS
    '.../edgePy/data/GSE49712_HTSeq.txt.gz'

    """
    import edgePy

    directory = Path(edgePy.__file__).expanduser().resolve().parent
    return directory / "data" / filename


def create_DGEList(
    sample_list: List[str],
    data_set: Dict[Hashable, Any],  # {sample: {gene1: x, gene2: y}},
    gene_list: List[str],
    sample_category: Dict[Hashable, str],
) -> "DGEList":
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

    return DGEList(
        counts=temp_data_store,
        genes=np.array(gene_list),
        samples=np.array(sample_list),
        groups_in_list=group,
        to_remove_zeroes=False,
    )


def create_DGEList_handle(data_handle: StringIO, group_file: Path, **kwargs: Mapping) -> "DGEList":
    """Read in a file-like object of delimited data for instantiation.

    Args:
        data_handle: Any handle supporting text streaming io.
        group_file: the json file defining the groups
        kwargs: Additional arguments supported by ``np.genfromtxt``.

    Returns:
        DGEList: Container for storing read counts for samples.

    """
    # First column is the header for the the gene names.
    # Remaining columns are sample names.
    _, *samples = next(data_handle).strip().split()

    genes = []
    frame = np.genfromtxt(
        fname=data_handle,
        dtype=np.int,
        converters={0: lambda _: genes.append(_) or 0},  # type: ignore
        autostrip=kwargs.pop("autostrip", True),
        replace_space=kwargs.pop("replace_space", "_"),
        case_sensitive=kwargs.pop("case_sensitive", True),
        invalid_raise=kwargs.pop("invalid_raise", True),
        # skip_header=kwargs.pop("skip_headers", 1),
        **kwargs,
    )

    print(f"First five genes: {genes[:5]}")
    print(f"Last five genes: {genes[-5:]}")
    print(f"number of genes: {len(genes)}")

    # Delete the first column as it is copied on assignment to `genes`.
    counts = np.delete(frame, 0, axis=1)
    # Delete the first element in the genes list:
    genes = genes[1:]

    with smart_open(group_file, 'r') as gr:
        group = json.load(gr)

    return DGEList(
        counts=counts, genes=genes, samples=samples, groups_in_dict=group, to_remove_zeroes=False
    )
