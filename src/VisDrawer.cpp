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
#include <p4vasp/VisDrawer.h>
#include <p4vasp/Exceptions.h>
#include <stdio.h>
#include <FL/gl.h>
#include <GL/glu.h>

const char *VisDrawer::getClassName(){return "VisDrawer";}

VisDrawer::VisDrawer(){
#if VERBOSE>0
  printf("VisDrawer() %p\n",this);
#endif  
  win      = NULL;
  previous = NULL;
  next     = NULL;
  is_init  = false;
}

VisDrawer::~VisDrawer(){
#if VERBOSE>0
  printf("~VisDrawer() %p\n",this);
#endif
  if (win!=NULL){
    if (previous==NULL){
#if CHECK>1
      if (win->getDrawer()!=this){
        THROW_EXC("1st Drawer is not the drawer of it's window\n"
	          " - found in VisDrawer::~VisDrawer()");
      }
#endif
      if (next!=NULL){
        next->previous=NULL;
      }

      win->setDrawer(next);
    }
  }
  win=NULL;
  if (next!=NULL){
    next->previous=previous;
  }
  if (previous != NULL){
    previous->next=next;
  }
  next=NULL;
  previous=NULL;
}

void VisDrawer::init(){
#if VERBOSE>1
  printf("VisDrawer::init()\n");
#endif
  is_init=true;
}

void VisDrawer::draw(){
#if VERBOSE>1
  printf("VisDrawer::draw()\n");
#endif
//  glClearColor(0.0, 1.0, 0.0, 0.0);
//  glShadeModel(GL_SMOOTH);
//  glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);  
}

int  VisDrawer::handle(int event){
#if VERBOSE>1
  printf("VisDrawer::handle(%d)\n",event);
#endif
  return 0;
}

VisWindow *VisDrawer::getWindow(){
  return win;
}


void VisDrawer::setWindow(const VisWindow *w){
#if VERBOSE>0
  printf("VisDrawer(%p)::setWindow(%p)\n",this,w);
#endif  
  win=(VisWindow *)w;
#if VERBOSE>0
  if (win!=NULL){
    printf("VisDrawer::setWindow(%s(%p))\n",win->getTitle(),win);
  }
#endif  
  VisDrawer *p = getFirst();
  while(p!=NULL){
#if VERBOSE>1
    printf("  p(%p)->win=(VisWindow *)w(%p);\n",p,win);
#endif    
    p->win=(VisWindow *)w;
    p=p->getNext();
  }
#if VERBOSE>0
  printf("VisDrawer(%p)::setWindow(%p) -\n",this,w);
#endif  
}



VisDrawer *VisDrawer::getPrevious(){
  return previous;
}

void VisDrawer::setPrevious(VisDrawer *d){
#if CHECK>0
  if (previous != NULL){
    THROW_EXC("Previous can not be changed in setPrevious().");
  }
  if (d->next != NULL){
    THROW_EXC("d->next is not null in setPrevious(d).");
  }
#endif
  previous = d;
  d->next  = this;
  d->win=win;
}

VisDrawer *VisDrawer::getNext(){
  return next;
}

void VisDrawer::setNext(VisDrawer *d){
#if CHECK>0
  if (next != NULL){
    THROW_EXC("Next can not be changed in setNext().");
  }
  if (d->previous != NULL){
    THROW_EXC("d->previous is not null in setNext(d).");
  }
#endif  
  next=d;
  d->previous=this;
  d->win=win;
}


VisDrawer *VisDrawer::getFirst(){
  VisDrawer *p=this;
  for(;;){
    VisDrawer *pp=p->previous;
    if (pp==NULL) return p;
    p=pp;
  }
}

VisDrawer *VisDrawer::getLast(){
  VisDrawer *p=this;
  for(;;){
    VisDrawer *pp=p->next;
    if (pp==NULL) return p;
    p=pp;
  }
}

int VisDrawer::countBefore(){
  VisDrawer *p=this;
  int c=0;
  for(;;){
    VisDrawer *pp=p->previous;
    if (pp==NULL) return c;
    p=pp;
    c++;
  }
}

int VisDrawer::countAfter(){
  VisDrawer *p=this;
  int c=0;
  for(;;){
    VisDrawer *pp=p->next;
    if (pp==NULL) return c;
    p=pp;
    c++;
  }
}

int VisDrawer::count(){
  return 1+countBefore()+countAfter();
}

void VisDrawer::insertAfter(VisDrawer *d){
#if CHECK>0
  if (d==NULL){
    THROW_NP_EXC("insertAfter(NULL)");
  }
  if (d->previous!=NULL){
    THROW_EXC("Can not insertAfter() member of sequence. (has previous)");
  }
  if (d->next!=NULL){
    THROW_EXC("Can not insertAfter() member of sequence. (has next)");
  }
#endif
  d->win      = win;
  d->next     = next;
  next        = d;
  d->previous = this;
}

void VisDrawer::insertBefore(VisDrawer *d){
#if CHECK>0
  if (d==NULL){
    THROW_NP_EXC("insertBefore(NULL)");
  }
  if (d->previous!=NULL){
    THROW_EXC("Can not insertAfter() member of sequence. (has previous)");
  }
  if (d->next!=NULL){
    THROW_EXC("Can not insertAfter() member of sequence. (has next)");
  }
#endif
  d->win      = win;
  d->previous = previous;
  previous    = d;
  d->next     = this;
}

void VisDrawer::insertSequenceAfter(VisDrawer *d){
#if CHECK>0
  if (d==NULL){
    THROW_NP_EXC("insertSequenceAfter(NULL)");
  }
#endif
  d->setWindow(win);
  d->getLast()->next      = next;
  next                    = d;
  d->getFirst()->previous = this;
}

void VisDrawer::insertSequenceBefore(VisDrawer *d){
#if CHECK>0
  if (d==NULL){
    THROW_NP_EXC("insertSequenceBefore(NULL)");
  }
#endif
  d->setWindow(win);
  d->getFirst()->previous = previous;
  previous                = d;
  d->getLast()->next      = this;
}

void VisDrawer::append(VisDrawer *d){
#if VERBOSE>0
  printf("VisDrawer(%p)::append(%p)\n",this,d);
#endif
#if CHECK>0
  if (d==NULL){
    THROW_NP_EXC("append(NULL)");
  }
  if (d->previous!=NULL){
    THROW_EXC("Can not append() member of sequence. (has previous)");
  }
  if (d->next!=NULL){
    THROW_EXC("Can not append() member of sequence. (has next)");
  }
#endif
  VisDrawer *p=getLast();
  d->win      = win;
  p->next     = d;
  d->previous = p;
}

void VisDrawer::appendSequence(VisDrawer *d){
#if VERBOSE>0
  printf("VisDrawer(%p)::appendSequence(%p)\n",this,d);
#endif
#if CHECK>0
  if (d==NULL){
    THROW_NP_EXC("appendSequence(NULL)");
  }
#endif
  VisDrawer *dp = d->getFirst();
  VisDrawer *p  = getLast();
  d->setWindow(win);
  p->next       = dp;
  dp->previous  = p;
}

int VisDrawer::getMouseX(){
#if CHECK>0
  if (win==NULL){
#if CHECK>1  
    fprintf(stderr,"Called VisDrawer::getMouseX() while Drawer window is NULL.\n");
#endif    
    return 0;
  }
  else{
    return win->mouse_x;
  }
#else
  return win->mouse_x;
#endif    
}

int VisDrawer::getMouseY(){
#if CHECK>0
  if (win==NULL){
#if CHECK>1  
    fprintf(stderr,"Called VisDrawer::getMouseY() while Drawer window is NULL.\n");
#endif    
    return 0;
  }
  else{
    return win->mouse_y;
  }
#else
  return win->mouse_y;
#endif    
}

int VisDrawer::getMouseButton(){
#if CHECK>0
  if (win==NULL){
#if CHECK>1  
    fprintf(stderr,"Called VisDrawer::getMouseButton() while Drawer window is NULL.\n");
#endif    
    return 0;
  }
  else{
    return win->mouse_button;
  }
#else
  return win->mouse_button;
#endif    
}


int VisDrawer::getMouseButton1(){
#if CHECK>0
  if (win==NULL){
#if CHECK>1  
    fprintf(stderr,"Called VisDrawer::getMouseButton1() while Drawer window is NULL.\n");
#endif    
    return 0;
  }
  else{
    return win->mouse_button1;
  }
#else
  return win->mouse_button1;
#endif    
}

int VisDrawer::getMouseButton2(){
#if CHECK>0
  if (win==NULL){
#if CHECK>1  
    fprintf(stderr,"Called VisDrawer::getMouseButton2() while Drawer window is NULL.\n");
#endif    
    return 0;
  }
  else{
    return win->mouse_button2;
  }
#else
  return win->mouse_button2;
#endif    
}

int VisDrawer::getMouseButton3(){
#if CHECK>0
  if (win==NULL){
#if CHECK>1  
    fprintf(stderr,"Called VisDrawer::getMouseButton3() while Drawer window is NULL.\n");
#endif    
    return 0;
  }
  else{
    return win->mouse_button3;
  }
#else
  return win->mouse_button3;
#endif    
}

int VisDrawer::getKey(){
#if CHECK>0
  if (win==NULL){
#if CHECK>1  
    fprintf(stderr,"Called VisDrawer::getKey() while Drawer window is NULL.\n");
#endif    
    return 0;
  }
  else{
    return win->key;
  }
#else
  return win->key;
#endif    
}

int VisDrawer::getWidth(){
#if CHECK>0
  if (win==NULL){
#if CHECK>1  
    fprintf(stderr,"Called VisDrawer::getWidth() while Drawer window is NULL.\n");
#endif    
    return 0;
  }
  else{
    return win->w;
  }
#else
  return win->w;
#endif    
}

int VisDrawer::getHeight(){
#if CHECK>0
  if (win==NULL){
#if CHECK>1  
    fprintf(stderr,"Called VisDrawer::getHeight() while Drawer window is NULL.\n");
#endif    
    return 0;
  }
  else{
    return win->h;
  }
#else
  return win->h;
#endif    
}

void VisDrawer::redraw(){
#if VERBOSE>0
  printf("VisDrawer::redraw()\n");
#endif
  if (getWindow()!=NULL){
#if VERBOSE>0
    printf("  getWindow()->redraw()\n");
#endif
    getWindow()->redraw();
  }
#if VERBOSE>0
  printf("VisDrawer::redraw() -\n");
#endif
}

