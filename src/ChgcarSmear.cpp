#include <p4vasp/ChgcarSmear.h>
#include <p4vasp/vecutils3d.h>

const char *ChgcarSmear::getClassName(){
  return "ChgcarSmear";
}

ChgcarSmear::~ChgcarSmear(){
}

void ChgcarSmear::setChgcar(Chgcar *c){
  chgcar=c;
}

double ChgcarSmear::get(int i,int j, int k){
#if CHECK>1
  if (chgcar==NULL){
    THROW_NP_EXC("Chgcar not set in ChgcarSmear.get(i,j,k).");
  }
#endif  
  return chgcar->get(i,j,k);
}

const char *GaussianChgcarSmear::getClassName(){
  return "GaussianChgcarSmear";
}

GaussianChgcarSmear::~GaussianChgcarSmear(){
  if (w !=NULL){
    delete w;
    w=NULL;
  }
}

void GaussianChgcarSmear::setChgcar(Chgcar *c){
#if VERBOSE>0
  printf("GaussianChgcarSmear::setChgcar(c)\n");
#endif  
  chgcar=c;
  if (w!=NULL){
    delete w;    
  }
//  printf("Lb %3d %3d %3d\n",lx,ly,lz);
  if (lx<0) lx=0;
  if (ly<0) ly=0;
  if (lz<0) lz=0;
//  printf("La %3d %3d %3d\n",lx,ly,lz);
  int N=(lx*2+1)*(ly*2+1)*(lz*2+1);
  w=new double[N];
  double *p=w;
  for (int i=0;i<N;i++){
    *p++=0.0;
  }
  double x,y,z;
  int nx=c->nx;
  int ny=c->ny;
  int nz=c->nz;
  double *basis1=c->structure->basis1;
  double *basis2=c->structure->basis2;
  double *basis3=c->structure->basis3;
  for(int i=-lx;i<=lx;i++){
    for(int j=-ly;j<=ly;j++){
      for(int k=-lz;k<=lz;k++){
	x=i*basis1[0]/nx + j*basis2[0]/ny + k*basis3[0]/nz;
	y=i*basis1[1]/nx + j*basis2[1]/ny + k*basis3[1]/nz;
	z=i*basis1[2]/nx + j*basis2[2]/ny + k*basis3[2]/nz;
	double lh=0.0,lv=0.0;
	switch (dir){
	  case 0:
	    lv=x*x;
	    lh=y*y+z*z;
	    break;
	  case 1:
	    lv=y*y;
	    lh=x*x+z*z;
	    break;
	  case 2:
	  default:
	    lv=z*z;
	    lh=x*x+y*y;
	    break;
	}

        w[(lx+i)+(2*lx+1)*(ly+j)+(2*lx+1)*(2*ly+1)*(lz+k)]=
        exp(-lh/(2*horizontal_sigma*horizontal_sigma)
	-lv/(2*vertical_sigma*vertical_sigma));
//	printf("w %+2d %+2d %+2d | %+10.5f %+10.5f %+10.5f :%12.10f\n",
//	i,j,k,x,y,z,w[(lx+i)+(2*lx+1)*(ly+j)+(2*lx+1)*(2*ly+1)*(lz+k)]);
      }
    }
  }
  double sum=0.0;
  p=w;
  for (int i=0;i<N;i++){
    sum+=*p++;
  }
  p=w;
  for (int i=0;i<N;i++){
    (*p)/=sum;
    p++;
  }  
#if VERBOSE>0
  printf("GaussianChgcarSmear::setChgcar(c) -\n");
#endif
}

double GaussianChgcarSmear::get(int I,int J, int K){
#if CHECK>1
  if (chgcar==NULL){
    THROW_NP_EXC("Chgcar not set in GaussianChgcarSmear.get(i,j,k).");
  }
#endif  
  double sum=0.0;  
  for(int i=-lx;i<=lx;i++){
    for(int j=-ly;j<=ly;j++){
      for(int k=-lz;k<=lz;k++){
//        printf("ijk %+2d %+2d %+2d w=%12.8f\n",i,j,k,w[(lx+i)+(2*lx+1)*(ly+j)+(2*lx+1)*(2*ly+1)*(lz+k)]);
       
sum+=w[(lx+i)+(2*lx+1)*(ly+j)+(2*lx+1)*(2*ly+1)*(lz+k)]*chgcar->get(I+i,J+j,K+k);
      }
    }
  }
//  printf("get %3d %3d %3d %12.8f -> %12.8f\n",I,J,K,chgcar->get(I,J,K),sum);
  return sum;
}


ChgcarSmearProcess::ChgcarSmearProcess(Chgcar *c,ChgcarSmear *s,int pstep){
  chgcar=c;
  smear=s;
  s->setChgcar(c);
  smeared=c->clone();
//  chgcar->lock();
  this->pstep=pstep;
  _step=0;  
  _total=c->nx*c->ny*c->nz;
}

long ChgcarSmearProcess::next(){
  int nx=chgcar->nx;
  int ny=chgcar->ny;
//  int nz=chgcar->nz;
  
  is_status=true;  
  is_error=false;  
  sprintf(buff,"Smoothing density %ld/%ld.",_step,_total);
  for (int i=0; i<pstep; i++){
    if (_step>=_total){
      return 0;
    }
    int I=_step%(nx*ny);
    int J=(_step/nx)%ny;
    int K=_step/(nx*ny);
//    printf("%3d %3d %3d ->%+10.6f\n",I,J,K,smear->get(I,J,K));
    smeared->set(I,J,K,smear->get(I,J,K));
    _step++;
  }
  return _step;
}

Chgcar *ChgcarSmearProcess::get(){
  return smeared;
}

ChgcarSmearProcess::~ChgcarSmearProcess(){
//  chgcar->unlock();
  chgcar=NULL;
  smear=NULL;
  if (smeared!=NULL){
    delete smeared;
    smeared=NULL;
  }
}

ChgcarSmearPlaneProcess::~ChgcarSmearPlaneProcess(){
  chgcar->unlock();
  smear=NULL;
  if (plane!=NULL){
    delete plane;
    plane=NULL;
  }
}

FArray2D *ChgcarSmearPlaneProcess::getPlane(){
  return plane->clone();
}

const char *ChgcarSmearProcess::getClassName(){
  return "ChgcarSmearProcess";
}

const char *ChgcarSmearPlaneProcess::getClassName(){
  return "ChgcarSmearPlaneProcess";
}

long ChgcarSmearPlaneProcess::next(){
  is_status=true;  
  is_error=false;  
  sprintf(buff,"Smoothing %s plane %ld/%ld.",planeName(),_step,_total);
  int nx=chgcar->nx;
  int ny=chgcar->ny;
//  int nz=chgcar->nz;
  switch(dir){
    case 0:
      for (int i=0; i<pstep; i++){
	if (_step>=_total){
	  return 0;
	}
	int I=_step%ny;
	int J=_step/ny;
	plane->set(I,J,smear->get(n,I,J));
	_step++;
      }
      break;
    case 1:
      for (int i=0; i<pstep; i++){
	if (_step>=_total){
	  return 0;
	}
	int I=_step%nx;
	int J=_step/nx;
	plane->set(I,J,smear->get(I,n,J));
	_step++;
      }
      break;
    case 2:
    default:
      for (int i=0; i<pstep; i++){
	if (_step>=_total){
	  return 0;
	}
	int I=_step%nx;
	int J=_step/nx;
	plane->set(I,J,smear->get(I,J,n));
	_step++;
      }
      break;
  }
  return _step;
}

void STMSearchProcess::update(){
  if (plane!=NULL){
    delete plane;
    plane=NULL;
  }
  if (chgcar==NULL){
    Nz=0;
    N=0;
    M=0;
    Z=1.0;
  }
  else{
    if (smear!=NULL){
      smear->setChgcar(chgcar);
    }
    switch(dir){
      case 0:
	if (autoplane||(n0<0)){
 	  n0=chgcar->searchMinPlaneX();
	}
	Nz=chgcar->nx;
	N=chgcar->ny;
	M=chgcar->nz;
	Z=veclength3d(chgcar->structure->basis1);
	break;
      case 1:
	if (autoplane||(n0<0)){
          n0=chgcar->searchMinPlaneY();
	}
	Nz=chgcar->ny;
	N=chgcar->nx;
	M=chgcar->nz;
	Z=veclength3d(chgcar->structure->basis2);
	break;
      case 2:
      default:
	if (autoplane||(n0<0)){
	  n0=chgcar->searchMinPlaneZ();
	}
	Nz=chgcar->nz;
	N=chgcar->nx;
	M=chgcar->ny;
	Z=veclength3d(chgcar->structure->basis3);
	break;
    }
    plane=new FArray2D(N,M);
    plane->clear();
  }
  _total=N*M;
  _step=0;
}

STMSearchProcess::STMSearchProcess(Chgcar *c,double val,ChgcarSmear *s,
int n0,int dir,int delta,int pstep,int mode){
  chgcar=c;
  smear=s;
  value=val;
  this->mode=mode;
  this->dir=dir;
  this->delta=delta;
  this->pstep=pstep;
  plane=NULL;
  this->n0=n0;
  autoplane=(n0<0);  
  update();
}


const char *STMSearchProcess::getClassName(){
  return "STMSearchProcess";
}
FArray2D *STMSearchProcess::getPlane(){
  if (plane ==NULL){
    return NULL;
  }
  return plane->clone();
}

int STMSearchProcess::processAll(){
  switch (mode){
    case 0:
      for (int I=0; I<N; I++){
        for (int J=0; J<M; J++){
 	  plane->set(I,J,getHeightFast(I,J));
	}
      }
      break;
    case 1:
      if (smear==NULL){
        return -1;
      }
      for (int I=0; I<N; I++){
        for (int J=0; J<M; J++){
  	  plane->set(I,J,getHeightSlow(I,J));
	}
      }
      break;
    case 2:
      for (int I=0; I<N; I++){
        for (int J=0; J<M; J++){
  	  plane->set(I,J,getHeightFastCubic(I,J));
	}
      }
      break;
    case 3:
      if (smear==NULL){
        return -1;
      }
      for (int I=0; I<N; I++){
        for (int J=0; J<M; J++){
  	  plane->set(I,J,getHeightSlowCubic(I,J));
	}
      }
      break;
  }
  return 0;
}

long STMSearchProcess::next(){
  is_status=true;  
  is_error=false;  
  sprintf(buff,"STM constant current isosurface creation %ld/%ld.",_step,_total);
  switch (mode){
    case 0:
      for (int i=0; i<pstep; i++){
	if (_step>=_total){
	  return 0;
	}
	int I=_step%N;
	int J=_step/N;
	plane->set(I,J,getHeightFast(I,J));
	_step++;
      }
      break;
    case 1:
      for (int i=0; i<pstep; i++){
	if (_step>=_total){
	  return 0;
	}
	int I=_step%N;
	int J=_step/N;
	plane->set(I,J,getHeightSlow(I,J));
	_step++;
      }
      break;
    case 2:
      for (int i=0; i<pstep; i++){
	if (_step>=_total){
	  return 0;
	}
	int I=_step%N;
	int J=_step/N;
	plane->set(I,J,getHeightFastCubic(I,J));
	_step++;
      }
      break;
    case 3:
      for (int i=0; i<pstep; i++){
	if (_step>=_total){
	  return 0;
	}
	int I=_step%N;
	int J=_step/N;
	plane->set(I,J,getHeightSlowCubic(I,J));
	_step++;
      }
      break;
  }
  return _step;
}

int STMSearchProcess::searchFast(int I,int J){
  switch(dir){
    case 0:
      if (delta<=0){
        for (int i=n0; i>=n0-Nz; i--){
	  if (chgcar->get(i,I,J)>=value){
	    return i;
	  }
	}
      }
      else{
        for (int i=n0; i<n0+Nz; i++){
	  if (chgcar->get(i,I,J)>=value){
	    return i;
	  }
	}
      }
      break;
    case 1:
      if (delta<=0){
        for (int i=n0; i>=n0-Nz; i--){
	  if (chgcar->get(I,i,J)>=value){
	    return i;
	  }
	}
      }
      else{
        for (int i=n0; i<n0+Nz; i++){
	  if (chgcar->get(I,i,J)>=value){
	    return i;
	  }
	}
      }
      break;
    case 2:
    default:
      if (delta<=0){
        for (int i=n0; i>=n0-Nz; i--){
	  if (chgcar->get(I,J,i)>=value){
	    return i;
	  }
	}
      }
      else{
        for (int i=n0; i<n0+Nz; i++){
	  if (chgcar->get(I,J,i)>=value){
	    return i;
	  }
	}
      }
      break;
  }
//  printf("FAIL\n");
  return -2*Nz;
}

int STMSearchProcess::searchSlow(int I,int J){
  switch(dir){
    case 0:
      if (delta<=0){
        for (int i=n0; i>=n0-Nz; i--){
	  if (smear->get(i,I,J)>=value){
	    return i;
	  }
	}
      }
      else{
        for (int i=n0; i<n0+Nz; i++){
	  if (smear->get(i,I,J)>=value){
	    return i;
	  }
	}
      }
      break;
    case 1:
      if (delta<=0){
        for (int i=n0; i>=n0-Nz; i--){
	  if (smear->get(I,i,J)>=value){
	    return i;
	  }
	}
      }
      else{
        for (int i=n0; i<n0+Nz; i++){
	  if (smear->get(I,i,J)>=value){
	    return i;
	  }
	}
      }
      break;
    case 2:
    default:
      if (delta<=0){
        for (int i=n0; i>=n0-Nz; i--){
	  if (smear->get(I,J,i)>=value){
	    return i;
	  }
	}
      }
      else{
        for (int i=n0; i<n0+Nz; i++){
	  if (smear->get(I,J,i)>=value){
	    return i;
	  }
	}
      }
      break;
  }
  return -1;
}

double STMSearchProcess::getHeightFast(int I,int J){
  int i1=searchFast(I,J);
  if (i1<=-2*Nz){
    return 0.0;
  }
  int i2=(delta<=0)?(i1+1):(i1-1);
  double y1,y2;
  switch(dir){
    case 0:
      y1=chgcar->get(i1,I,J);
      y2=chgcar->get(i2,I,J);
      break;
    case 1:
      y1=chgcar->get(I,i1,J);
      y2=chgcar->get(I,i2,J);
      break;
    case 2:
    default:
      y1=chgcar->get(I,J,i1);
      y2=chgcar->get(I,J,i2);
      break;
  }
  double x1=i1*Z/Nz;
  double x2=i2*Z/Nz;
//  printf("Fast %3d %3d: i(%3d %3d) v1(%+10.6f %+10.6f) v2(%+10.6f %+10.6f)\n",
//  I,J,i1,i2,x1,y1,x2,y2);
  if (y2==y1){
    return x1;
  }
  return x1+(x2-x1)*(value-y1)/(y2-y1);
}

double STMSearchProcess::getHeightFastCubic(int I,int J){
  int i0,i1,i2,i3;
  i1=searchFast(I,J);
  if (i1<=-2*Nz){
    return 0.0;
  }
  if (delta<=0){
    i0=i1-1;
    i2=i1+1;
    i3=i1+2;
  }
  else{
    i0=i1+1;
    i2=i1-1;
    i3=i1-2;
  }
  
  double y0,y1,y2,y3;
  switch(dir){
    case 0:
      y0=chgcar->get(i0,I,J);
      y1=chgcar->get(i1,I,J);
      y2=chgcar->get(i2,I,J);
      y3=chgcar->get(i3,I,J);
      break;
    case 1:
      y0=chgcar->get(I,i0,J);
      y1=chgcar->get(I,i1,J);
      y2=chgcar->get(I,i2,J);
      y3=chgcar->get(I,i3,J);
      break;
    case 2:
    default:
      y0=chgcar->get(I,J,i0);
      y1=chgcar->get(I,J,i1);
      y2=chgcar->get(I,J,i2);
      y3=chgcar->get(I,J,i3);
      break;
  }

  double a=0.5*( -y0+3*y1-3*y2+y3);
  double b=0.5*(2*y0-5*y1+4*y2-y3);
  double c=0.5*(  y2-  y0);
  double d=y1-value;
  double p=(3*a*c-b*b)/(9*a*a);
  double q=b*b*b/(27*a*a*a)-b*c/(6*a*a)+d/(2*a);
  double D=q*q+p*p*p;
//  double li=(value-y1)/(y2-y1);
//  if (fabs(li)>1.0){
//    printf("!!! li=%8.4f\n",li);
//  }
  if (D>=0){
    D=sqrt(D);
    double u=-q+D,v=-q-D;
    u=(u>=0)?(pow(u,1.0/3)):(-pow(-u,1.0/3));
    v=(v>=0)?(pow(v,1.0/3)):(-pow(-v,1.0/3));
//    printf("%3d %3d single:%+8.4f %+8.4f %+8.4f\n",
//    I,J,u+v-b/(3*a),li,u+v-b/(3*a)-li);
    return (i1+u+v-b/(3*a))*Z/Nz;
  }
  else{
    double r=(q>=0)?(sqrt(fabs(p))):(-sqrt(fabs(p)));
    double o=acos(q/(r*r*r));
    double x1=-2*r*cos(o/3)-b/(3*a);
    double x2=+2*r*cos(o/3-M_PI/3)-b/(3*a);
    double x3=+2*r*cos(o/3+M_PI/3)-b/(3*a);
//    printf("%3d %3d Multi :%+8.4f %+8.4f %+8.4f\n",I,J,x1,x2,x3);
    if (order(x1,x2,x3)){
//      printf("            1 :%+8.4f %+8.4f %+8.4f\n",x1,li,x1-li);
      return (i1+x1)*Z/Nz;
    }
    if (order(x2,x1,x3)){
//      printf("            2 :%+8.4f %+8.4f %+8.4f\n",x2,li,x2-li);
      return (i1+x2)*Z/Nz;
    }
    if (order(x3,x2,x1)){
//      printf("            3 :%+8.4f %+8.4f %+8.4f\n",x3,li,x3-li);
      return (i1+x3)*Z/Nz;
    }
//      printf("            0 :%+8.4f %+8.4f %+8.4f\n",x1,li,x1-li);
    return (i1+x1)*Z/Nz;
  }
}

double STMSearchProcess::getHeightSlow(int I,int J){
  int i1=searchSlow(I,J);
  int i2=(delta<=0)?(i1+1):(i1-1);
  double y1,y2;
  switch(dir){
    case 0:
      y1=smear->get(i1,I,J);
      y2=smear->get(i2,I,J);
      break;
    case 1:
      y1=smear->get(I,i1,J);
      y2=smear->get(I,i2,J);
      break;
    case 2:
    default:
      y1=smear->get(I,J,i1);
      y2=smear->get(I,J,i2);
      break;
  }
  double x1=i1*Z/Nz;
  double x2=i2*Z/Nz;
//  printf("Slow %3d %3d: i(%3d %3d) v1(%+10.6f %+10.6f) v2(%+10.6f %+10.6f)\n",
//  I,J,i1,i2,x1,y1,x2,y2);
  if (y2==y1){
    return x1;
  }
  return x1+(x2-x1)*(value-y1)/(y2-y1);
}

double STMSearchProcess::getHeightSlowCubic(int I,int J){
  int i0,i1,i2,i3;
  i1=searchSlow(I,J);
  if (delta<=0){
    i0=i1-1;
    i2=i1+1;
    i3=i1+2;
  }
  else{
    i0=i1+1;
    i2=i1-1;
    i3=i1-2;
  }
  
  double y0,y1,y2,y3;
  switch(dir){
    case 0:
      y0=smear->get(i0,I,J);
      y1=smear->get(i1,I,J);
      y2=smear->get(i2,I,J);
      y3=smear->get(i3,I,J);
      break;
    case 1:
      y0=smear->get(I,i0,J);
      y1=smear->get(I,i1,J);
      y2=smear->get(I,i2,J);
      y3=smear->get(I,i3,J);
      break;
    case 2:
    default:
      y0=smear->get(I,J,i0);
      y1=smear->get(I,J,i1);
      y2=smear->get(I,J,i2);
      y3=smear->get(I,J,i3);
      break;
  }

  double a=0.5*( -y0+3*y1-3*y2+y3);
  double b=0.5*(2*y0-5*y1+4*y2-y3);
  double c=0.5*(  y2-  y0);
  double d=y1-value;
  double p=(3*a*c-b*b)/(9*a*a);
  double q=b*b*b/(27*a*a*a)-b*c/(6*a*a)+d/(2*a);
  double D=q*q+p*p*p;
  if (D>=0){
    D=sqrt(D);
    double u=-q+D,v=-q-D;
    u=(u>=0)?(pow(u,1.0/3)):(-pow(-u,1.0/3));
    v=(v>=0)?(pow(v,1.0/3)):(-pow(-v,1.0/3));
    
    return (i1+u+v-b/(3*a))*Z/Nz;
  }
  else{
    double r=(q>=0)?(sqrt(fabs(p))):(-sqrt(fabs(p)));
    double o=acos(q/(r*r*r));
    double x1=-2*r*cos(o/3)-b/(3*a);
    double x2=+2*r*cos(o/3-M_PI/3)-b/(3*a);
    double x3=+2*r*cos(o/3+M_PI/3)-b/(3*a);
    if (order(x1,x2,x3)){
      return x1;
    }
    if (order(x2,x1,x3)){
      return x2;
    }
    if (order(x3,x2,x1)){
      return x3;
    }
    return x1;
  }
}


STMSearchProcess::~STMSearchProcess(){
  chgcar->unlock();
  smear=NULL;
  if (plane!=NULL){
    delete plane;
    plane=NULL;
  }
}
