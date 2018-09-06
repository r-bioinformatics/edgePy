

import pyensembl  # type: ignore


from typing import List, Optional


class EnsemblResrouce:
    def __init__(self, release: int = 93) -> None:
        self.ensembl = pyensembl.EnsemblRelease(release=release)
        self.gene_ids = self.ensembl.gene_ids()
        self.genes: Optional[List] = None
        self.coding_genes: Optional[List] = None

    def get_gene_ids(self) -> List:
        if not self.genes:
            self.genes = [self.ensembl.gene_by_id(gene_id) for gene_id in self.gene_ids]
        return self.genes

    def get_coding_genes(self) -> List:
        if not self.coding_genes:
            self.coding_genes = [
                gene for gene in self.get_gene_ids() if gene.biotype == 'protein_coding'
            ]
        return self.coding_genes
