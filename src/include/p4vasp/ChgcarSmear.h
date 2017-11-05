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

#ifndef ChgcarSmear_h
#define ChgcarSmear_h

#ifndef SWIG
#include <errno.h>
#include <string.h>
#include <math.h>
#endif

#include <p4vasp/Process.h>
#include <p4vasp/Chgcar.h>
#include <p4vasp/Structure.h>
#include <p4vasp/Exceptions.h>

class Chgcar;

class ChgcarSmear: public ClassInterface{
  friend class Chgcar;
  protected:
  Chgcar *chgcar;
  public:
  ChgcarSmear(){chgcar=NULL;}
  virtual const char *getClassName();
  virtual void setChgcar(Chgcar *c);
  virtual double get(int i,int j, int k);
  virtual ~ChgcarSmear();
};

class GaussianChgcarSmear: public ChgcarSmear{
  friend class Chgcar;
  protected:
  double *w;
  Chgcar *chgcar;
  public:
  int lx,ly,lz,dir;
  double horizontal_sigma,vertical_sigma;
  
  GaussianChgcarSmear(){
    chgcar=NULL;
    lx=2;
    ly=2;
    lz=2;
    horizontal_sigma=0.5;
    vertical_sigma=0.5;
    dir=2;
    w=NULL;
  }
  virtual const char *getClassName();
  virtual void setChgcar(Chgcar *c);
  virtual double get(int i,int j, int k);
  virtual ~GaussianChgcarSmear();
};

class ChgcarSmearProcess:public Process{
  Chgcar *chgcar,*smeared;
  ChgcarSmear *smear;
  int pstep;
  public:
  ChgcarSmearProcess(Chgcar *c,ChgcarSmear *s,int pstep=10);
  virtual long next();
  Chgcar *get();
  virtual const char *getClassName();
  virtual ~ChgcarSmearProcess();
};

class ChgcarSmearPlaneProcess:public Process{
  protected:
  Chgcar *chgcar;
  ChgcarSmear *smear;  
  FArray2D *plane;
  int n,dir,pstep;
  public:
  ChgcarSmearPlaneProcess(Chgcar *c,ChgcarSmear *s,int nplane,int dir,int pstep=10){
    chgcar=c;
    smear=s;
    this->pstep=pstep;
    s->setChgcar(c);
    this->n=nplane;
    this->dir=dir;    
    switch(dir){
      case 0:
        plane=new FArray2D(c->ny,c->nz);
        _total=c->ny*c->nz;
	break;
      case 1:
        plane=new FArray2D(c->nx,c->nz);
        _total=c->nx*c->nz;
	break;
      case 2:
      default:
        plane=new FArray2D(c->nx,c->ny);
        _total=c->nx*c->ny;
	break;
    }
    _step=0;
  }
  const char *planeName(){
    return planeName(dir);
  }
  const char *planeName(int i){
    switch(i){
      case 0:
        return "YZ";
      case 1:
        return "XZ";
      case 2:
        return "XY";
      default:
        return "?";
    }
  }
  public:
  virtual long next();
  virtual ~ChgcarSmearPlaneProcess();
  virtual const char *getClassName();
  FArray2D *getPlane();
};

class STMSearchProcess:public Process{
  ChgcarSmear *smear;  
  Chgcar *chgcar;
  FArray2D *plane;
  int N,M,Nz,dir;
  double Z;
  bool order(double x1,double x2,double x3){
    if ((x1>=0) && (x1<=1)){
      return true;
    /*
      if (delta<=0){
	return ((x1>=x2) && (x1>=x3));
      }
      else{
	return ((x1<=x2) && (x1<=x3));
      }*/
    }
    return false;
  }
  
  public:
  int mode,pstep,delta,n0;
  bool autoplane;
  double value;
  STMSearchProcess(Chgcar *c,double val,ChgcarSmear *s=NULL,int n0=-1,int dir=2,int
  delta=-1,int pstep=10,int mode=0);
  
  void update();
  int getDir(){return dir;}
  void setDir(int d){dir=d; update();}
  void setChgcar(Chgcar *c){
    chgcar=c;
    update();
  }
  void setSmear(ChgcarSmear *s){
    smear=s;
    if (smear!=NULL){
      if (chgcar!=NULL){
        smear->setChgcar(chgcar);
      }
    }
  }
  int searchFast(int I,int J);
  int searchSlow(int I,int J);
  double getHeightFast(int I,int J);
  double getHeightSlow(int I,int J);
  double getHeightFastCubic(int I,int J);
  double getHeightSlowCubic(int I,int J);
  virtual const char *getClassName();
  virtual ~STMSearchProcess();
  virtual long next();  
  virtual int processAll();
  FArray2D *getPlane();
};

#endif

