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
#include <FL/gl.h>

#include <p4vasp/utils.h>
#include <p4vasp/VisWindow.h>
#include <p4vasp/VisEvent.h>
#include <p4vasp/VisDrawer.h>
#include <p4vasp/Exceptions.h>
#include <p4vasp/VisMain.h>

/* ***************************************************************** *
 *  This is a HACK to compensate that GL_BGR definition is missing   *
 *  in FL/gl.h on some systems (windows/MinGW in paricular).         *
 * ***************************************************************** */
#ifndef GL_BGR
#define GL_BGR                                  0x80E0 
#endif

MUTEX(VisWindow_mutex);


VisWindow *VisWindow::root = NULL;


const char *VisWindow::getClassName(){
  return "VisWindow";
}

VisWindow::VisWindow(int x, int y, int w, int h,const char *title){
#if VERBOSE>0
  printf("new VisWindow()\n");
#endif  
  MUTEX_INIT(local_mutex);
  local_lock();
  this->x=x;
  this->y=y;
  this->w=w;
  this->h=h;
  drawer=NULL;
  if (title==NULL){
    this->title=NULL;
  }
  else{
    this->title=clone(title);
  }
  
  global_lock();
  next=NULL;

  if (VisWindow::root == NULL){
    VisWindow::root=this;
  }
  else{
    next=NULL;
    VisWindow::getLastWindow_nolock()->next=this;
  }
  this->win=NULL;
  VisEvent::add(VE_CREATE_WINDOW,this);
  local_unlock();
  global_unlock();
  VisSync();
#if VERBOSE>0
  printf("new VisWindow() -\n");
#endif  
}

const char *VisWindow::getTitle(){
  return title;
}

void VisWindow::setTitle(const char *title){
#if VERBOSE>0
  printf("VisWindow::setTitle('%s');\n",title);
#endif
  local_lock();
  if (this->title != NULL){
    delete []this->title;
  }
  if (title==NULL){
    this->title=NULL;
    VisEvent::add(VE_SET_WINDOW_TITLE,this,NULL);
  }
  else{
    this->title=clone(title);
    VisEvent::add(VE_SET_WINDOW_TITLE,this,clone(title));
  }
  
  local_unlock();
}

VisWindow *VisWindow::getFirstWindow(){
#if CHECK>0
  if (VisWindow::root==NULL){
    NTHROW_NP_EXC("No first window in VisWindow::getFirstWindow().");
  }
#endif  
  return VisWindow::root;  
}

VisWindow *VisWindow::getFirstWindow_nolock(){
#if CHECK>0
  if (VisWindow::root==NULL){
    NTHROW_NP_EXC("No first window in VisWindow::getFirstWindow_nolock().");
  }
#endif  
  return VisWindow::root;  
}

VisWindow *VisWindow::getLastWindow(){
  global_lock();
  VisWindow *l=getLastWindow_nolock();
  global_unlock();
  return l;
}

VisWindow *VisWindow::getLastWindow_nolock(){
  VisWindow *last = VisWindow::root;
#if CHECK>0
  if (last==NULL){
    NTHROW_NP_EXC("No first window in VisWindow::getLastWindow().");
  }
#endif  
  while (last->next!=NULL){
    last=last->next;
  }
  return last;  
}


int VisWindow::windowsCount(){
  global_lock();
  int l=windowsCount_nolock();
  global_unlock();
  return l;  
}

int VisWindow::windowsCount_nolock(){
  VisWindow *last = VisWindow::root;
#if CHECK>0
  if (last==NULL){
    NTHROW_NP_EXC("No first window in VisWindow::windowsCount().");
  }
#endif  
  int c=0;
  
  while (last!=NULL){
    last=last->next;
    c++;
  }
  return c;  
}


VisWindow *VisWindow::getWindow(int n){
  global_lock();
  VisWindow *l=getWindow_nolock(n);
  global_unlock();
  return l;
}

VisWindow *VisWindow::getWindow_nolock(int n){
  int count = windowsCount_nolock();
  if (n<0){
    n+=count;
  }
#if CHECK>0  
  if ((n<0)||(n>=count)){
    NTHROW_R_EXC("Index out of range in VisWindow::getWindow().",0,count,n);
  }
#endif  
  VisWindow *last = VisWindow::root;
#if CHECK>1
  if (last==NULL){
    NTHROW_NP_EXC("No first window in VisWindow::getWindow().");
  }
#endif  
  int c=0;
  
  while (last!=NULL){
    if (c==n){
      return last;
    }
    last=last->next;
    c++;
  }
#if CHECK>0
  if (n<0){
    NTHROW_EXC("Invalid index in VisWindow::getWindow(). (window not found)");
  }
#endif  
  return NULL;
}


VisWindow *VisWindow::getWindowByOutput(VisFLWindow *w){
  global_lock();
  VisWindow *l=getWindowByOutput_nolock(w);
  global_unlock();
  return l;
}

VisWindow *VisWindow::getWindowByOutput_nolock(VisFLWindow *w){
#if CHECK>0
  if (w==NULL){
    NTHROW_NP_EXC("NULL argument in VisWindow::getWindowByOutput()");
  }
#endif  
  VisWindow *last = VisWindow::root;
  
  while (last!=NULL){
    if (last->win==w){
      return last;
    }
    last=last->next;
  }
#if CHECK>0  
  NTHROW_EXC("Window not found in VisWindow::getWindowByOutput().");
#endif  
  return NULL;
}


int VisWindow::getWindowIndex(VisWindow *w){
  global_lock();
  int l=getWindowIndex_nolock(w);
  global_unlock();
  return l;  
}

int VisWindow::getWindowIndex_nolock(VisWindow *w){
  if (w==NULL){
    return -1;
  }

  VisWindow *last = VisWindow::root;
#if CHECK>0
  if (last==NULL){
    NTHROW_NP_EXC("No first window in VisWindow::getWindowIndex().");
  }
#endif  
  int c=0;
  
  while (last!=NULL){
    if (last==w){
      return c;
    }
    last=last->next;
    c++;
  }
  
  return -1;
}

VisWindow *VisWindow::getNextWindow(){
  global_lock();
  VisWindow *l=getNextWindow_nolock();
  global_unlock();
  return l;
}

VisWindow *VisWindow::getNextWindow_nolock(){
  return next;
}

VisWindow *VisWindow::getPreviousWindow(){
  global_lock();
  VisWindow *l=getPreviousWindow_nolock();
  global_unlock();
  return l;
}

VisWindow *VisWindow::getPreviousWindow_nolock(){
  VisWindow *last = VisWindow::root;
  if (last==this){
    return NULL;
  }
  
  while (last!=NULL){
    if (last->next==this){
      return last;
    }
    last=last->next;
  }
  
  return NULL;
}



VisWindow::~VisWindow(){
#if VERBOSE>0
  printf("~VisWindow()\n");
#endif  
  global_lock();
  local_lock();
  if (drawer!=NULL){
    drawer->setWindow(NULL);
    drawer=NULL;
  }
  if (win!=NULL){
    VisEvent::add(VE_DESTROY_WINDOW,this);
  }
  win=NULL;
  VisWindow *prev = getPreviousWindow_nolock();
  if (prev==NULL){
#if CHECK>1
    if (this!=VisWindow::root){
      fprintf(stderr,
      "Warning: getPreviousWindow()!=NULL and this!=VisWindow::root"
      " in VisWindow::~VisWindow().\n");
    }
#endif
    VisWindow::root=next;
  }
  else{
    prev->next=next;
  }
  local_unlock();
  global_unlock();
#if VERBOSE>0
  printf("~VisWindow() -\n");
#endif  
}


void VisWindow::deleteWindow(int n){
  global_lock();
  deleteWindow_nolock(n);
  global_unlock();
}

void VisWindow::deleteWindow_nolock(int n){
  VisWindow *p = getWindow_nolock(n);
  if (p!=NULL){
    delete p;
  }
}

VisWindow **VisWindow::getAllWindows(){
  global_lock();
  VisWindow **l=getAllWindows_nolock();
  global_unlock();
  return l;  
}

VisWindow **VisWindow::getAllWindows_nolock(){
  VisWindow **buff = new VisWindow *[VisWindow::windowsCount_nolock()+1];
#if CHECK>0
  if (buff==NULL){
    NTHROW_MA_EXC("VisWindow::getAllWindows() failed.");
  }
#endif
  VisWindow *last = VisWindow::root;
  int c=0;
  
  while (last!=NULL){
    buff[c]=last;
    last=last->next;
    c++;
  }
  buff[c]=NULL;
  return buff;
}

void VisWindow::deleteAllWindows(){
  global_lock();
  VisWindow **buff = getAllWindows_nolock();
  if (buff==NULL){
    NTHROW_NP_EXC("getAllWindows() failed => VisWindow::deleteAllWindows() failed.");
  }
  else{
    for (int i=0; buff[i]!=NULL; i++){
      delete buff[i];
    }
  }
  delete buff;
  global_unlock();
}

void VisWindow::init(){
  local_lock();
#if VERBOSE>0
  printf("VisWindow::init()\n");
#endif    
  for (VisDrawer *d=drawer; d!=NULL; d=d->getNext()){
    d->init();
  }
#if VERBOSE>0
  printf("VisWindow::init() -\n");
#endif    
  local_unlock();
}

void VisWindow::assure_init(){
  local_lock();
#if VERBOSE>0
  printf("VisWindow::assure_init()\n");
#endif    
  for (VisDrawer *d=drawer; d!=NULL; d=d->getNext()){
    if (!d->is_init){
      d->init();
    }
  }
#if VERBOSE>0
  printf("VisWindow::assure_init() -\n");
#endif    
  local_unlock();
}

void VisWindow::draw(){
#if VERBOSE>0
  printf("VisWindow::draw()\n");
#endif
  assure_init();
  local_lock();
  if (drawer!=NULL){
    for (VisDrawer *d=drawer; d!=NULL; d=d->getNext()){
#if VERBOSE>0
      printf("VisWindow::draw() drawer call\n");
#endif    
      d->draw();
#if VERBOSE>0
      printf("VisWindow::draw() drawer call -\n");
#endif    
    }
  }
  else{
#if VERBOSE>0
    printf("Warning: No drawer in VisWindow::draw().\n");
#endif    
    glClearColor(0.0, 0.0, 0.5, 0.0);
    glShadeModel(GL_SMOOTH);
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);  
  }
  glFinish();
  local_unlock();  
#if VERBOSE>0
  printf("VisWindow::draw() -\n");
#endif    
}

int VisWindow::handle(int event){
  local_lock();
  for (VisDrawer *d=drawer; d!=NULL; d=d->getNext()){
    int r = d->handle(event);
    if (r) {
      local_unlock();
      redraw();
      return r;
    }
  }
  local_unlock();  
  return 0;
}


void VisWindow::setOutputWindow(VisFLWindow *w){
  local_lock();
  win=w;
  local_unlock();
}

void init_mutexes(){
  MUTEX_INIT(VisWindow_mutex);
}

void destroy_mutexes(){
  MUTEX_DESTROY(VisWindow_mutex);
}

void VisWindow::global_lock(){
  MUTEX_LOCK(VisWindow_mutex);
}

void VisWindow::global_unlock(){
  MUTEX_UNLOCK(VisWindow_mutex);
}


void VisWindow::position(int x,int y){
  local_lock();
  this->x=x;
  this->y=y;
  VisEvent::add(VE_SET_WINDOW_POSITION,this);
  local_unlock();
}

void VisWindow::size(int w,int h){
  local_lock();
  this->w=w;
  this->h=h;
  VisEvent::add(VE_SET_WINDOW_SIZE,this);
  local_unlock();
}

void VisWindow::resize(int x,int y,int w,int h){
  local_lock();
  this->x=x;
  this->y=y;
  this->w=w;
  this->h=h;
  VisEvent::add(VE_RESIZE_WINDOW,this);
  local_unlock();
}

void VisWindow::resize(){
  local_lock();
  VisEvent::add(VE_RESIZE_WINDOW,this);
  local_unlock();
}

void VisWindow::show(){
  local_lock();
  VisEvent::add(VE_SHOW_WINDOW,this);
  local_unlock();
}

void VisWindow::hide(){
  local_lock();
  VisEvent::add(VE_HIDE_WINDOW,this);
  local_unlock();
}

void VisWindow::redraw(){
  local_lock();
  VisEvent::add(VE_REDRAW_WINDOW,this);
  local_unlock();
}

void VisWindow::setDrawer(VisDrawer *d){
#if VERBOSE>0
  printf("VisWindow(%s)::setDrawer(%p)\n",title,d);
#endif
  local_lock();
  if (drawer!=NULL){
    drawer->setWindow(NULL);
  }
#if CHECK>0
  if (d!=NULL){
    if (d->getPrevious()!=NULL){
      THROW_EXC("D is not the first drawer of drawers linked to D in VisWindow::setDrawer(D).");
    }
  }  
#endif

  drawer=d;

  if (d!=NULL){
    d->setWindow(this);
  }
#if VERBOSE>0
  printf("VisWindow(%s)::setDrawer(%p) -\n",title,d);
#endif

  local_unlock();  
}

VisDrawer *VisWindow::getDrawer(){
  return drawer;
}

int VisWindow::saveScreenshot(char *path){
  unsigned char *pixels;
  FILE * f;
  GLint viewport[4];
  draw();
  local_lock();
  glGetIntegerv(GL_VIEWPORT, viewport);
//  printf("x:%d y:%d Width:%d Height:%d\n",viewport[0],viewport[1],viewport[2],viewport[3]);

  int width =viewport[2];
  int height=viewport[3];
  
  pixels = new unsigned char[width*height*3];
  if (pixels==NULL){
    THROW_MA_EXC("Can not allocate pixels.");
  }

  glReadPixels(0,0, width, height, GL_BGR, GL_UNSIGNED_BYTE, pixels);

  f=fopen(path, "wb");
  if(f==NULL){
    THROW_NP_EXC("Error opening file in saveScreenshot.");
  }

  // uncompressed .tga headder
  unsigned char TGAheader[12]={0,0,2,0,0,0,0,0,0,0,0,0};
  if (fwrite(TGAheader, sizeof(unsigned char), 12, f)!=12){
    THROW_EXC("Error writing tga headder (part 1).");  
  }

  unsigned char header[6];
//  printf("Width:%d Height:%d\n",width,height);
  header[0]=(int)(width%256); //width
  header[1]=(int)(width/256);
  header[2]=(int)(height%256); //height
  header[3]=(int)(height/256);
  header[4]=24;                //bpp
  header[5]=0;                 //nothing

  if (fwrite(header, sizeof(unsigned char), 6, f)!=6){
    THROW_EXC("Error writing tga headder (part 2).");
  }
  if (fwrite(pixels, sizeof(unsigned char), 
                 width*height*3, f)!=(unsigned) width*height*3){
    THROW_EXC("Error writing pixels to the tga file.");
  }

  fclose(f);
  delete [] pixels;
  local_unlock();
  return 0;
}

