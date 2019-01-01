#include <Python.h>

static  char version[] = "1.0";

extern PyObject *_bdate(PyObject *self, PyObject *args, PyObject *kwargs);
  
static PyObject *_version(PyObject *self, PyObject *args, PyObject *kwargs)
{
    return Py_BuildValue("s", version);
}

PyObject* 
hello(PyObject* self)
{
    printf("Hello world!\n");
    Py_RETURN_NONE;
}

static PyMethodDef functions[] = {
    {"hello",    (PyCFunction)hello, METH_NOARGS},
    { "version",   (PyCFunction)_version, METH_VARARGS|METH_KEYWORDS, "Bluepy version."},
    { "builddate",   (PyCFunction)_bdate, METH_VARARGS|METH_KEYWORDS, "Bluepy bdate."},
    {NULL, NULL, 0, NULL},
};


DL_EXPORT(void)
inithello(void)
{
    Py_InitModule("hello", functions);
}


