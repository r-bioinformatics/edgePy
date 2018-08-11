from smart_open import smart_open
import numpy as np
import pytest

from edgePy import DGEList
from edgePy.io import *  # Explicitly test the import of __all__

TEST_DATASET = 'GSE49712_HTSeq.txt.gz'


@pytest.fixture
def dge_list():
    with smart_open(get_dataset_path(TEST_DATASET), 'r') as handle:
        return DGEList.read_handle(handle)


def test_blank_init():
    dge_list = DGEList(to_remove_zeroes=False)
    dge_list.counts
    dge_list.library_size


def test_too_much():
    # TODO: Refactor into smaller units.
    #    - Test blank non-parameterized `DGEList()`
    #    - Test opening handles, both gzipped or not
    #    - Test samples and genes are set, validated, typed right
    assert len(dge_list().samples) == 10
    assert len(dge_list().genes) == 21717

def test_setting_DGElist_counts():
    with pytest.raises(TypeError):
        dge_list().counts = None
    with pytest.raises(ValueError):
        dge_list().counts = np.array(-1, 1, 1)
    with pytest.raises(ValueError):
        dge_list().counts = np.array(1, 1, np.nan)

def test_repr():
    assert dge_list().__repr__() == 'DGEList(num_samples=10, num_genes=21,717)'



def test_non_implemented():
    with pytest.raises(NotImplementedError):
        dge_list().cpm()
    with pytest.raises(NotImplementedError):
        dge_list().rpkm(None)
    with pytest.raises(NotImplementedError):
        dge_list().tpm(None)

