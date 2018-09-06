import pytest

from edgePy.data_import.ensembl.ensembl import EnsemblResrouce


@pytest.fixture
def ensembl():
    return EnsemblResrouce(release='93')


def test_get_gene_ids():
    ens = ensembl()
    gene_ids = ens.get_gene_ids()
    assert len(gene_ids) == 58395


def test_coding_genes():
    ens = ensembl()
    coding_genes = ens.get_coding_genes()
    assert len(coding_genes) == 19912
