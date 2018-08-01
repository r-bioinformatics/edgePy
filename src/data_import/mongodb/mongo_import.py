import configparser
import argparse
import numpy as np

from src.data_import.mongodb.mongo_wrapper import MongoWrapper
from src.data_import.mongodb.gene_functions import get_canonical_raw
from src.data_import.mongodb.gene_functions import get_genelist_from_file
from src.data_import.mongodb.gene_functions import translate_genes

from src.DGEList import DGEList\

from typing import Dict, Hashable, Any, Tuple, List


def parse_arguments(parser=None) -> Any:
    if not parser:
        parser = argparse.ArgumentParser()

    parser.add_argument("--config", help="location of the config file", required=True)
    parser.add_argument("--key_name", default="Project")
    parser.add_argument("--key_value", default="RNA-Seq1")
    parser.add_argument("--gene_list", default=None)

    args = parser.parse_args()
    return args


class ImportFromMongodb(object):

    def __init__(self, args) -> None:
        config = configparser.ConfigParser()
        config.read(args.mongo_config)

        self.mongo_host = config.get("Mongo", "host")
        self.mongo_port = config.get("Mongo", "port")

        self.mongo_reader = MongoWrapper(host=config.get("Mongo", "host"),
                                         port=config.get("Mongo", "port"),
                                         connect=False)

        self.key_name = args.mongo_key_name
        self.key_value = args.mongo_key_value

        self.gene_list = None
        if args.gene_list:
            input_genes = get_genelist_from_file(args.gene_list)
            ensg_genes, gene_symbols = translate_genes(input_genes, self.mongo_reader)
            self.gene_list = ensg_genes

    def get_data_from_mongo(self) -> Tuple[List[str], Dict[Hashable, Any], List[str], Dict[Hashable, Any]]:

        if self.key_name and self.key_value:
            query = {self.key_name: self.key_value}

            # if self.key_value == 'regex':
            #     query = {self.key_name: {'$regex': 'myocyte|fibroblast'}}

        elif self.key_name and not self.key_value:
            query = {self.key_name: {'$exists': True}}
        elif not self.key_name and not self.key_value:
            query = {}
        else:
            raise Exception("Invalid input - you can't specify a key_value without specifying a key_name")

        cursor = self.mongo_reader.find_as_cursor('Tenaya', 'samples',
                                                  query=query,
                                                  projection={'sample_name': 1, self.key_name: 1, '_id': 0})
        sample_names = set()
        sample_category = {}
        for result in cursor:
            print(result)
            sample_names.add(result['sample_name'])
            # sample_category[result['sample_name']] = 'myocyte' if 'myocyte' in result[self.key_name] else 'fibroblast'
            sample_category[result['sample_name']] = result[self.key_name]
        sample_names = list(sample_names)
        print(f"get data.... for sample_names {sample_names}")

        query = {'sample_name': {'$in': sample_names}}
        if self.gene_list:
            print(self.gene_list)
            query['gene'] = {'$in': list(self.gene_list)}
        cursor = self.mongo_reader.find_as_cursor('Tenaya', 'RNASeq', query=query, projection={'_id': 0})

        # make it a list of lists
        print(f"Importing data from mongo ({self.mongo_host})....")
        dataset = {}
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

    @staticmethod
    def create_DGEList(sample_list: List[str],
                       data_set: Dict[Hashable, Any],
                       gene_list: List[str],
                       sample_category: Dict[Hashable, str]) -> object:
        """ sample list and gene list must be pre-sorted
            Use this to create the DGE object for future work."""

        print("Creating DGE list object...")

        temp_data_store = np.zeros(shape=(len(sample_list), len(gene_list)))
        group = []

        for idx_s, sample in enumerate(sample_list):
            for idx_g, gene in enumerate(gene_list):
                if sample in data_set and gene in data_set[sample]:
                    if data_set[sample][gene]:
                        temp_data_store[idx_s, idx_g] = data_set[sample][gene]
            group.append(sample_category[sample])

        return DGEList(counts=temp_data_store,
                       genes=np.array(gene_list),
                       samples=np.array(sample_list),
                       group=np.array(group),
                       to_remove_zeroes=False)
