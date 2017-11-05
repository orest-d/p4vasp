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
#include <p4vasp/VisStructureArrowsDrawer.h>
#include <math.h>
#include <FL/gl.h>
#include <GL/glu.h>
#include <stdio.h>
#include <string.h>
#include <p4vasp/vecutils.h>


const char *VisStructureArrowsDrawer::getClassName(){return "VisStructureArrowsDrawer";}

VisStructureArrowsDrawer::VisStructureArrowsDrawer(VisStructureDrawer *sd):VisDrawer(){
  this->structure_drawer=sd;
  arrows_len=0;
  arrows=NULL;
  arrow_radius     = 0.06;
  arrowhead_radius = 0.14;
  arrowhead_length = 0.4;
  red              = 0.5;
  green            = 0.5;
  blue             = 0.5;
  arrows_scale     = 1.0;
}


VisStructureArrowsDrawer::~VisStructureArrowsDrawer(){
  if (arrows!=NULL){
    delete []arrows;
    arrows=NULL;
    arrows_len=0;
  }
}


void VisStructureArrowsDrawer::draw(){
#if CHECK>0
  if (structure_drawer==NULL){
    THROW_NP_EXC("structure_drawer=NULL in draw()");
  }
#endif
  Structure *s=structure_drawer->getStructure();
  if ( (arrows_len>0) && (s!=NULL)){
    if (s->len()>0){
#if CHECK>0
      if (structure_drawer->info==NULL){
	THROW_NP_EXC("structure_drawer->info=NULL in draw()");
      }
      if (arrows==NULL){
	THROW_NP_EXC("arrows=NULL in draw()");
      }
#endif
      int count=arrows_len;
      if (s->len()<count){
	count=s->len();
      }
      glColor3d(red,green,blue);
      double sr   = structure_drawer->arrow_radius;
      double shr  = structure_drawer->arrowhead_radius;
      double shl  = structure_drawer->arrowhead_length;
      structure_drawer->arrow_radius      = arrow_radius;
      structure_drawer->arrowhead_radius  = arrowhead_radius;
      structure_drawer->arrowhead_length  = arrowhead_length;
      int nx=structure_drawer->getMultiple1();
      int ny=structure_drawer->getMultiple2();
      int nz=structure_drawer->getMultiple3();
      for (int i1=0;i1<nx;i1++){
	for (int i2=0;i2<ny;i2++){
	  for (int i3=0;i3<nz;i3++){
            double v[3]={0.0,0.0,0.0};
            add3(v,i1-nx/2,s->basis1);
            add3(v,i2-ny/2,s->basis2);
            add3(v,i3-nz/2,s->basis3);

            glPushMatrix();
            glTranslatef(v[0],v[1],v[2]);
	    for (int i=0; i<count; i++){
	      if (!structure_drawer->info->getRecord(i)->hidden){
	        double *d=s->get(i);
	        structure_drawer->arrow(
		  d[0],d[1],d[2],
		  arrows[3*i],arrows[3*i+1],arrows[3*i+2],arrows_scale);
	      }
	    }
            glPopMatrix();
	  }
	}
      }	
      structure_drawer->arrow_radius      = sr;
      structure_drawer->arrowhead_radius  = shr;
      structure_drawer->arrowhead_length  = shl;
    }
  }
}

void VisStructureArrowsDrawer::updateStructure(){
#if CHECK>0
  if (structure_drawer==NULL){
    THROW_NP_EXC("VisStructureDrawer *argument=NULL in constructor");
  }
#endif
  
  if (structure_drawer->getStructure()==NULL){
    if (arrows!=NULL){
      delete []arrows;
      arrows=NULL;
      arrows_len=0;
    }      
  }
  else{
    int newlen=structure_drawer->getStructure()->len();
  
    if (arrows_len != newlen){
      if (newlen==0){
	if (arrows != NULL){
	  delete []arrows;
	  arrows=NULL;
	  arrows_len=0;
	}      
      }
      else{
	double *newarrows=new double[3*newlen];
	if (arrows_len>0){
          if (arrows_len<=newlen){
	    for (int i=3*arrows_len; i<(3*newlen); i++){
	      newarrows[i]=0.0;
	    }
            memcpy(newarrows,arrows,sizeof(double)*3*arrows_len);
	  }
	  else{
            memcpy(newarrows,arrows,sizeof(double)*3*newlen);
	  }
	}
	else{
	  for (int i=0; i<(3*newlen); i++){
	    newarrows[i]=0.0;
	  }
	}
	if (arrows!=NULL){
	  delete []arrows;
	}      
	arrows=newarrows;
	arrows_len=newlen;
      }
    }
  }
}

int VisStructureArrowsDrawer::len(){
  return arrows_len;
}

double *VisStructureArrowsDrawer::getArrow(int i){
#if CHECK>0
  if ((i<0)||(i>=arrows_len)){
    THROW_R_EXC("getArrow() failed",0,arrows_len,i);
  }
#endif
#if CHECK>1
  if (arrows==NULL){
    THROW_NP_EXC("arrows=NULL in getArrow()");
  }
#endif
  return &arrows[3*i];
}

void VisStructureArrowsDrawer::setArrow(int i,double x, double y, double z){
#if CHECK>0
  if ((i<0)||(i>=arrows_len)){
    THROW_R_EXC("setArrow() failed",0,arrows_len,i);
  }
#endif
#if CHECK>1
  if (arrows==NULL){
    THROW_NP_EXC("arrows=NULL in getArrow()");
  }
#endif
  arrows[3*i+0]=x;
  arrows[3*i+1]=y;
  arrows[3*i+2]=z;
}

void VisStructureArrowsDrawer::setScale(double s){
  arrows_scale=s;
  redraw();
}

double VisStructureArrowsDrawer::getScale(){
  return arrows_scale;
}

