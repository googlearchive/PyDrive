#!/bin/bash

set -x
set -e

scriptdir="$(dirname $0)"

if [[ "$TRAVIS_OS_NAME" == "osx" ]]; then
    ulimit -a
    sudo sysctl -w kern.maxproc=2048
    sudo sysctl -w kern.maxprocperuid=2048
    echo '\nulimit -u 2048' >> ~/.bash_profile
    ulimit -a
fi

echo > env.sh
if [[ "$TRAVIS_OS_NAME" == "windows" ]]; then
    $scriptdir/retry.sh choco install python --version 3.7.5
    echo 'PATH="/c/Python37:/c/Python37/Scripts:$PATH"' >> env.sh
elif [[ "$TRAVIS_OS_NAME" == "osx" ]]; then
    ln -s -f /usr/local/bin/python3 /usr/local/bin/python
    ln -s -f /usr/local/bin/pip3 /usr/local/bin/pip
fi
