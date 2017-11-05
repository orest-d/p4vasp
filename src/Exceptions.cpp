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
#include <stdexcept>
#include <p4vasp/ClassInterface.h>
#include <p4vasp/Exceptions.h>

#ifndef NO_THROW
Exception::Exception(){
  place=NULL;
  strcpy(buff,"Exception.\n");
}


Exception::Exception(ClassInterface *c,const char *s){
  place=c;
  if (c==NULL){
    if (s==NULL){
      strcpy(buff,"Exception.\n");  
    }
    else{
      snprintf(buff,250,"Exception:\n%s\n",s);
    }
  }
  else{
    if (s==NULL){
      snprintf(buff,250,"Exception in class %s.\n",c->getClassName());
    }
    else{
      snprintf(buff,250,"Exception in class %s:\n%s\n",c->getClassName(),s);
    }
  }
}

Exception::Exception(const char *s){
  place=NULL;
  if (s==NULL){
    strcpy(buff,"Exception.\n");  
  }
  else{
    snprintf(buff,250,"Exception: %s\n",s);
  }
}

const char *Exception::what(){
  buff[255]='\0';
  return buff;
}



NullPointerException::NullPointerException(){
  place=NULL;
  strcpy(buff,"NULL pointer exception.\n");
}


NullPointerException::NullPointerException(ClassInterface *c,const char *s){
  place=c;
  if (c==NULL){
    if (s==NULL){
      strcpy(buff,"NULL pointer exception.\n");  
    }
    else{
      snprintf(buff,250,"NULL pointer exception:\n%s\n",s);
    }
  }
  else{
    if (s==NULL){
      snprintf(buff,250,"NULL pointer exception in class %s.\n",c->getClassName());
    }
    else{
      snprintf(buff,250,"NULL pointer exception in class %s:\n%s\n",c->getClassName(),s);
    }
  }
}

NullPointerException::NullPointerException(const char *s){
  place=NULL;
  if (s==NULL){
    strcpy(buff,"NULL pointer exception.\n");  
  }
  else{
    snprintf(buff,250,"NULL pointer exception:\n%s\n",s);
  }
}

const char *NullPointerException::what(){
  buff[255]='\0';
  return buff;
}



MemoryAllocationException::MemoryAllocationException(){
  place=NULL;
  strcpy(buff,"Memory allocation exception.\n");
}

MemoryAllocationException::MemoryAllocationException(ClassInterface *c,const char *s){
  place=c;
  if (c==NULL){
    if (s==NULL){
      strcpy(buff,"Memory allocation exception.\n");  
    }
    else{
      snprintf(buff,250,"Memory allocation exception:\n%s\n",s);
    }
  }
  else{
    if (s==NULL){
      snprintf(buff,250,"Memory allocation exception in class %s.\n",c->getClassName());
    }
    else{
      snprintf(buff,250,"Memory allocation exception in class %s:\n%s\n",c->getClassName(),s);
    }
  }
}

MemoryAllocationException::MemoryAllocationException(const char *s){
  place=NULL;
  if (s==NULL){
    strcpy(buff,"Memory allocation exception.\n");  
  }
  else{
    snprintf(buff,250,"Memory allocation exception: %s\n",s);
  }
}


const char *MemoryAllocationException::what(){
  buff[255]='\0';
  return buff;
}



RangeException::RangeException():out_of_range("Range exception.\n"){
  place=NULL;
  strcpy(buff,"Range exception.\n");
  min=0;
  max=0;
  value=0;
}


RangeException::RangeException(ClassInterface *c,
                               const char *s,
			       long min,
			       long max,
			       long value):out_of_range(s){
  place=c;
  this->min=min;
  this->max=max;
  this->value=value;
  if (c==NULL){
    if (s==NULL){
      snprintf(buff,250,
      "Range exception.\nValue %ld out of range [%ld,%ld].\n",value,min,max);  
    }
    else{
      snprintf(buff,250,
      "Range exception.\nValue %ld out of range [%ld,%ld];\n%s\n",value,min,max,s);
    }
  }
  else{
    if (s==NULL){
      snprintf(buff,250,
      "Range exception in class %s.\nValue %ld out of range [%ld,%ld].\n",
      c->getClassName(),value,min,max);
    }
    else{
      snprintf(buff,250,
      "Range exception in class %s.\nValue %ld out of range [%ld,%ld].\n%s\n",
      c->getClassName(),value,min,max,s);
    }
  }
}

RangeException::RangeException(const char *s):out_of_range(s){
  place=NULL;
  if (s==NULL){
    strcpy(buff,"Range exception.\n");  
  }
  else{
    snprintf(buff,250,"Range exception:\n%s\n",s);
  }
}

const char *RangeException::what(){
  buff[255]='\0';
  return buff;
}

#endif
