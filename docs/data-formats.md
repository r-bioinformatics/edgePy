## Input

Input should be given in tab-delimited format with the following header column names:

- `FeatureID` (Can be gene, transcript, splice variant or protein)
- `SampleID` (Generic label to keep track of an individual sample)

Input main content:

- `Data Matrix` A numeric matrix (Previously `counts`).
A numeric matrix. Each row represents a single feature and each column represent a single sample.

Sample data can be found in the [`data/`](../_src/data/) folder, which was derived from data on the [NCBI Gene Expression Ombnibus](https://www.ncbi.nlm.nih.gov/geo/).
