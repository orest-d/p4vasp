#include <p4vasp/FArray.h>
#include <p4vasp/utils.h>
#include <math.h>
#include <locale.h>

const char *FArray1D::getClassName(){
  return "FArray1D";
}

const char *FArray1DWrap::getClassName(){
  return "FArray1D";
}

const char *FArray2D::getClassName(){
  return "FArray2D";
}

void FArray1D::clear(){
  for (long i=0; i<_size; i++){
    d[i]=0.0;
  }
}

void FArray2D::clear(){
  long size=sizex*sizey;
  for (long i=0; i<size; i++){
    d[i]=0.0;
  }
}

double FArray1D::getMinimum(){
  if (_size<=0){
    THROW_EXC("getMinimum() called for an empty array");
  }
  double val=d[0];
  for (long i=1; i<_size; i++){
    if (d[i]<val){
      val=d[i];
    }
  }
  return val;
}

double FArray1D::getMaximum(){
  if (_size<=0){
    THROW_EXC("getMaximum() called for an empty array");
  }
  double val=d[0];
  for (long i=1; i<_size; i++){
    if (d[i]>val){
      val=d[i];
    }
  }
  return val;
}

double FArray1D::getAverage(){
  if (_size<=0){
    THROW_EXC("getAverage() called for an empty array");
  }
  double val=0.0;
  for (long i=0; i<_size; i++){
    val+=d[i];
  }
  return val/_size;
}

double FArray1D::getVariance(){
  if (_size<=0){
    THROW_EXC("getVariance() called for an empty array");
  }
  double val=0.0,val2=0.0;
  for (long i=0; i<_size; i++){
    val+=d[i];
    val2+=d[i]*d[i];
  }
  val/=_size;
  val2/=_size;
  return val2-val*val;
}

double FArray1D::getSigma(){
  if (_size<=1){
    THROW_EXC("getSigma() called for an array with size<=1");
  }
  return sqrt(_size*getVariance()/(_size-1));
}





double FArray2D::getMinimum(){
  long size=sizex*sizey;
  if (size<=0){
    THROW_EXC("getMinimum() called for an empty array");
  }
  double val=d[0];
  for (long i=1; i<size; i++){
    if (d[i]<val){
      val=d[i];
    }
  }
  return val;
}

double FArray2D::getMaximum(){
  long size=sizex*sizey;
  if (size<=0){
    THROW_EXC("getMaximum() called for an empty array");
  }
  double val=d[0];
  for (long i=1; i<size; i++){
    if (d[i]>val){
      val=d[i];
    }
  }
  return val;
}

double FArray2D::getAverage(){
  long size=sizex*sizey;
  if (size<=0){
    THROW_EXC("getAverage() called for an empty array");
  }
  double val=0.0;
  for (long i=0; i<size; i++){
    val+=d[i];
  }
  return val/size;
}

double FArray2D::getVariance(){
  long size=sizex*sizey;
  if (size<=0){
    THROW_EXC("getVariance() called for an empty array");
  }
  double val=0.0,val2=0.0;
  for (long i=0; i<size; i++){
    val+=d[i];
    val2+=d[i]*d[i];
  }
  val/=size;
  val2/=size;
  return val2-val*val;
}

double FArray2D::getSigma(){
  long size=sizex*sizey;
  if (size<=1){
    THROW_EXC("getSigma() called for an array with size<=1");
  }
  return sqrt(size*getVariance()/(size-1));
}

double FArray1D::get(long i){
#if CHECK>0
  if ((i<0) || (i>=_size)){
    THROW_R_EXC("FArray1D::get()",0,_size-1,i);
  }
#endif
  return d[i];
}

void FArray1D::set(long i,double x){
#if VERBOSE>1
  printf("FArray1D::set(%3ld,%+14.8f)\n",i,x);
#endif
#if CHECK>0
  if ((i<0) || (i>=_size)){
    THROW_R_EXC("FArray1D::get()",0,_size-1,i);
  }
#endif
  d[i]=x;
}

double FArray2D::get(long i,long j){
#if CHECK>0
  if ((i<0) || (i>=sizex)){
    THROW_R_EXC("FArray2D::get() - first index",0,sizex-1,i);
  }
  if ((j<0) || (j>=sizey)){
    THROW_R_EXC("FArray2D::get() - second index",0,sizey-1,j);
  }
#endif
  return d[i*sizey+j];
}

FArray1D *FArray2D::getArray(long i){
#if CHECK>0
  if ((i<0) || (i>=sizex)){
    THROW_R_EXC("FArray2D::get() - first index",0,sizex-1,i);
  }
#endif
  return new FArray1DWrap(&d[i*sizey],sizey);
}

void FArray2D::set(long i,long j,double x){
#if CHECK>0
  if ((i<0) || (i>=sizex)){
    THROW_R_EXC("FArray2D::set() - first index",0,sizex-1,i);
  }
  if ((j<0) || (j>=sizey)){
    THROW_R_EXC("FArray2D::set() - second index",0,sizey-1,j);
  }
#endif
  d[i*sizey+j]=x;
}

void FArray1D::printrepr(){
  printf("FArray1D(%ld){\n",_size);
  for (long i=0;i<_size;i++){
    printf("  %3ld : %+14.8f\n",i,d[i]);
  }
  printf("}\n");
}

void FArray2D::printrepr(){
  printf("FArray2D(%ld,%ld){\n",sizex,sizey);
  for (long i=0;i<sizex;i++){
    for (long j=0;j<sizey;j++){
      printf("  %3ld,%3ld : %+14.8f\n",i,j,get(i,j));
    }
  }
  printf("}\n");
}

void FArray1D::parseStringDestructively(char *s){
  char **w=splitWords(s);
  setlocale (LC_ALL,"C");
  if (w!=NULL){
    for (long i=0; i<_size; i++){
      if (w[i]==NULL){
        break;
      }
      d[i]=atof(w[i]);
    }
    delete w;
  }
}

void FArray2D::parseStringDestructively(long i,char *s){
  char **w=splitWords(s);
  setlocale (LC_ALL,"C");
  if (w!=NULL){
    for (long j=0; j<sizey; j++){
      if (w[j]==NULL){
        break;
      }
      set(i,j,atof(w[j]));
    }
    delete w;
  }
}

double *FArray2D::cloneVector(long i){
#if CHECK>0
  if ((i<0) || (i>=sizex)){
    THROW_R_EXC("FArray2D::cloneVector()",0,sizex-1,i);
  }
#endif
  double *b=new double[sizey];
  memcpy(b,&d[i*sizey],sizeof(double)*sizey);
  return b;
}


inline double cifunc(double x,double y0,double y1,double y2,double y3){
  double a=0.5*( -y0+3*y1-3*y2+y3);
  double b=0.5*(2*y0-5*y1+4*y2-y3);
  double c=0.5*(  y2-  y0);
  double d=y1;
  return a*x*x*x+b*x*x+c*x+d;
}

FArray2D *FArray2D::cubicInterpolation(int n,int m){
  if (n<0) n=0;
  if (m<0) m=0;
  if ((n==0)&&(m==0)){
    return this->clone();
  }

  FArray2D *a = new FArray2D(n*sizex,m*sizey);
  for (int i=0; i<sizex;i++){
    for (int j=0; j<sizey;j++){
//      double y11=get((i-1+sizex)%sizex,(j-1+sizey)%sizey);
      double y12=get((i        )%sizex,(j-1+sizey)%sizey);
      double y13=get((i+1      )%sizex,(j-1+sizey)%sizey);
//      double y14=get((i+2      )%sizex,(j-1+sizey)%sizey);
      double y21=get((i-1+sizex)%sizex,(j        )%sizey);
      double y22=get((i        )%sizex,(j        )%sizey);
      double y23=get((i+1      )%sizex,(j        )%sizey);
      double y24=get((i+2      )%sizex,(j        )%sizey);
      double y31=get((i-1+sizex)%sizex,(j+1      )%sizey);
      double y32=get((i        )%sizex,(j+1      )%sizey);
      double y33=get((i+1      )%sizex,(j+1      )%sizey);
      double y34=get((i+2      )%sizex,(j+1      )%sizey);
//      double y41=get((i-1+sizex)%sizex,(j+2      )%sizey);
      double y42=get((i        )%sizex,(j+2      )%sizey);
      double y43=get((i+1      )%sizex,(j+2      )%sizey);
//      double y44=get((i+2      )%sizex,(j+2      )%sizey);
      for (int ii=0; ii<=n;ii++){
        double x=double(ii)/n;
        long I=n*i+ii;
	if (I>=n*sizex){
	  continue;
	}
	for (int jj=0; jj<=m;jj++){
	  long J=m*j+jj;
	  if (J>=m*sizey){
	    continue;
	  }
          double y=double(jj)/m;

          double fa=cifunc(x,y21,y22,y23,y24);
          double fb=cifunc(x,y31,y32,y33,y34);
          double fc=cifunc(y,y12,y22,y32,y42);
          double fd=cifunc(y,y13,y23,y33,y43);
	  a->set(I,J,0.5*(fa*(1-y)+fb*y+fc*(1-x)+fd*x));
	}
      }
    }
  }
  return a;
}

FArray1DWrap::~FArray1DWrap(){
  _size=0;
  d=NULL;
}

FArray1D::~FArray1D(){
  _size=0;
  if (d!=NULL){
    delete d;
  }
  d=NULL;
}

FArray2D::~FArray2D(){
  sizex=0;
  sizey=0;
  if (d!=NULL){
    delete d;
  }
  d=NULL;
}

FArray2D *FArray2D::smear(double sigma,int n,int m,double *u,double *v){
  double *w=new double[(2*n+1)*(2*m+1)];
  double x,y,z;
  for (int i=-n;i<=n;i++){
    for (int j=-m;j<=m;j++){
      x=i*u[0]/sizex+j*v[0]/sizey;
      y=i*u[1]/sizex+j*v[1]/sizey;
      z=i*u[2]/sizex+j*v[2]/sizey;
      double l=sqrt(x*x+y*y+z*z);
      w[n+i+(2*n+1)*(m+j)]=exp(-0.5*l*l/sigma);
    }
  }
  int N=(2*n+1)*(2*m+1);
  double sum=0;
  for (int i=0;i<N;i++){
    sum+=w[i];
  }
  for (int i=0;i<N;i++){
    w[i]/=sum;
  }
  FArray2D *a=new FArray2D(sizex,sizey);
  for (int I=0;I<sizex;I++){
    for (int J=0;J<sizey;J++){
      double sum=0;
      for (int i=-n; i<=n; i++){
	for (int j=-m; j<=m; j++){
	  sum+=w[n+i+(2*n+1)*(m+j)]*get((I+sizex+i)%sizex,(J+sizey+j)%sizey);
	}
      }
      a->set(I,J,sum);
    }
  }
  return a;
}
