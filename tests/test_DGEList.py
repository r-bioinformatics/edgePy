import gzip
import numpy as np
import pytest

from src.DGEList import DGEList
from src.data_import.data_import import get_dataset_path


TEST_DATASET = 'GSE49712_HTSeq.txt.gz'
TEST_DATASET_NPZ = 'GSE49712_HTSeq.npz'


@pytest.fixture
def dge_list():
    with gzip.open(get_dataset_path(TEST_DATASET)) as handle:
        return DGEList.read_handle(handle)


def test_minimal_init():

    dge_list = DGEList(to_remove_zeroes=False,
                       counts=np.ones(shape=(5,5)),
                       samples=['A','B', 'C', 'D', 'E'],
                       genes=['ENSG001','ENSG002', 'ENSG003', 'ENSG004', 'ENSG005'])
    assert dge_list.__repr__() == 'DGEList(num_samples=5, num_genes=5)'


def test_too_much():
    # TODO: Refactor into smaller units.
    #    - Test blank non-parameterized `DGEList()`
    #    - Test opening handles, both gzipped or not
    #    - Test samples and genes are set, validated, typed right
    assert len(dge_list().samples) == 10
    assert len(dge_list().genes) == 21717


def test_too_many_options():
    with pytest.raises(Exception):
        DGEList(counts=np.zeros(shape=(5, 10)),
                filename=str(get_dataset_path(TEST_DATASET_NPZ)))


def test_too_many_options2():
    with pytest.raises(Exception):
        DGEList(counts=np.ones(shape=(5, 10)),
                filename=str(get_dataset_path(TEST_DATASET_NPZ)))


def test_library_size():
    dge_list = DGEList(filename=str(get_dataset_path(TEST_DATASET_NPZ)))
    assert np.array_equal(dge_list.library_size,
                          np.array([90895095, 82461005, 55676791, 111027083,
                                    65854416, 91305546, 95585464, 96313896,
                                    80069980, 52772642]))


def test_setting_DGElist_counts():

    dge_list = DGEList(counts=np.zeros(shape=(5, 10)))
    assert 5 == dge_list.counts.shape[0]
    assert 10 == dge_list.counts.shape[1]

    with pytest.raises(ValueError):
        c = np.array([[1, 1, 1], [-1, 1, 1]])
        DGEList(counts=c)
    with pytest.raises(ValueError):
        c = np.array([[1, 1, 1], [np.nan, 1, 1]])
        DGEList(counts=c)
    with pytest.raises(ValueError):
        c = np.array([1, 1, 1])
        DGEList(counts=c)
    with pytest.raises(TypeError):
        c = [1, 1, 1]
        dge_list.counts = c


def test_cycle_dge_npz():

    import tempfile
    import os
    tempdir = tempfile.mkdtemp(prefix='edgePy_tmp')
    file_name = tempdir + os.sep + next(tempfile._get_candidate_names())
    dge_list_first = dge_list()
    dge_list_first.export_file(filename=file_name)

    dge_list_second = DGEList(filename=file_name + ".npz")
    assert np.array_equal(dge_list_first.counts, dge_list_second.counts)
    assert np.array_equal(dge_list_first.genes, dge_list_second.genes)
    assert np.array_equal(dge_list_first.samples, dge_list_second.samples)
    assert np.array_equal(dge_list_first.norm_factors, dge_list_second.norm_factors)
    if dge_list_first.group:
        assert np.array_equal(dge_list_first.group, dge_list_second.group)
    os.remove(file_name + ".npz")
    os.rmdir(tempdir)


def testing_setting_samples_and_counts():
    # Empty list should fail
    with pytest.raises(Exception):
        DGEList(to_remove_zeroes=False)

    # Lists with just counts should pass
    DGEList(counts=np.array([[2, 2, 2], [2, 2, 2], [2, 2, 2]]))

    # Lists with just samples should fail
    with pytest.raises(Exception):
        DGEList(samples=np.array(['1', '2', '3']),
                to_remove_zeroes=False)

    # Properly formed samples and counts should pass
    DGEList(samples=np.array(['1', '2', '3']),
            counts=np.array([[2, 2, 2], [2, 2, 2], [2, 2, 2]]))

    # Lists with ill-matched samples and counts should fail
    pytest.raises(ValueError,
                  "DGEList(samples = np.array(['2', '3']),"
                  " counts = np.array([[2, 2, 2], [2, 2, 2], [2, 2, 2]]))")


def test_repr():
    assert dge_list().__repr__() == 'DGEList(num_samples=10, num_genes=21,717)'


def test_broken_dge_call():
    with pytest.raises(Exception):
        DGEList(filename='fake_filename', counts=np.array([[1, 1, 1], [1, 1, 1]]))
    with pytest.raises(Exception):
        DGEList(counts=None)


def test_non_implemented():
    with pytest.raises(NotImplementedError):
        dge_list().cpm()
    with pytest.raises(NotImplementedError):
        dge_list().rpkm(None)
    with pytest.raises(NotImplementedError):
        dge_list().tpm(None)
