// -----------------------------------------------------------------------
// Python bindings for bluepoint2.

#include <Python.h>
//#include <pygobject.h>

#include "bluepy.h"
#include "bluepoint2.h"
#include "bdate.h"

//#define OPEN_IMAGE 1
 
// -----------------------------------------------------------------------
// Vars:

PyObject *module;                   // This is us

static  char version[] = "1.0";
	
static PyObject *_bdate(PyObject *self, PyObject *args, PyObject *kwargs)
{
  return Py_BuildValue("s", bdate);
}
  
static PyObject *_version(PyObject *self, PyObject *args, PyObject *kwargs)
{
    return Py_BuildValue("s", version);
}

static PyObject *_encrypt(PyObject *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = { "buffer", "password",  NULL };
    char *buff = "";  char *passw = ""; char *mem;
    int  blen = 0, plen = 0;
    Py_buffer pb1, pb2;
    
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "y*y*", kwlist, 
                                &pb1, &pb2))
        return NULL;
        
    buff  = pb1.buf;  passw = pb2.buf;
    blen  = pb1.len;  plen  = pb2.len;
  
    //printf("in object: '%s'\n", pb1.buf);
      
    mem = malloc(blen+1);
    if(mem == NULL)
        {
        return PyErr_NoMemory();
        }
    memcpy(mem, buff, blen);
    bluepoint2_encrypt(mem, blen, passw, plen);
    mem[blen] = 0;
    
    return Py_BuildValue("y#", mem, blen);
}

static PyObject *_decrypt(PyObject *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = { "buffer", "password",  NULL };
    char *buff = ""; char *passw = ""; char *mem;
    int  blen = 0, plen = 0;
    
    Py_buffer pb1, pb2;
    
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "y*y*", kwlist, 
                                &pb1, &pb2))
        return NULL;
        
    buff  = pb1.buf;  passw = pb2.buf;
    blen  = pb1.len;  plen  = pb2.len;
  
    mem = malloc(blen + 1);
    if(mem == NULL)
        {
        return PyErr_NoMemory();
        }
    memcpy(mem, buff, blen);
    bluepoint2_decrypt(mem, blen, passw, plen);
    mem[blen] = 0;
    return Py_BuildValue("y#", mem, blen);
}

static PyObject *_tohex(PyObject *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = { "buffer", NULL };
    char *buff = ""; char *mem;
    int  blen = 0, plen = 0;
    Py_buffer pb1;
    
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "y*", kwlist, 
                        &pb1))
        return NULL;
        
    buff = pb1.buf; blen = pb1.len;    
        
    plen = 3*blen;
    mem = malloc(plen);
    if(mem == NULL)
        {
        return PyErr_NoMemory();
        }
    bluepoint2_tohex(buff, blen, mem, &plen);
    return Py_BuildValue("s#", mem, plen);
}

// Erase object. If null specified, encrypt it

static PyObject *_destroy(PyObject *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = { "buffer",  "fill", NULL };
    char *buff = ""; int  blen = 0; int fill = 0;
    
    Py_buffer pb1;
    
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "y*|i", kwlist, 
                        &pb1, &fill))
        return NULL;
        
    buff = pb1.buf; blen = pb1.len;    
    if(fill == 0)
        {
        char aa[] = "bluepoint2";
        srand(time(NULL));
        *((short *)aa) = rand();
        bluepoint2_encrypt(buff, blen, aa, strlen(aa));
        }
    else
        {
        memset(buff, fill, blen);
        }
        
    return Py_BuildValue("i", 0);
}

static PyObject *_fromhex(PyObject *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = { "buffer",  NULL };
    char *buff = ""; char *mem;
    int  blen = 0, plen = 0;
    
    Py_buffer pb1;
    
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "s*", kwlist, 
                        &pb1))
        return NULL;
        
    buff = pb1.buf; blen = pb1.len;    
   
    plen = 3*blen;
    mem = malloc(plen);
    if(mem == NULL)
        {
        return PyErr_NoMemory();
        }
    bluepoint2_fromhex(buff, blen, mem, &plen);
    return Py_BuildValue("y#", mem, plen);
}

// Define module

PyMethodDef bluepy_functions[] = 
    {
    
    { "version",   (PyCFunction)_version, METH_VARARGS|METH_KEYWORDS, "Bluepy version."},
    { "builddate", (PyCFunction)_bdate,   METH_VARARGS|METH_KEYWORDS, "Bluepy build date."},
    { "encrypt2",   (PyCFunction)_encrypt, METH_VARARGS|METH_KEYWORDS, \
        "Bluepy encryption. Pass buffer and pass."},
    { "decrypt2",   (PyCFunction)_decrypt, METH_VARARGS|METH_KEYWORDS, \
        "Bluepy decryption. Pass buffer and pass."},
    { "destroy",   (PyCFunction)_destroy, METH_VARARGS|METH_KEYWORDS, 
        "Bluepy destruction. Scramble variable. Fill with '0' or number. " \
        "Pass zero to randomize."},
    { "tohex",     (PyCFunction)_tohex,   METH_VARARGS|METH_KEYWORDS, \
        "Bluepy tohex. Convert to hex string."},
    { "fromhex",   (PyCFunction)_fromhex, METH_VARARGS|METH_KEYWORDS, \
        "Bluepy fromhex. Convert from hex string."},
    
    {  NULL },
    };
    
#if PY_MAJOR_VERSION >= 3
#define GETSTATE(m) ((struct module_state*)PyModule_GetState(m))
#else
#define GETSTATE(m) (&_state)
//static struct module_state _state;
#endif

#if PY_MAJOR_VERSION >= 3

static PyObject *
error_out(PyObject *m) {
    struct module_state *st = GETSTATE(m);
    //PyErr_SetString(st->error, "something bad happened");
    return NULL;
}

static PyMethodDef myextension_methods[] = {
    {"error_out", (PyCFunction)error_out, METH_NOARGS, NULL},
    {NULL, NULL}
};

struct module_state {
    PyObject *error;
};


static int myextension_traverse(PyObject *m, visitproc visit, void *arg) {
    Py_VISIT(GETSTATE(m)->error);
    return 0;
}

static int myextension_clear(PyObject *m) {
    Py_CLEAR(GETSTATE(m)->error);
    return 0;
}

    
static struct PyModuleDef moduledef = {
        PyModuleDef_HEAD_INIT,
        "bluepy",
        NULL,
        sizeof(struct module_state),
        bluepy_functions,
        NULL,
        myextension_traverse,
        myextension_clear,
        NULL
};    

#endif

// -----------------------------------------------------------------------
// Init:

#if PY_MAJOR_VERSION >= 3
PyMODINIT_FUNC
PyInit_bluepy2(void)

#else
DL_EXPORT(void) 
initbluepy(void)
#endif

{
    //init_pygobject ();

#if PY_MAJOR_VERSION >= 3
    module = PyModule_Create(&moduledef);
    #define IS_PY3K
#else
    module = Py_InitModule3("bluepy", bluepy_functions, "Bluepoint encryption library for Python.");
#endif

    //d = PyModule_GetDict (module);
    
    // Constants
    PyModule_AddIntConstant(module, (char *)"OPEN", 1);
    PyModule_AddStringConstant(module, (char *)"author", "Peter Glen");

    // Values:
    PyModule_AddObject(module, "verbose",   Py_BuildValue("i", 0));

    if (PyErr_Occurred ()) {       
	   Py_FatalError ("can't initialise bluepy module");
    }
    #if PY_MAJOR_VERSION >= 3
    return module;
#endif
}

// EOF



