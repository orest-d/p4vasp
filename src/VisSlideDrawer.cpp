#include <p4vasp/VisSlideDrawer.h>
#include <math.h>

const char *Clamp::getClassName(){
  return "Clamp";
}

const char *ThresholdClamp::getClassName(){
  return "ThresholdClamp";
}
double ThresholdClamp::f(double x){
  if (x<0.0){
    return 0.0;
  }
  if (x>1.0){
    return 1.0;
  }
  return x;
}

const char *SawtoothClamp::getClassName(){
  return "SawtoothClamp";
}
double SawtoothClamp::f(double x){
//  x=(x-lo)/(hi-lo);  
  return 1.0-fabs(fmod(fabs(x),2.0)-1.0);
}

const char *CosClamp::getClassName(){
  return "CosClamp";
}
double CosClamp::f(double x){
  if (x<0.0){
    return 0.0;
  }
  if (x>1.0){
    return 1.0;
  }
//  x=(x-lo)/(hi-lo);  
  return 0.5+0.5*sin(M_PI*(x-0.5));
}

const char *WaveClamp::getClassName(){
  return "WaveClamp";
}
double WaveClamp::f(double x){
//  x=(x-lo)/(hi-lo);  
  return 0.5+0.5*sin(M_PI*(x-0.5));
}

const char *AtanClamp::getClassName(){
  return "AtanClamp";
}
double AtanClamp::f(double x){
//  x=(x-lo)/(hi-lo);
  return 0.5+atan(4*x-2)/M_PI;
}

const char *FermiClamp::getClassName(){
  return "FermiClamp";
}

double FermiClamp::f(double x){
//  x=(x-lo)/(hi-lo);
  return 1.0/(1.0+exp(2.0-4.0*x));
}


const char *ColorGradient::getClassName(){
  return "ColorGradient";
}


void ColorGradient::glcolor(double x){  
  glColor3fv(f(x));
}

const char *GrayColorGradient::getClassName(){
  return "GrayColorGradient";
}

GLfloat *GrayColorGradient::f(double x){
  color[0]=x;
  color[1]=x;
  color[2]=x;
  return color;
}

const char *RainbowColorGradient::getClassName(){
  return "RainbowColorGradient";
}

GLfloat *RainbowColorGradient::f(double x){
  double xx=x;  
  if (x<0.0){
    x=0.0;
  }
  if (x>1.0){
    x=1.0;
  }
  int type=int(x*6.0)%6;
  x=x*6-type;
  double xp=1.0-saturation+(value-1.0+saturation)*x;
  double xm=1.0-saturation+(value-1.0+saturation)*(1.0-x);
  switch(type){
    case 0:
      color[0]=value;
      color[1]=xp;
      color[2]=1.0-saturation;
      break;
    case 1:
      color[0]=xm;
      color[1]=value;
      color[2]=1.0-saturation;
      break;
    case 2:
      color[0]=1.0-saturation;
      color[1]=value;
      color[2]=xp;
      break;
    case 3:
      color[0]=1.0-saturation;
      color[1]=xm;
      color[2]=value;
      break;
    case 4:
      color[0]=xp;
      color[1]=1.0-saturation;
      color[2]=value;
      break;
    case 5:
      color[0]=value;
      color[1]=1.0-saturation;
      color[2]=xm;
      break;
    default:
      printf("Warning: RainbowColorGradient::f(%f) type=%d\n",xx,type);
      color[0]=0.0;
      color[1]=0.0;
      color[2]=0.0;      
  }
  return color;
}

const char *VisSlideDrawer::getClassName(){
  return "VisSlideDrawer";
}

void VisSlideDrawer::vertex(int i,int j,double *h){
  long sx=a->sizeX();
  long sy=a->sizeY();
  
  double c =a->get((i+16*sx  )%sx,(j+16*sy  )%sy);
  double x1=a->get((i+16*sx+1)%sx,(j+16*sy  )%sy);
  double x2=a->get((i+16*sx-1)%sx,(j+16*sy  )%sy);
  double y1=a->get((i+16*sx  )%sx,(j+16*sy+1)%sy);
  double y2=a->get((i+16*sx  )%sx,(j+16*sy-1)%sy);
  double dx=x2-x1;
  double dy=y2-y1;  
  glcolor(c);
  glNormal3d(dx,-dy,1);
  glVertex3d(i,j,c);  
}

void VisSlideDrawer::setShadow(int f){
  shadowflag=f;
  redraw();
}

void VisSlideDrawer::draw(){
  double h[3];
  GLdouble M[16];
  GLboolean sflag=glIsEnabled(GL_LIGHTING);
  if (a!=NULL){
    if (shadowflag==0){
      glDisable(GL_LIGHTING);
    }
    else if (shadowflag==1){
      glEnable(GL_LIGHTING);
    }
    assureClampAndGradient();
    crossprod3d(h,b1,b2);
    normalize3d(h);
    scalmul3d(h,scale);
    /*
    printf("SLIDE:\n");
    printf("  b1 %p %+10.6f %+10.6f %+10.6f\n",b1,b1[0],b1[1],b1[2]);
    printf("  b2 %p %+10.6f %+10.6f %+10.6f\n",b2,b2[0],b2[1],b2[2]);
    printf("  size: %3ld %3ld\n",a->sizeX(),a->sizeY());*/
    M[ 0]=b1[0]/a->sizeX();
    M[ 1]=b1[1]/a->sizeX();
    M[ 2]=b1[2]/a->sizeX();
    M[ 3]=0;
    M[ 4]=b2[0]/a->sizeY();
    M[ 5]=b2[1]/a->sizeY();
    M[ 6]=b2[2]/a->sizeY();
    M[ 7]=0;
    M[ 8]=h[0];
    M[ 9]=h[1];
    M[10]=h[2];
    M[11]=0;
    for (int nx=0;nx<n1;nx++){
      for (int ny=0;ny<n2;ny++){
        glPushMatrix();
	M[12]=o[0]+nx*b1[0]+ny*b2[0];
	M[13]=o[1]+nx*b1[1]+ny*b2[1];
	M[14]=o[2]+nx*b1[2]+ny*b2[2];
	M[15]=1;
	glMultMatrixd(M);
	for (int i=0;i<a->sizeX();i++){
          glBegin(GL_TRIANGLE_STRIP);
	  for (int j=0;j<=a->sizeY();j++){
            vertex(i,j,h);	    
            vertex(i+1,j,h);
	  }
          glEnd();
	}
        glPopMatrix();
      }
    }
    if (sflag==GL_TRUE){
      glEnable(GL_LIGHTING);
    }
    else{
      glDisable(GL_LIGHTING);
    }
  }
}

VisSlideDrawer::~VisSlideDrawer(){
  if (a!=NULL){
    delete a;
    a=NULL;
  }
  if (clamp != NULL){
    delete clamp;
    clamp=NULL;
  }
  if (gradient != NULL){
    delete gradient;
    gradient=NULL;
  }
}

void VisSlideDrawer::setFArray(FArray2D *fa){
    if (a!=NULL){
      delete a;
      a=NULL;
    }
    if (fa!=NULL){
      a=fa->clone();
    }
}

