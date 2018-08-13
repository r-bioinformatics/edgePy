import pkgutil

import pytest
import numpy as np

from edgePy.data_import.data_import import get_dataset_path
from edgePy.data_import.data_import import GroupImporter
from edgePy.data_import.data_import import DataImporter
from edgePy.data_import.data_import import create_DGEList

# Unit tests for ``edgePy.data_import.Importer``.
def test_init():
    filename = get_dataset_path("GSE49712_HTSeq.txt.gz")
    import_module = DataImporter(filename)

    assert 10 == len(import_module.samples)
    assert 21716 == len(import_module.raw_data)

    import_module.process_data()
    assert 10 == len(import_module.samples)
    assert 21716 == len(import_module.data)


def test_failure():
    with pytest.raises(Exception):
        DataImporter(None)


# TestGroupImporter.
def test_GroupImporter_init():
    filename = get_dataset_path("groups.txt")
    group_importer = GroupImporter(filename)

    assert 2 == len(group_importer.groups)
    assert 5 == len(group_importer.groups["Group 1"])
    assert 5 == len(group_importer.groups["Group 2"])
    assert "Group 1" == group_importer.samples["A_1"]
    assert "Group 1" == group_importer.samples["A_3"]
    assert "Group 1" == group_importer.samples["A_5"]
    assert "Group 2" == group_importer.samples["B_2"]
    assert "Group 2" == group_importer.samples["B_4"]


def test_GroupImporter_failure():
    with pytest.raises(Exception):
        GroupImporter(None)


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

    assert np.array_equal(dge_list.group, np.array(["One", "Two", "One"]))
    assert np.array_equal(dge_list.genes, np.array(genes))
