#!/bin/bash

set -x
set -e

py.test -v -s -m "not manual"
