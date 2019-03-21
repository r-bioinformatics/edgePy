
from typing import Dict, Hashable, Any

import numpy as np
from scipy.stats import ks_2samp
from statsmodels.stats.multitest import multipletests

from edgePy.DGEList import DGEList

AVAILABLE_CORRECTION = [
    'bonferroni',
    'sidak',
    'holm-sidak',
    'holm',
    'simes-hochberg',
    'hommel',
    'fdr_bh',
    'fdr_by',
    'fdr_tsbh',
    'fdr_tsbky',
]


def ks_2_samples(dge_list: DGEList, alpha=0.1, correction_method=None):
    """Run a 2-tailed Kolmogorov-Smirnov test on the DGEList object.

    Args:
        None.

    correction methods available:
        None: don't use one!
        bonferroni : one-step correction
        sidak : one-step correction
        holm-sidak : step down method using Sidak adjustments
        holm : step-down method using Bonferroni adjustments
        simes-hochberg : step-up method (independent)
        hommel : closed method based on Simes tests (non-negative)
        fdr_bh : Benjamini/Hochberg (non-negative)
        fdr_by : Benjamini/Yekutieli (negative)
        fdr_tsbh : two stage fdr correction (non-negative)
        fdr_tsbky : two stage fdr correction (non-negative)

    Returns:
        gene_details: a dictionary of dictionary (key, gene), holding mean1 and mean2 for the two groups
        gene_likelihood: a dictionary (key, gene), holding the p-value of the separation of the two groups
        group_types: list of the groups in order.

    """
    p_corrected = None

    gene_likelihood1: Dict[Hashable, float] = {}
    group_types = set(dge_list.groups_list)
    group_types = list(group_types)
    group_filters: Dict[Hashable, Any] = {}
    gene_details: Dict[Hashable, Dict[Hashable, Any]] = {}
    for group in group_types:
        group_filters[group] = [g == group for g in dge_list.groups_list]
    for gene_idx, gene in enumerate(dge_list.genes):
        gene_row = dge_list.counts[gene_idx]
        if len(group_types) == 2:
            group_data1 = gene_row.compress(group_filters[group_types[0]])
            mean1 = np.mean(group_data1)

            group_data2 = gene_row.compress(group_filters[group_types[1]])
            mean2 = np.mean(group_data2)

            gene_likelihood1[gene] = ks_2samp(group_data1, group_data2)[1]

            gene_details[gene] = {'mean1': mean1, 'mean2': mean2}

    if correction_method and correction_method in AVAILABLE_CORRECTION:
        p_vals = []
        p_corrected = {}
        for gene_name in dge_list.genes:
            p_vals.append(gene_likelihood1[gene_name])

        reject, pval_corrected, alpha_sidak, alpha_bonf = \
            multipletests(p_vals, alpha=alpha, method=correction_method, is_sorted=False, returnsorted=False)

        for gene_idx, gene_name in enumerate(dge_list.genes):
            p_corrected[gene_name] = pval_corrected[gene_idx]

    return gene_details, gene_likelihood1, group_types, p_corrected
