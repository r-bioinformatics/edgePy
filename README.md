# edgePy

### Notice:

This project is still in development.  While we are a small band of bioinformaticians with big goals and aspirations, this code base is still too new for use on any real world projects. 
While there's no official timeline for the project, functionality is being developed rapidly, so please feel free to check back on our progress frequently.  If you'd like to do more 
than just check on our progress, we're always happy to welcome new members of the community, both to slack group where we're organizing this project, as well as on the git hub repository 
hosting the project.  To join the slack, send your email to @apfejes (on github) or /u/apfejes on reddit - we're looking forward to working with you.  

[//]: # (TODO: Remove sample-sheet dummy library until we release on PyPi)
[![PyPI Version](https://badge.fury.io/py/edgePy.svg)](https://pypi.org/project/edgePy)
[![Build Status](https://travis-ci.org/r-bioinformatics/edgePy.svg?branch=master)](https://travis-ci.org/r-bioinformatics/edgePy)
[![Documentation Status](https://readthedocs.org/projects/edgepy/badge/?version=latest)](http://edgepy.readthedocs.io/en/latest/?badge=latest)
[![codecov](https://codecov.io/gh/r-bioinformatics/edgePy/branch/master/graph/badge.svg)](https://codecov.io/gh/r-bioinformatics/edgePy)
[![Checked with MyPy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![GitHub License](https://img.shields.io/pypi/l/sample-sheet.svg)](https://github.com/r-bioinformatics/edgePy/blob/master/LICENSE)

The `edgePy` library will become an implementation of [`edgeR`](https://bioconductor.org/packages/release/bioc/html/edgeR.html) for differential expression analysis in the Python language.
This library will have advantages over [`edgeR`](https://bioconductor.org/packages/release/bioc/html/edgeR.html) in that it will be well-tested and will run faster by utilizing Cythonized routines.
`edgePy` will maintain the functionality of [`edgeR`](https://bioconductor.org/packages/release/bioc/html/edgeR.html) in that it's primary goals are differential expression analysis of RNA-Seq expression profiles with biological replication.
The statistical methods for negative binomial distributions will include empirical Bayes estimations, exact tests, generalized linear models, and quasi-likelihood tests.

## Project Aims

The `edgePy` library will be used for data import, normalization with respect to conditions, application of generalized linear models, and visualization.
