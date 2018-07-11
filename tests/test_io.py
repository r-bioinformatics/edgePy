import pkgutil
import gzip

from unittest import TestCase

from edgePy.io import *  # A bad habit in practice, this tests `__all__`


class TestCommonFunctions(TestCase):

    def test_get_open_function(self):

        file_name = "blah.gz"
        open_function, decode_required = get_open_function(filename=file_name)
        self.assertEqual(gzip.open, open_function)
        self.assertTrue(decode_required)

        file_name = "blah.txt"
        open_function, decode_required = get_open_function(filename=file_name)
        self.assertEqual(open, open_function)
        self.assertFalse(decode_required)


class TestImporter(TestCase):
    """Unit tests for ``edgePy.io.Importer``"""

    def test_init(self):
        """Tests instantiation of the ``Importer`` class"""
        filename = get_dataset_path('GSE49712_HTSeq.txt.gz')
        import_module = DataImporter(filename)

        self.assertEqual(10, len(import_module.samples))
        self.assertEqual(21716, len(import_module.raw_data))

        import_module.process_data()
        self.assertEqual(10, len(import_module.samples))
        self.assertEqual(21716, len(import_module.data))

    def test_failure(self):
        self.assertRaises(Exception, DataImporter, None)


class TestGroupImporter(TestCase):

    def test_init(self):
        filename = get_dataset_path('groups.txt')
        group_importer = GroupImporter(filename)

        self.assertEqual(2, len(group_importer.groups))
        self.assertEqual(5, len(group_importer.groups['Group 1']))
        self.assertEqual(5, len(group_importer.groups['Group 2']))
        self.assertEqual("Group 1", group_importer.samples['A_1'])
        self.assertEqual("Group 1", group_importer.samples['A_3'])
        self.assertEqual("Group 1", group_importer.samples['A_5'])
        self.assertEqual("Group 2", group_importer.samples['B_2'])
        self.assertEqual("Group 2", group_importer.samples['B_4'])

    def test_failure(self):
        self.assertRaises(Exception, GroupImporter, None)


class TestPackagedData(TestCase):
    """Unit tests for packaged (optionally zipped during install) data"""

    def test_get_data_stream(self):
        """Tests finding packaged data with ``pkgutil.get_data()``"""
        pkgutil.get_data('edgePy', 'data/GSE49712_HTSeq.txt.gz')
