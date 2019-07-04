#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

PYTHONPATH="${DIR}/../third_party:${DIR}/../third_party/3.6-only:${PYTHONPATH}"

# We only want to set PYTHONPATH for pylint, because it will try to load the
# third party modules but it cannot find them if we don't set PYTHONPATH.
PYTHONPATH="${PYTHONPATH}" pylint leetcode
