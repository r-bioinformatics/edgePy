Analysis workflow for Bulk-RNAseq to compare the differentially expressed genes (DEGs) produced by edgeR and limma.
=====
### 1. Script with all R packages and command lines
GSE49712.Rscript.txt 

### 2. Data matrix extract from GEO
GSE49712_gene_FPKM.txt

### 3. Figure produced by filtering the dataset based on Zero count rows/genes
diagnostic_fig1.png
![01 diagnostic_fig1](https://user-images.githubusercontent.com/13422225/44564680-eeff3300-a729-11e8-9446-0e7643dbb651.png)

### 4. Normalization of data distribution with TMM
diagnostic_fig2.png
![02 diagnostic_fig2](https://user-images.githubusercontent.com/13422225/44564681-f58daa80-a729-11e8-9fb0-5fb64de760cd.png)

### 5. Multidimensional scaling for general sample comparison.
mds.png
![03 mds](https://user-images.githubusercontent.com/13422225/44564682-f9213180-a729-11e8-9afc-0271fe9cea34.png)

### 6. Variance dispersion comparison for unnormalized and normalized data based on dispersion and a linear model 
diagnostic_fig3.png
![04 diagnostic_fig3](https://user-images.githubusercontent.com/13422225/44564686-fe7e7c00-a729-11e8-95e7-f2db1ba53d69.png)

### 7. Venn with quantity of DEGs
diagnostic_fig4.png
![05 diagnostic_fig4](https://user-images.githubusercontent.com/13422225/44564694-076f4d80-a72a-11e8-8bba-424dd4421883.png)

### 8. Sample heatmap for topDEGs
heatmap_fig5.png
![06 heatmap_fig5](https://user-images.githubusercontent.com/13422225/44564698-0b9b6b00-a72a-11e8-8e5d-8fe72477a942.png)


### 9. DEG list for 7001 genes
    * Filtered using p-value < 0.05 

**TODO: show file 07.DEGs.tsv**

### 10. Top DEG list for 300 genes
    * Filtered using p value < 0.01, FDR < 0.05 and fold change of 2. 

**TODO: show file 08.topDEGs.tsv**

### Versions 
    *R version 3.2.3 (2015-12-10)
    *Platform: x86_64-pc-linux-gnu (64-bit) Running under: Ubuntu 16.04.2 LTS

### Packages

```
    [1] ggplot2_2.2.1   pheatmap_1.0.10 edgeR_3.12.1    limma_3.26.9   
    loaded via a namespace (and not attached):
    [1] colorspace_1.3-2   scales_0.5.0       lazyeval_0.2.1     plyr_1.8.4
    [5] pillar_1.2.1       gtable_0.2.0       RColorBrewer_1.1-2 tibble_1.4.2
    [9] Rcpp_0.12.15       grid_3.2.3         rlang_0.2.0        munsell_0.4.3 
```
 
 
 
### Compute resources 

```

    Cores 4; 8GB RAM; 500GB HD
    Processor: AMD Phenom(tm) II X4 B97 Processor × 4 
    Graphics: Gallium 0.4 on AMD RS880 (DRM 2.50.0 / 4.15.0-32-generic, LLVM **3.8.0)

```
### Computing

```
Running the script from cero, including packages loading time:
   user  system elapsed 
  1.213   0.136 167.807 
   user  system elapsed 
 12.951   0.366 180.962 
 RAM used: 850mB
 Cores used: 1
```


