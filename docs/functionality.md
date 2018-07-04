# Functionality

OMICs analysis is made easy with R tools such as “edgeR” and “limma” packages. R has serious limitations when applied to large datasets. 

The First objective of edgePY is to offer an alternative free tool for such analysis.

# Components

    Input(1) -> Normalization(2) -> Analysis(3) -> Visualization/Results(4).

## Input 
 
    Read correctly the file -> Set the groups based on the samples

A data matrix separated by tab. Of genes/proteins in lines and samples/observations in columns. Groups for the main analysis usually are defined there, or assigned to the samples.

## Normalization

    Quality ->  Library -> (TMM or RLE or upperquartile or none) -> Norm. Matrix

## Analysis

    Norm. Matrix -> ebayes (Prob. Stats) -> treat Function ( ) -> commonDispersion -> DE genes list 

## Visualization/Results

    DE genes list -> Heatmap / Volcano plot / Dispersion / Statistics / pvalue 


More details should be added as we progress in the coding.
