#!/usr/bin/env sh

this="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

nosetests \
  --verbosity=2 \
  --ignore-files '^\.'\
  --ignore-files '^setup\.py$' \
  --with-doctest \
  --with-coverage \
  --cover-package=edgePy \
  --where "${this}"/..
