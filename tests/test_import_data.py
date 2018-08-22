import pkgutil

import numpy as np

from smart_open import smart_open

from edgePy.data_import.data_import import get_dataset_path
from edgePy.data_import.data_import import create_DGEList
from edgePy.data_import.data_import import create_DGEList_handle


TEST_DATASET = "GSE49712_HTSeq.txt.gz"
TEST_GROUPS = "groups.json"

# Unit tests for ``edgePy.data_import.Importer``.\
def test_init():
    dge_list = create_DGEList_handle(
        data_handle=smart_open(get_dataset_path(TEST_DATASET)),
        group_file=get_dataset_path(TEST_GROUPS),
    )

    assert dge_list.__repr__() == "DGEList(num_samples=10, num_genes=21,716)"


# TestGroupImporter.
def test_GroupImporter_init():
    dge_list = create_DGEList_handle(
        data_handle=smart_open(get_dataset_path(TEST_DATASET)),
        group_file=get_dataset_path(TEST_GROUPS),
    )
    assert 2 == len(dge_list.groups_dict)
    assert 5 == len(dge_list.groups_dict["Group 1"])
    assert 5 == len(dge_list.groups_dict["Group 2"])

    assert dge_list.samples.shape == dge_list.groups_list.shape


# Unit tests for packaged (optionally zipped during install) data.
def test_get_data_stream():
    """Tests finding packaged data with ``pkgutil.get_data()``"""
    pkgutil.get_data("edgePy", "data/GSE49712_HTSeq.txt.gz")


def test_create_DGEList():
    """Tests the function that converts data into a DGE_List object"""
    samples = ["AAA", "BBB", "CCC"]
    genes = ["ENSG001", "ENSG002"]

    data_set = {
        "AAA": {"ENSG001": 10, "ENSG002": 20},
        "BBB": {"ENSG001": 15, "ENSG002": 40},
        "CCC": {"ENSG001": 20, "ENSG002": 80},
    }
    categories = {"AAA": "One", "BBB": "Two", "CCC": "One"}

    dge_list = create_DGEList(
        sample_list=samples, data_set=data_set, gene_list=genes, sample_category=categories
    )

    assert np.array_equal(dge_list.samples, np.array(samples))
    # 2 rows (genes), 3 columns(samples)
    assert np.array_equal(dge_list.counts, np.array([[10, 15, 20], [20, 40, 80]]))

    assert np.array_equal(dge_list.groups_list, np.array(["One", "Two", "One"]))
    assert dge_list.groups_dict, {"One:"}
    assert np.array_equal(dge_list.genes, np.array(genes))
