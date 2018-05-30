from unittest import TestCase

from edgePy import DGEList
from edgePy.io import *  # Test import of __all__

import numpy as np


class TestDGEList(TestCase):
    """Unit tests for ``edgePy.DGEList``"""

    def test_init(self):
        """Tests instantiation of the ``DGEList`` class"""
        filename = get_dataset_path('GSE49712_HTSeq.txt.gz')
        import_module = Importer(filename=filename)
        counts = DGEList(np.asarray(import_module.raw_data))
        print(counts.counts)
