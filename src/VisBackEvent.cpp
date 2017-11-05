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

#include <p4vasp/VisBackEvent.h>
#include <stdio.h>
#include <string.h>


VisBackEvent::~VisBackEvent(){
#if VERBOSE>0
  printf("VisBackEvent::~VisBackEvent()\n");
#endif
}

VisBackEventQueue *VisBackEventQueue::queue=NULL;

VisStructureDrawer *VisBackEvent::getStructureDrawer()
{
  if ((type ==BE_SELECTED)||(type ==BE_DESELECTED)){
    return (VisStructureDrawer *)pointer;
  }
  else{
#if VERBOSE>0
  printf("VisBackEvent::getStructureDrawer() for incorrect type. (%d)\n",type);
#endif
    return NULL;
  }
}

VisWindow *VisBackEvent::getWindow()
{
  switch(type){
    case BE_SELECTED:
    case BE_DESELECTED:
      return ((VisStructureDrawer *)pointer)->getWindow();
    case BE_WIN_ACTIVATE:
    case BE_WIN_DEACTIVATE:
    case BE_WIN_SHOW: 
    case BE_WIN_HIDE: 
    case BE_WIN_CLOSE:
      return (VisWindow *)pointer;
    default:
#if VERBOSE>0
      printf("VisBackEvent::getWindow() for incorrect type. (%d)\n",type);
#endif
      return NULL;
  }
}

void VisBackEventQueue::pop(){
  MUTEX_LOCK(bemutex);
  if (first != NULL){
    VisBackEvent *x=first;
    first=x->next;
    delete x;
  }
  MUTEX_UNLOCK(bemutex);
}

VisBackEvent *VisBackEventQueue::last(){
  MUTEX_LOCK(bemutex);
  if (first != NULL){
    VisBackEvent *x=first;
    while(x->next!=NULL){
      x=x->next;
    }
    MUTEX_UNLOCK(bemutex);
    return x;
  }
  MUTEX_UNLOCK(bemutex);
  return NULL;
}

void VisBackEventQueue::append(VisBackEvent *e){
  MUTEX_LOCK(bemutex);
  VisBackEvent *l=last();
  if (l==NULL){
    first=e;
  }
  else{
    l->next=e;
  }
  MUTEX_UNLOCK(bemutex);
}

void VisBackEventQueue::prepend(VisBackEvent *e){
  MUTEX_LOCK(bemutex);
  e->next=first;
  first=e;
  MUTEX_UNLOCK(bemutex);
}

VisBackEventQueue::~VisBackEventQueue(){
  MUTEX_LOCK(bemutex);
  while(first!=NULL){
    pop();
  }
  MUTEX_UNLOCK(bemutex);
}

