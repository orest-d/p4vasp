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
#include <p4vasp/VisNavDrawer.h>
#include <FL/Fl.H>
#include <FL/gl.h>
#include <GL/glu.h>
#include <p4vasp/vecutils.h>
#include <p4vasp/Exceptions.h>

#define MODE_NONE   0
#define MODE_ROT    1
#define MODE_ZROT   2
#define MODE_ZOOM   3
#define MODE_MOVE   4

const char *VisNavDrawer::getClassName(){return "VisNavDrawer";}

VisNavDrawer::VisNavDrawer():VisDrawer(){
  bg_red  =0.0;
  bg_green=0.0;
  bg_blue =0.0;
  antialiasing_flag =1;
  view_mode=MODE_NONE;
  perspective_flag=0;
  setHome();
}

VisNavDrawer::~VisNavDrawer(){
  if (win!=NULL){
    win->setDrawer(NULL);
    win=NULL;
  }
}

void VisNavDrawer::init(){
#if VERBOSE>1
  printf("VisNavDrawer::init()\n");
#endif

  GLfloat specular [] = { 1.0, 1.0, 1.0, 1.0 };
  GLfloat shininess [] = { 100.0 };

  glViewport(0,0,getWidth(),getHeight());

  glEnable(GL_LIGHTING);
  glEnable(GL_LIGHT0);
  glClearColor(bg_red, bg_green, bg_blue, 0.0);
  glShadeModel(GL_SMOOTH);
  glPolygonMode(GL_FRONT_AND_BACK, GL_FILL);
  glEnable(GL_DEPTH_TEST);
  glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, specular);
  glMaterialfv(GL_FRONT_AND_BACK, GL_SHININESS, shininess);
  glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE);
  glEnable(GL_COLOR_MATERIAL);
  glEnable(GL_NORMALIZE);
  _antialiasing();
  is_init=true;
#if VERBOSE>1
  printf("VisNavDrawer::init() -\n");
#endif

}

double VisNavDrawer::getRotMatElement(int i,int j){
  if ((i<0)||(i>3)||(j<0)||(j>3)){
    return 0.0;
  }
  else{
    return rotmat[i+4*j];
  }
}

void VisNavDrawer::draw(){
#if VERBOSE>1
  printf("VisNavDrawer::draw()\n");
#endif
  GLfloat position [] = { 1.0, 1.0, 1.0, 0.0 };

  glViewport(0,0,getWidth(),getHeight());

  glMatrixMode(GL_PROJECTION);
  glLoadIdentity();
  if (perspective_flag){
      glFrustum(-0.02*getWidth(), 0.02*getWidth(),
                -0.02*getHeight(),0.02*getHeight(),10.0,50.0);
      glTranslatef(0.0, 0.0, -20.0);
  }
  else{
      glOrtho(-0.02*getWidth(),0.02*getWidth(),-0.02*getHeight(),0.02*getHeight(),-30.0,30.0);
  }

  glMatrixMode(GL_MODELVIEW);
  glLoadIdentity();
  glLightfv(GL_LIGHT0, GL_POSITION, position);


  glColor3f(1.0, 0.0, 1.0);

  glClearColor(bg_red, bg_green, bg_blue, 0.0);
  glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
  glLoadMatrixd(rotmat);
  glScalef(view_zoom,view_zoom,view_zoom);
  _antialiasing();

}

int  VisNavDrawer::handle(int event){
#if VERBOSE>1
  printf("VisNavDrawer::handle(%d)\n",event);
  printf("E:%3d X:%4d Y:%4d B:%2d K:%c\n",event,getMouseX(),getMouseY(),
  getMouseButton(),getKey());
#endif

  int dx,dy;

  switch(event){
    case FL_PUSH:
      switch(getMouseButton()){
        case FL_LEFT_MOUSE:
	  if (Fl::event_state()&FL_CTRL){
	    view_mode=MODE_ZROT;
	  }
	  else{
            view_mode=MODE_ROT;
	  }
          break;
        case FL_MIDDLE_MOUSE:
          view_mode=MODE_MOVE;
          break;
        case FL_RIGHT_MOUSE:
          view_mode=MODE_ZOOM;
          break;
      }
      mousex0=getMouseX();
      mousey0=getMouseY();
//      printf("pick (%3d %3d) -> %3d\n",mousex0,mousey0,identifyPick(mousex0,mousey0));
//      switchSelect(identifyPick(mousex0,mousey0));

      switch(view_mode){
        case MODE_ROT:
        case MODE_ZROT:
          copy(saverotmat,rotmat,16);
          break;
        case MODE_MOVE:
          copy(saverotmat,rotmat,16);
          break;
        case MODE_ZOOM:
          view_zoom0=view_zoom;
          break;
      }
      return 1;
    case FL_DRAG:
    case FL_RELEASE:
      dx = getMouseX() - mousex0;
      dy = getMouseY() - mousey0;
      switch(view_mode){
        case MODE_ROT:
          {
            double XX=-dx/100.0;
            double YY=-dy/100.0;
            double R =sqrt(XX*XX+YY*YY);
            if (R>0.000001){
#if VERBOSE>1
              printf("Rotation X=%f Y=%f angle=%f\n",XX,YY,R);
#endif
              makerotmat4(matbuff,YY,XX,0.0,R);
#if VERBOSE>2
              printmat(matbuff,4);
#endif
              copy(rotmat,saverotmat,16);
              mulmatmat4(rotmat,matbuff);
              copy(rotmat,matbuff,16);	      
#if VERBOSE>2
              printmat(rotmat,4);
#endif
              break;
            }
          }
        case MODE_ZROT:
          {
	    int xs=getWidth()/2;
	    int ys=getHeight()/2;
	    double A0=atan2(mousey0-ys,mousex0-xs);
              makerotmat4(matbuff,0.0,0.0,1.0,
	      atan2(getMouseY()-ys,getMouseX()-xs)-A0);
#if VERBOSE>2
              printmat(matbuff,4);
#endif
              copy(rotmat,saverotmat,16);
              mulmatmat4(rotmat,matbuff);
              copy(rotmat,matbuff,16);	      
#if VERBOSE>2
              printmat(rotmat,4);
#endif
              break;
          }
        case MODE_MOVE:
          copy(rotmat,saverotmat,16);
	  rotmat[12]+=double(dx)/getWidth()/0.04;
	  rotmat[13]-=double(dy)/getWidth()/0.04;
          break;
        case MODE_ZOOM:
          view_zoom=view_zoom0*exp(0.005*dx);
          break;
      }
      return 1;
  }
  
  return 0;
}


void VisNavDrawer::setHome(){
  double M[16]={ 1.0, 0.0, 0.0, 0.0,
                 0.0, 1.0, 0.0, 0.0,
                 0.0, 0.0, 1.0, 0.0,
                 0.0, 0.0, 0.0, 1.0};
  copy(rotmat,M,16);
  view_zoom=1.0;
  redraw();
}
void VisNavDrawer::setFrontView(){
  double M[16]={ 1.0, 0.0, 0.0, 0.0,
                 0.0, 1.0, 0.0, 0.0,
                 0.0, 0.0, 1.0, 0.0,
                 0.0, 0.0, 0.0, 1.0};
  double pos[3];
  copy3(pos,&rotmat[12]);
  copy(rotmat,M,16);
  copy3(&rotmat[12],pos);
  redraw();
}
void VisNavDrawer::setBackView(){
  double M[16]={-1.0, 0.0, 0.0, 0.0,
                 0.0, 1.0, 0.0, 0.0,
                 0.0, 0.0,-1.0, 0.0,
                 0.0, 0.0, 0.0, 1.0};
  double pos[3];
  copy3(pos,&rotmat[12]);
  copy(rotmat,M,16);
  copy3(&rotmat[12],pos);
  redraw();
}
void VisNavDrawer::setLeftView(){
  double M[16]={ 0.0, 0.0, 1.0, 0.0,
                 0.0, 1.0, 0.0, 0.0,
                -1.0, 0.0, 0.0, 0.0,
                 0.0, 0.0, 0.0, 1.0};
  double pos[3];
  copy3(pos,&rotmat[12]);
  copy(rotmat,M,16);
  copy3(&rotmat[12],pos);
  redraw();
}
void VisNavDrawer::setRightView(){
  double M[16]={ 0.0, 0.0,-1.0, 0.0,
                 0.0, 1.0, 0.0, 0.0,
                 1.0, 0.0, 0.0, 0.0,
                 0.0, 0.0, 0.0, 1.0};
  double pos[3];
  copy3(pos,&rotmat[12]);
  copy(rotmat,M,16);
  copy3(&rotmat[12],pos);
  redraw();
}
void VisNavDrawer::setTopView(){
  double M[16]={ 1.0, 0.0, 0.0, 0.0,
                 0.0, 0.0, 1.0, 0.0,
                 0.0,-1.0, 0.0, 0.0,
                 0.0, 0.0, 0.0, 1.0};
  double pos[3];
  copy3(pos,&rotmat[12]);
  copy(rotmat,M,16);
  copy3(&rotmat[12],pos);
  redraw();
}

void VisNavDrawer::setBottomView(){
  double M[16]={ 1.0, 0.0, 0.0, 0.0,
                 0.0, 0.0,-1.0, 0.0,
                 0.0, 1.0, 0.0, 0.0,
                 0.0, 0.0, 0.0, 1.0};
  double pos[3];
  copy3(pos,&rotmat[12]);
  copy(rotmat,M,16);
  copy3(&rotmat[12],pos);
  redraw();
}

int VisNavDrawer::getPerspective(){
  return perspective_flag;
}

void VisNavDrawer::setPerspective(int flag){
  perspective_flag=flag;
  redraw();
}

double VisNavDrawer::getZoom(){
  return view_zoom;
}

void VisNavDrawer::setZoom(double z){
  view_zoom=z;
  redraw();
}

void VisNavDrawer::mulZoom(double z){
  view_zoom*=z;
  redraw();
}

