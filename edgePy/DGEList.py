import re
import json
from io import StringIO
from pathlib import Path
from typing import Generator, Iterable, Mapping, Optional, Union, Dict, List, Hashable, Any

# TODO: Implement `mypy` stubs for NumPy imports
import numpy as np  # type: ignore
from smart_open import smart_open  # type: ignore

from edgePy.util import getLogger

__all__ = ["DGEList"]

PRIOR_COUNT: float = 0.25

log = getLogger(name=__name__)


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

        >>> from edgePy.data_import import get_dataset_path
        >>> dataset = 'GSE49712_HTSeq.txt.gz'
        >>> group_file = 'groups.json'
        >>> DGEList.create_DGEList_data_file(get_dataset_path(dataset), get_dataset_path(group_file))
        DGEList(num_samples=10, num_genes=21,711)

    """

    # Pattern to delete from field names anytime they are assigned.
    _field_strip_re = re.compile(r'[\s"]+')

    # Metatags used in older HTSeq datasets without underscore prefixes.
    _old_metatags = np.array(
        ['no_feature', 'ambiguous', 'too_low_aQual', 'not_aligned', 'alignment_not_unique']
    )

    def __init__(
        self,
        counts: Optional[np.ndarray] = None,
        samples: Optional[np.array] = None,
        genes: Optional[np.array] = None,
        norm_factors: Optional[np.array] = None,
        groups_in_list: Optional[np.array] = None,
        groups_in_dict: Optional[Dict] = None,
        to_remove_zeroes: Optional[bool] = False,
        filename: Optional[str] = None,
    ) -> None:

        self.to_remove_zeroes = to_remove_zeroes
        if filename:
            if counts or samples or genes or norm_factors or groups_in_list or groups_in_dict:
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

            if groups_in_dict and groups_in_list:
                self.groups_dict = groups_in_dict
                self.groups_list = groups_in_list
            elif groups_in_dict and self.samples is not None:
                self.groups_dict = groups_in_dict
                self.groups_list = self._sample_group_list(groups_in_dict, self.samples)
            elif groups_in_list is not None and self.samples is not None:
                self.groups_list = groups_in_list
                self.groups_dict = self._sample_group_dict(groups_in_list, self.samples)
            else:
                raise ValueError(
                    "You must provide either group by sample or sample by group, "
                    "and samples must be present"
                )

    @staticmethod
    def _sample_group_dict(groups_list: List[str], samples: np.array):
        """
        Converts data in the form ['group1', 'group1', 'group2', 'group2']
        to the form  {'group1': ['sample1', 'sample2'], 'group2': ['sample3', 'sample4'}
        :param groups_list:
        :return:
        """
        d: Dict[Hashable, Any] = {}
        log.info(samples)
        for idx, group in enumerate(groups_list):
            if group not in d:
                d[group] = []
            d[group].append(samples[idx])
        return d

    @staticmethod
    def _sample_group_list(groups_dict, samples):
        """
        Converts data in the form {'group1': ['sample1', 'sample2'], 'group2': ['sample3', 'sample4'}
        to the form ['group1', 'group1', 'group2', 'group2']
        :param groups_dict:
        :param samples:
        :return:
        """
        d = []
        temp_d = {}
        for group in groups_dict:
            for sample in groups_dict[group]:
                temp_d[sample] = group

        for sample in samples:
            d.append(temp_d[sample])

        return np.array(d)

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

        if not isinstance(counts, np.ndarray):
            raise TypeError("Counts matrix must be of type ``np.ndarray``.")

        if hasattr(self, "_counts"):
            # do checks for things here.  You shouldn't modify counts
            # if it has already been set.  Create a new obj.
            if hasattr(self, "_samples") and self._samples is not None:
                gene_count, sample_count = counts.shape
                log.info("sample count: %s, gene count: %s" % (sample_count, gene_count))
                log.info(
                    "samples shape %s, gene shape %s"
                    % (self.samples.shape[0], self.genes.shape[0])
                )
                log.info(self.genes)

                if sample_count != self.samples.shape[0] or gene_count != self.genes.shape[0]:

                    raise ValueError(
                        "Attempting to substitute counts data "
                        "into DGEList object with different "
                        "dimensions fails."
                    )

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
            # Creates boolean mask and filters out metatag rows from samples and counts
            metatag_mask = ~(
                np.isin(genes, self._old_metatags) | np.core.defchararray.startswith(genes, '__')
            )
            genes = genes[metatag_mask].copy()
            self._counts = self.counts[metatag_mask].copy()
        self._genes = genes

    @property
    def library_size(self) -> np.array:
        """The total read counts per sample.

        Returns:
            library_size: The size of the library.

        """
        return np.sum(self.counts, 0)

    def cpm(self, log: bool = False, prior_count: float = PRIOR_COUNT) -> None:
        """Return the DGEList normalized to read counts per million."""
        self.counts = 1e6 * self.counts / np.sum(self.counts, axis=0)
        if log:
            self.counts[self.counts == 0] = prior_count
            self.counts = np.log(self.counts)

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
        """Convert the object to a byte representation, which can be stored or imported."""

        # TODO: validate file name

        log.info("Exporting data to compressed .dge file (%s.npz)..." % filename)

        np.savez_compressed(
            filename,
            samples=self.samples,
            genes=self.genes,
            norm_factors=self.norm_factors,
            counts=self.counts,
            groups_list=self.groups_list,
        )

    def read_npz_file(self, filename: str) -> None:
        """Import a file name stored in the dge export format.

        :param filename:
        :return:
        """

        log.info(f"Importing data from .dge file ({filename})....")

        npzfile = np.load(filename)
        self.counts = npzfile["counts"]
        self.genes = npzfile["genes"]
        self.samples = npzfile["samples"]
        self.norm_factors = npzfile["norm_factors"]
        self.groups_list = npzfile["groups_list"].tolist()

        self.groups_dict = self._sample_group_dict(self.groups_list, self.samples)

    @classmethod
    def create_DGEList(
        cls,
        sample_list: List[str],
        data_set: Dict[Hashable, Any],  # {sample: {gene1: x, gene2: y}},
        gene_list: List[str],
        sample_to_category: Optional[List[str]] = None,
        category_to_samples: Optional[Dict[Hashable, List[str]]] = None,
    ) -> "DGEList":
        """ sample list and gene list must be pre-sorted
            Use this to create the DGE object for future work."""

        log.info("Creating DGE list object...")
        temp_data_store = np.zeros(shape=(len(gene_list), len(sample_list)))

        for idx_s, sample in enumerate(sample_list):
            for idx_g, gene in enumerate(gene_list):
                if sample in data_set and gene in data_set[sample]:
                    if data_set[sample][gene]:
                        temp_data_store[idx_g, idx_s] = data_set[sample][gene]

        return cls(
            counts=temp_data_store,
            genes=np.array(gene_list),
            samples=np.array(sample_list),
            groups_in_list=sample_to_category if sample_to_category else None,
            groups_in_dict=category_to_samples if category_to_samples else None,
            to_remove_zeroes=False,
        )

    @classmethod
    def create_DGEList_data_file(
        cls, data_file: Path, group_file: Path, **kwargs: Mapping
    ) -> "DGEList":
        """Wrapper for creating DGEList objects from file locations.  Performs open and passes
        the file handles to the method for creating a DGEList object.

        Args:
            data_file: Text file defining the data set.
            group_file: The JSON file defining the groups.
            kwargs: Additional arguments supported by ``np.genfromtxt``.

        Returns:
            DGEList: Container for storing read counts for samples.

        """
        with smart_open(data_file, 'r') as data_handle, smart_open(
            group_file, 'r'
        ) as group_handle:
            return cls.create_DGEList_handle(data_handle, group_handle, **kwargs)

    @classmethod
    def create_DGEList_handle(
        cls, data_handle: StringIO, group_handle: StringIO, **kwargs: Mapping
    ) -> "DGEList":
        """Read in a file-like object of delimited data for instantiation.

        Args:
            data_handle: Text file defining the data set.
            group_handle: The JSON file defining the groups.
            kwargs: Additional arguments supported by ``np.genfromtxt``.

        Returns:
            DGEList: Container for storing read counts for samples.

        """
        _, *samples = next(data_handle).strip().split()

        genes = []
        frame = np.genfromtxt(
            fname=data_handle,
            dtype=np.int,
            converters={0: lambda _: genes.append(_.decode("utf-8")) or 0},  # type: ignore
            autostrip=kwargs.pop("autostrip", True),
            replace_space=kwargs.pop("replace_space", "_"),
            case_sensitive=kwargs.pop("case_sensitive", True),
            invalid_raise=kwargs.pop("invalid_raise", True),
            # skip_header=kwargs.pop("skip_headers", 1),
            **kwargs,
        )

        # Delete the first column as it is copied on assignment to `genes`.
        counts = np.delete(frame, 0, axis=1)
        # Delete the first element in the genes list: (should be 'genes' but was a
        # duplicate gene name, due to a putative bug in genfromtxt
        genes = genes[1:]

        group = json.load(group_handle)

        return cls(
            counts=counts,
            genes=genes,
            samples=samples,
            groups_in_dict=group,
            to_remove_zeroes=False,
        )
