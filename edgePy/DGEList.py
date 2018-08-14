import re

from io import StringIO

# TODO: Implement `mypy` stubs for NumPy imports
import numpy as np  # type: ignore

from typing import Generator, Iterable, Mapping, Optional, Union

__all__ = ["DGEList"]

PRIOR_COUNT: float = 0.25


class DGEList(object):
    """Class containing read counts over genes for multiple samples and their
    corresponding metadata.

    Args:
        counts: Columns correspond to samples and row to genes.
        samples: Array of sample names, same length as ncol(counts).
        genes: Array of gene names, same length as nrow(counts).
        norm_factors: Weighting factors for each sample.
        group: ...
        to_remove_zeroes: To remove genes with zero counts for all samples.
        filename: a shortcut to import NPZ (zipped numpy format) files.

    Examples:
        >>> from smart_open import smart_open
        >>> from edgePy.data_import import get_dataset_path
        >>> dataset = 'GSE49712_HTSeq.txt.gz'
        >>> DGEList.read_handle(smart_open(get_dataset_path(dataset), 'r'))
        DGEList(num_samples=10, num_genes=21,717)

    """

    # Pattern to delete from field names anytime they are assigned.
    _field_strip_re = re.compile(r'[\s"]+')

    def __init__(
        self,
        counts: Optional[np.ndarray] = None,
        samples: Optional[np.array] = None,
        genes: Optional[np.array] = None,
        norm_factors: Optional[np.array] = None,
        group: Optional[np.array] = None,
        to_remove_zeroes: Optional[bool] = False,
        filename: Optional[str] = None,
    ) -> None:

        self.to_remove_zeroes = to_remove_zeroes
        if filename:
            if counts or samples or genes or norm_factors or group:
                raise Exception("if filename is provided, you can't also provide other parameters")
            self._counts = None
            self.read_npz_file(filename)

        else:
            if counts is None:
                raise Exception("counts must be provided at init")

            if norm_factors is None:
                try:
                    norm_factors = np.ones(np.size(counts, 1))
                except IndexError:
                    raise ValueError(
                        "counts must have more than one sample " "- eg, have two dimensions"
                    )

            self.counts = counts
            self.samples = samples
            self.genes = genes
            self.norm_factors = norm_factors
            self.group = group

    @staticmethod
    def _format_fields(fields: Iterable[Union[str, bytes]]) -> Generator[str, None, None]:
        """Clean fields in the header of any read data.

        Yields:
            The next field that has been cleaned.

        """
        for field in fields:
            if isinstance(field, bytes):
                field = field.decode()
            yield DGEList._field_strip_re.sub("", field)

    @property
    def counts(self) -> np.matrix:
        """The read counts for the genes in all samples.

        Returns:
            counts: Columns correspond to samples and row to genes.

        """
        return self._counts

    @counts.setter
    def counts(self, counts: np.ndarray) -> None:
        """Validate setting ``DGEList.counts`` for the illegal conditions:

            * Must be of type ``np.ndarray``
            * Negative values
            * Values that are not numbers
            * No values can be N/A

        Args:
            counts: Columns correspond to samples and row to genes.

        """
        if counts is None:
            self._counts = None
            return

        if hasattr(self, "_counts"):
            # do checks for things here.  You shouldn't modify counts
            # if it has already been set.  Create a new obj.
            if hasattr(self, "_samples") and self._samples is not None:
                gene_count, sample_count = counts.shape
                print(f" sample count: {sample_count}, gene count: {gene_count}")
                print(f" samples shape {self.samples.shape[0]}, gene shape {self.genes.shape[0]}")
                print(self.genes)

                if sample_count != self.samples.shape[0] or gene_count != self.genes.shape[0]:

                    raise ValueError(
                        "Attempting to substitute counts data "
                        "into DGEList object with different "
                        "dimensions fails."
                    )

        if not isinstance(counts, np.ndarray):
            raise TypeError("Counts matrix must be of type ``np.ndarray``.")
        if np.isnan(counts).any():
            raise ValueError("Counts matrix must have only real values.")
        if (counts < 0).any():
            raise ValueError("Counts matrix cannot contain negative values.")
        if self.to_remove_zeroes:
            # this is not working.  Does not remove rows with only zeros.
            counts = counts[np.all(counts != 0, axis=1)]

        self._counts = counts

    @property
    def samples(self) -> np.array:
        """Array of sample names."""
        return self._samples

    @samples.setter
    def samples(self, samples: Optional[np.ndarray]) -> None:
        """Validate setting ``DGEList.samples`` for the illegal conditions:

            * Must be the same length as the columns in counts`

        Args:
            samples: 1D string array representing identifiers of count columns

        """
        if samples is not None:
            if self.counts is not None and len(samples) != self.counts.shape[1]:
                raise ValueError(
                    f"Shape of counts does not match samples: "
                    f"len(samples) = {len(samples)},"
                    f" self.counts.shape = {self.counts.shape}"
                )

            samples = np.array(list(self._format_fields(samples)))
        self._samples = samples

    @property
    def genes(self) -> np.array:
        """Array of gene names."""
        return self._genes

    @genes.setter
    def genes(self, genes: Optional[np.ndarray]) -> None:
        # TODO: Validate genes here
        # - Genes same length as nrow(self.counts) if defined
        if genes is not None:
            genes = np.array(list(self._format_fields(genes)))
        self._genes = genes

    @property
    def library_size(self) -> np.array:
        """The total read counts per sample.

        Returns:
            library_size: The size of the library.

        """
        return np.sum(self.counts, 0)

    @classmethod
    def read_handle(cls, handle: StringIO, **kwargs: Mapping) -> "DGEList":
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
            converters={0: lambda _: genes.append(_) or 0},  # type: ignore
            autostrip=kwargs.pop("autostrip", True),
            replace_space=kwargs.pop("replace_space", "_"),
            case_sensitive=kwargs.pop("case_sensitive", True),
            invalid_raise=kwargs.pop("invalid_raise", True),
            **kwargs,
        )

        # Delete the first column as it is copied on assignment to `genes`.
        counts = np.delete(frame, 0, axis=1)

        return cls(counts=counts, samples=samples, genes=genes[1:])

    def cpm(self, log: bool = False, prior_count: float = PRIOR_COUNT) -> None:
        """Return the DGEList normalized to read counts per million."""
        self.counts = 1e6 * self.counts / np.sum(self.counts, axis=0)
        # np.sum(self.counts, axis=0)
        if log:
            self.counts[self.counts == 0] = prior_count
            self.counts = np.log(self.counts)

        raise NotImplementedError

    def rpkm(
        self, gene_lengths: Mapping, log: bool = False, prior_count: float = PRIOR_COUNT
    ) -> None:
        """Return the DGEList normalized to reads per kilobase of gene length
        per million reads.

        """
        raise NotImplementedError

        # TODO: Implement here
        # self = self.cpm(log=log, prior_count=prior_count)

    def tpm(
        self, transcripts: Mapping, log: bool = False, prior_count: float = PRIOR_COUNT
    ) -> None:
        """Return the DGEList normalized to reads per kilobase of transcript
        length.

        """
        raise NotImplementedError

        # TODO: Implement here

        # self = self.cpm(log=log, prior_count=prior_count)

    def __repr__(self) -> str:
        """Give a pretty non-executeable representation of this object."""
        num_samples = len(self._samples) if self._samples is not None else 0
        num_genes = len(self._genes) if self._genes is not None else 0

        return (
            f"{self.__class__.__name__}("
            f"num_samples={num_samples:,}, "
            f"num_genes={num_genes:,})"
        )

    def write_npz_file(self, filename: str) -> None:
        """ Convert the object to a byte representation, which can be stored or imported."""

        # TODO: validate file name

        print(f"Exporting data to compressed .dge file ({filename}.npz)....")

        np.savez_compressed(
            filename,
            samples=self.samples,
            genes=self.genes,
            norm_factors=self.norm_factors,
            counts=self.counts,
            group=self.group,
        )

    def read_npz_file(self, filename: str) -> None:
        """
        Import a file name stored in the dge export format.
        :param filename:
        :return:
        """

        print(f"Importing data from .dge file ({filename})....")

        npzfile = np.load(filename)
        self.counts = npzfile["counts"]
        self.genes = npzfile["genes"]
        self.samples = npzfile["samples"]
        self.norm_factors = npzfile["norm_factors"]
        self.group = npzfile["group"]
