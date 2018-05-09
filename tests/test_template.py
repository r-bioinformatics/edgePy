
import unittest

from src.Import.tsv_import import Importer


class TestImport(unittest.TestCase):

    def test_import1(self):
        filename = "../data/GSE49712_HTSeq.txt.gz"
        import_module = Importer(filename=filename)
        length = len(import_module.data)

        self.assertEqual(21717, length)



