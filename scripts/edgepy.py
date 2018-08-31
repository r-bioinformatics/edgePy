import argparse

from edgePy.DGEList import DGEList

from edgePy.data_import.mongodb.mongo_import import ImportFromMongodb
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
            self.dge_list = DGEList.create_DGEList(
                sample_list, data_set, gene_list, sample_category
            )

            self.dge_list.write_npz_file("./edgePy/data/example_data.cpe")

        else:
            self.dge_list = DGEList.create_DGEList_data_file(
                data_file=args.counts_file, group_file=args.groups_file
            )

    def run(self):
        pass


def main():

    args = parse_arguments()
    default_class = EdgePy(args)
    default_class.run()


if __name__ == "__main__":
    main()
