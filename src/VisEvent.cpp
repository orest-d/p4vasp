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

#include <stdio.h>
#include <string.h>
#include <p4vasp/VisEvent.h>
#include <p4vasp/Exceptions.h>
#include <p4vasp/threads.h>

MUTEX(VisEvent_mutex);

VisEvent *VisEvent::buff;
long VisEvent::event_counter;
int VisEvent::buff_len=0;

int VisEvent::length;
/*
VisEvent::VisEvent(int event,VisWindow *window,void *pointer){
  this->event   = event;
  this->window  = window;
  this->pointer = pointer;
  this->event_number = event_counter++;
  if (window!=NULL){
    this->flwindow=window->win;
    this->x=window->x;
    this->y=window->y;
    this->w=window->w;
    this->h=window->h;
  }
  else{
    this->flwindow=NULL;
    this->x=0;
    this->y=0;
    this->w=100;
    this->h=100;
  }
#if VERBOSE>1  
  printf("new VisEvent %3d/%4ld window:%p flwindow:%p ptr:%p (%3d %3d %3d %3d)\n",
  event,event_number,window,flwindow,pointer,x,y,w,h);
#endif  
}
*/

VisEvent::~VisEvent(){
}

void VisEvent::lock(){
  MUTEX_LOCK(VisEvent_mutex);
}
void VisEvent::unlock(){
  MUTEX_UNLOCK(VisEvent_mutex);
}

void VisEvent::init(){
#if VERBOSE>1  
  printf("VisEvent::init()\n");
#endif  
  buff = NULL;
  event_counter=0;
  MUTEX_INIT(VisEvent_mutex);
  length = 0;
  resize(EVENT_BUFF_LENGTH);
#if VERBOSE>1  
  printf("VisEvent::init() -\n");
#endif  
}

void VisEvent::resize(int l){
  VisEvent::lock();
#if VERBOSE>1  
  printf("VisEvent::resize(%d)\n",l);
#endif  
  if (length>l){
    l=length;
  }  
  VisEvent *nbuff=(VisEvent *)malloc(l*sizeof(VisEvent));
#if CHECK>0  
  if (nbuff==NULL){
    NTHROW_MA_EXC("VisEvent::resize() failed.");
  }
#endif
  if (buff!=NULL){
    if (length>0){
      memcpy(nbuff,buff,length*sizeof(VisEvent));
    }
    free(buff);
  }
  buff=nbuff;
  buff_len=l;
  VisEvent::unlock();
#if VERBOSE>1  
  printf("VisEvent::resize(%d) -\n",l);  
#endif  
}

long VisEvent::add(int event,VisWindow *window,void *pointer){
  VisEvent::lock();
  long num=0;
#if VERBOSE>1
  printf("VisEvent::add(%d,%p,%p); length=%d\n",event,window,pointer,length);
#endif  
#if CHECK>1
  if (buff==NULL){
    NTHROW_NP_EXC("buff=NULL in VisEvent::add().");
  }
#endif
  if (length>=buff_len){
    VisEvent::unlock();
    resize(buff_len*2);
    VisEvent::lock();
  }
  buff[length].event        = event;
  buff[length].window       = window;
  buff[length].pointer      = pointer;
  buff[length].event_number = event_counter++;
  if (window!=NULL){
    buff[length].flwindow=window->win;
    buff[length].x=window->x;
    buff[length].y=window->y;
    buff[length].w=window->w;
    buff[length].h=window->h;
  }
  else{
    buff[length].flwindow=NULL;
    buff[length].x=0;
    buff[length].y=0;
    buff[length].w=100;
    buff[length].h=100;
  }
#if VERBOSE>1
  printf(":::add ");
  buff[length].print();
#endif  
  num=buff[length].event_number;
  length++;
  VisEvent::unlock();
#if VERBOSE>1
  printf("VisEvent::add(%d ...) -\n",event);
#endif  
  return num;
}

VisEvent *VisEvent::getLast(){
#if CHECK>1
  if (buff==NULL){
    NTHROW_NP_EXC("buff=NULL in VisEvent::getLast().");
  }
#endif
  return &buff[length-1];
}

VisEvent *VisEvent::pop(){
  VisEvent::lock();
#if VERBOSE>1
  printf("VisEvent::pop(); length=%d\n",length);
#endif  

#if CHECK>1
  if (buff==NULL){
    NTHROW_NP_EXC("buff=NULL in VisEvent::pop().");
  }
#endif
  if (length<=1){
    length=0;
    VisEvent::unlock();
    return NULL;
  }
  memmove(&buff[0],&buff[1],(length-1)*sizeof(VisEvent));
  length--;
  VisEvent::unlock();
  return buff;
}

VisEvent *VisEvent::getCurrent(){
  VisEvent::lock();
#if CHECK>1
  if (buff==NULL){
    NTHROW_NP_EXC("buff=NULL in VisEvent::getLast().");
  }
#endif
  if (length>0){
    VisEvent::unlock(); 
    return &buff[0];
  }
  else{
    VisEvent::unlock(); 
    return NULL;
  }
}
