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

#ifndef VisBackEvent_h
#define VisBackEvent_h
#include <stdlib.h>
#include "threads.h"
#include "VisDrawer.h"
#include "VisStructureDrawer.h"
#include "VisWindow.h"

const int BE_NONE           =0;
const int BE_SELECTED       =1;
const int BE_DESELECTED     =2;
const int BE_WIN_ACTIVATE   =3;
const int BE_WIN_DEACTIVATE =4;
const int BE_WIN_SHOW       =5;
const int BE_WIN_HIDE       =6;
const int BE_WIN_CLOSE      =7;

class VisBackEventQueue;
class VisBackEvent{
  protected:
  friend class VisBackEventQueue;
  void *pointer;
  public:
    
  protected:
  VisBackEvent *next;
    VisBackEvent(){
      type=0;
      index=0;
      nx=0;
      ny=0;
      nz=0;
      next=NULL;
      pointer=NULL;
    }
  public:
  static VisBackEvent *create(){
    return new VisBackEvent();
  }
#ifndef SWIG
  static VisBackEvent *createSelected(int atom, int nx, int ny, int nz,
  VisStructureDrawer *d){
    VisBackEvent *e = new VisBackEvent();
    e->type=BE_SELECTED;
    e->index=atom;
    e->nx=nx;
    e->ny=ny;
    e->nz=nz;
    e->pointer=d;
    return e;
  }
  static VisBackEvent *createDeselected(int atom, int nx, int ny, int nz,
    VisStructureDrawer *d){
    VisBackEvent *e = new VisBackEvent();
    e->type=BE_DESELECTED;
    e->index=atom;
    e->nx=nx;
    e->ny=ny;
    e->nz=nz;
    e->pointer=d;
    return e;
  }  
  static VisBackEvent *createWinActivate(VisWindow *w){
    VisBackEvent *e = new VisBackEvent();
    e->type=BE_WIN_ACTIVATE;
    e->pointer=w;
    return e;
  }  
  static VisBackEvent *createWinDeactivate(VisWindow *w){
    VisBackEvent *e = new VisBackEvent();
    e->type=BE_WIN_DEACTIVATE;
    e->pointer=w;
    return e;
  }  
  static VisBackEvent *createWinShow(VisWindow *w){
    VisBackEvent *e = new VisBackEvent();
    e->type=BE_WIN_SHOW;
    e->pointer=w;
    return e;
  }  
  static VisBackEvent *createWinHide(VisWindow *w){
    VisBackEvent *e = new VisBackEvent();
    e->type=BE_WIN_HIDE;
    e->pointer=w;
    return e;
  }  
  static VisBackEvent *createWinClose(VisWindow *w){
    VisBackEvent *e = new VisBackEvent();
    e->type=BE_WIN_CLOSE;
    e->pointer=w;
    return e;
  }  
#endif    

    int type,index,nx,ny,nz;
  VisStructureDrawer *getStructureDrawer();
  VisWindow *getWindow();
  
  ~VisBackEvent();
};


class VisBackEventQueue{
  MUTEX(bemutex);
  VisBackEvent *first;
  static VisBackEventQueue *queue;
  public:
    static VisBackEventQueue *get(){
      if (queue==NULL){
        queue=new VisBackEventQueue();	
      }
      return queue;
    }
    VisBackEventQueue(){first=NULL;}
    VisBackEvent *current(){return first;}
    VisBackEvent *last();
    void pop();
    void append(VisBackEvent *e);
    void prepend(VisBackEvent *e);
    ~VisBackEventQueue();
};
#endif
