#!/usr/bin/env bash

this="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

pylint --errors-only --output-format=colorized "${this}"/../edgePy
