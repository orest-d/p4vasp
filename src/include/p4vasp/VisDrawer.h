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

#ifndef VisDrawer_h
#define VisDrawer_h
#include "ClassInterface.h"

#ifndef VisWindow
class VisWindow;
#endif


class VisDrawer : public ClassInterface{
  friend class VisWindow;
  protected:
  VisWindow *win;
  VisDrawer *previous, *next;
  bool is_init;

  void setPrevious(VisDrawer *d);
  void setNext(VisDrawer *d);
  
  public:
  VisDrawer();
  virtual const char *getClassName();

  VisWindow *getWindow();
  VisDrawer *getPrevious();
  VisDrawer *getNext();
  VisDrawer *getFirst();
  VisDrawer *getLast();
  int countBefore();
  int countAfter();
  int count();
  void insertAfter(VisDrawer *d);
  void insertBefore(VisDrawer *d);
  void insertSequenceAfter(VisDrawer *d);
  void insertSequenceBefore(VisDrawer *d);
  void append(VisDrawer *d);
  void appendSequence(VisDrawer *d);

  
#ifndef SWIG
  virtual void setWindow(const VisWindow *w);
    
  virtual void init();
  virtual void draw();
  virtual int handle(int event);  
#endif  
  virtual ~VisDrawer();
  int getMouseX();
  int getMouseY();
  int getMouseButton();
  int getMouseButton1();
  int getMouseButton2();
  int getMouseButton3();
  int getKey();
  int getWidth();
  int getHeight();
  
  void redraw();
};

#endif
