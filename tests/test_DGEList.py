import gzip

from unittest import TestCase

from edgePy import DGEList
from edgePy.io import *  # Explicitly test the import of __all__

TEST_DATASET = 'GSE49712_HTSeq.txt.gz'


class TestDGEList(TestCase):
    """Unit tests for ``edgePy.DGEList``"""

    @classmethod
    def setUpClass(self):
        """Imports a dataset for testing"""

        with gzip.open(get_dataset_path(TEST_DATASET)) as handle:
            self.dge_fixture = DGEList.read_handle(handle)

    def test_too_much(self):
        """Test instantiation of the ``DGEList`` class"""

        # TODO: Refactor into smaller units.
        #    - Test blank non-parameterized `DGEList()`
        #    - Test opening handles, both gzipped or not
        #    - Test self.samples and self.genes are set, validated, typed right
        self.assertEqual(len(self.dge_fixture.samples), 10)
        self.assertEqual(len(self.dge_fixture.genes), 21717)

    def test_repr(self):
        """Test ``__repr__()``"""
        self.assertEqual(
            self.dge_fixture.__repr__(),
            'DGEList(num_samples=10, num_genes=21,717)'
        )
