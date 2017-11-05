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

#include <string.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <p4vasp/utils.h>
#include <p4vasp/Structure.h>
#include <p4vasp/Chgcar.h>
#include <p4vasp/ChgcarSmear.h>
#include <p4vasp/Exceptions.h>
#include <p4vasp/vecutils3d.h>
#include <locale.h>

const char *Chgcar::getClassName(){
  return "Chgcar";
}

Chgcar::Chgcar(){
  locked=false;
  data=NULL;
  structure=NULL;
  nx=0;
  ny=0;
  nz=0;
  is_statistics=false;
}

void Chgcar::clean(){
  checklock("clean()");
  if (data!=NULL){
    delete data;
    data=NULL;
  }
  if (structure!=NULL){
    delete structure;
    structure=NULL;
  }
  nx=0;
  ny=0;
  nz=0;
  is_statistics=false;
}

Chgcar::~Chgcar(){
  clean();
}

Chgcar::Chgcar(FILE *f){
  locked=false;
  data=NULL;
  structure=NULL;
  nx=0;
  ny=0;
  nz=0;
  read(f);
}

Chgcar::Chgcar(char *path){
  locked=false;
  data=NULL;
  structure=NULL;
  nx=0;
  ny=0;
  nz=0;
  read(path);
}

void Chgcar::subtractChgcar(Chgcar *c){
  checklock("subtractChgcar()");
#if CHECK>0
  if (c==NULL){
    THROW_NP_EXC("subtractChgcar(NULL)");
  }
  if ((c->nx!=nx)||(c->ny!=ny)||(c->nz!=nz)){
    char s[256];
    snprintf(s,250,"Chgcar dimensions do not match in the method "
    "subtractChgcar:\n(%ld,%ld,%ld)!=(%ld,%ld,%ld)",nx,ny,nz,c->nx,c->ny,c->nz);
    THROW_EXC(s);
  }
  if (data==NULL){
    THROW_NP_EXC("data is NULL in Chgcar.subtractChgcar()");
  }
  if (c->data==NULL){
    THROW_NP_EXC("c->data is NULL in Chgcar.subtractChgcar(c)");
  }
#endif

  float *p=data;
  float *s=c->data;
  for (unsigned long l=nx*ny*nz;l!=0;l--){
   *p-=*s;
   p++;
   s++;
  }
  is_statistics=false;
}

void Chgcar::calculateStatistics(){
  checklock("calculateStatistics()");
#if CHECK>0
  if (data==NULL){
    THROW_NP_EXC("data is NULL in Chgcar.calculateStatistics()");
  }
#endif
  double min,max,avg,avg2;
  min =*data;
  max =*data;
  avg =0.0;
  avg2=0.0;
  unsigned long l=nx*ny*nz;
  for (float *p=data;l!=0;l--,p++){
    if (*p<min){
      min=*p;
    }
    if (*p>max){
      max=*p;
    }
    avg+=*p;
    avg2+=(*p)*(*p);
  }
  unsigned long N=nx*ny*nz;
  minimum=min;
  maximum=max;
  average=avg/N;
  variance=avg2/N-average*average;
}

int Chgcar::read(char *path){
  checklock("read(path)");
#if VERBOSE>0
  printf("Chgcar::read(\"%s\")\n",path);
#endif
  FILE *f=fopen(path,"r");
#if CHECK>0
  if (f==NULL){
    char s[256];
    snprintf(s,250,"Chgcar.read('%s') open error.\n%s",path,strerror(errno));
    THROW_EXC(s);
  }
#endif
  int r=this->read(f);
  fclose(f);
  return r;
}

int Chgcar::read(FILE *f){
  checklock("read(FILE)");
  setlocale (LC_ALL,"C");
  is_statistics=false;
  char *line;
  char **words;
  int r;
  clean();
#if CHECK>1
  if (f==NULL){
    THROW_NP_EXC("Invalid parameters Chgcar.read(FILE=NULL).");
  }
#endif
  structure=new Structure();
#if CHECK>0
  if (structure==NULL){
    THROW_MA_EXC("Memory allocation error in Chgcar.read(); (Structure)");
  }
#endif
  r=structure->read(f);
  if (r){
    THROW_EXC("Error reading Structure part in Chgcar.read();");
  }
  line=getLine(f);
  if (line==NULL){
    THROW_EXC("Error reading empty line after Structure part in Chgcar.read();");
  }
  delete line;
  line=getLine(f);
  if (line==NULL){
    THROW_EXC("Error reading grid size line in Chgcar.read();");
  }
  words=splitWords(line);
#if CHECK>0
  if (words[0]==NULL){
    THROW_EXC("Error reading grid size line in Chgcar.read(); (nx missing)");
  }
#endif
  nx=atol(words[0]);
#if CHECK>0
  if (nx<=0){
    THROW_EXC("Error reading grid size line in Chgcar.read(); "
              "(nx is not positive)");
  }
#endif

#if CHECK>0
  if (words[1]==NULL){
    THROW_EXC("Error reading grid size line in Chgcar.read(); (ny missing)");
  }
#endif
  ny=atol(words[1]);
#if CHECK>0
  if (ny<=0){
    THROW_EXC("Error reading grid size line in Chgcar.read(); "
              "(ny is not positive)");
  }
#endif

#if CHECK>0
  if (words[2]==NULL){
    THROW_EXC("Error reading grid size line in Chgcar.read(); (nz missing)");
  }
#endif
  nz=atol(words[2]);
#if CHECK>0
  if (nz<=0){
    THROW_EXC("Error reading grid size line in Chgcar.read(); "
              "(nz is not positive)");
  }
#endif
  delete line;
  delete words;

  length=nx*ny*nz;
  data=new float[length];
  for (long i=0; i<length; i++){
    line=getWord(f);
#if CHECK>0
    if (line==NULL){
      char s[256];
      snprintf(s,250,"Error reading grid point %ld/%ld in Chgcar.read(); (nx=%ld ny=%ld nz=%ld)\n",i+1,length,nx,ny,nz);
      THROW_EXC(s);
    }
#endif
    data[i]=float(atof(line));
    delete line;
  }
  return 0;
}

int Chgcar::write(FILE *f){
  checklock("write(FILE)");
#if CHECK>0
  if (structure==NULL){
    THROW_NP_EXC("No Structure in Chgcar.write();\n");
  }
#endif
  structure->write(f);
#if CHECK>0
  if (data==NULL){
    THROW_NP_EXC("No data in Chgcar.write();");
  }
  if ((nx<=0)||(ny<=0)||(nz<=0)){
    char s[256];
    snprintf(s,250,"Invalid grid size in Chgcar.write(); (nx=%ld ny=%ld nz=%ld)\n",nx,ny,nz);
    THROW_EXC(s);
  }
#endif
  fprintf(f,"\n%ld %ld %ld\n",nx,ny,nz);
  length=nx*ny*nz;
  for (int i=0; i<length; i++){
    fprintf(f," %+6E",data[i]);
    if ((i%10)==9){
      fprintf(f,"\n");
    }
  }
  return 0;
}

int Chgcar::write(char *path){
  checklock("write(path)");
  FILE *f=fopen(path,"w+");
#if CHECK>0
  if (f==NULL){
    char s[256];
    snprintf(s,250,"Chgcar.write('%s') open error.\n",path);
    THROW_EXC(s);
  }
#endif
  int r=this->write(f);
  fclose(f);
  return r;
}

int Chgcar::downSampleByFactors(int x,int y,int z){
#if VERBOSE>1
  printf("Chgcar::downSampleByFactors(%d,%d,%d)\n",x,y,z);
#endif
  checklock("downSampleByFactors()");
#if CHECK>0
  if (data==NULL){
    THROW_NP_EXC("No data in Chgcar.downSampleByFactors().");
  }
  if ((x<=0)||(x>nx)||(y<=0)||(y>ny)||(z<=0)||(z>nz)){
    char s[256];
    snprintf(s,250,"Factors out of range in Chgcar.downSampleByFactors(%d, %d, %d); (nx=%ld,ny=%ld,nz=%ld)\n",
      x,y,z,nx,ny,nz);
    THROW_EXC(s);
  }
#endif
  long nnx=nx/x;
  long nny=ny/y;
  long nnz=nz/z;
//  printf("nx,ny,nz    =(%3ld,%3ld,%3ld)\n",nx,ny,nz);
//  printf("nnx,nny,nnz =(%3ld,%3ld,%3ld)\n",nnx,nny,nnz);
  long nlength=nnx*nny*nnz;
  float *ndata=new float[nlength];
#if CHECK>0
  if (ndata==NULL){
    THROW_MA_EXC("Memory allocation error in Chgcar.downSampleByFactors();");
  }
#endif
  for (int i=0; i<nnx; i++){
    for (int j=0; j<nny; j++){
      for (int k=0; k<nnz; k++){
	fflush(stdout);
        float ch=0.0;
        for (int ii=0; ii<x; ii++){
          for (int jj=0; jj<y; jj++){
            for (int kk=0; kk<z; kk++){
              ch+=getRaw(i*x+ii,j*y+jj,k*z+kk);
            }
          }
        }
        ndata[i+(j+k*nny)*nnx]=ch;
      }
    }
  }
  nx=nnx;
  ny=nny;
  nz=nnz;
  delete data;
  data=ndata;
#if VERBOSE>1
  printf("Chgcar::downSampleByFactors(%d,%d,%d) -\n",x,y,z);
#endif
  return 0;
}

float Chgcar::get(int i,int j,int k){
#if CHECK>1
  if (data==NULL){
    THROW_NP_EXC("No data in Chgcar.get().");
  }
#endif
  i%=nx;
  j%=ny;
  k%=nz;
  if(i<0)i+=nx;
  if(j<0)j+=ny;
  if(k<0)k+=nz;

  return data[i+(j+k*ny)*nx];
}

float Chgcar::getRaw(int i,int j,int k){
//  printf("Chgcar::getRaw(%3d,%3d,%3d)\n",i,j,k);
#if CHECK>1
  if (data==NULL){
    THROW_NP_EXC("No data in Chgcar.getRaw().");
  }
  if ((i<0)||(i>=nx)){
    THROW_R_EXC("getRaw() 1st index out of range.",0,nx,i);
  }
  if ((j<0)||(j>=ny)){
    THROW_R_EXC("getRaw() 2nd index out of range.",0,ny,j);
  }
  if ((k<0)||(k>=nz)){
    THROW_R_EXC("getRaw() 3rd index out of range.",0,nz,k);
  }
#endif
  return data[i+(j+k*ny)*nx];
}

void Chgcar::set(int i,int j,int k,float val){
#if CHECK>1
  if (data==NULL){
    THROW_NP_EXC("No data in Chgcar.set().");
  }
#endif
  i%=nx;
  j%=ny;
  k%=nz;
  if(i<0)i+=nx;
  if(j<0)j+=ny;
  if(k<0)k+=nz;
  data[i+(j+k*ny)*nx]=val;
}

void Chgcar::setRaw(int i,int j,int k,float val){
#if CHECK>1
  if (data==NULL){
    THROW_NP_EXC("No data in Chgcar.setRaw().");
  }
  if ((i<0)||(i>=nx)){
    THROW_R_EXC("setRaw() 1st index out of range.",0,nx,i);
  }
  if ((j<0)||(j>=ny)){
    THROW_R_EXC("setRaw() 2nd index out of range.",0,ny,j);
  }
  if ((k<0)||(k>=nz)){
    THROW_R_EXC("setRaw() 3rd index out of range.",0,nz,k);
  }
#endif
  data[i+(j+k*ny)*nx]=val;
}

double *Chgcar::getDirGrad(double *dest,int i,int j, int k){
#if CHECK>1
  if (dest==NULL){
    THROW_NP_EXC("Chgcar.getDirGrad(NULL,...).");
  }
#endif
  dest[0]=get(i+1,j  ,k  )-get(i-1,j  ,k  );
  dest[1]=get(i  ,j+1,k  )-get(i  ,j-1,k  );
  dest[2]=get(i  ,j  ,k+1)-get(i  ,j  ,k-1);
  return dest;
}

double *Chgcar::getGrad(double *dest,int i,int j, int k){
#if CHECK>1
  if (dest==NULL){
    THROW_NP_EXC("Chgcar.getGrad(NULL,...).");
  }
  if (structure==NULL){
    THROW_NP_EXC("Chgcar.structure=NULL in Chgcar.getGrad().");
  }
#endif
  double a[3];
  a[0]=-(get(i+1,j  ,k  )-get(i-1,j  ,k  ));
  a[1]=-(get(i  ,j+1,k  )-get(i  ,j-1,k  ));
  a[2]=-(get(i  ,j  ,k+1)-get(i  ,j  ,k-1));
  dest[0]=structure->basis1[0]*a[0]+structure->basis2[0]*a[1]+structure->basis3[0]*a[2];
  dest[1]=structure->basis1[1]*a[0]+structure->basis2[1]*a[1]+structure->basis3[1]*a[2];
  dest[2]=structure->basis1[2]*a[0]+structure->basis2[2]*a[1]+structure->basis3[2]*a[2];
  return dest;
}

double Chgcar::sumElectrons(){
  checklock("sumElectrons()");
  double N=0.0;
  long NN=nx*ny*nz;
  for (long l = 0;l<NN;l++){
    N+=data[l];
  }
#if VERBOSE>3
  printf("Chargcar.sumElectrons()=%f\n",N/(nx*ny*nz));
#endif
  return N/(nx*ny*nz);
}

void Chgcar::gaussianSmearingX(double sigma,double limit){
  checklock("gaussianSmearingX()");
#if VERBOSE>0
  printf("Chgcar::gaussianSmearingX(%f,%f)\n",sigma,limit);
#endif
  float *line = new float[nx];
#if CHECK>0
  if (line==NULL){
    THROW_MA_EXC("gaussianSmearingX()");
  }
#endif
  double sum;
  double llen=veclength3d(structure->basis1);
  double factor= llen*llen/(nx*nx*2.0*sigma*sigma);
  long d=int(sqrt(-log(limit*sigma*sqrt(2*M_PI))/factor));
  printf("  factor=%f d=%ld\n",factor,d);
  for (long a=0; a<ny; a++){
    for (long b=0; b<nz; b++){
      for (long i=0; i<nx; i++){
        sum=0.0;
	for (long j=-d; j<=d; j++){
	  sum+=exp(-j*j*factor)*get(i+j,a,b);
	}
	line[i]=sum/sigma/sqrt(2*M_PI);
      }
      for (long i=0; i<nx; i++){
        setRaw(i,a,b,line[i]);
      }
    }
  }
}

void Chgcar::gaussianSmearingY(double sigma,double limit){
  checklock("gaussianSmearingY()");
  float *line = new float[ny];
#if CHECK>0
  if (line==NULL){
    THROW_MA_EXC("gaussianSmearingY()");
  }
#endif
  double sum;
  double llen=veclength3d(structure->basis2);
  double factor= llen*llen/(ny*ny*2.0*sigma*sigma);
  long d=int(sqrt(-log(limit*sigma*sqrt(2*M_PI))/factor));
  for (long a=0; a<nx; a++){
    for (long b=0; b<nz; b++){
      for (long i=0; i<ny; i++){
        sum=0.0;
	for (long j=-d; j<=d; j++){
	  sum+=exp(-j*j*factor)*get(a,i+j,b);
	}
	line[i]=sum/sigma/sqrt(2*M_PI);
      }
      for (long i=0; i<ny; i++){
        setRaw(a,i,b,line[i]);
      }
    }
  }
}

void Chgcar::gaussianSmearingZ(double sigma,double limit){
  checklock("gaussianSmearingZ()");
  float *line = new float[nz];
#if CHECK>0
  if (line==NULL){
    THROW_MA_EXC("gaussianSmearingZ()");
  }
#endif
  double sum;
  double llen=veclength3d(structure->basis3);
  double factor= llen*llen/(nz*nz*2.0*sigma*sigma);
  long d=int(sqrt(-log(limit*sigma*sqrt(2*M_PI))/factor));
  for (long a=0; a<nx; a++){
    for (long b=0; b<ny; b++){
      for (long i=0; i<nz; i++){
        sum=0.0;
	for (long j=-d; j<=d; j++){
	  sum+=exp(-j*j*factor)*get(a,b,i+j);
	}
	line[i]=sum/sigma/sqrt(2*M_PI);
      }
      for (long i=0; i<nz; i++){
        setRaw(a,b,i,line[i]);
      }
    }
  }
}

void Chgcar::setChgcar(Chgcar *c){
  checklock("setChgcar() (a)");
  clean();
  if (c!=NULL){
    c->checklock("setChgcar() (b)");
    nx=c->nx;
    ny=c->ny;
    nz=c->nz;
    if (c->structure != NULL){
      structure=c->structure->clone();
    }
    unsigned long length=nx*ny*nz;
    data=new float[length];
    memcpy(data,c->data,length*sizeof(float));
    is_statistics=c->is_statistics;
    minimum=c->minimum;
    maximum=c->maximum;
    average=c->average;
    variance=c->variance;
  }
}

Chgcar *Chgcar::clone(){
  checklock("clone()");
  Chgcar *c=new Chgcar();
  c->setChgcar(this);
  return c;
}


ReadChgcarProcess::ReadChgcarProcess(Chgcar *c, FILE *f,bool closeflag){
  chgcar=c;
  file=f;
  c->lock();
  _total=0;
  _step=0;
  this->closeflag=closeflag;
}

ReadChgcarProcess::~ReadChgcarProcess(){
  chgcar->unlock();
  if (closeflag){
    fclose(file);
  }
}

long ReadChgcarProcess::next(){
  char *line;
  char **words;
  int r;
  is_status=true;
  is_error=false;
  setlocale (LC_ALL,"C");
  if (_step==0){
    sprintf(buff,"Reading Chgcar headder");
    chgcar->unlock();
    chgcar->clean();
    chgcar->lock();
    if (file==NULL){
      is_error=true;
      is_status=false;
      sprintf(buff,"Invalid parameters ReadChgcarProcess::next() FILE=NULL).");
      return 0;
    }
    chgcar->structure=new Structure();
    if (chgcar->structure==NULL){
      is_error=true;
      is_status=false;
      sprintf(buff,"Memory allocation error in ReadChgcarProcess::next() (Structure)");
      return 0;
    }
    r=chgcar->structure->read(file);
    if (r){
      is_error=true;
      is_status=false;
      sprintf(buff,"Error reading Structure part in ReadChgcarProcess::next()");
      return 0;
    }
    line=getLine(file);
    if (line==NULL){
      is_error=true;
      is_status=false;
      sprintf(buff,"Error reading empty line after Structure part ReadChgcarProcess::next()");
      return 0;
    }
    delete line;
    line=getLine(file);
    if (line==NULL){
      is_error=true;
      is_status=false;
      sprintf(buff,"Error reading grid size line in ReadChgcarProcess::next()");
      return 0;
    }
    words=splitWords(line);
    if (words[0]==NULL){
      is_error=true;
      is_status=false;
      sprintf(buff,"Error reading grid size line in ReadChgcarProcess::next() (nx missing)");
      return 0;
    }
    chgcar->nx=atol(words[0]);
    if (chgcar->nx<=0){
      is_error=true;
      is_status=false;
      sprintf(buff,"Error reading grid size line in ReadChgcarProcess::next() "
        	"(nx is not positive)");
      return 0;
    }

    if (words[1]==NULL){
      is_error=true;
      is_status=false;
      sprintf(buff,"Error reading grid size line in ReadChgcarProcess::next() (ny missing)");
      return 0;
    }
    chgcar->ny=atol(words[1]);
    if (chgcar->ny<=0){
      is_error=true;
      is_status=false;
      sprintf(buff,"Error reading grid size line in ReadChgcarProcess::next() "
        	"(ny is not positive)");
      return 0;
    }

    if (words[2]==NULL){
      is_error=true;
      is_status=false;
      sprintf(buff,"Error reading grid size line in ReadChgcarProcess::next() (nz missing)");
      return 0;
    }
    chgcar->nz=atol(words[2]);
    if (chgcar->nz<=0){
      is_error=true;
      is_status=false;
      sprintf(buff,"Error reading grid size line in ReadChgcarProcess::next() "
        	"(nz is not positive)");
      return 0;
    }
    delete line;
    delete words;

    chgcar->length=chgcar->nx*chgcar->ny*chgcar->nz;
    chgcar->data=new float[chgcar->length];
    _step=1;
    _total=chgcar->length;
    return 1;
  }
  else{
    is_error=false;
    for (long i=_step-1;i<chgcar->length; i++){
      line=getWord(file);
      if (line==NULL){
        is_error=true;
        is_status=false;
        sprintf(buff,"Error reading grid point %ld/%ld in ReadChgcarProcess::next() (nx=%ld ny=%ld nz=%ld)",
	i+1,chgcar->length,chgcar->nx,chgcar->ny,chgcar->nz);
        return 0;
      }
      chgcar->data[i]=float(atof(line));
      delete line;
      if (i>=_step+100+chgcar->length/100){
        sprintf(buff,"Reading gridpoint %ld/%ld",i+1,chgcar->length);
        _step=i+2;
	return _step;
      }
    }
  }
  chgcar->unlock();
  sprintf(buff,"Chgcar read OK.");
  return 0;
}


void Chgcar::calculatePlaneStatisticsX(int n){
#if CHECK>0
  if (data==NULL){
    THROW_NP_EXC("data is NULL in Chgcar.calculatePlaneStatistics(n)");
  }
#endif
  double min,max,avg,avg2;
  min =getRaw(n,0,0);
  max =min;
  avg =0.0;
  avg2=0.0;
  for(int i=0; i<ny; i++){
    for (int j=0; j<nz; j++){
      double x=getRaw(n,i,j);
      if (x<min){
	min=x;
      }
      if (x>max){
	max=x;
      }
      avg+=x;
      avg2+=x*x;
    }
  }
  unsigned long N=ny*nz;
  plane_minimum=min;
  plane_maximum=max;
  plane_average=avg/N;
  plane_variance=avg2/N-average*average;
}

void Chgcar::calculatePlaneStatisticsY(int n){
#if CHECK>0
  if (data==NULL){
    THROW_NP_EXC("data is NULL in Chgcar.calculatePlaneStatistics(n)");
  }
#endif
  double min,max,avg,avg2;
  min =getRaw(0,n,0);
  max =min;
  avg =0.0;
  avg2=0.0;
  for(int i=0; i<nx; i++){
    for (int j=0; j<nz; j++){
      double x=getRaw(i,n,j);
      if (x<min){
	min=x;
      }
      if (x>max){
	max=x;
      }
      avg+=x;
      avg2+=x*x;
    }
  }
  unsigned long N=nx*nz;
  plane_minimum=min;
  plane_maximum=max;
  plane_average=avg/N;
  plane_variance=avg2/N-average*average;
}


void Chgcar::calculatePlaneStatisticsZ(int n){
#if CHECK>0
  if (data==NULL){
    THROW_NP_EXC("data is NULL in Chgcar.calculatePlaneStatistics(n)");
  }
#endif
  double min,max,avg,avg2;
  min =getRaw(0,0,n);
  max =min;
  avg =0.0;
  avg2=0.0;
  for(int i=0; i<nx; i++){
    for (int j=0; j<ny; j++){
      double x=getRaw(i,j,n);
      if (x<min){
	min=x;
      }
      if (x>max){
	max=x;
      }
      avg+=x;
      avg2+=x*x;
    }
  }
  unsigned long N=nx*ny;
  plane_minimum=min;
  plane_maximum=max;
  plane_average=avg/N;
  plane_variance=avg2/N-average*average;
}


FArray2D *Chgcar::getPlaneX(int n){
#if CHECK>0
  if (data==NULL){
    THROW_NP_EXC("data is NULL in Chgcar.getPlaneX(n)");
  }
#endif
  FArray2D *a=new FArray2D(ny,nz);
  for(int i=0; i<ny; i++){
    for (int j=0; j<nz; j++){
      a->set(i,j,getRaw(n,i,j));
    }
  }
  return a;
}

FArray2D *Chgcar::getPlaneY(int n){
#if CHECK>0
  if (data==NULL){
    THROW_NP_EXC("data is NULL in Chgcar.getPlaneX(n)");
  }
#endif
  FArray2D *a=new FArray2D(nx,nz);
  for(int i=0; i<nx; i++){
    for (int j=0; j<nz; j++){
      a->set(i,j,getRaw(i,n,j));
    }
  }
  return a;
}

FArray2D *Chgcar::getPlaneZ(int n){
#if CHECK>0
  if (data==NULL){
    THROW_NP_EXC("data is NULL in Chgcar.getPlaneX(n)");
  }
#endif
  FArray2D *a=new FArray2D(nx,ny);
  for(int i=0; i<nx; i++){
    for (int j=0; j<ny; j++){
      a->set(i,j,getRaw(i,j,n));
    }
  }
  return a;
}

int Chgcar::searchMinPlaneX(){
  calculatePlaneStatisticsX(0);
  double min=plane_average;
  int index=0;
  for (int i=1; i<nx; i++){
    calculatePlaneStatisticsX(i);
    if (plane_average<min){
      min=plane_average;
      index=i;
    }
  }
  return index;
}

int Chgcar::searchMinPlaneY(){
  calculatePlaneStatisticsY(0);
  double min=plane_average;
  int index=0;
  for (int i=1; i<ny; i++){
    calculatePlaneStatisticsY(i);
    if (plane_average<min){
      min=plane_average;
      index=i;
    }
  }
  return index;
}

int Chgcar::searchMinPlaneZ(){
  calculatePlaneStatisticsZ(0);
  double min=plane_average;
  int index=0;
  for (int i=1; i<nz; i++){
    calculatePlaneStatisticsZ(i);
     if (plane_average<min){
      min=plane_average;
      index=i;
    }
  }
  return index;
}

FArray2D *Chgcar::createCCPlaneX(double val,int n,int delta){
  STMSearchProcess s(this,val,NULL,n,0,delta,10,0);
  s.processAll();
  return s.getPlane();
}
FArray2D *Chgcar::createCCPlaneY(double val,int n,int delta){
  STMSearchProcess s(this,val,NULL,n,1,delta,10,0);
  s.processAll();
  return s.getPlane();
}
FArray2D *Chgcar::createCCPlaneZ(double val,int n,int delta){
  STMSearchProcess s(this,val,NULL,n,2,delta,10,0);
  s.processAll();
  return s.getPlane();
}
FArray2D *Chgcar::createCCPlaneCubicX(double val,int n,int delta){
  STMSearchProcess s(this,val,NULL,n,0,delta,10,2);
  s.processAll();
  return s.getPlane();
}
FArray2D *Chgcar::createCCPlaneCubicY(double val,int n,int delta){
  STMSearchProcess s(this,val,NULL,n,1,delta,10,2);
  s.processAll();
  return s.getPlane();
}
FArray2D *Chgcar::createCCPlaneCubicZ(double val,int n,int delta){
  STMSearchProcess s(this,val,NULL,n,2,delta,10,2);
  s.processAll();
  return s.getPlane();
}

ChgcarPlaneProcess::ChgcarPlaneProcess(Chgcar *c,long n,int dir,double
sigmax, double sigmay,double sigmaz,double limit=0.01){
  chgcar=c;
  c->lock();
  _total=0;
  _step=0;
  this->n=n;
  this->dir=dir;
  this->limit=limit;
  sx=sigmax;
  sy=sigmay;
  sz=sigmaz;
  double fx=factor(0);
  double fy=factor(1);
  double fz=factor(2);
  dx=(sx<=0.0)?(0):int(sqrt(-log(limit*sx*sqrt(2*M_PI))/fx));
  dy=(sy<=0.0)?(0):int(sqrt(-log(limit*sy*sqrt(2*M_PI))/fy));
  dz=(sz<=0.0)?(0):int(sqrt(-log(limit*sz*sqrt(2*M_PI))/fz));
  wx=createWeights(dx,fx);
  wy=createWeights(dy,fy);
  wz=createWeights(dz,fz);
  switch (dir){
    case 0:
      plane=new FArray2D(c->ny,c->nz);
      _total=c->ny;
      dim=c->nz;
      break;
    case 1:
      plane=new FArray2D(c->nx,c->nz);
      _total=c->nx;
      dim=c->nz;
      break;
    case 2:
      plane=new FArray2D(c->nx,c->ny);
      _total=c->nx;
      dim=c->ny;
      break;
    default:
      plane=new FArray2D(c->nx,c->ny);
      _total=c->nx;
      dim=c->ny;
      dir=2;
      break;
  }
  plane->clear();
  _step=0;
}

double *ChgcarPlaneProcess::createWeights(int d,double factor){
  double *w;
  if (d==0){
    w=new double[1];
    w[0]=1.0;
    return w;
  }
  double sum=0.0;
  w= new double[2*d+1];
  for (int i=-d;i<=d;i++){
    w[d+i]=exp(-i*i*factor);
    sum+=w[d+i];
  }
  for (int i=-d;i<=d;i++){
    w[d+i]/=sum;
  }
  return w;
}

double ChgcarPlaneProcess::factor(int i){
  double b,sigma;
  long n;
  switch(i){
    case 0:
      b=veclength3d(chgcar->structure->basis1);
      n=chgcar->nx;
      sigma=sx;
      break;
    case 1:
      b=veclength3d(chgcar->structure->basis2);
      n=chgcar->ny;
      sigma=sy;
      break;
    case 2:
      b=veclength3d(chgcar->structure->basis3);
      n=chgcar->nz;
      sigma=sz;
      break;
    default:
      return 0.0;
  }
  if (sigma<=0.0){
    return 0.0;
  }
  return b*b/(n*n*2.0*sigma*sigma);
}

ChgcarPlaneProcess::~ChgcarPlaneProcess(){
  chgcar->unlock();
  if (plane!=NULL){
    delete plane;
    plane=NULL;
  }
  delete wx;
  wx=NULL;
  delete wy;
  wy=NULL;
  delete wz;
  wz=NULL;
}

FArray2D *ChgcarPlaneProcess::getPlane(){
  return plane->clone();
}

long ChgcarPlaneProcess::next(){
  is_status=true;
  is_error=false;
  sprintf(buff,"Smoothing %ld %s plane.",n,planeName());
  if (_step<_total){
    for (long i=0; i<dim;i++){
      double sum=0.0;
      switch(dir){
        case 0:
	  for (int jx=-dx;jx<=dx;jx++){
	    for (int jy=-dy;jy<=dy;jy++){
	      for (int jz=-dz;jz<=dz;jz++){
	        sum+=wx[dx+jx]*wy[dy+jy]*wz[dz+jz]*chgcar->get(n+jx,_step+jy,i+jz);
	      }
	    }
	  }
	  break;
	case 1:
	  for (int jx=-dx;jx<=dx;jx++){
	    for (int jy=-dy;jy<=dy;jy++){
	      for (int jz=-dz;jz<=dz;jz++){
	        sum+=wx[dx+jx]*wy[dy+jy]*wz[dz+jz]*chgcar->get(_step+jx,n+jy,i+jz);
	      }
	    }
	  }
	  break;
	default:
	  for (int jx=-dx;jx<=dx;jx++){
	    for (int jy=-dy;jy<=dy;jy++){
	      for (int jz=-dz;jz<=dz;jz++){
	        sum+=wx[dx+jx]*wy[dy+jy]*wz[dz+jz]*chgcar->get(_step+jx,i+jy,n+jz);
	      }
	    }
	  }
	  break;
      }
      plane->set(_step,i,sum);
    }
    _step++;
    return _step;
  }
  return 0;
}
