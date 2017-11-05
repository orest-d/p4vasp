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

#ifndef VisPrimitiveDrawer_h
#define VisPrimitiveDrawer_h
#include "VisDrawer.h"
#include "threads.h"
#include <FL/gl.h>
#include <GL/glu.h>

#ifndef VisWindow
class VisWindow;
#endif

int   getDefaultPrimitivesResolution();
void  setDefaultPrimitivesResolution(int r);


class VisPrimitiveDrawer : public VisDrawer{
  protected:
  int sphere_slices,sphere_stacks;
  int cylinder_slices,cylinder_stacks;
  int cone_slices,cone_stacks;
#ifndef NO_GL_LISTS
  int sphere_list,cylinder_list,cone_list;
  int list_init_flag;
#endif  
  int primitives_resolution;
  GLUquadricObj *quadObj;
  void initPrimitives();
    
  public:
#ifdef SWIG
%mutable;
#endif  
  double arrow_radius,arrowhead_radius,arrowhead_length;

  VisPrimitiveDrawer();
  virtual const char *getClassName();
#ifndef SWIG    
  virtual void init();
  virtual void draw();  
  virtual int handle(int event);  
#endif  
  virtual ~VisPrimitiveDrawer();

  void setPrimitivesResolution(int r);

  void color(double red,double green,double blue);  
  void sphere(double x,double y,double z,double radius);
  void cylinder(double x1,double y1, double z1,
                double x2,double y2, double z2, double radius);
  void cone(    double x1,double y1, double z1,
                double x2,double y2, double z2, double radius);
  void line(    double x1,double y1, double z1,
                double x2,double y2, double z2);
  void arrow(   double  x,double  y, double  z,
                double dx,double dy, double dz,double scale=1.0,int normalize=0);
		
};

#endif
