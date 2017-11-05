/*
 * Copyright (C) 2003 Orest Dubay <odubay@users.sourceforge.net>
 *
 * This file is part of ODPdom, a free DOM XML parser library.
 * See http://sourceforge.net/projects/odpdom/ for updates.
 * 
 * ODPdom is free software; you can redistribute it and/or modify
 * it under the terms of the GNU Lesser General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * ODPdom is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with ODPdom; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */
 
#include <stdio.h>
#include <string.h>
#include <exception>
#include <ODP/Exceptions.h>


DOMException::DOMException(unsigned short c, const char *sb){
  code=c;
  switch (c){
    case INDEX_SIZE_ERR:
      snprintf(buff, 250, "DOMException INDEX_SIZE_ERR:\n%s\n",sb);
      break;
    case DOMSTRING_SIZE_ERR:
      snprintf(buff, 250, "DOMException DOMSTRING_SIZE_ERR:\n%s\n",sb);
      break;
    case HIERARCHY_REQUEST_ERR:
      snprintf(buff, 250, "DOMException HIERARCHY_REQUEST_ERR:\n%s\n",sb);
      break;
    case WRONG_DOCUMENT_ERR:
      snprintf(buff, 250, "DOMException WRONG_DOCUMENT_ERR:\n%s\n",sb);
      break;
    case INVALID_CHARACTER_ERR:
      snprintf(buff, 250, "DOMException INVALID_CHARACTER_ERR:\n%s\n",sb);
      break;
    case NO_DATA_ALLOWED_ERR:
      snprintf(buff, 250, "DOMException NO_DATA_ALLOWED_ERR:\n%s\n",sb);
      break;
    case NO_MODIFICATION_ALLOWED_ERR:
      snprintf(buff, 250, "DOMException NO_MODIFICATION_ALLOWED_ERR:\n%s\n",sb);
      break;
    case NOT_FOUND_ERR:
      snprintf(buff, 250, "DOMException NOT_FOUND_ERR:\n%s\n",sb);
      break;
    case NOT_SUPPORTED_ERR:
      snprintf(buff, 250, "DOMException NOT_SUPPORTED_ERR:\n%s\n",sb);
      break;
    case INUSE_ATTRIBUTE_ERR:
      snprintf(buff, 250, "DOMException INUSE_ATTRIBUTE_ERR:\n%s\n",sb);
      break;
  }
}

const char *DOMException::what(){
  buff[255]='\0';
  return buff;
}

ODPException::ODPException(const char *s){
  snprintf(buff, 250, "ODPException: %s\n",s);
}

const char *ODPException::what(){
  buff[255]='\0';
  return buff;
}

