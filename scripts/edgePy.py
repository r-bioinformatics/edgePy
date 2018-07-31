#!/usr/bin/env python3
import argparse

from edgepy.DGEList import DGEList

from edgepy.data_import.data_import import DataImporter
from edgepy.data_import.data_import import GroupImporter

from edgepy.data_import.mongodb.mongo_import import ImportFromMongodb


def parse_arguments(parser=None):
    if not parser:
        parser = argparse.ArgumentParser()

    parser.add_argument("--count_file", help="name of the count file")
    parser.add_argument("--groups_file", help="name of the groups file")
    parser.add_argument("--dge_file", help='import from .dge file;')
    parser.add_argument("--gene_list", default=None, help='a list of genes to filter the data set')

    # mongo parameters
    parser.add_argument("--mongo_config", help='a way to import data from a supported mongo database')
    parser.add_argument("--mongo_key_name", default="Project")
    parser.add_argument("--mongo_key_value", default="RNA-Seq1")

    args = parser.parse_args()

    return args


class edgePy(object):

    def __init__(self, args):

        self.dge_list = None

        if args.dge_file:
            self.dge_list = DGEList(filename=args.dge_file)

        elif args.mongo_config:
            mongo_importer = ImportFromMongodb(args)
            sample_list, data_set, gene_list = mongo_importer.get_data_from_mongo()
            self.dge_list = mongo_importer.create_DGEList(sample_list, data_set, gene_list)

            self.dge_list.export_file('edgePy_src/data/example_data.cpe')

        else:
            importer = DataImporter(args.count_file)
            groups = GroupImporter(args.group_file)
            print(groups.samples)
            print(importer.data)  # just a placeholder for the moment.

            # Todo: convert this to a dge_list object.
            # self.dge_list = ???

    def run(self):
        pass


def main():

    args = parse_arguments()
    default_class = edgePy(args)
    default_class.run()


if __name__ == '__main__':
    main()
