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

#ifndef Chgcar_h
#define Chgcar_h

#ifndef SWIG
#include <errno.h>
#include <string.h>
#include <math.h>
#endif

#include <p4vasp/Process.h>
#include <p4vasp/Structure.h>
#include <p4vasp/Exceptions.h>
#include <p4vasp/FArray.h>

class Chgcar;


class ReadChgcarProcess:public Process{
  protected:
  ReadChgcarProcess(Chgcar *c, FILE *f,bool closeflag=false);
  Chgcar *chgcar;
  FILE *file;
  bool closeflag;
  public:
  virtual long next();
  virtual ~ReadChgcarProcess();
  friend class Chgcar;
};

class ChgcarPlaneProcess:public Process{
  protected:
  ChgcarPlaneProcess(Chgcar *c,long n,int dir,double
sigmax, double sigmay,double sigmaz,double limit);
  Chgcar *chgcar;
  FArray2D *plane;
  double limit;
  double sx,sy,sz,*wx,*wy,*wz;
  long n,dx,dy,dz,dim;
  int dir;
  double factor(int i);
  double *createWeights(int d,double factor);
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
  virtual ~ChgcarPlaneProcess();
  friend class Chgcar;
  FArray2D *getPlane();
};

class Chgcar:public ClassInterface{
  friend class ReadChgcarProcess;
  friend class ChgcarPlaneProcess;
  friend class ChgcarSmearProcess;
  bool is_statistics;
  bool locked;
  double minimum,maximum,average,variance;
  long length;


  public:

#ifndef SWIG
  void lock(){locked=true;}
  void unlock(){locked=false;}
#endif
  double plane_minimum,plane_maximum,plane_average,plane_variance;
  virtual const char *getClassName();
  /// Pointer to a Structure from the Chgcar file.
  Structure *structure;
  /// Grid dimensions.
  long nx,ny,nz;
  float *data;

  Chgcar();
#ifndef SWIG
  Chgcar(FILE *f);
  Chgcar(char *path);
  int read(FILE *f);
  void checklock(char *msg=NULL){
#if CHECK>0  
    if (locked){
      if (msg!=NULL){
        char buff[255];
        sprintf(buff,"Chgcar locked in %s",msg);
        THROW_EXC(buff);
      }
      else{
        THROW_EXC("Chgcar locked");
      }
    }
#endif
  }

  ReadChgcarProcess *createReadProcess(FILE *f){
    checklock("createReadProcess(FILE)");
    return new ReadChgcarProcess(this,f);
  }
  int write(FILE *f);
#endif  
  virtual ~Chgcar();
  void subtractChgcar(Chgcar *c);
  void calculateStatistics();

  double getMinimum(){
    if (!is_statistics){
      calculateStatistics();
    }
    return minimum;
  }
  double getMaximum(){
    if (!is_statistics){
      calculateStatistics();
    }
    return maximum;
  }
  double getAverage(){
    if (!is_statistics){
      calculateStatistics();
    }
    return average;
  }
  double getVariance(){
    if (!is_statistics){
      calculateStatistics();
    }
    return variance;
  }
  double getSigma(){
    if (!is_statistics){
      calculateStatistics();
    }
    unsigned long N=nx*ny*nz;
    return sqrt(N*variance/(N-1));
  }
  
  void clean();

  int read(char *path);
  
  ReadChgcarProcess *createReadProcess(char *path){
    checklock("createReadProcess(path)");
    FILE *f=fopen(path,"r");
#if CHECK>0
    if (f==NULL){
      char s[256];
      snprintf(s,250,"Chgcar.createReadProcess('%s') open error.\n%s",path,strerror(errno));
      THROW_EXC(s);
    }
#endif
    return new ReadChgcarProcess(this,f,true);
  }

  int write(char *path);

  /**
   * Get the grid value at i,j,k.
   * If the index exceeds range (nx,ny,nz), it is folded back.
   */
  float get(int i,int j,int k);
  /**
   * Get the grid value at i,j,k.
   * If the index exceeds range (nx,ny,nz), the result is undetermined.
   */
  float getRaw(int i,int j,int k);
  void set(int i,int j,int k,float val);
  void setRaw(int i,int j,int k,float val);
  double *getDirGrad(double *dest,int i,int j, int k);
  double *getGrad(double *dest,int i,int j, int k);

  int downSampleByFactors(int i, int j,int k);
  ///Count number of electrons in the Chgcar
  double sumElectrons();
  ///
  void gaussianSmearingX(double sigma, double limit=0.01);
  void gaussianSmearingY(double sigma, double limit=0.01);
  void gaussianSmearingZ(double sigma, double limit=0.01);
  
  Chgcar *clone();
  void setChgcar(Chgcar *c);
  
  void calculatePlaneStatisticsX(int n);
  void calculatePlaneStatisticsY(int n);
  void calculatePlaneStatisticsZ(int n);
  int searchMinPlaneX();
  int searchMinPlaneY();
  int searchMinPlaneZ();
  
  FArray2D *getPlaneX(int n);
  FArray2D *getPlaneY(int n);
  FArray2D *getPlaneZ(int n);
  ChgcarPlaneProcess *createSmoothPlaneProcessX(int n,
  double sigmax,double sigmay,double sigmaz,double limit=0.01){
    return new ChgcarPlaneProcess(this,n,0,sigmax,sigmay,sigmaz,limit);
  }
  ChgcarPlaneProcess *createSmoothPlaneProcessY(int n,
  double sigmax,double sigmay,double sigmaz,double limit=0.01){
    return new ChgcarPlaneProcess(this,n,1,sigmax,sigmay,sigmaz,limit);
  }
  ChgcarPlaneProcess *createSmoothPlaneProcessZ(int n,
  double sigmax,double sigmay,double sigmaz,double limit=0.01){
    return new ChgcarPlaneProcess(this,n,2,sigmax,sigmay,sigmaz,limit);
  }
  FArray2D *createCCPlaneX(double val,int n=-1,int delta=-1);
  FArray2D *createCCPlaneY(double val,int n=-1,int delta=-1);
  FArray2D *createCCPlaneZ(double val,int n=-1,int delta=-1);
  FArray2D *createCCPlaneCubicX(double val,int n=-1,int delta=-1);
  FArray2D *createCCPlaneCubicY(double val,int n=-1,int delta=-1);
  FArray2D *createCCPlaneCubicZ(double val,int n=-1,int delta=-1);
};

#endif

