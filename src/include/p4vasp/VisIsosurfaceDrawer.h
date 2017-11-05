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

#ifndef VisIsosurfaceDrawer_h
#define VisIsosurfaceDrawer_h
#include "VisDrawer.h"
#include "Chgcar.h"
#include "threads.h"
#include <FL/gl.h>
#include <GL/glu.h>

#ifndef VisWindow
class VisWindow;
#endif
/*
class VisIsosurfaceDrawer;


class CreateIsosurfaceProcess:public Process{
  protected:
  CreateIsosurfaceProcess(VisIsosurfaceDrawer *d);
  VisIsosurfaceDrawer *drawer;
  public:
  virtual int next();
  virtual ~CreateIsosurfaceProcess();
  friend class VisIsosurfaceDrawer;
};
*/

class VisIsosurfaceDrawer:public VisDrawer
{
  friend class CreateIsosurfaceProcess;
  public:
#ifndef NO_GL_LISTS
  int list;
  bool list_update_required;
#endif
  double level;
  bool draw_as_points;
  int mx,my,mz;
  Chgcar * chgcar;

  void paint_isosurface (Chgcar * c, double level);

  int handle_tetrahedron (Chgcar * c, int a1, int a2, int a3,
			  int b1, int b2, int b3,
			  int c1, int c2, int c3,
			  int d1, int d2, int d3, double level);
  int handle_type1 (double *va, double *vb, double *vc, double *vd,
		    double *nA, double *nB, double *nC, double *nD,
		    double A, double B, double C, double D);
  int handle_type2 (double *va, double *vb, double *vc, double *vd,
		    double *nA, double *nB, double *nC, double *nD,
		    double A, double B, double C, double D);

  float red,green,blue;
public:
#ifdef SWIG
   %mutable;
#endif

    VisIsosurfaceDrawer ();
  virtual const char *getClassName ();
  void                setMultiple(int a,int b,int c);
  void                setMultiple1(int a);
  void                setMultiple2(int a);
  void                setMultiple3(int a);
  int                 getMultiple1();
  int                 getMultiple2();
  int                 getMultiple3();

  void                updateIsosurface ();
  void                setLevel(double l){level=l;updateIsosurface();}
  void                setChgcar(Chgcar *c){chgcar=c;updateIsosurface();}
  double              getLevel(){return level;}
  bool                getDrawAsPoints(){return draw_as_points;}
  void                setDrawAsPoints(bool b);
#ifndef SWIG
  virtual void init ();
  virtual void draw ();
#ifndef NO_GL_LISTS
  void updateList();
#endif  
#endif
    virtual ~ VisIsosurfaceDrawer ();

};

#endif
