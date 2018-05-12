import pkgutil

from nose.tools import eq_

from unittest import TestCase

from edgePy.io import *  # Test import of __all__


class TestImporter(TestCase):
    """Unit tests for ``edgePy.io.Importer``"""

    def test_init(self):
        """Tests instantiation of the ``Importer`` class"""
        filename = get_dataset_path('GSE49712_HTSeq.txt.gz')
        import_module = Importer(filename=filename)
        eq_(10, len(import_module.samples))
        eq_(21716, len(import_module.raw_data))

        import_module.process_data()
        eq_(10, len(import_module.samples))
        eq_(21716, len(import_module.data))


class TestPackagedData(TestCase):
    """Unit tests for packaged (optionally zipped during install) data"""

    def test_get_data_stream(self):
        """Tests finding packaged data with ``pkgutil.get_data()``"""
        pkgutil.get_data('edgePy', 'data/GSE49712_HTSeq.txt.gz')
