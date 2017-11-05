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

#ifndef _MATH_H
#include <math.h>
#endif

#include <stdio.h>
#include <p4vasp/Exceptions.h>
#include <p4vasp/utils.h>
#include <p4vasp/vecutils3d.h>
#include <locale.h>

double *createvec3d(char *s){
  double *v= new double [3];
  setlocale (LC_ALL,"C");
  s=strip(s);
  char **words=splitWords(s);
  if (words[0]==NULL){
    v[0]=0.0;
    v[1]=0.0;
    v[2]=0.0;
  }
  else if (words[1]==NULL){
    v[0]=atof(words[0]);
    v[1]=0.0;
    v[2]=0.0;
  }
  else if (words[2]==NULL){
    v[0]=atof(words[0]);
    v[1]=atof(words[1]);
    v[2]=0.0;
  }
  else{
    v[0]=atof(words[0]);
    v[1]=atof(words[1]);
    v[2]=atof(words[2]);
  }
  delete []words;
  return v;
}

double *createvec3d(double x,double y,double z){
  double *v= new double [3];
  v[0]=x;
  v[1]=y;
  v[2]=z;
  return v;
}

void setvec3d(double *dest,double x,double y,double z){
  dest[0]=x;
  dest[1]=y;
  dest[2]=z;
}

void deletevec3d(double *dest){
  if (dest!=NULL){
    delete dest;
    dest=NULL;
  }
}

double *createmat3d(double a11,double a12,double a13,
                    double a21,double a22,double a23,
		    double a31,double a32,double a33){

  double *m = new double[9];
  m[0]=a11;
  m[1]=a12;
  m[2]=a13;
  m[3]=a21;
  m[4]=a22;
  m[5]=a23;
  m[6]=a31;
  m[7]=a32;
  m[8]=a33;
  return m;
}

void setmat3d(double *dest,
              double a11,double a12,double a13,
              double a21,double a22,double a23,
	      double a31,double a32,double a33){

  dest[0]=a11;
  dest[1]=a12;
  dest[2]=a13;
  dest[3]=a21;
  dest[4]=a22;
  dest[5]=a23;
  dest[6]=a31;
  dest[7]=a32;
  dest[8]=a33;
}

void deletemat3d(double *dest){
  if (dest!=NULL){
    delete dest;
    dest=NULL;
  }
}


double getVecElement3d(double *dest, int i){
#if CHECK>0
  if (dest==NULL){
    NTHROW_NP_EXC("dest=NULL in getVecElement3d(dest,i)");
  }
  if ((i<0) || (i>=3)){
    NTHROW_R_EXC("Index out of range in getVecElement3d(dest,i)",0,3,i);
  }
#endif
  return dest[i];
}

void setVecElement3d(double *dest, int i,double value){
#if CHECK>0
  if (dest==NULL){
    NTHROW_NP_EXC("dest=NULL in setVecElement3d(dest,i,value)");
  }
  if ((i<0) || (i>=3)){
    NTHROW_R_EXC("Index out of range in setVecElement3d(dest,i,value)",0,3,i);
  }
#endif
  dest[i]=value;
}


double *getMatVecElement3d(double *m, int i){
#if CHECK>0
  if (m==NULL){
    NTHROW_NP_EXC("m=NULL in getMatVecElement3d(m,i)");
  }
  if ((i<0) || (i>=3)){
    NTHROW_R_EXC("Index out of range in getMatVecElement3d(m,i)",0,3,i);
  }
#endif
  return &m[3*i];
}

void setMatVecElement3d(double *m, int i,double *v){
#if CHECK>0
  if (m==NULL){
    NTHROW_NP_EXC("m=NULL in setMatVecElement3d(m,i,value)");
  }
  if (v==NULL){
    NTHROW_NP_EXC("value=NULL in setMatVecElement3d(m,i,value)");
  }
  if ((i<0) || (i>=3)){
    NTHROW_R_EXC("Index out of range in setMatVecElement3d(m,i,value)",0,3,i);
  }
#endif

  m[3*i]  =v[0];
  m[3*i+1]=v[1];
  m[3*i+2]=v[2];
}

double getMatElement3d(double *m, int i,int j){
#if CHECK>0
  if (m==NULL){
    NTHROW_NP_EXC("m=NULL in getMatElement3d(m,i,j)");
  }
  if ((i<0) || (i>=3)){
    NTHROW_R_EXC("Index i out of range in getMatElement3d(m,i,j)",0,3,i);
  }
  if ((j<0) || (j>=3)){
    NTHROW_R_EXC("Index j out of range in getMatElement3d(m,i,j)",0,3,j);
  }
#endif
  return m[3*i+j];
}

void setMatElement3d(double *m, int i,int j,double value){
#if CHECK>0
  if (m==NULL){
    NTHROW_NP_EXC("m=NULL in setMatElement3d(m,i,j,value)");
  }
  if ((i<0) || (i>=3)){
    NTHROW_R_EXC("Index i out of range in setMatElement3d(m,i,j,value)",0,3,i);
  }
  if ((j<0) || (j>=3)){
    NTHROW_R_EXC("Index j out of range in setMatElement3d(m,i,j,value)",0,3,j);
  }
#endif
  m[3*i+j]=value;
}



double *add3d(double *dest,double *a){
#if CHECK>0
  if (dest==NULL){
    NTHROW_NP_EXC("dest=NULL in add3d(dest,a)");
  }
  if (a==NULL){
    NTHROW_NP_EXC("a=NULL in add3d(dest,a)");
  }
#endif
  dest[0]+=a[0];
  dest[1]+=a[1];
  dest[2]+=a[2];
  return dest;
}

double *plus3d(double *dest,double *a,double *b){
#if CHECK>0
  if (dest==NULL){
    NTHROW_NP_EXC("dest=NULL in plus3d(dest,a,b)");
  }
  if (a==NULL){
    NTHROW_NP_EXC("a=NULL in plus3d(dest,a,b)");
  }
  if (b==NULL){
    NTHROW_NP_EXC("b=NULL in plus3d(dest,a,b)");
  }
#endif
  dest[0]=a[0]+b[0];
  dest[1]=a[1]+b[1];
  dest[2]=a[2]+b[2];
  return dest;
}

double *createplus3d(double *a,double *b){
  double *dest = new double[3];
#if CHECK>0
  if (dest==NULL){
    NTHROW_MA_EXC("dest allocation failed in createplus3d(a,b)");
  }
  if (a==NULL){
    NTHROW_NP_EXC("a=NULL in createplus3d(a,b)");
  }
  if (b==NULL){
    NTHROW_NP_EXC("b=NULL in createplus3d(a,b)");
  }
#endif
  dest[0]=a[0]+b[0];
  dest[1]=a[1]+b[1];
  dest[2]=a[2]+b[2];
  return dest;
}

double *createplusmat3d(double *a,double *b){
  double *dest = new double[9];
#if CHECK>0
  if (dest==NULL){
    NTHROW_MA_EXC("dest allocation failed in createplusmat3d(a,b)");
  }
  if (a==NULL){
    NTHROW_NP_EXC("a=NULL in createplusmat3d(a,b)");
  }
  if (b==NULL){
    NTHROW_NP_EXC("b=NULL in createplusmat3d(a,b)");
  }
#endif
  dest[0]=a[0]+b[0];
  dest[1]=a[1]+b[1];
  dest[2]=a[2]+b[2];
  dest[3]=a[3]+b[3];
  dest[4]=a[4]+b[4];
  dest[5]=a[5]+b[5];
  dest[6]=a[6]+b[6];
  dest[7]=a[7]+b[7];
  dest[8]=a[8]+b[8];
  return dest;
}


double *sub3d(double *dest,double *a){
#if CHECK>0
  if (dest==NULL){
    NTHROW_NP_EXC("dest=NULL in sub3d(dest,a)");
  }
  if (a==NULL){
    NTHROW_NP_EXC("a=NULL in sub3d(dest,a)");
  }
#endif
  dest[0]-=a[0];
  dest[1]-=a[1];
  dest[2]-=a[2];
  return dest;
}

double *minus3d(double *dest,double *a,double *b){
#if CHECK>0
  if (dest==NULL){
    NTHROW_NP_EXC("dest=NULL in minus3d(dest,a,b)");
  }
  if (a==NULL){
    NTHROW_NP_EXC("a=NULL in minus3d(dest,a,b)");
  }
  if (b==NULL){
    NTHROW_NP_EXC("b=NULL in minus3d(dest,a,b)");
  }
#endif
  dest[0]=a[0]-b[0];
  dest[1]=a[1]-b[1];
  dest[2]=a[2]-b[2];
  return dest;
}

double *createminus3d(double *a,double *b){
  double *dest = new double[3];
#if CHECK>0
  if (dest==NULL){
    NTHROW_MA_EXC("dest allocation failed in createminus3d(a,b)");
  }
  if (a==NULL){
    NTHROW_NP_EXC("a=NULL in createminus3d(a,b)");
  }
  if (b==NULL){
    NTHROW_NP_EXC("b=NULL in createminus3d(a,b)");
  }
#endif
  dest[0]=a[0]-b[0];
  dest[1]=a[1]-b[1];
  dest[2]=a[2]-b[2];
  return dest;
}

double *createminusmat3d(double *a,double *b){
  double *dest = new double[9];
#if CHECK>0
  if (dest==NULL){
    NTHROW_MA_EXC("dest allocation failed in createminusmat3d(a,b)");
  }
  if (a==NULL){
    NTHROW_NP_EXC("a=NULL in createminusmat3d(a,b)");
  }
  if (b==NULL){
    NTHROW_NP_EXC("b=NULL in createminusmat3d(a,b)");
  }
#endif
  dest[0]=a[0]-b[0];
  dest[1]=a[1]-b[1];
  dest[2]=a[2]-b[2];
  dest[3]=a[3]-b[3];
  dest[4]=a[4]-b[4];
  dest[5]=a[5]-b[5];
  dest[6]=a[6]-b[6];
  dest[7]=a[7]-b[7];
  dest[8]=a[8]-b[8];
  return dest;
}

double *createneg3d(double *v){
  double *dest = new double[3];
#if CHECK>0
  if (dest==NULL){
    NTHROW_MA_EXC("dest allocation failed in createneg3d(v)");
  }
  if (v==NULL){
    NTHROW_NP_EXC("createneg3d(NULL)");
  }
#endif
  dest[0]=-v[0];
  dest[1]=-v[1];
  dest[2]=-v[2];
  return dest;
}

double *createnegmat3d(double *m){
  double *dest = new double[9];
#if CHECK>0
  if (dest==NULL){
    NTHROW_MA_EXC("dest allocation failed in createnegmat3d(m)");
  }
  if (m==NULL){
    NTHROW_NP_EXC("createnegmat3d(NULL)");
  }
#endif
  dest[0]=-m[0];
  dest[1]=-m[1];
  dest[2]=-m[2];
  dest[3]=-m[3];
  dest[4]=-m[4];
  dest[5]=-m[5];
  dest[6]=-m[6];
  dest[7]=-m[7];
  dest[8]=-m[8];
  return dest;
}

double *neg3d(double *v){
#if CHECK>0
  if (v==NULL){
    NTHROW_NP_EXC("neg3d(NULL)");
  }
#endif
  v[0]=-v[0];
  v[1]=-v[1];
  v[2]=-v[2];
  return v;
}

double *scalmul3d(double *dest,double a){
#if CHECK>0
  if (dest==NULL){
    NTHROW_NP_EXC("dest=NULL in scalmul3d(dest,a)");
  }
#endif
  dest[0]*=a;
  dest[1]*=a;
  dest[2]*=a;
  return dest;
}

double *createscalmultiply3d(double *v,double a){
  double *dest = new double[3];
#if CHECK>0
  if (dest==NULL){
    NTHROW_MA_EXC("dest allocation failed in createscalmultiply3d(v,a)");
  }
  if (v==NULL){
    NTHROW_NP_EXC("v=NULL in createscalmultiply3d(v,a)");
  }
#endif
  dest[0]=v[0]*a;
  dest[1]=v[1]*a;
  dest[2]=v[2]*a;
  return dest;
}


double *scaldiv3d(double *dest,double a){
#if CHECK>0
  if (dest==NULL){
    NTHROW_NP_EXC("dest=NULL in scaldiv3d(NULL,a)");
  }
  if (a==0.0){
    NTHROW_NP_EXC("a=0.0 in scaldiv3d(dest,a)");
  }
#endif

  dest[0]/=a;
  dest[1]/=a;
  dest[2]/=a;
  return dest;
}

double *createscaldivide3d(double *v,double a){
  double *dest = new double[3];
#if CHECK>0
  if (dest==NULL){
    NTHROW_MA_EXC("dest allocation failed in createscaldivide3d(v,a)");
  }
  if (v==NULL){
    NTHROW_NP_EXC("v=NULL in createscaldivide3d(v,a)");
  }
  if (a==0.0){
    NTHROW_NP_EXC("a=0.0 in createscaldivide3d(v,a)");
  }
#endif
  dest[0]=v[0]/a;
  dest[1]=v[1]/a;
  dest[2]=v[2]/a;
  return dest;
}


double *copy3d(double *dest,double *a){
#if CHECK>0
  if (dest==NULL){
    NTHROW_NP_EXC("dest=NULL in copy3d(dest,a)");
  }
  if (a==NULL){
    NTHROW_NP_EXC("a=NULL in copy3d(dest,a)");
  }
#endif
  dest[0]=a[0];
  dest[1]=a[1];
  dest[2]=a[2];
  return dest;
}

double *copymat3d(double *dest,double *a){
#if CHECK>0
  if (dest==NULL){
    NTHROW_NP_EXC("dest=NULL in copymat3d(dest,a)");
  }
  if (a==NULL){
    NTHROW_NP_EXC("a=NULL in copymat3d(dest,a)");
  }
#endif
  memcpy(dest,a,9*sizeof(double));
  return dest;
}

double *clone3d(double *a){
  double *dest = new double[3];
#if CHECK>0
  if (dest==NULL){
    NTHROW_MA_EXC("dest allocation failed in clone3d(v)");
  }
  if (a==NULL){
    NTHROW_NP_EXC("v=NULL in clone3d(v)");
  }
#endif
  dest[0]=a[0];
  dest[1]=a[1];
  dest[2]=a[2];
  return dest;
}

double *clonemat3d(double *m){
  double *dest = new double[9];
#if CHECK>0
  if (dest==NULL){
    NTHROW_MA_EXC("dest allocation failed in clonemat3d(m)");
  }
  if (m==NULL){
    NTHROW_NP_EXC("m=NULL in clonemat3d(m)");
  }
#endif
  memcpy(dest,m,9*sizeof(double));
  return dest;
}

double veclength3d(double *dest){
#if CHECK>0
  if (dest==NULL){
    NTHROW_NP_EXC("dest=NULL in veclength3d(dest)");
  }
#endif
  return sqrt(dest[0]*dest[0]+dest[1]*dest[1]+dest[2]*dest[2]);
}

double *normalize3d(double *dest){
#if CHECK>0
  if (dest==NULL){
    NTHROW_NP_EXC("dest=NULL in veclength3d(dest)");
  }
#endif
  double l=sqrt(dest[0]*dest[0]+dest[1]*dest[1]+dest[2]*dest[2]);
  if (l>0){
    dest[0]/=l;
    dest[1]/=l;
    dest[2]/=l;
  }
  return dest;
}

double scalprod3d(double *a,double *b){
#if CHECK>0
  if (a==NULL){
    NTHROW_NP_EXC("a=NULL in scalprod3d(a,b)");
  }
  if (b==NULL){
    NTHROW_NP_EXC("b=NULL in scalprod3d(a,b)");
  }
#endif
  return a[0]*b[0]+a[1]*b[1]+a[2]*b[2];
}

double *crossprod3d(double *dest,double *a,double *b){
#if CHECK>0
  if (dest==NULL){
    NTHROW_NP_EXC("dest=NULL in crossprod3d(dest,a,b)");
  }
  if (a==NULL){
    NTHROW_NP_EXC("a=NULL in crossprod3d(dest,a,b)");
  }
  if (b==NULL){
    NTHROW_NP_EXC("b=NULL in crossprod3d(dest,a,b)");
  }
#endif
  dest[0]=a[1]*b[2]-a[2]*b[1];
  dest[1]=a[2]*b[0]-a[0]*b[2];
  dest[2]=a[0]*b[1]-a[1]*b[0];
  return dest;
}

double *createcrossprod3d(double *a,double *b){
  double *dest = new double[3];
#if CHECK>0
  if (dest==NULL){
    NTHROW_MA_EXC("dest allocation failed in createcrossprod3d(a,b)");
  }
  if (a==NULL){
    NTHROW_NP_EXC("a=NULL in createcrossprod3d(a,b)");
  }
  if (b==NULL){
    NTHROW_NP_EXC("b=NULL in createcrossprod3d(a,b)");
  }
#endif
  dest[0]=a[1]*b[2]-a[2]*b[1];
  dest[1]=a[2]*b[0]-a[0]*b[2];
  dest[2]=a[0]*b[1]-a[1]*b[0];
  return dest;
}

double *multiplymatvec3d(double *dest,double *a,double *v){
#if CHECK>0
  if (dest==NULL){
    NTHROW_NP_EXC("dest=NULL in multiplymatvec3d(dest,a,b)");
  }
  if (a==NULL){
    NTHROW_NP_EXC("a=NULL in multiplymatvec3d(dest,a,b)");
  }
  if (v==NULL){
    NTHROW_NP_EXC("v=NULL in multiplymatvec3d(dest,a,b)");
  }
#endif
  dest[0]=a[0]*v[0]+a[1]*v[1]+a[2]*v[2];
  dest[1]=a[3]*v[0]+a[4]*v[1]+a[5]*v[2];
  dest[2]=a[6]*v[0]+a[7]*v[1]+a[8]*v[2];
  return dest;
}

double *createmultiplymatscal3d(double *a,double v){
  double *dest = new double[9];
#if CHECK>0
  if (dest==NULL){
    NTHROW_NP_EXC("dest=NULL in createmultiplymatscal3d(m,b)");
  }
  if (a==NULL){
    NTHROW_NP_EXC("a=NULL in createmultiplymatvec3d(NULL,?)");
  }
#endif
  dest[0]=a[0]*v;
  dest[1]=a[1]*v;
  dest[2]=a[2]*v;
  dest[3]=a[3]*v;
  dest[4]=a[4]*v;
  dest[5]=a[5]*v;
  dest[6]=a[6]*v;
  dest[7]=a[7]*v;
  dest[8]=a[8]*v;
  return dest;
}

double *createmultiplymatvec3d(double *a,double *v){
  double *dest = new double[3];
#if CHECK>0
  if (dest==NULL){
    NTHROW_MA_EXC("dest allocation failed in createmultiplymatvec3d(a,v)");
  }
  if (a==NULL){
    NTHROW_NP_EXC("a=NULL in createmultiplymatvec3d(a,v)");
  }
  if (v==NULL){
    NTHROW_NP_EXC("v=NULL in createmultiplymatvec3d(a,v)");
  }
#endif
  dest[0]=a[0]*v[0]+a[1]*v[1]+a[2]*v[2];
  dest[1]=a[3]*v[0]+a[4]*v[1]+a[5]*v[2];
  dest[2]=a[6]*v[0]+a[7]*v[1]+a[8]*v[2];
  return dest;
}


double *mulmatvec3d(double *a,double *v){
#if CHECK>0
  if (a==NULL){
    NTHROW_NP_EXC("a=NULL in mulmatvec3d(a,v)");
  }
  if (v==NULL){
    NTHROW_NP_EXC("v=NULL in mulmatvec3d(a,v)");
  }
#endif
  double dest[3];
  dest[0]=a[0]*v[0]+a[1]*v[1]+a[2]*v[2];
  dest[1]=a[3]*v[0]+a[4]*v[1]+a[5]*v[2];
  dest[2]=a[6]*v[0]+a[7]*v[1]+a[8]*v[2];
  v[0]=dest[0];
  v[1]=dest[1];
  v[2]=dest[2];
  return v;
}


double *multiplymatmat3d(double *dest,double *a,double *b){
#if CHECK>0
  if (dest==NULL){
    NTHROW_NP_EXC("dest=NULL in multiplymatmat3d(NULL,?,?)");
  }
  if (a==NULL){
    NTHROW_NP_EXC("a=NULL in multiplymatmat3d(?,NULL,?)");
  }
  if (b==NULL){
    NTHROW_NP_EXC("b=NULL in multiplymatmat3d(?,?,NULL)");
  }
#endif
  dest[0]=a[0]*b[0]+a[1]*b[3]+a[2]*b[6];
  dest[1]=a[0]*b[1]+a[1]*b[4]+a[2]*b[7];
  dest[2]=a[0]*b[2]+a[1]*b[5]+a[2]*b[8];
  dest[3]=a[3]*b[0]+a[4]*b[3]+a[5]*b[6];
  dest[4]=a[3]*b[1]+a[4]*b[4]+a[5]*b[7];
  dest[5]=a[3]*b[2]+a[4]*b[5]+a[5]*b[8];
  dest[6]=a[6]*b[0]+a[7]*b[3]+a[8]*b[6];
  dest[7]=a[6]*b[1]+a[7]*b[4]+a[8]*b[7];
  dest[8]=a[6]*b[2]+a[7]*b[5]+a[8]*b[8];
  return dest;
}

double *createmultiplymatmat3d(double *a,double *b){
  double *dest = new double[9];
#if CHECK>0
  if (dest==NULL){
    NTHROW_MA_EXC("dest allocation failed in createmultiplymatmat3d(a,b)");
  }
  if (a==NULL){
    NTHROW_NP_EXC("a=NULL in createmultiplymatmat3d(a,b)");
  }
  if (b==NULL){
    NTHROW_NP_EXC("b=NULL in createmultiplymatmat3d(a,b)");
  }
#endif
  dest[0]=a[0]*b[0]+a[1]*b[3]+a[2]*b[6];
  dest[1]=a[0]*b[1]+a[1]*b[4]+a[2]*b[7];
  dest[2]=a[0]*b[2]+a[1]*b[5]+a[2]*b[8];
  dest[3]=a[3]*b[0]+a[4]*b[3]+a[5]*b[6];
  dest[4]=a[3]*b[1]+a[4]*b[4]+a[5]*b[7];
  dest[5]=a[3]*b[2]+a[4]*b[5]+a[5]*b[8];
  dest[6]=a[6]*b[0]+a[7]*b[3]+a[8]*b[6];
  dest[7]=a[6]*b[1]+a[7]*b[4]+a[8]*b[7];
  dest[8]=a[6]*b[2]+a[7]*b[5]+a[8]*b[8];
  return dest;
}


double *mulmatmat3d(double *a,double *b){
#if CHECK>0
  if (a==NULL){
    NTHROW_NP_EXC("a=NULL in mulmatmat3d(NULL,?)");
  }
  if (b==NULL){
    NTHROW_NP_EXC("b=NULL in mulmatmat3d(?,NULL)");
  }
#endif
  double dest[9];
  dest[0]=a[0]*b[0]+a[1]*b[3]+a[2]*b[6];
  dest[1]=a[0]*b[1]+a[1]*b[4]+a[2]*b[7];
  dest[2]=a[0]*b[2]+a[1]*b[5]+a[2]*b[8];
  dest[3]=a[3]*b[0]+a[4]*b[3]+a[5]*b[6];
  dest[4]=a[3]*b[1]+a[4]*b[4]+a[5]*b[7];
  dest[5]=a[3]*b[2]+a[4]*b[5]+a[5]*b[8];
  dest[6]=a[6]*b[0]+a[7]*b[3]+a[8]*b[6];
  dest[7]=a[6]*b[1]+a[7]*b[4]+a[8]*b[7];
  dest[8]=a[6]*b[2]+a[7]*b[5]+a[8]*b[8];
  memcpy(b,dest,9*sizeof(double));
  return b;
}


double *createrotmat3d(double x,double y,double z){
  double *dest = new double[9];
#if CHECK>0
  if (dest==NULL){
    NTHROW_MA_EXC("dest allocation failed in createrotmat3d(x,y,z)");
  }
#endif
  double cx=cos(x);
  double cy=cos(y);
  double cz=cos(z);
  double sx=sin(x);
  double sy=sin(y);
  double sz=sin(z);
  dest[0]=  cy*cz;
  dest[1]= -sz*cy;
  dest[2]=  sy;

  dest[3]=  sx*sy*cz+cx*sz;
  dest[4]=  cx*cz-sx*sy*sz;
  dest[5]=  -sx*cy;

  dest[6]= sx*sz - cx*sy*cz;
  dest[7]= cx*sy*sz+sx*cz;
  dest[8]= cx*cy;
  return dest;
}

double *createrotmat3da(double x,double y,double z,double a){
  double *dest = new double[9];
#if CHECK>0
  if (dest==NULL){
    NTHROW_MA_EXC("dest allocation failed in createrotmat3da(x,y,z,a)");
  }
#endif
  double S=a/sqrt(x*x+y*y+z*z);
  x*=S;
  y*=S;
  z*=S;
  double cx=cos(x);
  double cy=cos(y);
  double cz=cos(z);
  double sx=sin(x);
  double sy=sin(y);
  double sz=sin(z);
  dest[0]=  cy*cz;
  dest[1]= -sz*cy;
  dest[2]=  sy;

  dest[3]=  sx*sy*cz+cx*sz;
  dest[4]=  cx*cz-sx*sy*sz;
  dest[5]=  -sx*cy;

  dest[6]= sx*sz - cx*sy*cz;
  dest[7]= cx*sy*sz+sx*cz;
  dest[8]= cx*cy;
  return dest;
}


double *identitymat3d(double *dest){
#if CHECK>0
  if (dest==NULL){
    NTHROW_NP_EXC("dest=NULL in identitymat3d(NULL)");
  }
#endif
  dest[0]=1.0;
  dest[1]=0.0;
  dest[2]=0.0;
  dest[3]=0.0;
  dest[4]=1.0;
  dest[5]=0.0;
  dest[6]=0.0;
  dest[7]=0.0;
  dest[8]=1.0;
  return dest;
}

double *createidentitymat3d(){
  double *dest = new double[9];
#if CHECK>0
  if (dest==NULL){
    NTHROW_MA_EXC("dest allocation failed in createidentitymat3d()");
  }
#endif
  dest[0]=1.0;
  dest[1]=0.0;
  dest[2]=0.0;
  dest[3]=0.0;
  dest[4]=1.0;
  dest[5]=0.0;
  dest[6]=0.0;
  dest[7]=0.0;
  dest[8]=1.0;
  return dest;
}


double *zeromat3d(double *dest){
#if CHECK>0
  if (dest==NULL){
    NTHROW_NP_EXC("zeromat3d(NULL)");
  }
#endif
  dest[0]=0.0;
  dest[1]=0.0;
  dest[2]=0.0;
  dest[3]=0.0;
  dest[4]=0.0;
  dest[5]=0.0;
  dest[6]=0.0;
  dest[7]=0.0;
  dest[8]=0.0;
  return dest;
}

double *createzeromat3d(){
  double *dest = new double[9];
#if CHECK>0
  if (dest==NULL){
    NTHROW_MA_EXC("dest allocation failed in createzeromat3d()");
  }
#endif
  dest[0]=0.0;
  dest[1]=0.0;
  dest[2]=0.0;
  dest[3]=0.0;
  dest[4]=0.0;
  dest[5]=0.0;
  dest[6]=0.0;
  dest[7]=0.0;
  dest[8]=0.0;
  return dest;
}

double *transmat3d(double *dest){
#if CHECK>0
  if (dest==NULL){
    NTHROW_NP_EXC("transmat3d(NULL)");
  }
#endif
  double c;

  c=dest[1];
  dest[1]=dest[3];
  dest[3]=c;

  c=dest[6];
  dest[6]=dest[2];
  dest[2]=c;

  c=dest[7];
  dest[7]=dest[5];
  dest[5]=c;

  return dest;
}

double detmat3d(double *dest){
#if CHECK>0
  if (dest==NULL){
    NTHROW_NP_EXC("detmat3d(NULL)");
  }
#endif
  return dest[0]*dest[4]*dest[8]+dest[1]*dest[5]*dest[6]+dest[3]*dest[7]*dest[2]
        -dest[2]*dest[4]*dest[6]-dest[1]*dest[3]*dest[8]-dest[5]*dest[7]*dest[0];

}
