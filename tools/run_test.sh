#!/bin/bash

set -e -o pipefail

echo [mypy] Type checking ...
mypy leetcode

echo [pylint] Checking coding style ...

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

PYTHONPATH="${DIR}/../third_party:${DIR}/../third_party/3.6-only:${PYTHONPATH}"

# We only want to set PYTHONPATH for pylint, because it will try to load the
# third party modules but it cannot find them if we don't set PYTHONPATH.
PYTHONPATH="${PYTHONPATH}" pylint leetcode

echo [unittest] Running unit tests ...
coverage run -m unittest -v -k leetcode.test

echo [coverage] Reporting coverage ...
coverage report || (echo Under minimum required coverage && false)
