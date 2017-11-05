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

#ifndef vecutils3d_h
#define vecutils3d_h

double *createvec3d(char *s);
double *createvec3d(double x,double y,double z);
void    setvec3d(double *dest, double x,double y,double z);
void    deletevec3d(double *dest);
double *createmat3d(double a11,double a12,double a13,
                    double a21,double a22,double a23,
		    double a31,double a32,double a33);
void    setmat3d(double *dest,
                    double a11,double a12,double a13,
                    double a21,double a22,double a23,
		    double a31,double a32,double a33);
void    deletemat3d(double *dest);

double  getVecElement3d(double *dest, int i);  
void    setVecElement3d(double *dest, int i,double value);  
double *getMatVecElement3d(double *dest, int i);  
void    setMatVecElement3d(double *dest, int i,double *value);  
double  getMatElement3d(double *dest, int i,int j);  
void    setMatElement3d(double *dest, int i,int j,double value);  

double *add3d(double *dest,double *a);
double *plus3d(double *dest,double *a,double *b);  
double *createplus3d(double *a,double *b);  
double *createplusmat3d(double *a,double *b);  

double *sub3d(double *dest,double *a);
double *minus3d(double *dest,double *a,double *b);
double *createminus3d(double *a,double *b);
double *createminusmat3d(double *a,double *b);

double *neg3d(double *v);
double *createneg3d(double *v);
double *createnegmat3d(double *v);

double *scalmul3d(double *dest,double a);
double *createscalmultiply3d(double *v,double a);
double *scaldiv3d(double *dest,double a);
double *createscaldivide3d(double *dest,double a);

double *copy3d(double *dest,double *a);
double *clone3d(double *a);
double *copymat3d(double *dest,double *a);
double *clonemat3d(double *a);

double veclength3d(double *dest);
double *normalize3d(double *dest);
double scalprod3d(double *a,double *b);
double *crossprod3d(double *dest,double *a,double *b);
double *createcrossprod3d(double *a,double *b);

double *createmultiplymatscal3d(double *a,double v);
double *createmultiplymatvec3d(double *a,double *v);
double *multiplymatvec3d(double *dest,double *a,double *v);
double *mulmatvec3d(double *a,double *v);
double *multiplymatmat3d(double *dest,double *a,double *b);
double *createmultiplymatmat3d(double *a,double *b);

double *mulmatmat3d(double *a,double *b);
double *createrotmat3d(double x,double y,double z);
double *createrotmat3da(double x,double y,double z,double a);
double *identitymat3d(double *dest);
double *createidentitymat3d();
double *zeromat3d(double *dest);
double *createzeromat3d();
double detmat3d(double *dest);
double *transmat3d(double *dest);

#endif
