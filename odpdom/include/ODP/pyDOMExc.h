#ifndef ODPpyDOMExc_h
#define ODPpyDOMExc_h

void throwPythonDOMException(unsigned short code,const char *msg){
  PyObject *exc;
  switch (code){
    case INDEX_SIZE_ERR  	   :
      exc = PyErr_NewException(PY_DOMEXC_MODULE "IndexSizeErr",NULL,NULL);
      PyErr_SetObject(exc,PyString_FromString(msg));
      break;
    case DOMSTRING_SIZE_ERR	   :
      exc = PyErr_NewException(PY_DOMEXC_MODULE "DomstringSizeErr",NULL,NULL);
      PyErr_SetObject(exc,PyString_FromString(msg));
      break;
    case HIERARCHY_REQUEST_ERR	   :
      exc = PyErr_NewException(PY_DOMEXC_MODULE "HierarchyRequestErr",NULL,NULL);
      PyErr_SetObject(exc,PyString_FromString(msg));
      break;
    case WRONG_DOCUMENT_ERR	   :
      exc = PyErr_NewException(PY_DOMEXC_MODULE "WrongDocumentErr",NULL,NULL);
      PyErr_SetObject(exc,PyString_FromString(msg));
      break;
    case INVALID_CHARACTER_ERR	   :
      exc = PyErr_NewException(PY_DOMEXC_MODULE "InvalidCharacterErr",NULL,NULL);
      PyErr_SetObject(exc,PyString_FromString(msg));
      break;
    case NO_DATA_ALLOWED_ERR	   :
      exc = PyErr_NewException(PY_DOMEXC_MODULE "NoDataAllowedErr",NULL,NULL);
      PyErr_SetObject(exc,PyString_FromString(msg));
      break;
    case NO_MODIFICATION_ALLOWED_ERR:
      exc = PyErr_NewException(PY_DOMEXC_MODULE "NoModificationAllowedErr",NULL,NULL);
      PyErr_SetObject(exc,PyString_FromString(msg));
      break;
    case NOT_FOUND_ERR		   :
      exc = PyErr_NewException(PY_DOMEXC_MODULE "NotFoundErr",NULL,NULL);
      PyErr_SetObject(exc,PyString_FromString(msg));
      break;
    case NOT_SUPPORTED_ERR	   :
      exc = PyErr_NewException(PY_DOMEXC_MODULE "NotSupportedErr",NULL,NULL);
      PyErr_SetObject(exc,PyString_FromString(msg));
      break;
    case INUSE_ATTRIBUTE_ERR	   :
      exc = PyErr_NewException(PY_DOMEXC_MODULE "InuseAttributeErr",NULL,NULL);
      PyErr_SetObject(exc,PyString_FromString(msg));
      break;
    default:  
      exc = PyErr_NewException(PY_DOMEXC_MODULE "DOMException",NULL,NULL);
      PyErr_SetObject(exc,PyString_FromString(msg));
  }
}

#endif
