#!/bin/bash

set -x
set -e

scriptdir="$(dirname $0)"

# NOTE: it is not uncommon for pip to hang on travis for what seems to be
# networking issues. Thus, let's retry a few times to see if it will eventually
# work or not.
$scriptdir/retry.sh pip install --upgrade pip setuptools wheel
$scriptdir/retry.sh pip install .[tests]

git config --global user.email "dvctester@example.com"
git config --global user.name "DVC Tester"
