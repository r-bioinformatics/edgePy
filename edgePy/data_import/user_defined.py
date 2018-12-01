import numpy as np

class CustomDataStore(object):
    """
    A data structure allowing user-defined gene data; analogous to CanonicalDataStore generated from Ensembl data.

    Args:
        genes: list of gene names
        transcripts: list of transcript names
        lengths: length of transcripts
        canonical: defines whether transcript is canonical or not
        symbols: list of gene symbols
    """

    def __init__(
        self,
        genes: Optional[np.array] = None,
        transcripts: Optional[np.ndarray] = None,
        lengths: Optional[np.ndarray] = None,
        canonical: Optional[np.ndarray] = None,
        symbols: Optional[np.ndarray] = None
    ) -> None:

        if genes or transcripts or lengths or symbols is None:
            raise Exception("All DataStore components must be provided at init")
        else:
            if genes.size != transcripts.size:
                raise Exception("Gene array and transcript array are not the same size")
            if genes.size != lengths.size:
                raise Exception("Gene array and length array are not the same size")
            if genes.size != symbols.size:
                raise Exception("Gene array and symbol array are not the same size")
            if canonical is None:
                for i in genes:
                    canonical[i] = True
                log.info(f"No canonical status input. All input lengths assumed to be canonical.")

            self.genes = genes
            self.transcripts = transcripts
            self.lengths = lengths
            self.canonical = canonical
            self.symbols = symbols

    @classmethod
    def create_CustomDataStore(
            cls,
            gene_list: List[str],
            transcript_list: List[str],
            length_list: List[int],
            is_canonical: List[bool],
            symbols_list: List[str]
    ) -> "CustomDataStore" :
        """
        Creates a CustomDataStore for use with DGElist operations. Alternative for data lacking Ensembl files.
        """

        log.info(f"Creating CustomDataStore object using user-defined data")