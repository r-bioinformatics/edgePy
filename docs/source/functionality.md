# Functionality

OMICs analysis is made easy with R tools such as “edgeR” and “limma” packages. R has serious limitations when applied to large datasets. 

The First objective of edgePY is to offer an alternative free tool for such analysis.

# Components

    Input(1) -> Normalization(2) -> Analysis(3) -> Visualization/Results(4).

## Input 
 
    Read correctly the file 

A data matrix separated by tab. Of genes/proteins in lines and samples/observations in columns. Groups for the main analysis usually are defined there, or assigned to the samples.

## Normalization

    Quality ->  Library -> (TMM or RLE or upperquartile or none) -> commonDispersion -> TagwiseDispersion -> Norm. Matrix

## Analysis

    Norm. Matrix -> Set the sample groups to be compared  -> Statistical analysis of choice (ebayes/treat/QLF) -> DE genes list and statistics

## Visualization/Results

    DE genes list / Statistics -> Visualization ( Venn / The mean-variance relationship of log-CPM / Heatmaps / Volcano plots / Dispersion plots 


More details should be added as we progress in the coding.
