from edgePy.data_import.mongodb.mongo_import import ImportFromMongodb
from edgePy.data_import.mongodb.mongo_import import parse_arguments
from edgePy.data_import.data_import import get_dataset_path


def test_parse_arguments():
    config = "file.txt"
    gene_list = "groups.txt"
    key_name = "Project"
    key_value = "Publie Data"

    ci_values = [
        "--config",
        config,
        "--gene_list",
        gene_list,
        "--key_name",
        "Project",
        "--key_value",
        "Publie Data",
    ]

    args = parse_arguments(None, ci_values=ci_values)

    assert config == args.config
    assert gene_list == args.gene_list
    assert key_name == args.key_name
    assert key_value == args.key_value


def test_get_data_from_mongo_nofilters(mongodb):
    im = ImportFromMongodb(
        host="localhost", port=27017, mongo_key=None, mongo_value=None, gene_list_file=None
    )
    im.mongo_reader.session = mongodb
    sample_list, dataset, gene_list, sample_category = im.get_data_from_mongo(database="pytest")
    assert sample_list == ["SRR5189264", "SRR5189265", "SRR5189266"]
    assert dataset == {
        "SRR5189264": {"ENSG00000012048": 70, "ENSG00000139618": 105, "ENSG00000141510": 270},
        "SRR5189265": {"ENSG00000012048": 76, "ENSG00000139618": 168, "ENSG00000141510": 347},
        "SRR5189266": {"ENSG00000012048": 62, "ENSG00000139618": 104, "ENSG00000141510": 191},
    }
    assert gene_list == ["ENSG00000012048", "ENSG00000139618", "ENSG00000141510"]
    assert sample_category == {
        "SRR5189264": "SRR5189264",
        "SRR5189265": "SRR5189265",
        "SRR5189266": "SRR5189266",
    }


def test_get_data_from_mongo_filters(mongodb):
    im = ImportFromMongodb(
        host="localhost",
        port=27017,
        mongo_key="Project",
        mongo_value="Public Data",
        gene_list_file=None,
    )
    im.mongo_reader.session = mongodb
    sample_list, dataset, gene_list, sample_category = im.get_data_from_mongo(database="pytest")
    assert sample_list == ["SRR5189264", "SRR5189265", "SRR5189266"]
    assert dataset == {
        "SRR5189264": {"ENSG00000012048": 70, "ENSG00000139618": 105, "ENSG00000141510": 270},
        "SRR5189265": {"ENSG00000012048": 76, "ENSG00000139618": 168, "ENSG00000141510": 347},
        "SRR5189266": {"ENSG00000012048": 62, "ENSG00000139618": 104, "ENSG00000141510": 191},
    }
    assert gene_list == ["ENSG00000012048", "ENSG00000139618", "ENSG00000141510"]
    assert sample_category == {
        "SRR5189264": "Public Data",
        "SRR5189265": "Public Data",
        "SRR5189266": "Public Data",
    }


def test_get_data_from_mongo_gene_list(mongodb):
    filename = str(get_dataset_path("example_gene_list.txt"))
    im = ImportFromMongodb(
        host="localhost",
        port=27017,
        mongo_key="Project",
        mongo_value="Public Data",
        gene_list_file=filename,
    )
    im.mongo_reader.session = mongodb
    sample_list, dataset, gene_list, sample_category = im.get_data_from_mongo(database="pytest")
    assert sample_list == ["SRR5189264", "SRR5189265", "SRR5189266"]
    assert dataset == {
        "SRR5189264": {"ENSG00000012048": 70, "ENSG00000139618": 105, "ENSG00000141510": 270},
        "SRR5189265": {"ENSG00000012048": 76, "ENSG00000139618": 168, "ENSG00000141510": 347},
        "SRR5189266": {"ENSG00000012048": 62, "ENSG00000139618": 104, "ENSG00000141510": 191},
    }
    assert gene_list == ["ENSG00000012048", "ENSG00000139618", "ENSG00000141510"]
    assert sample_category == {
        "SRR5189264": "Public Data",
        "SRR5189265": "Public Data",
        "SRR5189266": "Public Data",
    }
