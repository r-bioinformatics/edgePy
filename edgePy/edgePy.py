
import argparse
from edgePy.io import Importer


def parse_arguments(parser=None):
    if not parser:
        parser = argparse.ArgumentParser()

    parser.add_argument("--count_file", help="name of the file to tweet")
    parser.add_argument("--output_dir", help="Where to put the combined files")
    args = parser.parse_args()

    return args


class edgePy(object):

    def __init__(self, args):
        importer = Importer(args.count_file)
        print(importer.data)  # just a placeholder for the moment.

    def run(self):
        pass


def main():

    args = parse_arguments()
    default_class = edgePy(args)
    default_class.run()


if __name__ == '__main__':
    main()
