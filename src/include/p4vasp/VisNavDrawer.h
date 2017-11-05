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

#ifndef VisNavDrawer_h
#define VisNavDrawer_h
#include <FL/gl.h>

class VisNavDrawer : public VisDrawer{
  protected:
#ifndef SWIG  
  double rotmat[16];
  double saverotmat[16],matbuff[16];
  double view_zoom, view_zoom0;
#endif  
  int view_mode;
  int mousex0,mousey0;
  int perspective_flag;
  int antialiasing_flag;
  void _antialiasing(){
    if (antialiasing_flag){
      glEnable(GL_LINE_SMOOTH);
      glHint(GL_POINT_SMOOTH_HINT,GL_NICEST);
      glHint(GL_LINE_SMOOTH_HINT,GL_NICEST);
      glHint(GL_POLYGON_SMOOTH_HINT,GL_NICEST);
    }
    else{
      glHint(GL_POINT_SMOOTH_HINT,GL_FASTEST);
      glHint(GL_LINE_SMOOTH_HINT,GL_FASTEST);
      glHint(GL_POLYGON_SMOOTH_HINT,GL_FASTEST);
    }
  }
  
  public:
#ifdef SWIG  
  %immutable;
#endif  
  double bg_red,bg_green,bg_blue;
#ifdef SWIG  
  %mutable;
#endif

  VisNavDrawer();

  double getRotMatElement(int i,int j);

  void setBackground(double red,double green, double blue){
    bg_red  =red;
    bg_green=green;
    bg_blue  =blue;
    redraw();
  }
  void setAntialiasing(int a){
    if (a != antialiasing_flag){
      antialiasing_flag=a;
      redraw();
    }    
  }
  int getAntialiasing(){
    return antialiasing_flag;
  }
  virtual const char *getClassName();
#ifndef SWIG
  virtual void init();
  virtual void draw();
  virtual int  handle(int event);  
#endif  
  virtual ~VisNavDrawer();
  
  virtual void   setHome();
  virtual void   setFrontView();
  virtual void   setBackView();
  virtual void   setLeftView();
  virtual void   setRightView();
  virtual void   setTopView();
  virtual void   setBottomView();  
  
  virtual int    getPerspective();
  virtual void   setPerspective(int flag);
  virtual double getZoom();
  virtual void   setZoom(double z);
  virtual void   mulZoom(double z);
};

#endif
