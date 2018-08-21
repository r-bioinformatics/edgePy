from smart_open import smart_open
import numpy as np
import pytest

from edgePy.DGEList import DGEList
from edgePy.data_import.data_import import get_dataset_path
from edgePy.data_import.data_import import create_DGEList_handle


TEST_DATASET = "GSE49712_HTSeq.txt.gz"
TEST_DATASET_NPZ = "GSE49712_HTSeq.npz"
TEST_GROUPS = "groups.json"


@pytest.fixture
def dge_list():
    with smart_open(get_dataset_path(TEST_DATASET), 'r') as handle:
        return create_DGEList_handle(handle, get_dataset_path(TEST_GROUPS))


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
    assert len(dge_list().genes) == 21716


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
                90895095,
                82461005,
                55676791,
                111027083,
                65854416,
                91305546,
                95585464,
                96313896,
                80069980,
                52772642,
            ]
        ),
    )


def test_setting_DGElist_counts():

    dge_list = DGEList(counts=np.zeros(shape=(5, 10)),
                       groups_in_list=['A', 'A', 'B', 'B', 'B'],
                       samples=['S0', 'S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8', 'S9'])
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

    # dge_list_first.write_npz_file(filename="/Users/anthony/Development/edgePy/edgePy/data/GSE49712_HTSeq.npz")

    dge_list_second = DGEList(filename=file_name + ".npz")
    assert np.array_equal(dge_list_first.counts, dge_list_second.counts)
    assert np.array_equal(dge_list_first.genes, dge_list_second.genes)
    assert np.array_equal(dge_list_first.samples, dge_list_second.samples)
    assert np.array_equal(dge_list_first.norm_factors, dge_list_second.norm_factors)
    if dge_list_first.group:
        assert np.array_equal(dge_list_first.group_list, dge_list_second.groups_list)
    os.remove(file_name + ".npz")
    os.rmdir(tempdir)


def testing_setting_samples_and_counts():
    # Empty list should fail
    with pytest.raises(Exception):
        DGEList(to_remove_zeroes=False,
                groups_in_list=['A', 'A', 'A', 'A', 'A', 'B', 'B', 'B', 'B', 'B'])

    # Lists with just counts should fail
    with pytest.raises(ValueError):
        DGEList(counts=np.array([[2, 2, 2], [2, 2, 2], [2, 2, 2]]),
                groups_in_list=['A', 'A', 'B'])

    # lists sith samples and counts and groups should pass:
    DGEList(counts=np.array([[2, 2, 2], [2, 2, 2], [2, 2, 2]]),
            groups_in_list=['A', 'A', 'B'],
            samples=["S1", 'S2', 'S3'])

    # Lists with just samples should fail
    with pytest.raises(Exception):
        DGEList(samples=np.array(["1", "2", "3"]), to_remove_zeroes=False,
                groups_in_list=['A', 'A', 'B'])

    # Properly formed samples and counts should pass
    DGEList(samples=np.array(["1", "2", "3"]), counts=np.array([[2, 2, 2], [2, 2, 2], [2, 2, 2]]),
            groups_in_list=['A', 'A', 'B'])

    # Lists with ill-matched samples and counts should fail
    pytest.raises(
        ValueError,
        "DGEList(samples = np.array(['2', '3']),"
        " counts = np.array([[2, 2, 2], [2, 2, 2], [2, 2, 2]]))",
    )


def test_repr():
    assert dge_list().__repr__() == "DGEList(num_samples=10, num_genes=21,716)"


def test_broken_dge_call():
    with pytest.raises(Exception):
        DGEList(filename="fake_filename", counts=np.array([[1, 1, 1], [1, 1, 1]]))
    with pytest.raises(Exception):
        DGEList(counts=None)


def test_non_implemented():
    with pytest.raises(NotImplementedError):
        dge_list().cpm()
    with pytest.raises(NotImplementedError):
        dge_list().rpkm(None)
    with pytest.raises(NotImplementedError):
        dge_list().tpm(None)
