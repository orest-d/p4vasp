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

#ifndef VisFLWindow_h
#define VisFLWindow_h

#include <FL/Fl_Gl_Window.H>
#include <FL/gl.h>
#include <GL/glu.h>
#include "VisWindow.h"

class VisFLWindow : public Fl_Gl_Window{
  int gl_init_flag;
  public:
  VisWindow *win;
  
 
  VisFLWindow(int x,int y,int w,int h, const char *title);
//  VisFLWindow(int x,int y,int w,int h, const char *title, VisWindow *win);
//  ~VisFLWindow();
  virtual void setVisWindow(VisWindow *win);
  virtual void draw();
  virtual int handle(int event);
  virtual ~VisFLWindow();
};
#endif
