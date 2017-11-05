#!/bin/bash

cd ..
make appletlist
export PYTHONPATH=$PWD/lib:$PWD/src
cd -
python test.py
