LIBS=  -L../odpdom -lODP `python2 fltk-config.py --use-gl --ldstaticflags` -lpthread
CFLAGS?= -g -Wall
CFLAGS+= -fpic $(FLAGS) `python2 fltk-config.py --cxxflags` -I$(PYINCLUDE) \
        -Iinclude -I../odpdom/include
PYINCLUDE=`python2 -c "import sys;import os.path;print os.path.join(sys.prefix,\"include\",\"python\"+sys.version[:3])"`
LDFLAGS+= -shared -L.
