from smart_open import smart_open  # type: ignore
from typing import Optional, Union, Dict, Hashable, Any, List
from pathlib import Path


class ImportCanonicalData(object):
    """
    A simple tool for reading canonical data, generated from the canonical_transcripts.py script provided with edgePy.

    Args:
        transcript_filename: the name of the transcript file, generated by canonical_transcripts.py
        symbols_filename: the name of the gene symbol file, generated by canonical_transcripts.py

    """

    def __init__(
        self, transcript_filename: Union[str, Path], symbols_filename: Union[str, Path]
    ) -> None:

        self.by_transcript: Dict[Hashable, Dict[Hashable, Any]] = {}
        self.canonical_transcript: Dict[Hashable, str] = {}

        self.gene_to_symbol: Dict[Hashable, str] = {}
        self.symbol_to_genes: Dict[Hashable, List] = {}

        with smart_open(transcript_filename, 'r') as data:
            for line in data:
                gene_info = line.strip().split("\t")
                gene = gene_info[0]
                transcript = gene_info[1]
                length = int(gene_info[2])
                canonical = True if gene_info[3] == "True" else False

                self.by_transcript[transcript] = {'len': length, 'can': canonical}

                if canonical:
                    self.canonical_transcript[gene] = transcript

        with smart_open(symbols_filename, 'r') as data:
            for line in data:
                symbol_info = line.strip().split("\t")
                symbol = symbol_info[0]
                gene = symbol_info[1]

                if gene not in self.gene_to_symbol:
                    self.gene_to_symbol[gene] = symbol

                if symbol not in self.symbol_to_genes:
                    self.symbol_to_genes[symbol] = []
                if gene not in self.symbol_to_genes[symbol]:
                    self.symbol_to_genes[symbol].append(gene)

    def has_gene(self, gene: Optional[str]) -> bool:
        if gene and gene in self.canonical_transcript:
            return True
        else:
            return False

    def get_symbol_from_gene(self, gene: Optional[str]) -> Optional[str]:
        if not gene:
            return None
        try:
            return self.gene_to_symbol[gene]
        except KeyError as ke:
            print(f"gene {gene} not found in gene to symbol.")
            raise ke

    def get_genes_from_symbol(self, symbol: str) -> List:
        try:
            return self.symbol_to_genes[symbol]
        except KeyError as ke:
            print(f"symbol {symbol} not found in gene to symbol.")
            raise ke

    @staticmethod
    def pick_gene_id(gene_ids: List) -> Optional[str]:
        if not gene_ids:
            return None
        length = len(gene_ids)
        if length == 1:
            return gene_ids[0]
        else:
            ids = [int(gene[4:]) for gene in gene_ids]
            max_id = max(ids)
            return f"ENSG{max_id}"

    def is_known_symbol(self, symbol: str) -> bool:
        if symbol in self.symbol_to_genes:
            return True
        return False

    def is_known_gene(self, gene: str) -> bool:
        if gene in self.gene_to_symbol:
            return True
        return False

    def is_canonical_by_transcript(self, transcript_id: str) -> bool:
        """
        Return a boolean indicating whether the supplied transcript is canonical or not.

        Args:
            transcript_id: an Ensembl transcript ID, starting with ENST
        """

        if transcript_id not in self.by_transcript:
            return False
        else:
            return self.by_transcript[transcript_id]['can']

    def get_canonical_transcript(self, gene_id: str) -> Optional[str]:
        """
        Return the Ensembl canonical transcript ID, given an ensembl transcript ID.

        Args:
            gene_id: An Ensembl gene ID, starting with ENSG
        """

        if gene_id in self.canonical_transcript:
            return self.canonical_transcript[gene_id]
        else:
            return None

    def get_length_of_transcript(self, transcript_id: str) -> int:
        """
        Return the length of a transcript, given an ensembl transcript ID.

        Args:
             transcript_id: an Ensembl transcript ID, starting with ENST
        """
        if transcript_id not in self.by_transcript:
            return False
        else:
            return self.by_transcript[transcript_id]['len']

    def get_length_of_canonical_transcript(self, gene_id: Optional[str]) -> int:
        """
        Return the length of a transcript, given an ensembl gene ID.

        Args:
             gene_id: An Ensembl gene ID, starting with ENSG
        """
        if not gene_id:
            return 0

        transcript_id = self.get_canonical_transcript(gene_id)

        if not transcript_id or transcript_id not in self.by_transcript:
            return False
        else:
            return self.by_transcript[transcript_id]['len']
