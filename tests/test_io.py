import pkgutil
import gzip

from nose.tools import eq_

from unittest import TestCase

from edgePy.io import DataImporter, GroupImporter, get_dataset_path, get_open_function  # Test import of __all__


class TestCommonFunctions(TestCase):

    def test_get_open_function(self):

        file_name = "blah.gz"
        open_function, decode_required = get_open_function(filename=file_name)
        eq_(gzip.open, open_function)
        eq_(True, decode_required)

        file_name = "blah.txt"
        open_function, decode_required = get_open_function(filename=file_name)
        eq_(open, open_function)
        eq_(False, decode_required)


class TestImporter(TestCase):
    """Unit tests for ``edgePy.io.Importer``"""

    def test_init(self):
        """Tests instantiation of the ``Importer`` class"""
        filename = get_dataset_path('GSE49712_HTSeq.txt.gz')
        import_module = DataImporter(filename)
        eq_(10, len(import_module.samples))
        eq_(21716, len(import_module.raw_data))

        import_module.process_data()
        eq_(10, len(import_module.samples))
        eq_(21716, len(import_module.data))


class TestGroupImporter(TestCase):

    def test_init(self):
        filename = get_dataset_path('groups.txt')
        group_importer = GroupImporter(filename)

        eq_(2, len(group_importer.groups))
        eq_(5, len(group_importer.groups['Group 1']))
        eq_(5, len(group_importer.groups['Group 2']))
        eq_("Group 1", group_importer.samples['A_1'])
        eq_("Group 1", group_importer.samples['A_3'])
        eq_("Group 1", group_importer.samples['A_5'])
        eq_("Group 2", group_importer.samples['B_2'])
        eq_("Group 2", group_importer.samples['B_4'])


class TestPackagedData(TestCase):
    """Unit tests for packaged (optionally zipped during install) data"""

    def test_get_data_stream(self):
        """Tests finding packaged data with ``pkgutil.get_data()``"""
        pkgutil.get_data('edgePy', 'data/GSE49712_HTSeq.txt.gz')
