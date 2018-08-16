import argparse

from edgePy.DGEList import DGEList

from edgePy.data_import.data_import import DataImporter
from edgePy.data_import.data_import import GroupImporter
from edgePy.data_import.data_import import create_DGEList
from edgePy.data_import.mongodb.mongo_import import ImportFromMongodb
import numpy as np

from scipy.stats import ks_2samp
from smart_open import smart_open

import configparser


def parse_arguments(parser=None):
    if not parser:
        parser = argparse.ArgumentParser()

    parser.add_argument("--count_file", help="name of the count file")
    parser.add_argument("--groups_file", help="name of the groups file")
    parser.add_argument("--dge_file", help="import from .dge file;")
    parser.add_argument("--gene_list", default=None, help="a list of genes to filter the data set")

    # mongo parameters
    parser.add_argument(
        "--mongo_config", help="a way to import data from a supported mongo database"
    )
    parser.add_argument("--mongo_key_name", default="Project")
    parser.add_argument("--mongo_key_value", default="RNA-Seq1")

    parser.add_argument("--output", help="optional output file for results")

    args = parser.parse_args()

    return args


class EdgePy(object):
    def __init__(self, args):

        self.dge_list = None

        if args.dge_file:
            self.dge_list = DGEList(filename=args.dge_file)
            print(self.dge_list)

        elif args.mongo_config:
            config = configparser.ConfigParser()
            config.read(args.mongo_config)

            mongo_importer = ImportFromMongodb(
                host=config.get("Mongo", "host"),
                port=config.get("Mongo", "port"),
                mongo_key_name=args.mongo_key_name,
                mongo_key_value=args.mongo_key_value,
                gene_list_file=args.gene_list,
            )
            sample_list, data_set, gene_list, sample_category = (
                mongo_importer.get_data_from_mongo()
            )
            self.dge_list = create_DGEList(sample_list, data_set, gene_list, sample_category)

            self.dge_list.write_npz_file("./edgePy/data/example_data.cpe")

            self.ensg_to_symbol = mongo_importer.mongo_reader.find_as_dict('ensembl_90_37', "symbol_by_ensg", query={})
            # for r in self.ensg_to_symbol:
            #     print(r, self.ensg_to_symbol[r])

        else:
            importer = DataImporter(args.count_file)
            groups = GroupImporter(args.group_file)
            print(groups.samples)
            print(importer.data)  # just a placeholder for the moment.

            # Todo: convert this to a dge_list object.
            # self.dge_list = ???

        self.output = args.output if args.output else None


    @staticmethod
    def group_type(g):
        if 'fibroblast' in g:
            return 'fibroblast'
        elif 'myocyte' in g or 'iCM' in g:
            return 'cardiomyocte'
        raise ValueError("don't know what to do with this string.")

    def fake_groups(self):
        self.dge_list.group = [self.group_type(x) for x in self.dge_list.group]

    def run_ks(self):

        gene_likelyhood1 = {}
        # self.dge_list.group = ['A', 'A', 'A', 'A', 'A', 'B', 'B', 'B', 'B', 'B']

        print(self.dge_list.group)
        group_types = set(self.dge_list.group)
        group_types = list(group_types)
        group_filters = {}
        gene_details = {}
        for group in group_types:
            group_filters[group] = [g == group for g in self.dge_list.group]
        for gene_idx, gene in enumerate(self.dge_list.genes):
            gene_row = self.dge_list.counts[gene_idx]
            if len(group_types) == 2:
                group_data1 = gene_row.compress(group_filters[group_types[0]])
                mean1 = np.mean(group_data1)

                group_data2 = gene_row.compress(group_filters[group_types[1]])
                mean2 = np.mean(group_data2)
                gene_likelyhood1[gene] = ks_2samp(group_data1, group_data2)[1]

                gene_details[gene] = {'mean1': mean1,
                                      'mean2': mean2}

        sorted_likely = [(gene, gene_likelyhood1[gene]) for gene in sorted(gene_likelyhood1, key=gene_likelyhood1.get)]

        print(f"gene_name p-value {group_types[0]} {group_types[1]}")

        if self.output:
            with smart_open(self.output, 'w') as out:
                out.write(f"gene_name p-value {group_types[0]} {group_types[1]}\n")
                for gene, p in sorted_likely:
                    m1 = gene_details[gene]['mean1']
                    m2 = gene_details[gene]['mean2']

                    if p < 0.05 and (m1 > 10 or m2 > 10) and m1 < m2:
                        out.write(
                            (f"{self.ensg_to_symbol[gene]['symbols'][0] if gene in self.ensg_to_symbol else gene} "
                             f"{gene_likelyhood1[gene]} "
                             f"{gene_details[gene]['mean1']:.2f} "
                             f"{gene_details[gene]['mean2']:.2f}\n"))
            print(f"wrote to {self.output}")

        # for gene, p in sorted_likely:
        #     if p < 0.05 and (gene_details[gene]['mean1'] > 10 or gene_details[gene]['mean2'] > 10):
        #         print(f"{self.ensg_to_symbol[gene]['symbols'][0] if gene in self.ensg_to_symbol else gene} "
        #               f"{gene_likelyhood1[gene]} "
        #               f"{gene_details[gene]['mean1']:.2f} "
        #               f"{gene_details[gene]['mean2']:.2f}")


def main():

    args = parse_arguments()
    default_class = EdgePy(args)
    default_class.fake_groups()
    default_class.run_ks()


if __name__ == "__main__":
    main()
