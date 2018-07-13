#!/usr/bin/env bash

this="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

flake8 --ignore=E501,F401,F403 "${this}"/../edgePy
