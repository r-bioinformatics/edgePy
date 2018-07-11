# edgePy

[![Build Status](https://travis-ci.org/r-bioinformatics/edgePy.svg?branch=master)](https://travis-ci.org/r-bioinformatics/edgePy)
[![codecov](https://codecov.io/gh/r-bioinformatics/edgePy/branch/master/graph/badge.svg)](https://codecov.io/gh/r-bioinformatics/edgePy)
[![PyPI Version](https://badge.fury.io/py/edgePy.svg)](https://pypi.org/project/edgePy)
[![GitHub License](https://img.shields.io/github/license/mashape/apistatus.svg)](https://github.com/r bioinformatics/edgePy/blob/master/LICENSE)

The `edgePy` library will become an implementation of [`edgeR`](https://bioconductor.org/packages/release/bioc/html/edgeR.html) for differential expression analysis in the Python language.
This library will have advantages over [`edgeR`](https://bioconductor.org/packages/release/bioc/html/edgeR.html) in that it will be well-tested and will run faster by utilizing Cythonized routines.
`edgePy` will maintain the functionality of [`edgeR`](https://bioconductor.org/packages/release/bioc/html/edgeR.html) in that it's primary goals are differential expression analysis of RNA-Seq expression profiles with biological replication.
The statistical methods for negative binomial distributions will include empirical Bayes estimations, exact tests, generalized linear models, and quasi-likelihood tests. 

## Project Aims

The `edgePy` library will be used for data import, normalization with respect to conditions, application of generalized linear models, and visualization.
