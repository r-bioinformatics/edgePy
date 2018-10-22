import pytest
import unittest

from edgePy.data_import.data_import import get_dataset_path

TEST_DATASET = "transcripts_homo_sapiens_core_75_37.tsv"
TEST_GENE_SYMBOLS = "symbols_homo_sapiens_core_75_37.tsv"
from edgePy.data_import.ensembl.ensembl_flat_file_reader import CanonicalDataStore


class TestCanonicalTranscripts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.canonicaldata = CanonicalDataStore(
            get_dataset_path(TEST_DATASET), get_dataset_path(TEST_GENE_SYMBOLS)
        )

    def test_is_canonical_by_transcript(self):
        # ENSG00000224451	ENST00000433775	567	True
        # ENSG00000175063	ENST00000405520	1441	False
        assert self.canonicaldata.is_canonical_by_transcript("ENST00000433775") is True
        assert self.canonicaldata.is_canonical_by_transcript("ENST00000405520") is False

    def test_get_canonical_transcript(self):
        # ENSG00000104047	ENST00000403028	1579	False
        # ENSG00000104047	ENST00000557968	932	False
        # ENSG00000104047	ENST00000559223	789	False
        # ENSG00000104047	ENST00000558653	1126	False
        # ENSG00000104047	ENST00000561188	588	False
        # ENSG00000104047	ENST00000557988	1195	False
        # ENSG00000104047	ENST00000560735	596	False
        # ENSG00000104047	ENST00000559164	673	False
        # ENSG00000104047	ENST00000560632	548	False
        # ENSG00000104047	ENST00000559405	580	False
        # ENSG00000104047	ENST00000251250	2674	True
        # ENSG00000104047	ENST00000329873	476	False
        # ENSG00000104047	ENST00000415425	2208	False
        assert self.canonicaldata.get_canonical_transcript("ENSG00000104047") == "ENST00000251250"

    def test_get_length_of_transcript(self):

        # ENSG00000224451	ENST00000433775	567	True
        # ENSG00000175063	ENST00000405520	1441	False
        assert self.canonicaldata.get_length_of_transcript("ENST00000433775") == 567
        assert self.canonicaldata.get_length_of_transcript("ENST00000405520") == 1441

    def test_get_length_of_canonical_transcript(self):
        # ENSG00000224451	ENST00000433775	567	True
        # ENSG00000104047	ENST00000251250	2674	True
        assert self.canonicaldata.get_length_of_canonical_transcript("ENSG00000224451") == 567
        assert self.canonicaldata.get_length_of_canonical_transcript("ENSG00000104047") == 2674
