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

#include <p4vasp/VisWindow.h>
#include <p4vasp/VisPrimitiveDrawer.h>
#include <math.h>
#include <FL/gl.h>
#include <GL/glu.h>
#include <stdio.h>
#include <p4vasp/Exceptions.h>

int  default_primitives_resolution=16;
int  getDefaultPrimitivesResolution(){return default_primitives_resolution;}
void setDefaultPrimitivesResolution(int r){default_primitives_resolution=r;}


const char *VisPrimitiveDrawer::getClassName(){return "VisPrimitiveDrawer";}

VisPrimitiveDrawer::VisPrimitiveDrawer():VisDrawer(){
#if VERBOSE>0
  printf("new VisPrimitiveDrawer\n");
#endif
  quadObj=NULL;
#ifndef NO_GL_LISTS  
  list_init_flag=0;
#endif  
  primitives_resolution=-1;
  arrow_radius=0.07;
  arrowhead_radius=0.15;
  arrowhead_length=0.3;
#if VERBOSE>0
  printf("new VisPrimitiveDrawer -\n");
#endif
}

VisPrimitiveDrawer::~VisPrimitiveDrawer(){
#if VERBOSE>0
  printf("~VisPrimitiveDrawer\n");
#endif
  if (quadObj!=NULL){
    gluDeleteQuadric(quadObj);
    quadObj=NULL;
  }
#ifndef NO_GL_LISTS  
  if (list_init_flag){
    if (glIsList(sphere_list)){
      glDeleteLists(sphere_list,1);
    }
    if (glIsList(cylinder_list)){
      glDeleteLists(cylinder_list,1);
    }
    if (glIsList(cone_list)){
      glDeleteLists(cone_list,1);
    }
  }
#endif  
#if VERBOSE>0
  printf("~VisPrimitiveDrawer -\n");
#endif
}

void VisPrimitiveDrawer::setPrimitivesResolution(int r){
#if VERBOSE>0
  printf("VisPrimitiveDrawer::setPrimitivesResolution(%d)\n",r);
#endif
  primitives_resolution=r;
  sphere_slices = r;
  sphere_stacks = r*10/16;
  cylinder_slices = r;
  cylinder_stacks = 2;
  cone_slices = r;
  cone_stacks = 2;
  initPrimitives();
#if VERBOSE>0
  printf("VisPrimitiveDrawer::setPrimitivesResolution(%d) -\n",r);
#endif
}

void VisPrimitiveDrawer::initPrimitives(){
#if VERBOSE>0
  printf("VisPrimitiveDrawer::initPrimitives()\n");
#endif  
  if (quadObj==NULL){  
#  if VERBOSE>0
    printf("  create new quadObj (gluNewQuadric) in initPrimitives\n");
#  endif  
    quadObj = gluNewQuadric();
#  if CHECK>1
    if (quadObj==NULL){
      THROW_NP_EXC("quadObj=NULL in VisPrimitiveDrawer::initPrimitives()");
    }
#  endif  
  }


#ifndef NO_GL_LISTS
  if (!list_init_flag){
#  if VERBOSE>1
    printf("  init lists\n");
#  endif  
    sphere_list            = glGenLists(3);
    cylinder_list          = sphere_list+1;
    cone_list              = sphere_list+2;
    list_init_flag         = 1;
  }

  //printf("sphere init %d %d\n",sphere_slices, sphere_stacks);
  glNewList(sphere_list,GL_COMPILE);
  gluSphere(quadObj, 1.0, sphere_slices, sphere_stacks);
  glEndList();

  //printf("cone init %d %d\n",cone_slices, cone_stacks);
  glNewList(cone_list,GL_COMPILE);
  gluCylinder(quadObj, 1.0, 0.0, 1.0, cone_slices, cone_stacks);
  glEndList();

  //printf("cylinder init %d %d\n",cylinder_slices, cylinder_stacks);
  glNewList(cylinder_list,GL_COMPILE);
  gluCylinder(quadObj, 1.0, 1.0, 1.0, cylinder_slices, cylinder_stacks);
  glEndList();      
#endif
#if VERBOSE>0
  printf("VisPrimitiveDrawer::initPrimitives() -\n");
#endif  
}

void VisPrimitiveDrawer::init(){
#if VERBOSE>0
  printf("VisPrimitiveDrawer::init()\n");
#endif
  if (quadObj==NULL){  
#if VERBOSE>0
    printf("  create new quadObj (gluNewQuadric) in init\n");
#endif  
    quadObj = gluNewQuadric();
#if CHECK>1
    if (quadObj==NULL){
      THROW_NP_EXC("quadObj=NULL in VisPrimitiveDrawer::init()");
    }
#endif  
  }
  setPrimitivesResolution(default_primitives_resolution);  
  is_init=true;
#if VERBOSE>0
  printf("VisPrimitiveDrawer::init() -\n");
#endif
}

void VisPrimitiveDrawer::draw(){
#if VERBOSE>1
  printf("VisPrimitiveDrawer::draw()\n");
#endif
  glClearColor(0.0, 0.0, 0.0, 0.0);
  glShadeModel(GL_SMOOTH);
  glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
  glColor3d(1.0,0.0,0.0);
  sphere(-1,0,0,0.5);
  glColor3d(0.0,1.0,0.0);
  cone(0,0,0,0,1,0,0.5);
  glColor3d(0.0,0.0,1.0);
  cylinder(1,0,0,1,1,0,0.5);  
  glColor3d(0.5,0.5,1.0);
  arrow(-0.5,0.0,2,1.0,0.0,0.0);
}

int  VisPrimitiveDrawer::handle(int event){
#if VERBOSE>1
  printf("VisPrimitiveDrawer::handle(%d)\n",event);
#endif
  return 0;
}

void VisPrimitiveDrawer::sphere(double x,double y, double z, double radius){
#if VERBOSE>0
  printf("VisPrimitiveDrawer.sphere(%f,%f,%f,%f)\n",x,y,z,radius);
#endif  
  glPushMatrix();
  glTranslatef(x,y,z);
  glScalef(radius,radius,radius);
#ifdef NO_GL_LISTS    
#if CHECK>1
  if (quadObj==NULL){
    THROW_NP_EXC("quadObj=NULL in VisPrimitiveDrawer::sphere()");
  }
#endif  
  sphere_slices,sphere_stacks);
  gluSphere(quadObj, 1.0, sphere_slices, sphere_stacks);
  sphere_slices,sphere_stacks);
#else
  glCallList(sphere_list);
#endif  
  glPopMatrix();
#if VERBOSE>0
  printf("VisPrimitiveDrawer.sphere(%f,%f,%f,%f) -\n",x,y,z,radius);
#endif  
}

void VisPrimitiveDrawer::cylinder(double x1,double y1, double z1,double x2,double y2, double z2, double radius){
  double dx=x2-x1;
  double dy=y2-y1;
  double dz=z2-z1;
  double l = sqrt(dx*dx+dy*dy+dz*dz);
  if (l>0.0){
    double a=acos(dz/l)*180/M_PI;
    glPushMatrix();
    glTranslatef(x1,y1,z1);
    glPushMatrix();
//    if ((dx!=0.0)||(dy!=0.0)){
    if ((sqrt(dx*dx+dy*dy)/l)>0.001){
      glRotatef(a,-dy,dx,0.0);
      glScalef(radius,radius,l);
    }
    else{
      glScalef(radius,radius,dz);
    }
#ifdef NO_GL_LISTS    
#if CHECK>1
    if (quadObj==NULL){
      THROW_NP_EXC("quadObj=NULL in VisPrimitiveDrawer::cylinder()");
    }
#endif  
    gluCylinder(quadObj, 1.0, 1.0, 1.0, cylinder_slices, cylinder_stacks);
#else    
    glCallList(cylinder_list);
#endif    
    glPopMatrix();
    glPopMatrix();
  }
}

void VisPrimitiveDrawer::cone(double x1,double y1, double z1,double x2,double y2, double z2, double radius){
  double dx=x2-x1;
  double dy=y2-y1;
  double dz=z2-z1;
  double l = sqrt(dx*dx+dy*dy+dz*dz);
  if (l>0.0){
    double a=acos(dz/l)*180/M_PI;
    glPushMatrix();
    glTranslatef(x1,y1,z1);
    glPushMatrix();
    if ((dx!=0.0)||(dy!=0.0)){
      glRotatef(a,-dy,dx,0.0);
    }
    glScalef(radius,radius,l);
#ifdef NO_GL_LISTS    
#if CHECK>1
    if (quadObj==NULL){
      THROW_NP_EXC("quadObj=NULL in VisPrimitiveDrawer::cone()");
    }
#endif  
    gluCylinder(quadObj, 1.0, 0.0, 1.0, cone_slices, cone_stacks);
#else    
    glCallList(cone_list);
#endif    
    glPopMatrix();
    glPopMatrix();
  }
}

void VisPrimitiveDrawer::line(double x1,double y1, double z1,double x2,double y2, double z2){
  glBegin(GL_LINES);
  glVertex3d(x1,y1,z1);
  glVertex3d(x2,y2,z2);
  glEnd();
}

void VisPrimitiveDrawer::arrow(double x,double y, double z,
   double dx,double dy, double dz, double scale, int normalize){
  double l = sqrt(dx*dx+dy*dy+dz*dz);
  if (l>1.0e-50){
    dx*=scale;
    dy*=scale;
    dz*=scale;
    if (normalize){
      dx/=l;
      dy/=l;
      dz/=l;
      l=scale;
    }
    else{
      l*=scale;
    }
    double f =arrowhead_length/l;
    double ff=1.0-f;
    double g=1.0-f*arrow_radius/arrowhead_radius;

    cylinder(x, y, z, x+g*dx, y+g*dy, z+g*dz,arrow_radius);
    cone(    x+dx*ff, y+dy*ff, z+dz*ff, x+dx, y+dy, z+dz,arrowhead_radius);
  }
}
  
void VisPrimitiveDrawer::color(double red,double green,double blue){
  glColor3d(red,green,blue);
}
