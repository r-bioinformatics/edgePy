import argparse

from edgePy.DGEList import DGEList

from edgePy.data_import.data_import import DataImporter
from edgePy.data_import.data_import import GroupImporter
from edgePy.data_import.data_import import create_DGEList
from edgePy.data_import.mongodb.mongo_import import ImportFromMongodb
import numpy as np

from scipy.stats import ks_2samp
from smart_open import smart_open

from typing import List, Dict, Hashable, Any

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
    parser.add_argument("--cutoff", help="p-value cutoff to accept.", default=0.05)
    parser.add_argument(
        "--minimum_cpm", help="discard results for which no group has this many counts", default=10
    )

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

            self.ensg_to_symbol = mongo_importer.mongo_reader.find_as_dict(
                'ensembl_90_37', "symbol_by_ensg", query={}
            )

        else:
            importer = DataImporter(args.count_file)
            groups = GroupImporter(args.group_file)
            print(groups.samples)
            print(importer.data)  # just a placeholder for the moment.

            # Todo: convert this to a dge_list object.
            # self.dge_list = ???

        self.output = args.output if args.output else None
        self.p_value_cutoff = args.cutoff
        self.minimum_cpm = args.minimum_cpm

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

        gene_likelyhood1: Dict[Hashable, float] = {}

        print(self.dge_list.group)
        group_types = set(self.dge_list.group)
        group_types = list(group_types)
        group_filters: Dict[Hashable, Any] = {}
        gene_details: Dict[Hashable, Dict[Hashable, Any]] = {}
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

                gene_details[gene] = {'mean1': mean1, 'mean2': mean2}

        results = self.generate_results(
            gene_details, gene_likelyhood1, group_types[0], group_types[1]
        )

        if self.output:
            with smart_open(self.output, 'w') as out:
                out.writelines(results)
            print(f"wrote to {self.output}")
        else:
            for line in results:
                print(line)

    def generate_results(
        self,
        gene_details: Dict[Hashable, Dict[Hashable, Any]],
        gene_likelyhood1: Dict[Hashable, float],
        group_type1: str,
        group_type2: str,
    ) -> List[str]:

        results: List[str] = []
        sorted_likely = [
            (gene, gene_likelyhood1[gene])
            for gene in sorted(gene_likelyhood1, key=gene_likelyhood1.get)
        ]
        results.append(f"gene_name p-value {group_type1} {group_type2}")
        for gene, p in sorted_likely:
            m1 = gene_details[gene]['mean1']
            m2 = gene_details[gene]['mean2']
            symbol = (
                self.ensg_to_symbol[gene]['symbols'][0] if gene in self.ensg_to_symbol else gene
            )

            if (
                p < self.p_value_cutoff
                and not (m1 < self.minimum_cpm and m2 < self.minimum_cpm)
                and m1 < m2
            ):
                results.append(
                    f"{gene} "
                    f"{symbol} "
                    f"{gene_likelyhood1[gene]} "
                    f"{gene_details[gene]['mean1']:.2f} "
                    f"{gene_details[gene]['mean2']:.2f}\n"
                )

        return results


def main():

    args = parse_arguments()
    default_class = EdgePy(args)
    default_class.fake_groups()
    default_class.run_ks()


if __name__ == "__main__":
    main()
