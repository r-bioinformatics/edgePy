import numpy as np

__all__ = [
    'DGEList'
]


class DGEList(object):

    def __init__(
        self,
        counts=None,
        norm_factors=None,
        samples=None,
        group=None,
        genes=None,
        remove_zeroes=False
    ):
        self.counts = counts if counts is not None else np.zeros(3)

        # Library size is an array of the sums of each column of counts, same as edgeR.
        self.lib_size = np.sum(counts, 0)

        # `norm_factors` multiplies each column by one unless specified (I think?).
        # Same behavior as edgeR.
        if norm_factors is not None:
            self.norm_factors = norm_factors
        else:
            self.norm_factors = np.ones(np.shape(counts)[0])

    @property
    def counts(self):
        return self._counts

    @counts.setter
    def counts(self, counts):
        # Removes rows where counts are all zero.
        counts = counts[np.all(counts != 0, axis=1)]

        # Basic sanity checks on the counts matrix before assigning it.
        if np.any(counts < 0):
            raise ValueError("Counts matrix cannot contain negative values")
        elif np.any(counts == np.nan):
            raise ValueError("Counts must have real values")

        self._counts = counts
