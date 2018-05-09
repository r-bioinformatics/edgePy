# edgePy

edgePy is a python-based implementation of edgeR for differential expression analysis. It has advantages over edgeR in that in uses unit tests, is open-sourced, and performs faster. edgePy maintains the functionality of edgeR in that it performs differential expression analysis of RNA-Seq expression profiels with biological replication. The statistical methods for negative binomial distributions include empirical Bayes estimations, exact tests, generalized linear models, and quasi-likelihood tests. 

## Outline

edgePy uses a general outline of importing data counts data from genomics analyses, normalizaiton with respect to conditions, generalized linear models, and visualization.

## Input

Input should be given in a tab-delimited matrix of GeneID, SampleID, and counts.

Sample matrix:
GeneID SampleID counts
1 2 10
2 3 20

