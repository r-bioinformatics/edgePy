import pytest

from edgePy.data_import.ensembl.ensembl import EnsemblResrouce


@pytest.fixture
def ensembl():
    return EnsemblResrouce(release='93')


def test_get_gene_ids():
    gene_ids = ensembl().get_gene_ids()
    assert len(gene_ids) == 58395


def test_coding_genes():
    coding_genes = ensembl().get_coding_genes()
    assert len(coding_genes) == 19912


def test_non_implemented():
    with pytest.raises(NotImplementedError):
        ensembl().get_transcript_ids("gene")
    with pytest.raises(NotImplementedError):
        ensembl().get_canonical_transcript_id("gene")
    with pytest.raises(NotImplementedError):
        ensembl().get_length_of_transcript("gene")
