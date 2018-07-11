#!/usr/bin/env bash

this="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

py.test \
  "${this}" \
  --verbose \
  --doctest-modules \
  --cov="${this}"/../edgePy
