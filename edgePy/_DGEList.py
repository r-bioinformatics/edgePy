import re

import numpy as np

from typing import Generator, Iterable, Mapping, Optional

__all__ = [
    'DGEList'
]


PRIOR_COUNT = 0.25


class DGEList(object):
    """Class containing read counts over genes for multiple samples and their
    corresponding metadata.

    Args:
        counts: Columns correspond to samples and row to genes.
        samples: Array of sample names, same length as ncol(counts).
        genes: Array of gene names, same length as nrow(counts).
        norm_factors: Weighting factors for each sample.
        group: ...
        remove_zeroes: To remove genes with zero counts for all samples.

    Examples:
        >>> import gzip
        >>> from edgePy.io import get_dataset_path
        >>> dataset = 'GSE49712_HTSeq.txt.gz'
        >>> DGEList.read_handle(gzip.open(get_dataset_path(dataset)))
        DGEList(num_samples=10, num_genes=21,717)

    """

    # Pattern to delete from field names anytime they are assigned.
    _field_strip_re = re.compile(r'[\s"]+')

    def __init__(
        self,
        counts: Optional[np.matrix]=None,
        samples: Optional[np.array]=None,
        genes: Optional[np.array]=None,
        norm_factors: Optional[np.array]=None,
        group: Optional[np.array]=None,
        to_remove_zeroes: Optional[bool]=True
    ):
        if counts is None:
            counts = np.matrix(np.zeros(3))
        if norm_factors is None:
            norm_factors = np.ones(np.size(counts, 1))

        self.to_remove_zeroes = to_remove_zeroes
        self.counts = counts
        self.samples = samples
        self.genes = genes
        self.norm_factors = norm_factors
        self.group = group

    @staticmethod
    def _format_fields(fields: Iterable[str]) -> Generator[str, None, None]:
        """Clean fields in the header of any read data.

        Yields:
            The next field that has been cleaned.

        """
        for field in fields:
            try:
                field = field.decode()
            except AttributeError:
                pass
            yield DGEList._field_strip_re.sub('', field)

    @property
    def counts(self) -> np.matrix:
        """The read counts for the genes in all samples.

        Returns:
            counts: Columns correspond to samples and row to genes.

        """
        return self._counts

    @counts.setter
    def counts(self, counts) -> np.matrix:
        """Validate setting ``DGEList.counts`` for the illegal conditions:

            * Must be of type ``np.ndarray``
            * Negative values
            * Values that are not numbers
            * No values can be N/A

        Args:
            counts: Columns correspond to samples and row to genes.

        """
        if not isinstance(counts, np.ndarray):
            raise ValueError('Counts matrix must be of type ``np.ndarray``.')
        elif np.any(counts < 0):
            raise ValueError('Counts matrix cannot contain negative values.')
        elif np.any(counts == np.nan):
            raise ValueError('Counts matrix must have only real values.')
        if self.to_remove_zeroes:
            counts = counts[np.all(counts != 0, axis=1)]

        self._counts = np.matrix(counts)

    @property
    def samples(self) -> np.array:
        """Array of sample names."""
        return self._samples

    @samples.setter
    def samples(self, samples):
        # TODO: Validate samples here
        # - Samples same length as ncol(self.counts) if defined
        samples = np.array(list(DGEList._format_fields(samples)))
        self._samples = samples

    @property
    def genes(self) -> np.array:
        """Array of gene names."""
        return self._genes

    @genes.setter
    def genes(self, genes):
        # TODO: Validate genes here
        # - Genes same length as nrow(self.counts) if defined
        genes = np.array(list(DGEList._format_fields(genes)))
        self._genes = genes

    @property
    def library_size(self) -> np.array:
        """The total read counts per sample.

        Returns:
            library_size: The size of the library.

        """
        return np.sum(self.counts, 0)

    @classmethod
    def read_handle(cls, handle, **kwargs: Mapping):
        """Read in a file-like object of delimited data for instantiation.

        Args:
            handle: Any handle supporting text streaming io.
            kwargs: Additional arguments supported by ``np.genfromtxt``.

        Returns:
            DGEList: Container for storing read counts for samples.

        """
        # First column is the header for the the gene names.
        # Remaining columns are sample names.
        _, *samples = next(handle).strip().split()

        genes = []
        frame = np.genfromtxt(
            fname=handle,
            dtype=np.int,
            converters={0: lambda _: genes.append(_) or 0},
            autostrip=kwargs.pop('autostrip', True),
            replace_space=kwargs.pop('replace_space', '_'),
            case_sensitive=kwargs.pop('case_sensitive', True),
            invalid_raise=kwargs.pop('invalid_raise', True),
            **kwargs
        )

        # Delete the first column as it is copied on assignment to `genes`.
        counts = np.delete(frame, 0, axis=1)

        return DGEList(counts=counts, samples=samples, genes=genes)

    def cpm(
        self,
        log: bool=False,
        prior_count: float=PRIOR_COUNT
    ):
        """Return the DGEList normalized to read counts per million."""
        raise NotImplementedError
        self.counts = 1e6 * self.counts / np.sum(self.counts, axis=0)
        if log:
            self.counts[self.counts == 0] = prior_count
            self.counts = np.log(self.counts)
        return self

    def rpkm(
        self,
        gene_lengths: Mapping,
        log: bool=False,
        prior_count: float=PRIOR_COUNT
    ):
        """Return the DGEList normalized to reads per kilobase of gene length
        per million reads.

        """
        raise NotImplementedError

        # TODO: Implement here

        self = self.cpm(log=log, prior_count=prior_count)
        return self

    def tpm(
        self,
        transcripts: Mapping,
        log: bool=False,
        prior_count: float=PRIOR_COUNT
    ):
        """Return the DGEList normalized to reads per kilobase of transcript
        length.

        """
        raise NotImplementedError

        # TODO: Implement here

        self = self.cpm(log=log, prior_count=prior_count)
        return self

    def __repr__(self) -> str:
        """Give a pretty non-executeable representation of this object."""
        num_samples = len(self.samples) if self.samples is not None else 0
        num_genes = len(self.genes) if self.genes is not None else 0

        return (
            f'{self.__class__.__name__}('
            f'num_samples={num_samples:,}, '
            f'num_genes={num_genes:,})'
        )
