import pytest

from edgePy.data_import.ensembl.mysql_wrapper import MySQLWrapper

@pytest.fixture
def ensembl():
    return MySQLWrapper()


def test_get_gene_ids():
    gene_ids = ensembl().get_gene_ids()
    assert len(gene_ids) == 58395


def test_coding_genes():
    coding_genes = ensembl().get_coding_genes()
    assert len(coding_genes) == 19912


def test_get_transcript_ids():
    transcript_ids = ensembl().get_transcript_ids("ENSG00000139697")  # SBNO1
    assert transcript_ids == ['ENST00000267176', 'ENST00000420886', 'ENST00000602398']


def test_get_canonical_transcript():
    canonical = ensembl().get_canonical_transcript_id("ENSG00000139697")
    print(canonical)
    assert canonical == "hello"


def test_non_implemented():
    with pytest.raises(NotImplementedError):
        ensembl().get_length_of_transcript("gene")
