import pytest
import unittest
from edgePy.data_import.data_import import get_dataset_path
from edgePy.data_import.ensembl.ensembl_flat_file_reader import CanonicalDataStore


TEST_GENE_SET_DATA = "transcripts_homo_sapiens_core_75_37.tsv"
TEST_GENE_SYMBOLS = "symbols_homo_sapiens_core_75_37.tsv"


class TestEnsembleFlatFileReader(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.icd = CanonicalDataStore(
            get_dataset_path(TEST_GENE_SET_DATA), get_dataset_path(TEST_GENE_SYMBOLS)
        )

    def test_pick_gene_id_1(self):
        gene_list = ["ENG000000123", "ENG000000125", "ENG000000130"]

        best_gene = self.icd.pick_gene_id(gene_list)

        assert best_gene == "ENG000000130"

    def test_has_gene(self):
        # SLC25A26	ENSG00000261657
        assert self.icd.has_gene("ENSG00000261657")
        # HMGA1P6	ENSG00000233440
        assert self.icd.has_gene("ENSG00000233440")
        # fake genes that don't exist.
        assert not self.icd.has_gene("ENSG00000000001")
        assert not self.icd.has_gene("ENSG00000000010")

    def test_get_symbol_from_gene(self):
        # FABP3P2 ENSG00000233259
        # DHFRP1 ENSG00000188985
        # LINC01050 ENSG00000271216

        assert self.icd.get_symbol_from_gene("ENSG00000233259") == "FABP3P2"
        assert self.icd.get_symbol_from_gene("ENSG00000188985") == "DHFRP1"
        assert self.icd.get_symbol_from_gene("ENSG00000271216") == "LINC01050"
        assert self.icd.get_symbol_from_gene("ENSG00000271216") == "LINC01050"
        with self.assertRaises(KeyError):
            self.icd.get_symbol_from_gene("NOTAREALGENE")

    def test_get_genes_from_symbol(self):

        assert self.icd.get_genes_from_symbol("FABP3P2") == ['ENSG00000233259']
        assert self.icd.get_genes_from_symbol("FAKEGENE1") == []
        print(self.icd.get_genes_from_symbol("PAN1"))
        self.assertListEqual(
            self.icd.get_genes_from_symbol("PAN1"),
            [
                'ENSG00000022556',
                'ENSG00000270370',
                'ENSG00000262615',
                'ENSG00000262886',
                'ENSG00000262329',
                'ENSG00000262811',
                'ENSG00000262175',
                'ENSG00000262929',
                'ENSG00000262260',
            ],
        )

    def test_is_known_symbol(self):
        # SLC25A26	ENSG00000261657
        assert self.icd.is_known_symbol("FABP3P2")
        # HMGA1P6	ENSG00000233440
        assert self.icd.is_known_symbol("DHFRP1")
        # fake genes that don't exist.
        assert not self.icd.is_known_symbol("FAKEGENE1")

    def test_is_known_gene(self):
        # SLC25A26	ENSG00000261657
        assert self.icd.is_known_gene("ENSG00000261657")
        # HMGA1P6	ENSG00000233440
        assert self.icd.is_known_gene("ENSG00000233440")
        # fake genes that don't exist.
        assert not self.icd.is_known_gene("ENSG00000000001")
        assert not self.icd.is_known_gene("ENSG00000000010")

    def test_is_canonical_by_transcript(self):
        """
        ENSG00000171448	ENST00000373656	4441	True
        ENSG00000171448	ENST00000373654	2045	False

        ENSG00000140157	ENST00000337451	3225	True
        ENSG00000140157	ENST00000398013	2274	False
        """
        assert self.icd.is_canonical_by_transcript("ENST00000373656") is True
        assert self.icd.is_canonical_by_transcript("ENST00000373654") is False
        assert self.icd.is_canonical_by_transcript("ENST00000337451") is True
        assert self.icd.is_canonical_by_transcript("ENST00000398013") is False

    def test_get_canonical_transcript(self):
        """
        ENSG00000171448	ENST00000373656	4441	True
        ENSG00000171448	ENST00000373654	2045	False

        ENSG00000140157	ENST00000337451	3225	True
        ENSG00000140157	ENST00000398013	2274	False
        """
        assert self.icd.get_canonical_transcript("ENSG00000171448") == "ENST00000373656"
        assert self.icd.get_canonical_transcript("ENSG00000140157") == "ENST00000337451"

    def test_get_length_of_transcript(self):
        """
        ENSG00000171448	ENST00000373656	4441	True
        ENSG00000171448	ENST00000373654	2045	False

        ENSG00000140157	ENST00000337451	3225	True
        ENSG00000140157	ENST00000398013	2274	False
        """
        assert self.icd.get_length_of_transcript("ENST00000373656") == 4441
        assert self.icd.get_length_of_transcript("ENST00000373654") == 2045
        assert self.icd.get_length_of_transcript("ENST00000337451") == 3225
        assert self.icd.get_length_of_transcript("ENST00000398013") == 2274

    def test_get_length_of_canonical_transcript(self):
        """
        ENSG00000171448	ENST00000373656	4441	True
        ENSG00000171448	ENST00000373654	2045	False

        ENSG00000140157	ENST00000337451	3225	True
        ENSG00000140157	ENST00000398013	2274	False
        """
        assert self.icd.get_length_of_canonical_transcript("ENSG00000171448") == 4441
        assert self.icd.get_length_of_canonical_transcript("ENSG00000140157") == 3225
