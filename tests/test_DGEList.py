import gzip
import numpy as np
import pytest

from src.DGEList import DGEList
from src.data_import.data_import import get_dataset_path


TEST_DATASET = 'GSE49712_HTSeq.txt.gz'


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


def test_repr():
    assert dge_list().__repr__() == 'DGEList(num_samples=10, num_genes=21,717)'


def test_non_implemented():
    with pytest.raises(NotImplementedError):
        dge_list().cpm()
    with pytest.raises(NotImplementedError):
        dge_list().rpkm(None)
    with pytest.raises(NotImplementedError):
        dge_list().tpm(None)
