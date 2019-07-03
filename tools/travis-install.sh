#!/bin/bash

if [[ $TRAVIS_OS_NAME = 'osx' ]]; then
    echo not implemented
else
    pip install -r dev-requirements.txt
fi
