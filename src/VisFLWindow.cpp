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

#include <p4vasp/VisFLWindow.h>
#include <p4vasp/Exceptions.h>
#include <p4vasp/VisBackEvent.h>
#include <FL/Fl.H>

void win_close_callback(Fl_Widget *w){
#if VERBOSE>0
  printf("win_close_callback\n");
#endif
  if (((VisFLWindow*)w)->win!=NULL){
    VisBackEventQueue::get()->append(VisBackEvent::createWinClose(((VisFLWindow*)w)->win));  
  }
//  ((VisFLWindow *)w)->hide();
}

VisFLWindow::~VisFLWindow(){
#if VERBOSE>0
  printf("VisFLWindow::~VisFLWindow()\n");
#endif
}


VisFLWindow::VisFLWindow(int x,int y,int w,int h, const char *title):
  Fl_Gl_Window(x,y,w,h,title)
{
  mode(FL_RGB|FL_DOUBLE|FL_DEPTH);
  this->win=NULL;
  gl_init_flag=0;
  callback(win_close_callback);
  size_range(10,10);
}

/*
VisFLWindow::VisFLWindow(int x,int y,int w,int h, const char *title,
                         VisWindow *win) : Fl_Gl_Window(x,y,w,h,title)
{
  this->win=win;
  win->setOutputWindow(this);
  gl_init_flag=0;
}
*/

void VisFLWindow::setVisWindow(VisWindow *win){
#if CHECK>0
  if (this->win != NULL){
    NTHROW_EXC("VisWindow already set in VisFLWindow::setVisWindow().");
  }
#endif
  this->win=win;
  win->setOutputWindow(this);
  gl_init_flag=0;
}

void VisFLWindow::draw(){
#if VERBOSE>0
  printf("VisFLWindow::draw()\n");
#endif
  gl_init_flag=1;
#ifdef DRAWBUFFERHACK
#  ifndef MESA
  glDrawBuffer(GL_FRONT_AND_BACK);
#  endif
#endif      
  if (this->win == NULL){
    glViewport(0,0,w(),h());
    glClearColor(0.0, 0.0, 1.0, 0.0);
    glShadeModel(GL_SMOOTH);
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
  }
  else{
    if (visible()){
    win->local_lock();
    win->x=x();
    win->y=y();
    win->w=w();
    win->h=h();
    win->local_unlock();
    
    if (!valid()){
      glViewport(0,0,w(),h());
      win->init();
    }
    win->draw();
    }
  }
#ifdef DRAWBUFFERHACK
#  ifndef MESA
  glDrawBuffer(GL_BACK);
#  endif      
#endif      

}

int VisFLWindow::handle(int event){
  if (this->win != NULL){
    win->local_lock();
    win->x=x();
    win->y=y();
    win->w=w();
    win->h=h();
    win->mouse_x=Fl::event_x();
    win->mouse_y=Fl::event_y();
    win->mouse_button1=Fl::event_button1();
    win->mouse_button2=Fl::event_button2();
    win->mouse_button3=Fl::event_button3();
    if ((event==FL_PUSH)||(event==FL_RELEASE)){
      win->mouse_button=Fl::event_button();
    }
    else{
      win->mouse_button=0;
    }
    if (event==FL_KEYBOARD){
      win->key=Fl::event_key();
    }
    else{
      win->key=0;
    }      
    if (event==FL_FOCUS){
      VisBackEventQueue::get()->append(VisBackEvent::createWinActivate(win));  
    }
    if (event==FL_UNFOCUS){
      VisBackEventQueue::get()->append(VisBackEvent::createWinDeactivate(win));  
    }
    if (event==FL_SHOW){
      VisBackEventQueue::get()->append(VisBackEvent::createWinShow(win));
    }
    if (event==FL_HIDE){
      VisBackEventQueue::get()->append(VisBackEvent::createWinHide(win));
    }

    win->local_unlock();
    
    if (!win->handle(event)){
      return Fl_Gl_Window::handle(event);
    }
  }
  return Fl_Gl_Window::handle(event);
}
