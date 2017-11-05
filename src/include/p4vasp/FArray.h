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

#ifndef FArray_h
#define FArray_h
#include "ClassInterface.h"
#include "Exceptions.h"
#include <stdio.h>
#include <string.h>

class FArray1D: public ClassInterface{
  protected:
  double *d;
  long _size;
  public:
  
#ifndef SWIG
  FArray1D(FArray1D &f){
    _size=f._size;
    if (_size){
      d=new double[_size];
      memcpy(d,f.d,_size*sizeof(double));
    }
    else{
      d=NULL;
    }  
  }
#endif

  FArray1D(long size=0){
    _size=size;
    if (size){
      d=new double[size];
    }
    else{
      d=NULL;
    }
  }
  void clear();
  long size(){return _size;}
  double get(long i);
  void set(long i,double x);
  void printrepr();
#ifndef SWIG
  void parseStringDestructively(char *s);
#endif
  void parseString(const char *s){
    char *b=strdup(s);
    parseStringDestructively(b);
    free(b);
  }

  double *cloneBuff(){
    double *b=new double[_size];
    memcpy(b,d,sizeof(double)*_size);
    return b;
  }
  FArray1D *clone(){
    return new FArray1D(*this);
  }  
  double getMinimum();
  double getMaximum();
  double getAverage();
  double getVariance();
  double getSigma();
  
  virtual const char *getClassName();
  virtual ~FArray1D();
};

#ifndef SWIG
class FArray1DWrap: public FArray1D{
  public:
  FArray1DWrap(double *dd,long size){
    _size=size;
    if (size){
      d=dd;
    }
    else{
      d=NULL;
    }
  }
  virtual const char *getClassName();
  virtual ~FArray1DWrap();
};
#endif

class FArray2D: public ClassInterface{
  long sizex,sizey;
  double *d;
  public:  
#ifndef SWIG
  FArray2D(FArray2D &f){
    sizex=f.sizex;
    sizey=f.sizey;
    long size=sizex*sizey;
    if (size){
      d=new double[size];
      memcpy(d,f.d,size*sizeof(double));
    }
    else{
      d=NULL;
    }
  }
#endif

  FArray2D(long sizex=0,long sizey=0){
    this->sizex=sizex;
    this->sizey=sizey;
    long size=sizex*sizey;
    if (size){
      d=new double[size];
    }
    else{
      d=NULL;
    }
  }  
  double getMinimum();
  double getMaximum();
  double getAverage();
  double getVariance();
  double getSigma();

  long sizeX(){return sizex;}
  long sizeY(){return sizey;}
  void clear();
  double get(long i,long j);
  void set(long i,long j,double x);
  void printrepr();
#ifndef SWIG
  void parseStringDestructively(long i,char *s);
#endif
  void parseString(long i,const char *s){
    char *b=strdup(s);
    parseStringDestructively(i,b);
    free(b);
  }
  FArray1D *getArray(long i);
  double *cloneBuff(){
    double *b=new double[sizex*sizey];
    memcpy(b,d,sizeof(double)*sizex*sizey);
    return b;
  }
  FArray2D *clone(){
    return new FArray2D(*this);
  }
  FArray2D *cubicInterpolation(int n,int m);
  FArray2D *smear(double sigma,int n,int m,double *u,double *v);
  
  double *cloneVector(long i);
  virtual const char *getClassName();
  virtual ~FArray2D();
};

#endif
