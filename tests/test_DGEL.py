import pkgutil

from nose.tools import eq_

from edgePy.io import *

from edgePy.DGEList import *

filename = get_dataset_path('GSE49712_HTSeq.txt.gz')

import_module = Importer(filename=filename)

counts = DGEList(np.asarray(import_module.raw_data))

print(counts.counts)
