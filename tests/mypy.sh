#!/usr/bin/env bash

this="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

mypy \
  --python-version 3.6 \
  --strict-optional \
  --follow-imports=skip \
  --warn-unused-ignores \
  --warn-redundant-casts \
  --disallow-untyped-defs \
  --disallow-untyped-calls \
  "${this}"/../src
