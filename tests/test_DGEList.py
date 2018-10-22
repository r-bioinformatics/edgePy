import pytest
import pkgutil
import numpy as np
from smart_open import smart_open  # type: ignore

from edgePy.DGEList import DGEList
from edgePy.data_import.data_import import get_dataset_path
from edgePy.data_import.ensembl.ensembl_flat_file_reader import CanonicalDataStore

TEST_GENE_SET_DATA = "transcripts_homo_sapiens_core_75_37.tsv"
TEST_GENE_SYMBOLS = "symbols_homo_sapiens_core_75_37.tsv"

TEST_DATASET = "GSE49712_HTSeq.txt.gz"
TEST_DATASET_NPZ = "GSE49712_HTSeq.txt.npz"
TEST_GROUPS = "groups.json"


@pytest.fixture
def dge_list():
    with smart_open(get_dataset_path(TEST_DATASET), 'r') as data_handle, smart_open(
        get_dataset_path(TEST_GROUPS), 'r'
    ) as group_handle:
        return DGEList.create_DGEList_handle(data_handle, group_handle)


def test_sample_by_group():
    samples = ["A", "B", "C", "D", "E"]
    expected_output = {'group1': ["A", "B"], 'group2': ["C", "D", "E"]}
    group_by_sample = ['group1', 'group1', 'group2', 'group2', 'group2']
    output = DGEList._sample_group_dict(group_by_sample, samples)
    assert output == expected_output


def test_sample_group_list():
    samples = ["A", "B", "C", "D", "E"]
    sample_by_group = {'group1': ["A", "B"], 'group2': ["C", "D", "E"]}
    expected_output = np.array(['group1', 'group1', 'group2', 'group2', 'group2'])
    output = DGEList._sample_group_list(sample_by_group, samples)
    assert np.array_equal(output, expected_output)


def test_minimal_init():

    dge_list = DGEList(
        to_remove_zeroes=False,
        counts=np.ones(shape=(5, 5)),
        samples=["A", "B", "C", "D", "E"],
        genes=["ENSG001", "ENSG002", "ENSG003", "ENSG004", "ENSG005"],
        groups_in_dict={'group1': ["A", "B"], 'group2': ["C", "D", "E"]},
    )
    assert dge_list.__repr__() == "DGEList(num_samples=5, num_genes=5)"


def test_too_much():
    # TODO: Refactor into smaller units.
    #    - Test blank non-parameterized `DGEList()`
    #    - Test opening handles, both gzipped or not
    #    - Test samples and genes are set, validated, typed right
    assert len(dge_list().samples) == 10
    assert len(dge_list().genes) == 21711


def test_too_many_options():
    with pytest.raises(Exception):
        DGEList(counts=np.zeros(shape=(5, 10)), filename=str(get_dataset_path(TEST_DATASET_NPZ)))


def test_too_many_options2():
    with pytest.raises(Exception):
        DGEList(counts=np.ones(shape=(5, 10)), filename=str(get_dataset_path(TEST_DATASET_NPZ)))


def test_library_size():
    dge_list = DGEList(filename=str(get_dataset_path(TEST_DATASET_NPZ)))
    assert np.array_equal(
        dge_list.library_size,
        np.array(
            [
                63_579_607,
                58_531_933,
                39_138_521,
                78_565_885,
                48_667_119,
                62_799_917,
                66_032_107,
                66_194_776,
                55_085_875,
                37_760_315,
            ]
        ),
    )


def test_setting_DGElist_counts():

    dge_list = DGEList(
        counts=np.zeros(shape=(5, 10)),
        groups_in_list=['A', 'A', 'B', 'B', 'B'],
        samples=['S0', 'S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8', 'S9'],
    )
    assert 5 == dge_list.counts.shape[0]
    assert 10 == dge_list.counts.shape[1]

    with pytest.raises(ValueError):
        c = np.array([[1, 1, 1], [-1, 1, 1]])
        DGEList(counts=c, groups_in_list=["a", "b"])
    with pytest.raises(ValueError):
        c = np.array([[1, 1, 1], [np.nan, 1, 1]])
        DGEList(counts=c, groups_in_list=["a", "b"])
    with pytest.raises(ValueError):
        c = np.array([1, 1, 1])
        DGEList(counts=c, groups_in_list=["a", "b"])
    with pytest.raises(TypeError):
        c = [1, 1, 1]
        dge_list.counts = c


def test_cycle_dge_npz():

    import tempfile
    import os

    tempdir = tempfile.mkdtemp(prefix="edgePy_tmp")
    file_name = tempdir + os.sep + next(tempfile._get_candidate_names())
    dge_list_first = dge_list()
    dge_list_first.write_npz_file(filename=file_name)

    dge_list_second = DGEList(filename=file_name + ".npz")
    assert np.array_equal(dge_list_first.counts, dge_list_second.counts)
    assert np.array_equal(dge_list_first.genes, dge_list_second.genes)
    assert np.array_equal(dge_list_first.samples, dge_list_second.samples)
    assert np.array_equal(dge_list_first.norm_factors, dge_list_second.norm_factors)
    assert np.array_equal(dge_list_first.groups_list, dge_list_second.groups_list)
    os.remove(file_name + ".npz")
    os.rmdir(tempdir)


def testing_setting_samples_and_counts():
    # Empty list should fail
    with pytest.raises(Exception):
        DGEList(
            to_remove_zeroes=False,
            groups_in_list=['A', 'A', 'A', 'A', 'A', 'B', 'B', 'B', 'B', 'B'],
        )

    # Lists with just counts should fail
    with pytest.raises(ValueError):
        DGEList(counts=np.array([[2, 2, 2], [2, 2, 2], [2, 2, 2]]), groups_in_list=['A', 'A', 'B'])

    # lists sith samples and counts and groups should pass:
    DGEList(
        counts=np.array([[2, 2, 2], [2, 2, 2], [2, 2, 2]]),
        groups_in_list=['A', 'A', 'B'],
        samples=["S1", 'S2', 'S3'],
    )

    # Lists with just samples should fail
    with pytest.raises(Exception):
        DGEList(
            samples=np.array(["1", "2", "3"]),
            to_remove_zeroes=False,
            groups_in_list=['A', 'A', 'B'],
        )

    # Properly formed samples and counts should pass
    DGEList(
        samples=np.array(["1", "2", "3"]),
        counts=np.array([[2, 2, 2], [2, 2, 2], [2, 2, 2]]),
        groups_in_list=['A', 'A', 'B'],
    )

    # Lists with ill-matched samples and counts should fail
    pytest.raises(
        ValueError,
        "DGEList(samples = np.array(['2', '3']),"
        " counts = np.array([[2, 2, 2], [2, 2, 2], [2, 2, 2]]))",
    )


def test_repr():
    assert dge_list().__repr__() == "DGEList(num_samples=10, num_genes=21,711)"


def test_broken_dge_caGENE_SYMBOL_SQLll():
    with pytest.raises(Exception):
        DGEList(filename="fake_filename", counts=np.array([[1, 1, 1], [1, 1, 1]]))
    with pytest.raises(Exception):
        DGEList(counts=None)


def test_cpm():
    dge_list = DGEList(filename=str(get_dataset_path(TEST_DATASET_NPZ)))
    first_pos = dge_list.counts[0][0]
    col_sum = np.sum(dge_list.counts, axis=0)
    assert isinstance(first_pos, np.integer)
    new_dge_list = dge_list.cpm()
    assert new_dge_list.counts[0][0] == first_pos * 1e6 / col_sum[0]


def test_rpkm():
    dge_list = DGEList(filename=str(get_dataset_path(TEST_DATASET_NPZ)))
    icd = CanonicalDataStore(
        get_dataset_path(TEST_GENE_SET_DATA), get_dataset_path(TEST_GENE_SYMBOLS)
    )
    first_pos = dge_list.counts[0][0]
    first_gene = dge_list.genes[0]

    col_sum = np.sum(dge_list.counts, axis=0)
    assert isinstance(first_pos, np.integer)
    rpm_dge = dge_list.rpkm(icd)
    ensg_gene = icd.pick_gene_id(icd.get_genes_from_symbol(first_gene))
    gene_len = icd.get_length_of_canonical_transcript(ensg_gene)
    # RPKM=numReads / (geneLength / 1000 * totalNumReads / 1, 000, 000)
    assert rpm_dge.counts[0][0] == (first_pos / ((gene_len / 1e3) * (col_sum[0] / 1e6)))


def test_tpm():
    # example hand calculated as in https://www.youtube.com/watch?time_continue=611&v=TTUrtCY2k-w
    counts = np.array([[10, 12, 30], [20, 25, 60], [5, 8, 15], [0, 0, 1]])
    gene_lengths = np.array([2000, 4000, 1000, 10000])

    expected = np.array(
        [
            [333_333.333_333_33, 296_296.296_296_3, 332_594.235_033_26],
            [333_333.333_333_33, 308_641.975_308_64, 332_594.235_033_26],
            [333_333.333_333_33, 395_061.728_395_06, 332_594.235_033_26],
            [0.0, 0.0, 2217.294_900_22],
        ]
    )

    dge_list = DGEList(
        counts=counts,
        samples=np.array(['a', 'b', 'c']),
        genes=np.array(['a', 'b', 'c', 'd']),
        groups_in_dict={'group1': ['a', 'c'], 'group2': ['b', 'd']},
    )
    assert isinstance(dge_list.counts[0][0], np.integer)
    new_dge_list = dge_list.tpm(gene_lengths)

    assert np.allclose(new_dge_list.counts, expected, atol=1e-1)

    # make sure that the sums of all genes across are the same the each sample (an important property of TPM)
    gene_sums = new_dge_list.counts.sum(axis=0)
    assert np.allclose(gene_sums, [gene_sums[0]] * len(gene_sums))


# Unit tests for ``edgePy.data_import.Importer``.\
def test_init():
    dge_list = DGEList.create_DGEList_data_file(
        data_file=get_dataset_path(TEST_DATASET), group_file=get_dataset_path(TEST_GROUPS)
    )

    assert dge_list.__repr__() == "DGEList(num_samples=10, num_genes=21,711)"

    dge_list = DGEList.create_DGEList_handle(
        data_handle=smart_open(get_dataset_path(TEST_DATASET)),
        group_handle=smart_open(get_dataset_path(TEST_GROUPS)),
    )

    assert dge_list.__repr__() == "DGEList(num_samples=10, num_genes=21,711)"


# TestGroupImporter.
def test_create_DGEList_handle_init():
    dge_list = DGEList.create_DGEList_handle(
        data_handle=smart_open(get_dataset_path(TEST_DATASET)),
        group_handle=smart_open(get_dataset_path(TEST_GROUPS)),
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
    categories = {"One": ["AAA", "BBB"], "Two": ["CCC"]}

    dge_list = DGEList.create_DGEList(
        sample_list=samples, data_set=data_set, gene_list=genes, category_to_samples=categories
    )

    assert np.array_equal(dge_list.samples, np.array(samples))
    # 2 rows (genes), 3 columns(samples)
    assert np.array_equal(dge_list.counts, np.array([[10, 15, 20], [20, 40, 80]]))

    assert np.array_equal(dge_list.groups_list, np.array(["One", "One", "Two"]))
    assert dge_list.groups_dict, {"One:"}
    assert np.array_equal(dge_list.genes, np.array(genes))
