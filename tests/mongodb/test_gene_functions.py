"""The core Python code for generating data."""
import pytest
from src.data_import.data_import import get_dataset_path

from src.data_import.mongodb.gene_functions import *
from src.data_import.mongodb.mongo_wrapper import MongoWrapper

GENE_LIST_DATASET = 'example_gene_list.txt'

RNASeq_RECORD = {"_id": "5a7519801fd85c0e41c94c51",
                 "gene": "ENSG00000232977",
                 "sample_name": "SRR4011901",
                 "transcripts": {"ENST00000575689": {"size": 720, "canonical": "0",
                                                     "exons": {"ENSE00002642039": {"raw": 6.435643564356435,
                                                                                   "rpkm": 0.3682833603326866},
                                                               "ENSE00002663544": {"raw": 1.960896089608961,
                                                                                   "rpkm": 0.5189869430916676}},
                                                     "rpkm": 0.39507510837872767},
                                 "ENST00000576696": {"size": 1306, "canonical": "0",
                                                     "exons": {"ENSE00002663544": {"raw": 1.960896089608961,
                                                                                   "rpkm": 0.5189869430916676},
                                                               "ENSE00002672617": {"raw": 5.564356435643564,
                                                                                   "rpkm": 0.16002265523850875}},
                                                     "rpkm": 0.195204453741728},
                                 "ENST00000443778": {"size": 2084, "canonical": "1",
                                                     "exons": {"ENSE00001729822": {"raw": 2,
                                                                                   "rpkm": 0.0997865579744511},
                                                               "ENSE00001608298": {"raw": 1.1777177717771776,
                                                                                   "rpkm": 0.22669418591124607}},
                                                     "rpkm": 0.05165702955135873}},
                 "star_rpkm": None}


RNASeq_RECORD_NO_CANONICAL = {"_id": "5a7519801fd85c0e41c94c51",
                              "gene": "ENSG00000232977",
                              "sample_name": "SRR4011901",
                              "transcripts": {"ENST00000575689": {"size": 720, "canonical": "0",
                                                                  "exons": {
                                                                      "ENSE00002642039": {"raw": 6.435643564356435,
                                                                                          "rpkm": 0.3682833603326866},
                                                                      "ENSE00002663544": {"raw": 1.960896089608961,
                                                                                          "rpkm": 0.5189869430916676}},
                                                                  "rpkm": 0.39507510837872767},
                                              "ENST00000576696": {"size": 1306, "canonical": "0",
                                                                  "exons": {
                                                                      "ENSE00002663544": {"raw": 1.960896089608961,
                                                                                          "rpkm": 0.5189869430916676},
                                                                      "ENSE00002672617": {"raw": 5.564356435643564,
                                                                                          "rpkm": 0.16002265523850875}},
                                                                  "rpkm": 0.195204453741728}},
                              "star_rpkm": None}


@pytest.fixture
def gene_list_file():
    return get_dataset_path(GENE_LIST_DATASET)


def test_get_genelist_from_file():
    gene_list = get_genelist_from_file(gene_list_file())
    assert gene_list == ['TP53', 'BRCA1', 'BRCA2']


def test_get_genelist_from_file_no_file():
    gene_list = get_genelist_from_file(None)
    assert gene_list is None


def test_translate_genes_symbol(mongodb):
    mw = MongoWrapper('localhost', '27017')
    mw.session = mongodb
    gene_list = get_genelist_from_file(gene_list_file())
    ensg_genes, gene_symbols = translate_genes(gene_list, mw, 'pytest')
    assert ensg_genes == ['ENSG00000012048', 'ENSG00000139618', 'ENSG00000141510']
    assert gene_symbols == {'ENSG00000012048': 'BRCA1',
                            'ENSG00000139618': 'BRCA2',
                            'ENSG00000141510': 'TP53'}


def test_translate_genes_ensg(mongodb):
    mw = MongoWrapper('localhost', '27017')
    mw.session = mongodb
    gene_list = ['ENSG00000012048', 'ENSG00000139618', 'ENSG00000141510']
    ensg_genes, gene_symbols = translate_genes(gene_list, mw, 'pytest')
    assert ensg_genes == ['ENSG00000012048', 'ENSG00000139618', 'ENSG00000141510']
    assert gene_symbols == {'ENSG00000012048': 'BRCA1',
                            'ENSG00000139618': 'BRCA2',
                            'ENSG00000141510': 'TP53'}


def test_get_gene_list(mongodb):
    mw = MongoWrapper('localhost', '27017')
    mw.session = mongodb
    gene_list = get_gene_list(mw, database='pytest')
    assert gene_list == {'ENSG00000012048': 'BRCA1',
                         'ENSG00000139618': 'BRCA2',
                         'ENSG00000141510': 'TP53'}


def test_get_sample_details(mongodb):
    mw = MongoWrapper('localhost', '27017')
    mw.session = mongodb
    details = get_sample_details("Project", mw, 'pytest')
    assert details == {'SRR5189264': {'category': 'Public Data', 'description': 'SRR5189264'},
                       'SRR5189265': {'category': 'Public Data', 'description': 'SRR5189265'},
                       'SRR5189266': {'category': 'Public Data', 'description': 'SRR5189266'}}


def test_get_canonical_rpkm():
    rpkm = get_canonical_rpkm(RNASeq_RECORD)
    assert rpkm == 0.05165702955135873


def test_get_canonical_rpkm_no_canonical():
    rpkm = get_canonical_rpkm(RNASeq_RECORD_NO_CANONICAL)
    assert rpkm is None


def test_get_canonical_raw_no_canonical():
    raw = get_canonical_raw(RNASeq_RECORD_NO_CANONICAL)
    assert raw is None
