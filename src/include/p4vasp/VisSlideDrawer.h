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

#ifndef VisSlideDrawer_h
#define VisSlideDrawer_h
#include "VisDrawer.h"
#include "FArray.h"
#include "vecutils3d.h"
#include <FL/gl.h>

class Clamp: public ClassInterface{
  public:
  virtual const char *getClassName();    
  virtual double f(double x)=0;
};

class ThresholdClamp:public Clamp{
  virtual const char *getClassName();    
  virtual double f(double x);
};

class SawtoothClamp:public Clamp{
  virtual const char *getClassName();    
  virtual double f(double x);
};

class CosClamp:public Clamp{
  virtual const char *getClassName();    
  virtual double f(double x);
};

class WaveClamp:public Clamp{
  virtual const char *getClassName();    
  virtual double f(double x);
};

class AtanClamp:public Clamp{
  virtual const char *getClassName();    
  virtual double f(double x);
};

class FermiClamp:public Clamp{
  virtual const char *getClassName();    
  virtual double f(double x);
};


class ColorGradient: public ClassInterface{
  public:
  GLfloat color[3];
  virtual const char *getClassName();    
  virtual GLfloat *f(double x)=0;
  virtual void glcolor(double x);
};

class GrayColorGradient: public ColorGradient{
  public:
  virtual const char *getClassName();
  virtual GLfloat *f(double x);
};

class RainbowColorGradient: public ColorGradient{
  public:
  float saturation, value;
  RainbowColorGradient(float saturation=1.0,float value=1.0){
    this->saturation=saturation;
    this->value=value;
  }
  virtual const char *getClassName();
  virtual GLfloat *f(double x);
};

class VisSlideDrawer : public VisDrawer{
  protected:
  double b1[3];
  double b2[3];
  double o[3];
  FArray2D *a;
  ColorGradient *gradient;
  Clamp *clamp;
  int shadowflag;
    
  public:
  int n1,n2;
  double lo,hi;
  double scale;
  VisSlideDrawer(){
    a=NULL;
    b1[0]=1.0;
    b1[1]=0.0;
    b1[2]=0.0;
    b2[0]=0.0;
    b2[1]=1.0;
    b2[2]=0.0;
    o[0]=0.0;
    o[1]=0.0;
    o[2]=0.0;
    n1=1;
    n2=1;
    gradient=new GrayColorGradient();
    clamp=new ThresholdClamp();
    scale=0.0;
    shadowflag=0;
  }
  
  void setShadow(int f);
  int getShadow(){return shadowflag;}
  
  void setB1(double *b){
//    printf("  copy b1 %p %+10.6f %+10.6f %+10.6f\n",b1,b1[0],b1[1],b1[2]);
//    printf("       b  %p %+10.6f %+10.6f %+10.6f\n",b ,b[0],b[1],b[2]);
    copy3d(&b1[0],b);
//    printf("       b1 %p %+10.6f %+10.6f %+10.6f\n",b1,b1[0],b1[1],b1[2]);
  }
  void setB2(double *b){
//    printf("  copy b2 %p %+10.6f %+10.6f %+10.6f\n",b2,b2[0],b2[1],b2[2]);
//    printf("       b  %p %+10.6f %+10.6f %+10.6f\n",b ,b[0],b[1],b[2]);
    copy3d(&b2[0],b);
//    printf("       b2 %p %+10.6f %+10.6f %+10.6f\n",b2,b2[0],b2[1],b2[2]);
  }
  void setOrigin(double *b){
    copy3d(o,b);
  }
  void setFArray(FArray2D *fa);
  void setGradient(ColorGradient *g){
    if (gradient != NULL){
      delete gradient;
    }
    gradient=g;
  }
  void setClamp(Clamp *c){
    if (clamp != NULL){
      delete clamp;
    }
    clamp=c;
  }
  
  void assureClampAndGradient(){
    if (gradient==NULL){
      gradient=new GrayColorGradient();
    }
    if (clamp==NULL){
      clamp=new ThresholdClamp();
    }
  }
  
#ifndef SWIG
  virtual const char *getClassName();
//  virtual void init();
  virtual void draw();
#endif
  virtual ~VisSlideDrawer();
  protected:
  void glcolor(double x){
    gradient->glcolor(clamp->f((x-lo)/(hi-lo)));
  }
  void vertex(int i,int j,double *h);
};

#endif
