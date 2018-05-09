# edgePy

edgePy is a python-based implementation of edgeR for differential expression analysis. It has advantages over edgeR in that in uses unit tests and performs faster. edgePy maintains the functionality of edgeR in that it performs differential expression analysis of RNA-Seq expression profiels with biological replication. The statistical methods for negative binomial distributions include empirical Bayes estimations, exact tests, generalized linear models, and quasi-likelihood tests. 

## Outline

edgePy uses a general outline of importing data counts data from genomics analyses, normalization with respect to conditions, generalized linear models, and visualization.

## Input

Input should be given in a tab-delimited matrix of GeneID, SampleID, and counts.

Sample data can be found in the data folder, which was derived from data on the NCBI Gene Expression Ombnibus (https://www.ncbi.nlm.nih.gov/geo/)

## To-do list

There is a list of Bioconductor libraries here: http://bioconductor.org/packages/3.6/bioc/ The libraries will need to be written in python.

limma and edgeR need to be ported. The dependency graphs for those libraries should be used as well. 

