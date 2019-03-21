import argparse
from typing import Dict, Hashable, Any, Tuple, List, Optional, Union

from edgePy.data_import.mongodb.mongo_wrapper import MongoWrapper
from edgePy.data_import.mongodb.gene_functions import get_canonical_rpkm
from edgePy.data_import.mongodb.gene_functions import get_canonical_raw
from edgePy.data_import.mongodb.gene_functions import get_genelist_from_file
from edgePy.data_import.mongodb.gene_functions import translate_genes
from logging import getLogger

log = getLogger(name=__name__)


def parse_arguments(parser: Any = None, ci_values: List[str] = None) -> Any:

    """
    Standard argparse wrapper for interpreting command line arguments.

    Args:
        parser: if there's an existing parser, provide it, else, this will
        create a new one.
        ci_values: use for testing purposes only.
    """
    if not parser:
        parser = argparse.ArgumentParser()

    parser.add_argument("--config", help="location of the config file", required=True)
    parser.add_argument("--key_name", default="Project")
    parser.add_argument("--key_value", default="RNA-Seq1")
    parser.add_argument("--gene_list", default=None)

    if ci_values:
        args = parser.parse_args(ci_values)
    else:
        args = parse_arguments()
    return args


class ImportFromMongodb(object):
    """
    A utility for importing mongo data from a proprietary mongodb database - hopefully we'll
    open this database up in the future.  If not, we can re-engineer it from the examples given.

    Args:
        host: the name of the machine hosting the database
        port: the port number (usually 27017)
        mongo_key: a key in the samples collection to filter on
        mongo_value: accepted values in the samples collection to
        gene_list_file: a list of genes to filter the results on.

    """

    def __init__(
        self,
        host: str,
        port: int,
        mongo_key: Optional[str],
        mongo_value: Union[str, List, None],
        gene_list_file: Optional[str],
    ) -> None:

        self.mongo_host = host
        self.mongo_port = port

        self.mongo_reader = MongoWrapper(host=self.mongo_host, port=self.mongo_port, connect=False)

        self.search_key = mongo_key
        self.search_value = mongo_value

        self.input_gene_file = gene_list_file
        self.gene_list: Optional[List[str]] = None

    def translate_gene_list(self, database: str) -> None:
        """
        If there was a list of genes provided, convert them to ENSG symbols.

        Args:
            database: name of the database

        """

        if self.input_gene_file:
            input_genes = get_genelist_from_file(self.input_gene_file)
            ensg_genes, gene_symbols = translate_genes(
                input_genes, self.mongo_reader, database=database
            )
            self.gene_list = ensg_genes

    def get_data_from_mongo(
        self, database: str, rpkm_flag: bool = False
    ) -> Tuple[List[str], Dict[Hashable, Any], List[str], Dict[Hashable, Any]]:
        """
        Run the queries to get the samples, from mongo, and then use that data to retrieve
        the counts.

        Args:
            database: name of the database to retrieve data from.
            rpkm_flag: takes the rpkm values from the mongodb, instead of the raw counts

        Returns:
            the list of samples, the data itself,
            the gene list and the categories of the samples.

        """

        if self.input_gene_file and not self.gene_list:
            self.translate_gene_list(database)

        query: Dict[Hashable, Any] = {}
        if self.search_key and self.search_value:

            if self.search_value == 'regex':
                query = {self.search_key: {'$regex': 'myocyte|fibroblast'}}
            else:
                if isinstance(self.search_value, list):
                    query[self.search_key] = {'$in': self.search_value}
                else:
                    query[self.search_key] = self.search_value

        elif self.search_key and not self.search_value:
            query[self.search_key] = {"$exists": True}
        elif not self.search_key and not self.search_value:
            pass
        else:
            raise Exception(
                "Invalid input - you can't specify a " "key_value without specifying a key_name"
            )

        projection: Dict[Hashable, Any] = {"sample_name": 1, "_id": 0}
        if self.search_key and not self.search_key == "sample_name":
            projection[self.search_key] = 1

        cursor = self.mongo_reader.find_as_cursor(
            database=database, collection="samples", query=query, projection=projection
        )
        sample_names = set()
        sample_category = {}
        for result in cursor:
            log.info(result)
            sample_names.add(result["sample_name"])
            sample_category[result["sample_name"]] = (
                result[self.search_key] if self.search_key else result["sample_name"]
            )
        log.info(f"Get data for sample_names {list(sample_names)}")

        query = {"sample_name": {"$in": list(sample_names)}}
        if self.gene_list:
            log.info(self.gene_list)
            query["gene"] = {"$in": list(self.gene_list)}
        cursor = self.mongo_reader.find_as_cursor(
            database=database, collection="RNASeq", query=query, projection={"_id": 0}
        )

        # make it a list of lists
        log.info(f"Importing data from mongo ({self.mongo_host})...")
        dataset: Dict[Hashable, Dict[Hashable, Optional[int]]] = {}
        gene_list = set()
        sample_list = set()
        for count, result in enumerate(cursor):
            if count % 100_000 == 0:
                log.info(f"{count} rows processed.")
            sample = result["sample_name"]
            rpkm = get_canonical_rpkm(result) if rpkm_flag else get_canonical_raw(result)
            gene = result["gene"]
            if sample not in dataset:
                dataset[sample] = {}
            dataset[sample][gene] = rpkm
            sample_list.add(sample)
            gene_list.add(gene)

        return sorted(sample_list), dataset, sorted(gene_list), sample_category
