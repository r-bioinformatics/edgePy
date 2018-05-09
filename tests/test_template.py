
import unittest

from src.Import.tsv_import import Importer


class TestImport(unittest.TestCase):

    def test_import1(self):
        filename = "../data/GSE49712_HTSeq.txt.gz"
        import_module = Importer(filename=filename)

        self.assertEqual(10, len(import_module.headers))
        self.assertEqual(21716, len(import_module.data))



