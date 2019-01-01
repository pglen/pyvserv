#include <Python.h>

static char bdate[] = "1/1/2000";

PyObject *_bdate(PyObject *self, PyObject *args, PyObject *kwargs)
{
  return Py_BuildValue("s", bdate);
}


