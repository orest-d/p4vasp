-include Configuration.mk

CPP=g++
LD=g++
#CPP=icc
#LD=icc

FLAGS= -Wall -DPY_DOMEXC_MODULE="\"p4vasp.ODPdom.\"" \
       -DCHECK=1 \
       -DVERBOSE=0 \
       -DNO_GL_LISTS_S \
       -DNO_THREADS \

#       -DNO_THROW \
#       -DSIMPLE_EXCEPTION \
#       -DDRAWBUFFERHACK \
#       -DNO_GL_LISTS \
#       -DNO_GL_LISTS_S 
#       -DNO_THREADS \
       
SWIGFLAGS= -python -c++  $(FLAGS) -I../odpdom/include -Iinclude
      
SWIG = swig

OBJECTS= Exceptions.o \
	 AtomtypesRecord.o \
	 AtomInfo.o \
	 vecutils3d.o \
	 vecutils.o \
	 utils.o \
	 domutils.o \
	 FArray.o \
	 Structure.o \
	 Chgcar.o \
	 ChgcarSmear.o \
	 Process.o \
	 VisFLWindow.o \
	 VisMain.o \
	 VisWindow.o \
	 VisEvent.o \
	 VisDrawer.o \
	 VisNavDrawer.o \
	 VisStructureDrawer.o \
	 VisStructureArrowsDrawer.o \
	 VisIsosurfaceDrawer.o \
	 ClassInterface.o \
	 VisSlideDrawer.o \
	 VisPrimitiveDrawer.o \
	 VisBackEvent.o 



PYLIBOBJECTS = $(OBJECTS) cp4vasp_wrap.o
	 

all: _cp4vasp.so

%.o: %.cpp
	$(CPP) $(CFLAGS) -c $< -o $@
%.o: %.c 
	$(CPP) $(CFLAGS) -c $< -o $@
cp4vasp_wrap.cpp: cp4vasp.i
	$(SWIG) $(SWIGFLAGS) -o cp4vasp_wrap.cpp cp4vasp.i 
	
#_cp4vasp.so: $(PYLIBOBJECTS)
#	$(LD) $(LDFLAGS) -o _cp4vasp.so $(PYLIBOBJECTS) $(LIBS) 
_cp4vasp.so: libp4vasp.a cp4vasp_wrap.o
	$(LD) $(LDFLAGS) -o _cp4vasp.so cp4vasp_wrap.o -lp4vasp $(LIBS) 

testprog1: testprog1.o libp4vasp.a
	$(LD) -o testprog1 testprog1.o -lp4vasp.a $(LIBS)
testprog2: testprog2.o libp4vasp.a
	$(LD) -o testprog2 testprog2.o -lp4vasp $(LIBS)
viewer1: viewer1.o libp4vasp.a
	$(LD) -o viewer1 viewer1.o -L. -lp4vasp $(LIBS)
viewer2: viewer2.o libp4vasp.a
	$(LD) -o viewer2 viewer2.o -L. -lp4vasp $(LIBS) -ldl
viewer3: viewer3.o libp4vasp.a
	$(LD) -o viewer3 viewer3.o -L. -lp4vasp $(LIBS)
#testdombug: testdombug.o libp4vasp.a
#	$(LD) -o testdombug testdombug.o -L. -lp4vasp $(LIBS)
#viewer3: viewer3.o $(OBJECTS)
#	$(LD) -static -o viewer3 viewer3.o $(OBJECTS) $(LIBS) -ldl

libp4vasp.a: $(OBJECTS)
	ar -r libp4vasp.a $(OBJECTS)
	ranlib libp4vasp.a
doc:
	doxygen Doxyfile

cleanwrap:
	-rm *_wrap.cpp
	-rm *.py
	-rm *.pyc

clean:
	-rm *.o
cleanall: clean
	-rm *.so *.a
	-rm testprog*
	-rm viewer1
	-rm viewer2
	-rm *.tmp
	-rm *.pyc
	-rm *.pyo
	-rm *~
