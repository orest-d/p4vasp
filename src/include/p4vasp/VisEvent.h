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

#ifndef VisEvent_h
#define VisEvent_h
#include "VisWindow.h"
#include "threads.h"

#define VE_SYNC                -1
#define VE_END                  0
#define VE_CREATE_WINDOW        1
#define VE_DESTROY_WINDOW       2
#define VE_SET_WINDOW_TITLE     3
#define VE_SET_WINDOW_POSITION  4
#define VE_SET_WINDOW_SIZE      5
#define VE_RESIZE_WINDOW        6
#define VE_SHOW_WINDOW          7
#define VE_HIDE_WINDOW          8
#define VE_REDRAW_WINDOW        9

#ifndef EVENT_BUFF_LENGTH
#define EVENT_BUFF_LENGTH 16
#endif

class VisFLWindow;

class VisEvent{
#ifndef NO_THREADS
  static MUTEX(mutex);
#endif  
  static VisEvent  *buff;
//  static VisEvent  *last;
  static long event_counter;
  static int buff_len;
//  VisEvent(int event,VisWindow *window=NULL,void *pointer=NULL);
  public:
  long event_number;
  int event;
  int x,y,w,h;
  VisWindow   *window;  
  VisFLWindow *flwindow;
  void *pointer;
  ~VisEvent();

//  VisEvent  *next;

  static int length;  
  static void init();
  static void resize(int l);
  static long add(int event,VisWindow *window=NULL,void *pointer=NULL);
  static VisEvent *pop();
  static VisEvent *getLast();
  static VisEvent *getCurrent();
  static void lock();
  static void unlock();
  void print(){
    printf("VisEvent %3d/%4ld window:%p flwindow:%p ptr:%p (%3d %3d %3d %3d)\n",
    event,event_number,window,flwindow,pointer,x,y,w,h); 
  }
};

#endif
