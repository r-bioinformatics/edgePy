
import sys
import argparse

from edgePy.io import DataImporter, GroupImporter


def parse_arguments(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--count_file", help="name of the file to tweet")
    parser.add_argument("--groups_file", help="Where to put the combined files")
    args = parser.parse_args(args)

    return args


class edgePy(object):

    def __init__(self, args):
        importer = DataImporter(args.count_file)
        groups = GroupImporter(args.group_file)
        print(groups.samples)
        print(importer.data)  # just a placeholder for the moment.

    def run(self):
        pass


def main():

    args = parse_arguments(sys.argv)
    default_class = edgePy(args)
    default_class.run()


if __name__ == '__main__':
    main()
