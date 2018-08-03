import configparser
import argparse

from src.data_import.mongodb.mongo_wrapper import MongoWrapper
from src.data_import.mongodb.gene_functions import get_canonical_raw
from src.data_import.mongodb.gene_functions import get_genelist_from_file
from src.data_import.mongodb.gene_functions import translate_genes


from typing import Dict, Hashable, Any, Tuple, List, Optional, Union


def parse_arguments(parser: Any=None, ci_values:List[str]=None) -> Any:
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

    def __init__(self, host: str, port: int,
                 mongo_key_name: Union[str, None],
                 mongo_key_value: Union[str, None],
                 gene_list_file: Union[str, None]) -> None:

        self.mongo_host = host
        self.mongo_port = port

        self.mongo_reader = MongoWrapper(host=self.mongo_host,
                                         port=self.mongo_port,
                                         connect=False)

        self.key_name = mongo_key_name
        self.key_value = mongo_key_value

        self.input_gene_file = gene_list_file
        self.gene_list: Union[List[str], None] = None

    def translate_gene_list(self, database: str) -> None:

        if self.input_gene_file:
            input_genes = get_genelist_from_file(self.input_gene_file)
            ensg_genes, gene_symbols = translate_genes(input_genes, self.mongo_reader, database=database)
            self.gene_list = ensg_genes

    def get_data_from_mongo(self, database: str='Tenaya') -> Tuple[List[str], Dict[Hashable, Any], List[str], Dict[Hashable, Any]]:

        if self.input_gene_file and not self.gene_list:
            self.translate_gene_list(database)

        query: Dict[Hashable, Any] = {}
        if self.key_name and self.key_value:
            query[self.key_name] = self.key_value

            # if self.key_value == 'regex':
            #     query = {self.key_name: {'$regex': 'myocyte|fibroblast'}}

        elif self.key_name and not self.key_value:
            query[self.key_name] = {'$exists': True}
        elif not self.key_name and not self.key_value:
            pass
        else:
            raise Exception("Invalid input - you can't specify a key_value without specifying a key_name")

        projection: Dict[Hashable, Any] = {'sample_name': 1, '_id': 0}
        if self.key_name:
            projection[self.key_name] = 1

        cursor = self.mongo_reader.find_as_cursor(database=database, collection='samples',
                                                  query=query, projection=projection)
        sample_names = set()
        sample_category = {}
        for result in cursor:
            print(result)
            sample_names.add(result['sample_name'])
            # sample_category[result['sample_name']] = 'myocyte' if 'myocyte' in result[self.key_name] else 'fibroblast'
            sample_category[result['sample_name']] = result[self.key_name] if self.key_name else result['sample_name']
        print(f"get data.... for sample_names {list(sample_names)}")

        query = {'sample_name': {'$in': list(sample_names)}}
        if self.gene_list:
            print(self.gene_list)
            query['gene'] = {'$in': list(self.gene_list)}
        cursor = self.mongo_reader.find_as_cursor(database=database, collection='RNASeq',
                                                  query=query, projection={'_id': 0})

        # make it a list of lists
        print(f"Importing data from mongo ({self.mongo_host})....")
        dataset: Dict[Hashable, Dict[Hashable, Optional[int]]] = {}
        gene_list = set()
        sample_list = set()
        count = 0
        for result in cursor:
            count += 1
            if count % 100000 == 0:
                print(f"{count} rows processed")
            sample = result['sample_name']
            rpkm = get_canonical_raw(result)
            gene = result['gene']
            # print("{}-{}".format(sample, gene))
            if sample not in dataset:
                dataset[sample] = {}
            dataset[sample][gene] = rpkm
            sample_list.add(sample)
            gene_list.add(gene)

        return sorted(sample_list), dataset, sorted(gene_list), sample_category
