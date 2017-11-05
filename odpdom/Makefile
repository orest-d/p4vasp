CPP     = g++
LD      = g++
LIBS    =
LDFLAGS += -shared -L.
FLAGS   = -DPY_DOMEXC_MODULE="\"xml.dom.\""
          -DCHECK=5 \
          -DVERBOSE=5 \

#          -DNO_POS_CACHE
#	  -DNO_THROW

PYINCLUDE=`python -c "import sys;import os.path;print os.path.join(sys.prefix,\"include\",\"python\"+sys.version[:3])"`
CFLAGS  += -fpic -g $(FLAGS) -I$(PYINCLUDE)  -Iinclude

SWIGFLAGS = -python -c++ $(FLAGS)

OBJECTS = string.o \
          markText.o \
	  Exceptions.o \
	  Node.o \
	  NodeSequences.o \
	  Document.o \
	  CharacterNodes.o \
	  Element.o \
	  parse.o

#SWIG = ../../SWIG-1.3.16/swig -I../../SWIG-1.3.16/Lib -I../../SWIG-1.3.16/Lib/python 
SWIG = swig

all: _cODP.so

cODP_wrap.cpp: include/ODP/NodeSequences.h      \
               include/ODP/CharacterNodes.h     \
	       include/ODP/Element.h include/ODP/Node.h \
	       include/ODP/Document.h           \
	       include/ODP/parse.h              \
	       ODP.i
	$(SWIG) $(SWIGFLAGS) -o cODP_wrap.cpp ODP.i

_cODP.so : libODP.a cODP_wrap.o
	$(LD) $(LDFLAGS) -o _cODP.so cODP_wrap.o -lODP $(LIBS)

libODP.a: $(OBJECTS)
	ar -r libODP.a $(OBJECTS)
	ranlib libODP.a
%.o:%.cpp
	$(CPP) $(CFLAGS) -c $< -o $@

cleanwrap:
	-rm cODP_wrap.cpp
clean:
	-rm *.o
	
cleanall:clean
	-rm *.so
	-rm *.a
