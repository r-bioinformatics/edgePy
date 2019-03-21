import re
import json
from io import StringIO
from pathlib import Path
from typing import Generator, Iterable, Mapping, Optional, Union, Dict, List, Hashable, Any

# TODO: Implement `mypy` stubs for NumPy imports
import numpy as np  # type: ignore
from smart_open import smart_open  # type: ignore

from logging import getLogger
from edgePy.data_import.ensembl.ensembl_flat_file_reader import CanonicalDataStore

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
        groups_in_list: a list of groups to which each sample belongs, in the same order as samples *or*
        groups_in_dict: a dictionary of groups, containing sample names.
        to_remove_zeroes: To remove genes with zero counts for all samples.
        filename: a shortcut to import NPZ (zipped numpy format) files.
        current_type:  None means raw counts, otherwise, if transformed, store a string (eg. 'cpm', 'rpkm', etc)
        current_log: Optional[bool] = False,  If counts has already been log transformed, store True.
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
        current_transform_type: Optional[str] = None,
        current_log_status: Optional[bool] = False,
    ) -> None:

        self.to_remove_zeroes = to_remove_zeroes
        self.current_data_format = current_transform_type
        self.current_log_status = current_log_status

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

            if groups_in_dict is not None and groups_in_list is not None:
                self.groups_dict = groups_in_dict
                self.groups_list = groups_in_list
            elif groups_in_dict is not None and self.samples is not None:
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

    def copy(
        self,
        counts: Optional[np.ndarray] = None,
        samples: Optional[np.array] = None,
        genes: Optional[np.array] = None,
        norm_factors: Optional[np.array] = None,
        groups_in_list: Optional[np.array] = None,
        groups_in_dict: Optional[Dict] = None,
        to_remove_zeroes: Optional[bool] = False,
        current_type: Optional[str] = None,
        current_log: Optional[bool] = False,
    ) -> "DGEList":

        return DGEList(
            counts=self.counts if counts is None else counts,
            samples=self.samples if samples is None else samples,
            genes=self.genes if genes is None else genes,
            norm_factors=self.norm_factors if norm_factors is None else norm_factors,
            groups_in_list=self.groups_dict if groups_in_dict is None else groups_in_dict,
            groups_in_dict=self.groups_list if groups_in_list is None else groups_in_list,
            to_remove_zeroes=self.to_remove_zeroes
            if to_remove_zeroes is None
            else to_remove_zeroes,
            current_transform_type=self.current_data_format
            if current_type is None
            else current_type,
            current_log_status=self.current_log_status if current_log is None else current_log,
        )

    @staticmethod
    def _sample_group_dict(groups_list: List[str], samples: np.array):
        """
        Converts data in the form ['group1', 'group1', 'group2', 'group2']
        to the form  {'group1': ['sample1', 'sample2'], 'group2': ['sample3', 'sample4'}

        Args:
            groups_list: group names in a list, in the same order as samples.

        Returns:
            dictionary containing the sample types, each with a list of samples.

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

        Args:
            groups_dict: dictionary containing the sample types, each with a list of samples.
            samples: order of samples in the DGEList

        Returns:
            data in a list, in the same order as samples.

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
                log.info(f"sample count: {sample_count}, gene count: {gene_count}")
                log.info(
                    f"samples shape {self.samples.shape[0]}, gene shape {self.genes.shape[0]}"
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
        if not self.current_log_status and (counts < 0).any():
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
            metatag_mask = ~(np.isin(genes, self._old_metatags) | np.char.startswith(genes, '__'))
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

    def log_transform(self, counts, prior_count):
        """Compute the log of the counts"""
        counts[counts == 0] = prior_count
        return np.log(counts)

    def cpm(self, transform_to_log: bool = False, prior_count: float = PRIOR_COUNT) -> "DGEList":
        """Normalize the DGEList to read counts per million."""
        counts = 1e6 * self.counts / np.sum(self.counts, axis=0)
        current_log = self.current_log_status
        if transform_to_log:
            counts = self.log_transform(counts, prior_count)
            current_log = True

        return self.copy(counts=counts, current_log=current_log)

    def rpkm(
        self,
        gene_data: CanonicalDataStore,
        transform_to_log: bool = False,
        prior_count: float = PRIOR_COUNT,
    ) -> "DGEList":
        """Return the DGEList normalized to reads per kilobase of gene length
        per million reads. (RPKM =   numReads / ( geneLength/1000 * totalNumReads/1,000,000 )

        Args:
            gene_data: An object that works to import Ensembl based data, for use in calculations
            transform_to_log: true, if you wish to convert to log after converting to RPKM
            prior_count: a minimum value for genes, if you do log transforms.
        """
        current_log = self.current_log_status

        if self.current_log_status:
            self.counts = np.exp(self.counts)
            current_log = False
        col_sum = np.sum(self.counts, axis=0)

        gene_len_ordered, gene_mask = self.get_gene_mask_and_lengths(gene_data)

        genes = self.genes[gene_mask].copy()
        counts = self.counts[gene_mask].copy()

        counts = (counts.T / gene_len_ordered).T
        counts = counts / (col_sum / 1e6)

        if transform_to_log:
            counts = self.log_transform(counts, prior_count)
            current_log = True

        return self.copy(counts=counts, current_log=current_log, genes=genes)

    def get_gene_mask_and_lengths(self, gene_data):

        """
        use gene_data to get the gene lenths and a gene mask for the tranformation.
        Args:
            gene_data: the object that holds gene data from ensembl

        """
        gene_len_ordered = []
        gene_mask = []
        gene_ensg = []
        for gene in self.genes:
            if gene.startswith("ENSG"):
                gene_name = gene
                gene_ensg.append(gene_name)
                if gene_data.has_gene(gene_name):
                    gene_mask.append(True)
                    gene_len_ordered.append(
                        gene_data.get_length_of_canonical_transcript(gene_name) / 1e3
                    )
                else:
                    gene_mask.append(False)
            else:
                t_gene = gene_data.get_genes_from_symbol(gene)
                if t_gene:
                    if len(t_gene) > 1:
                        gene_name = gene_data.pick_gene_id(t_gene)
                    else:
                        gene_name = t_gene[0]
                    gene_ensg.append(gene_name)
                    if gene_data.has_gene(gene_name):
                        gene_mask.append(True)
                        gene_len_ordered.append(
                            gene_data.get_length_of_canonical_transcript(gene_name) / 1e3
                        )
                    else:
                        gene_mask.append(False)
                else:
                    gene_mask.append(False)
        return gene_len_ordered, gene_mask

    def tpm(
        self,
        gene_lengths: np.ndarray,
        transform_to_log: bool = False,
        prior_count: float = PRIOR_COUNT,
        mean_fragment_lengths: np.ndarray = None,
    ) -> "DGEList":
        """Normalize the DGEList to transcripts per million.

        Adapted from Wagner, et al. 'Measurement of mRNA abundance using RNA-seq data:
        RPKM measure is inconsistent among samples.' doi:10.1007/s12064-012-0162-3

        Read counts :math:`X_i` (for each gene :math:`i` with gene length :math:`\widetilde{l_j}` )
        are normalized as follows:

        .. math::

           TPM_i = \\frac{X_i}{\\widetilde{l_i}}\cdot \\
           \\left(\\frac{1}{\sum_j \\frac{X_j}{\widetilde{l_j}}}\\right) \cdot 10^6

        Args:
            gene_lengths: 1D array of gene lengths for each gene in the rows of `DGEList.counts`.
            transform_to_log: store log outputs
            prior_count:
            mean_fragment_lengths: 1D array of mean fragment lengths for each sample in the columns of `DGEList.counts`
                (optional)

        """

        # compute effective length not allowing negative lengths
        if mean_fragment_lengths:
            effective_lengths = (
                gene_lengths[:, np.newaxis] - mean_fragment_lengths[np.newaxis, :]
            ).clip(min=1)
        else:
            effective_lengths = gene_lengths[:, np.newaxis]

        # how many counts per base
        base_counts = self.counts / effective_lengths

        counts = 1e6 * base_counts / np.sum(base_counts, axis=0)[np.newaxis, :]
        current_log = self.current_log_status
        if transform_to_log:
            counts = self.log_transform(counts, prior_count)
            current_log = True

        return self.copy(counts=counts, current_log=current_log)

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

        log.info(f"Exporting data to compressed .dge file ({filename}.npz)...")

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

        Args:
            filename: the name of the file to read from.

        """

        log.info(f"Importing data from .dge file ({filename})...")

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

        This function uses smart_open, which provides a broad list of data sources that can be
        opened.  For a full list of data sources, see smart_open's documentation at
        https://github.com/RaRe-Technologies/smart_open/blob/master/README.rst

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

        Args:get_canonical
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
