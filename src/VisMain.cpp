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
#include <p4vasp/VisWindow.h>
#include <p4vasp/VisMain.h>
#include <p4vasp/VisEvent.h>
#include <p4vasp/Exceptions.h>
#include <FL/Fl.H>
#include <FL/Fl_Gl_Window.H>
#include <FL/gl.h>
#include <GL/glu.h>
#include <p4vasp/VisFLWindow.h>

THREAD(Vis_thread);

int VisEndFlag;

#ifndef NO_THREADS
MUTEX(sync_mutex);
pthread_cond_t sync_cond;
long sync_event_number;
#endif
int runningMainLoop=0;

void VisHandleWindowEvents(){
  VisEvent *e;
  e=VisEvent::getCurrent();
  while(e!=NULL){
#if VERBOSE>1
    printf("VisHandleWindowEvents() event count %d\n",e->length);
    printf(":::handle ");
    e->print();
#endif	
    switch(e->event){

/*------------------------------------------------------------------*/
      case VE_SYNC:
#if VERBOSE>0
        printf("Visual sync\n");
#  ifdef NO_THREADS
        printf("While compilled with NO_THREADS, VisSync does nothing.\n");
#  endif	
#endif
#ifndef NO_THREADS
      MUTEX_LOCK(sync_mutex);
      sync_event_number = e->event_number;
      pthread_cond_broadcast(&sync_cond);
      MUTEX_UNLOCK(sync_mutex);
#endif      
      break;

/*------------------------------------------------------------------*/
      case VE_END:
#if VERBOSE>0      
        printf("Visual end\n");
#endif	
      VisEndFlag=1;
      break;

/*------------------------------------------------------------------*/
      case VE_CREATE_WINDOW:
#if VERBOSE>0      
        printf("Create window\n");
#endif	
      
#if CHECK>0
        if (e->window==NULL){
	  NTHROW_NP_EXC("Event.window is NULL while processing CREATE_WINDOW event.");
	}
#endif      
        
	VisFLWindow *win;
	if (e->window->getTitle()==NULL){
          win = new VisFLWindow(e->window->x,e->window->y,
	                        e->window->w,e->window->h,"");
	}
	else{
          win = new VisFLWindow(e->window->x,e->window->y,
	                        e->window->w,e->window->h,e->window->getTitle());
        }				

#if CHECK>0
	if (win==NULL){
	  NTHROW_MA_EXC("new VisFLWindow() failed"
	                " while processing CREATE_WINDOW event.");
	}
#endif	

	win->setVisWindow(e->window);
	win->resizable(win);
	win->end();
	win->show();

        break;


/*------------------------------------------------------------------*/
      case VE_DESTROY_WINDOW:
#if VERBOSE>0      
        printf("Destroy window\n");
#endif	
#if CHECK>1
        if (e->flwindow==NULL){
	  NTHROW_NP_EXC("Event.flwindow is NULL while processing DESTROY_WINDOW event.");
	}
#endif        
        delete e->flwindow;
        break;

/*------------------------------------------------------------------*/
      case VE_SET_WINDOW_TITLE:
#if VERBOSE>0      
        printf("Set window title\n");
#endif	
#if CHECK>0
        if (e->flwindow==NULL){
	  NTHROW_NP_EXC("Event.flwindow is NULL while processing SET_WINDOW_TITLE event.");
	}
#endif
#if CHECK>1
	if (e->window == NULL){
	  printf("Warning: e.window=NULL.\n");
	}
	else{
          if (e->flwindow != e->window->win){
            printf("Warning: e.flwindow(%p)!=e.window.win(%p).\n",e->flwindow,e->window->win);
	  }
	}
#endif
	
        if (e->pointer==NULL){
	  e->flwindow->label("");
	}        
	else{
	  e->flwindow->label((char *)e->pointer);
	}
	break;


/*------------------------------------------------------------------*/
      case VE_SET_WINDOW_POSITION:	
#if VERBOSE>0      
        printf("Set window position\n");
#endif	
#if CHECK>0
        if (e->flwindow==NULL){
	  NTHROW_NP_EXC("Event.flwindow is NULL while processing "
	                "SET_WINDOW_POSITION event.");
	}
#endif
#if CHECK>1
	if (e->window == NULL){
	  printf("Warning: e.window=NULL.\n");
	}
	else{
          if (e->flwindow != e->window->win){
            printf("Warning: e.flwindow(%p)!=e.window.win(%p).\n",e->flwindow,e->window->win);
	  }
	}
#endif
        e->flwindow->position(e->x,e->y);
	break;

/*------------------------------------------------------------------*/
      case VE_SET_WINDOW_SIZE:	
#if VERBOSE>0      
        printf("Set window size\n");
#endif	
#if CHECK>0
        if (e->flwindow==NULL){
	  NTHROW_NP_EXC("Event.flwindow is NULL while processing "
	                "SET_WINDOW_SIZE event.");
	}
#endif
#if CHECK>1
	if (e->window == NULL){
	  printf("Warning: e.window=NULL.\n");
	}
	else{
          if (e->flwindow != e->window->win){
            printf("Warning: e.flwindow(%p)!=e.window.win(%p).\n",e->flwindow,e->window->win);
	  }
	}
#endif
        e->flwindow->size(e->w,e->h);
	break;

/*------------------------------------------------------------------*/
      case VE_RESIZE_WINDOW:	
#if VERBOSE>0      
        printf("Set resize window\n");
#endif	
#if CHECK>0
        if (e->flwindow==NULL){
	  NTHROW_NP_EXC("Event.flwindow is NULL while processing "
	                "RESIZE_WINDOW event.");
	}
#endif
#if CHECK>1
	if (e->window == NULL){
	  printf("Warning: e.window=NULL.\n");
	}
	else{
          if (e->flwindow != e->window->win){
            printf("Warning: e.flwindow(%p)!=e.window.win(%p).\n",e->flwindow,e->window->win);
	  }
	}
#endif
        e->flwindow->resize(e->x,e->y,e->w,e->h);
	break;

/*------------------------------------------------------------------*/
      case VE_SHOW_WINDOW:	
#if VERBOSE>0      
        printf("Show window\n");
#endif	
#if CHECK>0
        if (e->flwindow==NULL){
	  NTHROW_NP_EXC("Event.flwindow is NULL while processing "
	                "SHOW_WINDOW event.");
	}
#endif
#if CHECK>1
	if (e->window == NULL){
	  printf("Warning: e.window=NULL.\n");
	}
	else{
          if (e->flwindow != e->window->win){
            printf("Warning: e.flwindow(%p)!=e.window.win(%p).\n",e->flwindow,e->window->win);
	  }
	}
#endif
        e->flwindow->show();
	break;

/*------------------------------------------------------------------*/
      case VE_HIDE_WINDOW:	
#if VERBOSE>0      
        printf("Hide window\n");
#endif	
#if CHECK>0
        if (e->flwindow==NULL){
	  NTHROW_NP_EXC("Event.flwindow is NULL while processing "
	                "HIDE_WINDOW event.");
	}
#endif
#if CHECK>1
	if (e->window == NULL){
	  printf("Warning: e.window=NULL.\n");
	}
	else{
          if (e->flwindow != e->window->win){
            printf("Warning: e.flwindow(%p)!=e.window.win(%p).\n",e->flwindow,e->window->win);
	  }
	}
#endif
	fflush(NULL);
        e->flwindow->hide();
#if VERBOSE>0      
        printf("Hide window -\n");
	fflush(NULL);
#endif	
	break;

/*------------------------------------------------------------------*/
      case VE_REDRAW_WINDOW:	
#if VERBOSE>0      
        printf("Redraw window\n");
#endif	
#if CHECK>0
        if (e->flwindow==NULL){
	  NTHROW_NP_EXC("Event.flwindow is NULL while processing "
	                "REDRAW_WINDOW event.");
	}
#endif
#if CHECK>1
	if (e->window == NULL){
	  printf("Warning: e.window=NULL.\n");
	}
	else{
          if (e->flwindow != e->window->win){
            printf("Warning: e.flwindow(%p)!=e.window.win(%p).\n",e->flwindow,e->window->win);
	  }
	}
#endif
        e->flwindow->redraw();
#if VERBOSE>0      
        printf("Redraw window OK\n");
#endif	
	
	break;
      
/*------------------------------------------------------------------*/
      default:
        char s[255];
	snprintf(s,250,"Unknown VisEvent number %d.",e->event);
        NTHROW_EXC(s);

/*------------------------------------------------------------------*/
    }
    VisEvent::pop();
    e=VisEvent::getCurrent();    
  }
}


void VisIdleFunc(){
  VisHandleWindowEvents();
}


void VisInit(){
#ifndef NO_THREADS  
  pthread_cond_init(&sync_cond,NULL);
#endif  
  VisEvent::init();
  Fl::visual(FL_DOUBLE|FL_RGB);
  Fl::set_idle(VisIdleFunc);
  init_mutexes();
  VisEndFlag=0;
}


void VisMainLoop(){
  runningMainLoop=1;
  while(!VisEndFlag){
/*
#if VERBOSE>0
    printf("VisMainLoop->VisHandleWindowEvents()\n");
#endif    
    VisHandleWindowEvents();
#if VERBOSE>0
    printf("VisMainLoop->VisHandleWindowEvents() -\n");
    printf("VisMainLoop->Fl::check()\n");
#endif    
    Fl::check();
#if VERBOSE>0
    printf("VisMainLoop->Fl::check() -\n");
#endif
*/

    Fl::wait();
  }
  runningMainLoop=0;
}

void VisCheck(){
#if VERBOSE>3
  printf("VisCheck()\n");
#endif  
  VisHandleWindowEvents();
#if VERBOSE>3
  printf("VisCheck() (vis event handling finished)\n");
#endif  
  Fl::check();
#if VERBOSE>3  
  printf("VisCheck() -\n");
#endif  
}

int checkThreadsSupport(){
#ifdef NO_THREADS
#  if VERBOSE>0
  printf("Threads are NOT supported.\n");
#  endif
  return 0;
#else
#  if VERBOSE>0
  printf("Threads are supported.\n");
#  endif
  return 1;
#endif    
}

#ifndef NO_THREADS
void *VisMainLoop_thrd(void *arg){
#if VERBOSE>0
  printf("Vis thread started.\n");
#endif
  VisMainLoop();
#if VERBOSE>0
  printf("Vis thread terminated.\n");
#endif
  return NULL;
}
#endif

void VisMainLoopInThread(){
#ifdef NO_THREADS
  NTHROW_EXC("Built without threads support.");
#else
  THREAD_CREATE(Vis_thread,VisMainLoop_thrd);
#endif  
}

void VisSync(){
#if VERBOSE>0
  printf("VisSync()\n");
#endif  
#ifndef NO_THREADS
  if (runningMainLoop){
    long num = VisEvent::add(VE_SYNC);
    MUTEX_LOCK(sync_mutex);
    while(sync_event_number!=num){
      pthread_cond_wait(&sync_cond,&sync_mutex);
    }
    MUTEX_UNLOCK(sync_mutex);
  }
  else{
    VisCheck();
  }
#else
  VisCheck();  
#endif    
#if VERBOSE>0
  printf("VisSync() -\n");
#endif  
}
