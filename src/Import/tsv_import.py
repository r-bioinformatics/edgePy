
""" Skeleton class for importing files """

import gzip


class Importer(object):

    def __init__(self, filename=None):
        self.filename = filename
        self.data = []

        if self.filename.endswith("gz"):
            open_function = gzip.open
        else:
            open_function = open

        with open_function(self.filename) as f:
            for line in f:
                self.data.append(line)

