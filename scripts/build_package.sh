#!/bin/bash

set -e
set -x

if [ ! -d "pydrive" ]; then
    echo "Please run this script from repository root"
    exit 1
fi

python setup.py sdist
python setup.py bdist_wheel --universal
