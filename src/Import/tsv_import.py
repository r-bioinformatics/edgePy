
""" Skeleton class for importing files """

import gzip


class Importer(object):

    def __init__(self, filename=None):
        self.filename = filename
        self.data = []
        self.headers = None

        self.read_file()
        self.validate()

    def read_file(self):
        decode_required = False
        if self.filename.endswith("gz"):
            open_function = gzip.open
            decode_required = True
        else:
            open_function = open

        header_read = False

        with open_function(self.filename) as f:
            for line in f:
                if decode_required:
                    line = line.decode('utf-8')  # this is needed if we are using gzip, which returns a binary-string.
                line = line.strip()
                if not header_read:
                    self.headers = line.split("\t")
                    header_read = True
                else:
                    self.data.append(line.split("\t"))

    def validate(self):
        columns = len(self.data[1])
        for row in self.data:
            if len(row) != columns:
                raise Exception("Inconsistent number of rows")
