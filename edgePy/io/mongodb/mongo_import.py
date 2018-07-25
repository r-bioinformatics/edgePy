import configparser
import argparse
import numpy as np

from edgePy.io.mongodb.mongo_wrapper import MongoWrapper
from edgePy.io.mongodb.gene_functions import get_canonical_rpkm
from edgePy.io.mongodb.gene_functions import get_genelist_from_file
from edgePy.io.mongodb.gene_functions import translate_genes

from edgePy._DGEList import DGEList


def parse_arguments(parser=None):
    if not parser:
        parser = argparse.ArgumentParser()

    parser.add_argument("--config", help="location of the config file", required=True)
    parser.add_argument("--key_name", default="Project")
    parser.add_argument("--key_value", default="RNA-Seq1")
    parser.add_argument("--gene_list", default=None)

    args = parser.parse_args()
    return args


class ExportToCVS(object):

    def __init__(self, args):
        config = configparser.ConfigParser()
        config.read(args.config)

        self.mongo_host = config.get("Mongo", "host")
        self.mongo_port = config.get("Mongo", "port")

        self.mongo_reader = MongoWrapper(host=config.get("Mongo", "host"),
                                         port=config.get("Mongo", "port"),
                                         connect=False)

        self.key_name = args.key_name
        self.key_value = args.key_value

        self.gene_list = None
        if args.gene_list:
            input_genes = get_genelist_from_file(args.gene_list)
            ensg_genes, gene_symbols = translate_genes(input_genes, self.mongo_reader)
            self.gene_list = ensg_genes

    def get_data_from_mongo(self):

        if self.key_name and self.key_value:
            query = {self.key_name: self.key_value}
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
            sample_category[result['sample_name']] = result[self.key_name]
        sample_names = list(sample_names)
        print(f"get data.... for sample_names {sample_names}")

        query = {'sample_name': {'$in': sample_names}}
        if self.gene_list:
            print(self.gene_list)
            query['gene'] = {'$in': list(self.gene_list)}
        cursor = self.mongo_reader.find_as_cursor('Tenaya', 'RNASeq', query=query, projection={'_id': 0})

        # make it a list of lists
        print("Importing data....")
        dataset = {}
        gene_list = set()
        sample_list = set()
        count = 0
        for result in cursor:
            count += 1
            if count % 100000 == 0:
                print(f"{count} rows processed")
            sample = result['sample_name']
            rpkm = get_canonical_rpkm(result)
            gene = result['gene']
            # print("{}-{}".format(sample, gene))
            if sample not in dataset:
                dataset[sample] = {}
            dataset[sample][gene] = rpkm
            sample_list.add(sample)
            gene_list.add(gene)

        return sorted(sample_list), dataset, sorted(gene_list)

    def create_DGEList(self, sample_list, data_set, gene_list):
        """ sample list and gene list must be pre-sorted
            Use this to create the DGE object for future work."""

        print("Creating DGE list object...")
        dge_list = DGEList()

        temp_data_store = np.zeros((len(sample_list), len(gene_list)))

        dge_list.samples = np.array(sample_list)
        dge_list.genes = np.array(gene_list)

        for idx_s, sample in enumerate(sample_list):
            for idx_g, gene in enumerate(gene_list):
                if sample in data_set and gene in data_set[sample]:
                    if data_set[sample][gene]:
                        temp_data_store[idx_s, idx_g] = data_set[sample][gene]

        dge_list.counts = temp_data_store

        return dge_list


def main():
    args = parse_arguments()
    default_class = ExportToCVS(args)
    sample_list, data_set, gene_list = default_class.get_data_from_mongo()
    dge_list = default_class.create_DGEList(sample_list, data_set, gene_list)

    print(dge_list)


if __name__ == '__main__':
    main()
