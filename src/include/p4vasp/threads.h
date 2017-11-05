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

#ifndef threads_h
#define threads_h

#ifdef NO_THREADS
#  define MUTEX(x)
#  define MUTEX_INIT(x)
#  define MUTEX_LOCK(x)
#  define MUTEX_UNLOCK(x)
#  define MUTEX_DESTROY(x)

#  define THREAD(x)
#  define THREAD_CREATE(t,f)
#  define THREAD_EXIT(x)

#else
#  include <pthread.h>
#  define MUTEX(x)                   pthread_mutex_t x
#  define MUTEX_INIT(x)              pthread_mutex_init(&(x),NULL)
#  define MUTEX_LOCK(x)              pthread_mutex_lock(&(x))
#  define MUTEX_UNLOCK(x)            pthread_mutex_unlock(&(x))
#  define MUTEX_DESTROY(x)           pthread_mutex_destroy(&(x))

#  define THREAD(x)                  pthread_t x
#  define THREAD_CREATE(t,f)         pthread_create(&(t),NULL,f,NULL)
#  define THREAD_EXIT(x)             pthread_exit(x)

#endif

#endif
