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

#ifndef VisWindow_h
#define VisWindow_h
#include "ClassInterface.h"
#include "threads.h"
#include "VisDrawer.h"

#ifndef SWIG
class VisFLWindow;

void init_mutexes();
void destroy_mutexes();
#endif

class VisWindow : public ClassInterface{
  char *title;
  VisWindow *next;
  VisDrawer *drawer;
  
  public:
  int mouse_x,mouse_y;
  int mouse_button1,mouse_button2,mouse_button3,mouse_button;
  int key;
  
#ifndef SWIG
  VisFLWindow *win;
#endif  
  
  virtual const char *getClassName();
  
#ifndef SWIG
  MUTEX(local_mutex);
  static VisWindow *root;
#endif
  
#ifdef SWIG
%immutable;
#endif
  int x,y,w,h;

  VisWindow(int x,int y, int w, int h, const char *title);
  virtual ~VisWindow();  
  
  static VisWindow *getFirstWindow();
  static VisWindow *getLastWindow();
  static VisWindow *getWindow(int n);
  static VisWindow *getWindowByOutput(VisFLWindow *w);

  static int windowsCount();
  static int getWindowIndex(VisWindow *w);
  static void deleteAllWindows();
  VisWindow *getNextWindow();
  VisWindow *getPreviousWindow();
  static void deleteWindow(int n);


  const char *getTitle();
  void setTitle(const char *title);  
  void position(int x,int y);
  void size(int x,int y);
  void resize(int x,int y,int w,int h);
#ifndef SWIG
  void resize();
#endif
  void show();
  void hide();
  void redraw();
    
#ifndef SWIG
  static VisWindow *getFirstWindow_nolock();
  static VisWindow *getLastWindow_nolock();
  static VisWindow *getWindow_nolock(int n);
  static VisWindow *getWindowByOutput_nolock(VisFLWindow *w);
  static int windowsCount_nolock();
  static int getWindowIndex_nolock(VisWindow *w);
  VisWindow *getNextWindow_nolock();
  VisWindow *getPreviousWindow_nolock();
  static void deleteWindow_nolock(int n);

  static VisWindow **getAllWindows();
  static VisWindow **getAllWindows_nolock();
  void draw();
  void init();
  void assure_init();
  int handle(int event);

  void setOutputWindow(VisFLWindow *win);
  
  static void global_lock();
  static void global_unlock();
  inline void local_lock(){MUTEX_LOCK(local_mutex);}
  inline void local_unlock(){MUTEX_UNLOCK(local_mutex);}
#endif

  void setDrawer(VisDrawer *d);
  VisDrawer *getDrawer();
  int saveScreenshot(char *path);
};

#endif
