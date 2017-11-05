/*
 *  p4vasp is a GUI-program and library for processing outputs of the
 *  Vienna Ab-inition Simulation Package (VASP)
 *  (see http://cms.mpi.univie.ac.at/vasp/Welcome.html)
 *  
 *  Copyright (C) 2003  Orest Dubay <odubay@users.sourceforge.net>
 *
 *  This program is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; either version 2 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *   You should have received a copy of the GNU General Public License
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */

#ifndef Exceptions_h
#define Exceptions_h
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <new>
#include "ClassInterface.h"

#ifndef NO_THROW

#include <exception>
#include <stdexcept>

using namespace std;
///General exception
class Exception: public exception {
  char buff[256];
  ClassInterface *place;
  public:
#ifndef SWIG
  Exception();
  Exception(ClassInterface *c,const char *s);
#endif
  Exception(const char *s);
  virtual const char *what();
};

///Thrown when a NULL pointer if found where a valid pointer should be.
class NullPointerException: public Exception{
  char buff[256];
  ClassInterface *place;
  public:
#ifndef SWIG
  NullPointerException();
  NullPointerException(ClassInterface *c,const char *s);
#endif
  NullPointerException(const char *s);
  virtual const char *what();
};

///Thrown when memory allocation failed.
class MemoryAllocationException: public bad_alloc{
  char buff[256];
  ClassInterface *place;
  public:
#ifndef SWIG
  MemoryAllocationException();
  MemoryAllocationException(ClassInterface *c,const char *s);
#endif
  MemoryAllocationException(const char *s);
  virtual const char *what();
};

///Thrown when index exceeds valid range
class RangeException: public out_of_range{
  char buff[256];
  ClassInterface *place;
  public:
  long min,max,value;
#ifndef SWIG
  RangeException();
  RangeException(ClassInterface *c,const char *s,long min,long max,long value);
#endif
  RangeException(const char *s);
  virtual const char *what();
};

#endif

#ifndef SWIG
#  ifdef NO_THROW
#    define THROW_EXC(x)     fprintf(stderr,"Exception in class %s.\n%s\n",\
                             getClassName(),x);\
			     exit(-1);
#    define THROW_NP_EXC(x)  fprintf(stderr,"Null pointer exception in class %s:\n",\
                             getClassName());\
			     fprintf(stderr,"%s\n",x);\
			     exit(-1);             
#    define THROW_MA_EXC(x)  fprintf(stderr,"Memory allocation exception in class %s:\n",\
                             getClassName());\
			     fprintf(stderr,"%s\n",x);\
			     exit(-1);                          
#    define THROW_R_EXC(x,min,max,value) fprintf(stderr,"Range exception in class %s.\n",\
                             getClassName());\
			     fprintf(stderr,"Value %ld out of range[%ld,%ld]:\n",\
			     long(value),long(min),long(max));\
			     fprintf(stderr,"%s\n",x);\
			     exit(-1);              

#    define NTHROW_EXC(x)    fprintf(stderr,"Exception:\n%s\n",x);\
			     exit(-1);
#    define NTHROW_NP_EXC(x)  fprintf(stderr,"Null pointer exception:\n");\
			     fprintf(stderr,"%s\n",x);\
			     exit(-1);             
#    define NTHROW_MA_EXC(x)  fprintf(stderr,"Memory allocation exception:\n");\
			     fprintf(stderr,"%s\n",x);\
			     exit(-1);                          
#    define NTHROW_R_EXC(x,min,max,value) fprintf(stderr,"Range exception:\n");\
			     fprintf(stderr,"Value %ld out of range[%ld,%ld]:\n",\
			     long(value),long(min),long(max));\
			     fprintf(stderr,"%s\n",x);\
			     exit(-1);              
#  else
#    define THROW_EXC(x)                  throw Exception(this,x)
#    define THROW_NP_EXC(x)               throw NullPointerException(this,x)
#    define THROW_MA_EXC(x)               throw MemoryAllocationException(this,x)
#    define THROW_R_EXC(x,min,max,value)  throw RangeException(this,x,min,max,value)

#    define NTHROW_EXC(x)                  throw Exception(NULL,x)
#    define NTHROW_NP_EXC(x)               throw NullPointerException(NULL,x)
#    define NTHROW_MA_EXC(x)               throw MemoryAllocationException(NULL,x)
#    define NTHROW_R_EXC(x,min,max,value)  throw RangeException(NULL,x,min,max,value)
#  endif
#endif

#endif
