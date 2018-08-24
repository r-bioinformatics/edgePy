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


# TO-DO
* Significant DEG list 
    * Filtered using p value or FDR? 
    * Log fold change?
    * Or both 
*Versions 
    *R 
    *edgeR
    *R session info - better
* Compute resources 
    * output of `memory.profile()`
    * system information 
    * cores, cpu etc. 



