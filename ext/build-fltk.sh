#!/usr/bin/sh

EXT=$PWD
export CFLAGS=-fPIC
export CXXFLAGS=-fPIC
cd fltk-1.3.0
./configure --enable-gl --prefix $EXT
make
make install
make clean
cd ..

