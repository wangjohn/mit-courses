/**
 * PyAudio: Python Bindings for PortAudio.
 *
 * Copyright (c) 2006-2012 Hubert Pham
 *
 * Permission is hereby granted, free of charge, to any person
 * obtaining a copy of this software and associated documentation
 * files (the "Software"), to deal in the Software without
 * restriction, including without limitation the rights to use, copy,
 * modify, merge, publish, distribute, sublicense, and/or sell copies
 * of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be
 * included in all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 * EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
 * MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 * NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
 * BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
 * ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
 * CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

#include <stdio.h>
#include "Python.h"
#include "portaudio.h"
#include "_portaudiomodule.h"

#ifdef MACOSX
#include "pa_mac_core.h"
#endif

#define DEFAULT_FRAMES_PER_BUFFER 1024
/* #define VERBOSE */

#define min(a,b) \
   ({ __typeof__ (a) _a = (a); \
       __typeof__ (b) _b = (b); \
     _a < _b ? _a : _b; })

/************************************************************
 *
 * Table of Contents
 *
 * I. Exportable PortAudio Method Definitions
 * II. Python Object Wrappers
 *     - PaDeviceInfo
 *     - PaHostInfo
 *     - PaStream
 * III. PortAudio Method Implementations
 *     - Initialization/Termination
 *     - HostAPI
 *     - DeviceAPI
 *     - Stream Open/Close
 *     - Stream Start/Stop/Info
 *     - Stream Read/Write
 * IV. Python Module Init
 *     - PaHostApiTypeId enum constants
 *
 ************************************************************/


/************************************************************
 *
 * I. Exportable Python Methods
 *
 ************************************************************/

static PyMethodDef paMethods[] = {

  /* version */
  {"get_version", pa_get_version, METH_VARARGS, "get version"},
  {"get_version_text", pa_get_version_text, METH_VARARGS,
   "get version text"},

  /* inits */
  {"initialize", pa_initialize, METH_VARARGS, "initialize portaudio"},
  {"terminate", pa_terminate, METH_VARARGS, "terminate portaudio"},

  /* host api */
  {"get_host_api_count", pa_get_host_api_count, METH_VARARGS,
   "get host API count"},

  {"get_default_host_api", pa_get_default_host_api, METH_VARARGS,
   "get default host API index"},

  {"host_api_type_id_to_host_api_index",
   pa_host_api_type_id_to_host_api_index, METH_VARARGS,
   "get default host API index"},

  {"host_api_device_index_to_device_index",
   pa_host_api_device_index_to_device_index,
   METH_VARARGS,
   "get default host API index"},

  {"get_host_api_info", pa_get_host_api_info, METH_VARARGS,
   "get host api information"},

  /* device api */
  {"get_device_count", pa_get_device_count, METH_VARARGS,
   "get host API count"},

  {"get_default_input_device", pa_get_default_input_device, METH_VARARGS,
   "get default input device index"},

  {"get_default_output_device", pa_get_default_output_device, METH_VARARGS,
   "get default output device index"},

  {"get_device_info", pa_get_device_info, METH_VARARGS,
   "get device information"},

  /* stream open/close */
  {"open", (PyCFunction) pa_open, METH_VARARGS | METH_KEYWORDS,
   "open port audio stream"},
  {"close", pa_close, METH_VARARGS, "close port audio stream"},
  {"get_sample_size", pa_get_sample_size, METH_VARARGS,
   "get sample size of a format in bytes"},
  {"is_format_supported", (PyCFunction) pa_is_format_supported,
   METH_VARARGS | METH_KEYWORDS,
   "returns whether specified format is supported"},

  /* stream start/stop */
  {"start_stream", pa_start_stream, METH_VARARGS, "starts port audio stream"},
  {"stop_stream", pa_stop_stream, METH_VARARGS, "stops  port audio stream"},
  {"abort_stream", pa_abort_stream, METH_VARARGS, "aborts port audio stream"},
  {"is_stream_stopped", pa_is_stream_stopped, METH_VARARGS,
   "returns whether stream is stopped"},
  {"is_stream_active", pa_is_stream_active, METH_VARARGS,
   "returns whether stream is active"},
  {"get_stream_time", pa_get_stream_time, METH_VARARGS,
   "returns stream time"},
  {"get_stream_cpu_load", pa_get_stream_cpu_load, METH_VARARGS,
   "returns stream CPU load -- always 0 for blocking mode"},

  /* stream read/write */
  {"write_stream", pa_write_stream, METH_VARARGS, "write to stream"},
  {"read_stream", pa_read_stream, METH_VARARGS, "read from stream"},

  {"get_stream_write_available",
   pa_get_stream_write_available, METH_VARARGS,
   "get buffer available for writing"},

  {"get_stream_read_available",
   pa_get_stream_read_available, METH_VARARGS,
   "get buffer available for reading"},

  {NULL, NULL, 0, NULL}
};


/************************************************************
 *
 * II. Python Object Wrappers
 *
 ************************************************************/


/*************************************************************
 * PaDeviceInfo Type : Python object wrapper for PaDeviceInfo
 *************************************************************/

typedef struct {
  PyObject_HEAD
  PaDeviceInfo *devInfo;
} _pyAudio_paDeviceInfo;


/* sepcific getters into the PaDeviceInfo struct */

static PyObject *
_pyAudio_paDeviceInfo_get_structVersion(_pyAudio_paDeviceInfo *self,
					void *closure)
{
  /* sanity check */
  if (!self->devInfo) {
    PyErr_SetString(PyExc_AttributeError,
		    "No Device Info available");
    return NULL;
  }

  return PyLong_FromLong(self->devInfo->structVersion);
}

static PyObject *
_pyAudio_paDeviceInfo_get_name(_pyAudio_paDeviceInfo *self,
			       void *closure)
{
  /* sanity check */
  if ((!self->devInfo) || (self->devInfo->name == NULL)) {
    PyErr_SetString(PyExc_AttributeError,
		    "No Device Info available");
    return NULL;
  }

  return PyUnicode_FromString(self->devInfo->name);
}

static PyObject *
_pyAudio_paDeviceInfo_get_hostApi(_pyAudio_paDeviceInfo *self,
				  void *closure)
{
  /* sanity check */
  if (!self->devInfo) {
    PyErr_SetString(PyExc_AttributeError,
		    "No Device Info available");
    return NULL;
  }

  return PyLong_FromLong(self->devInfo->hostApi);
}

static PyObject *
_pyAudio_paDeviceInfo_get_maxInputChannels(_pyAudio_paDeviceInfo *self,
					   void *closure)
{
  /* sanity check */
  if (!self->devInfo) {
    PyErr_SetString(PyExc_AttributeError,
		    "No Device Info available");
    return NULL;
  }

  return PyLong_FromLong(self->devInfo->maxInputChannels);
}

static PyObject *
_pyAudio_paDeviceInfo_get_maxOutputChannels(_pyAudio_paDeviceInfo *self,
					    void *closure)
{
  /* sanity check */
  if (!self->devInfo) {
    PyErr_SetString(PyExc_AttributeError,
		    "No Device Info available");
    return NULL;
  }

  return PyLong_FromLong(self->devInfo->maxOutputChannels);
}

static PyObject *
_pyAudio_paDeviceInfo_get_defaultLowInputLatency(_pyAudio_paDeviceInfo *self,
						 void *closure)
{
  /* sanity check */
  if (!self->devInfo) {
    PyErr_SetString(PyExc_AttributeError,
		    "No Device Info available");
    return NULL;
  }

  return PyFloat_FromDouble(self->devInfo->defaultLowInputLatency);
}

static PyObject *
_pyAudio_paDeviceInfo_get_defaultLowOutputLatency(_pyAudio_paDeviceInfo *self,
						  void *closure)
{
  /* sanity check */
  if (!self->devInfo) {
    PyErr_SetString(PyExc_AttributeError,
		    "No Device Info available");
    return NULL;
  }

  return PyFloat_FromDouble(self->devInfo->defaultLowOutputLatency);
}


static PyObject *
_pyAudio_paDeviceInfo_get_defaultHighInputLatency(_pyAudio_paDeviceInfo *self,
						  void *closure)
{
  /* sanity check */
  if (!self->devInfo) {
    PyErr_SetString(PyExc_AttributeError,
		    "No Device Info available");
    return NULL;
  }

  return PyFloat_FromDouble(self->devInfo->defaultHighInputLatency);
}

static PyObject *
_pyAudio_paDeviceInfo_get_defaultHighOutputLatency(_pyAudio_paDeviceInfo *self,
						   void *closure)
{
  /* sanity check */
  if (!self->devInfo) {
    PyErr_SetString(PyExc_AttributeError,
		    "No Device Info available");
    return NULL;
  }

  return PyFloat_FromDouble(self->devInfo->defaultHighOutputLatency);
}

static PyObject *
_pyAudio_paDeviceInfo_get_defaultSampleRate(_pyAudio_paDeviceInfo *self,
					    void *closure)
{
  /* sanity check */
  if (!self->devInfo) {
    PyErr_SetString(PyExc_AttributeError,
		    "No Device Info available");
    return NULL;
  }

  return PyFloat_FromDouble(self->devInfo->defaultSampleRate);
}



static int
_pyAudio_paDeviceInfo_antiset(_pyAudio_paDeviceInfo *self,
			  PyObject *value,
			  void *closure)
{
  /* read-only: do not allow users to change values */
  PyErr_SetString(PyExc_AttributeError,
		  "Fields read-only: cannot modify values");
  return -1;
}

static PyGetSetDef _pyAudio_paDeviceInfo_getseters[] = {
  {"name",
   (getter) _pyAudio_paDeviceInfo_get_name,
   (setter) _pyAudio_paDeviceInfo_antiset,
   "device name",
   NULL},

  {"structVersion",
   (getter) _pyAudio_paDeviceInfo_get_structVersion,
   (setter) _pyAudio_paDeviceInfo_antiset,
   "struct version",
   NULL},

  {"hostApi",
   (getter) _pyAudio_paDeviceInfo_get_hostApi,
   (setter) _pyAudio_paDeviceInfo_antiset,
   "host api index",
   NULL},

  {"maxInputChannels",
   (getter) _pyAudio_paDeviceInfo_get_maxInputChannels,
   (setter) _pyAudio_paDeviceInfo_antiset,
   "max input channels",
   NULL},

  {"maxOutputChannels",
   (getter) _pyAudio_paDeviceInfo_get_maxOutputChannels,
   (setter) _pyAudio_paDeviceInfo_antiset,
   "max output channels",
   NULL},

  {"defaultLowInputLatency",
   (getter) _pyAudio_paDeviceInfo_get_defaultLowInputLatency,
   (setter) _pyAudio_paDeviceInfo_antiset,
   "default low input latency",
   NULL},

  {"defaultLowOutputLatency",
   (getter) _pyAudio_paDeviceInfo_get_defaultLowOutputLatency,
   (setter) _pyAudio_paDeviceInfo_antiset,
   "default low output latency",
   NULL},

  {"defaultHighInputLatency",
   (getter) _pyAudio_paDeviceInfo_get_defaultHighInputLatency,
   (setter) _pyAudio_paDeviceInfo_antiset,
   "default high input latency",
   NULL},

  {"defaultHighOutputLatency",
   (getter) _pyAudio_paDeviceInfo_get_defaultHighOutputLatency,
   (setter) _pyAudio_paDeviceInfo_antiset,
   "default high output latency",
   NULL},

  {"defaultSampleRate",
   (getter) _pyAudio_paDeviceInfo_get_defaultSampleRate,
   (setter) _pyAudio_paDeviceInfo_antiset,
   "default sample rate",
   NULL},

  {NULL}
};

static void
_pyAudio_paDeviceInfo_dealloc(_pyAudio_paDeviceInfo* self)
{
  /* reset the pointer */
  self->devInfo = NULL;

  /* free the object */
  Py_TYPE(self)->tp_free((PyObject*) self);
}

static PyTypeObject _pyAudio_paDeviceInfoType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_portaudio.paDeviceInfo", /*tp_name*/
    sizeof(_pyAudio_paDeviceInfo),   /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor) _pyAudio_paDeviceInfo_dealloc, /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    0,                         /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT,        /*tp_flags*/
    "Port Audio Device Info",       /* tp_doc */
    0,  /* tp_traverse */
    0,  /* tp_clear */
    0,  /* tp_richcompare */
    0,  /* tp_weaklistoffset */
    0,  /* tp_iter */
    0,  /* tp_iternext */
    0,  /* tp_methods */
    0,  /* tp_members */
    _pyAudio_paDeviceInfo_getseters, /* tp_getset */
    0,  /* tp_base */
    0,  /* tp_dict */
    0,  /* tp_descr_get */
    0,  /* tp_descr_set */
    0,  /* tp_dictoffset */
    0,  /* tp_init */
    0,  /* tp_alloc */
    0,  /* tp_new */
};

static _pyAudio_paDeviceInfo *
_create_paDeviceInfo_object(void)
{
  _pyAudio_paDeviceInfo *obj;

  /* don't allow subclassing? */
  obj = (_pyAudio_paDeviceInfo *) PyObject_New(_pyAudio_paDeviceInfo,
					       &_pyAudio_paDeviceInfoType);

  /* obj = (_pyAudio_Stream*)
     _pyAudio_StreamType.tp_alloc(&_pyAudio_StreamType, 0); */
  return obj;
}




/*************************************************************
 * PaHostApi Info Python Object
 *************************************************************/

typedef struct {
  PyObject_HEAD
  PaHostApiInfo *apiInfo;
} _pyAudio_paHostApiInfo;

/* sepcific getters into the PaDeviceInfo struct */

static PyObject *
_pyAudio_paHostApiInfo_get_structVersion(_pyAudio_paHostApiInfo *self,
					 void *closure)
{
  /* sanity check */
  if ((!self->apiInfo)) {
    PyErr_SetString(PyExc_AttributeError,
		    "No HostApi Info available");
    return NULL;
  }

  return PyLong_FromLong(self->apiInfo->structVersion);
}

static PyObject *
_pyAudio_paHostApiInfo_get_type(_pyAudio_paHostApiInfo *self,
				void *closure)
{
  /* sanity check */
  if ((!self->apiInfo)) {
    PyErr_SetString(PyExc_AttributeError,
		    "No HostApi Info available");
    return NULL;
  }

  return PyLong_FromLong((long) self->apiInfo->type);
}

static PyObject *
_pyAudio_paHostApiInfo_get_name(_pyAudio_paHostApiInfo *self,
				void *closure)
{
  /* sanity check */
  if ((!self->apiInfo) || (self->apiInfo->name == NULL)) {
    PyErr_SetString(PyExc_AttributeError,
		    "No HostApi Info available");
    return NULL;
  }

  return PyUnicode_FromString(self->apiInfo->name);
}

static PyObject *
_pyAudio_paHostApiInfo_get_deviceCount(_pyAudio_paHostApiInfo *self,
				       void *closure)
{
  /* sanity check */
  if ((!self->apiInfo)) {
    PyErr_SetString(PyExc_AttributeError,
		    "No HostApi Info available");
    return NULL;
  }

  return PyLong_FromLong(self->apiInfo->deviceCount);
}

static PyObject *
_pyAudio_paHostApiInfo_get_defaultInputDevice(_pyAudio_paHostApiInfo *self,
					      void *closure)
{
  /* sanity check */
  if ((!self->apiInfo)) {
    PyErr_SetString(PyExc_AttributeError,
		    "No HostApi Info available");
    return NULL;
  }

  return PyLong_FromLong(self->apiInfo->defaultInputDevice);
}

static PyObject *
_pyAudio_paHostApiInfo_get_defaultOutputDevice(_pyAudio_paHostApiInfo *self,
					       void *closure)
{
  /* sanity check */
  if ((!self->apiInfo)) {
    PyErr_SetString(PyExc_AttributeError,
		    "No HostApi Info available");
    return NULL;
  }

  return PyLong_FromLong(self->apiInfo->defaultOutputDevice);
}

static int
_pyAudio_paHostApiInfo_antiset(_pyAudio_paDeviceInfo *self,
			       PyObject *value,
			       void *closure)
{
  /* read-only: do not allow users to change values */
  PyErr_SetString(PyExc_AttributeError,
		  "Fields read-only: cannot modify values");
  return -1;
}

static void
_pyAudio_paHostApiInfo_dealloc(_pyAudio_paHostApiInfo* self)
{
  /* reset the pointer */
  self->apiInfo = NULL;

  /* free the object */
  Py_TYPE(self)->tp_free((PyObject*) self);
}

static PyGetSetDef _pyAudio_paHostApiInfo_getseters[] = {
  {"name",
   (getter) _pyAudio_paHostApiInfo_get_name,
   (setter) _pyAudio_paHostApiInfo_antiset,
   "host api name",
   NULL},

  {"structVersion",
   (getter) _pyAudio_paHostApiInfo_get_structVersion,
   (setter) _pyAudio_paHostApiInfo_antiset,
   "struct version",
   NULL},

  {"type",
   (getter) _pyAudio_paHostApiInfo_get_type,
   (setter) _pyAudio_paHostApiInfo_antiset,
   "host api type",
   NULL},

  {"deviceCount",
   (getter) _pyAudio_paHostApiInfo_get_deviceCount,
   (setter) _pyAudio_paHostApiInfo_antiset,
   "number of devices",
   NULL},

  {"defaultInputDevice",
   (getter) _pyAudio_paHostApiInfo_get_defaultInputDevice,
   (setter) _pyAudio_paHostApiInfo_antiset,
   "default input device index",
   NULL},

  {"defaultOutputDevice",
   (getter) _pyAudio_paHostApiInfo_get_defaultOutputDevice,
   (setter) _pyAudio_paDeviceInfo_antiset,
   "default output device index",
   NULL},

  {NULL}
};

static PyTypeObject _pyAudio_paHostApiInfoType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_portaudio.paHostApiInfo", /*tp_name*/
    sizeof(_pyAudio_paHostApiInfo),   /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor) _pyAudio_paHostApiInfo_dealloc, /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    0,                         /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT,        /*tp_flags*/
    "Port Audio HostApi Info",       /* tp_doc */
    0,  /* tp_traverse */
    0,  /* tp_clear */
    0,  /* tp_richcompare */
    0,  /* tp_weaklistoffset */
    0,  /* tp_iter */
    0,  /* tp_iternext */
    0,  /* tp_methods */
    0,  /* tp_members */
    _pyAudio_paHostApiInfo_getseters, /* tp_getset */
    0,  /* tp_base */
    0,  /* tp_dict */
    0,  /* tp_descr_get */
    0,  /* tp_descr_set */
    0,  /* tp_dictoffset */
    0,  /* tp_init */
    0,  /* tp_alloc */
    0,  /* tp_new */
};

static _pyAudio_paHostApiInfo *
_create_paHostApiInfo_object(void)
{
  _pyAudio_paHostApiInfo *obj;

  /* don't allow subclassing? */
  obj = (_pyAudio_paHostApiInfo *) PyObject_New(_pyAudio_paHostApiInfo,
						&_pyAudio_paHostApiInfoType);
  return obj;
}

/*************************************************************
 * Host-Specific Objects
 *************************************************************/

/*************************************************************
 * --> Mac OS X
 *************************************************************/

#ifdef MACOSX
typedef struct {
  PyObject_HEAD
  PaMacCoreStreamInfo *paMacCoreStreamInfo;
  int flags;
  SInt32 *channelMap;
  int channelMapSize;
} _pyAudio_MacOSX_hostApiSpecificStreamInfo;

typedef _pyAudio_MacOSX_hostApiSpecificStreamInfo _pyAudio_Mac_HASSI;

static void
_pyAudio_MacOSX_hostApiSpecificStreamInfo_cleanup(_pyAudio_Mac_HASSI *self)
{
  if (self->paMacCoreStreamInfo != NULL) {
    free(self->paMacCoreStreamInfo);
    self->paMacCoreStreamInfo = NULL;
  }

  if (self->channelMap != NULL) {
    free(self->channelMap);
    self->channelMap = NULL;
  }

  self->flags = paMacCorePlayNice;
  self->channelMapSize = 0;
}

static void
_pyAudio_MacOSX_hostApiSpecificStreamInfo_dealloc(_pyAudio_Mac_HASSI *self)
{
  _pyAudio_MacOSX_hostApiSpecificStreamInfo_cleanup(self);
  Py_TYPE(self)->tp_free((PyObject *) self);
}

static int
_pyAudio_MacOSX_hostApiSpecificStreamInfo_init(PyObject *_self,
					       PyObject *args,
					       PyObject *kwargs)
{
  _pyAudio_Mac_HASSI *self = (_pyAudio_Mac_HASSI *) _self;
  PyObject *channel_map = NULL;
  int flags = paMacCorePlayNice;

  static char *kwlist[] = {"flags", "channel_map", NULL};

  if (! PyArg_ParseTupleAndKeywords(args, kwargs, "|iO", kwlist,
				    &flags, &channel_map)) {
    return -1;
  }

  // cleanup (just in case)
  _pyAudio_MacOSX_hostApiSpecificStreamInfo_cleanup(self);

  if (channel_map != NULL) {
    // ensure channel_map is an array
    if (! PyTuple_Check(channel_map)) {
      PyErr_SetString(PyExc_ValueError, "Channel map must be a tuple");
      return -1;
    }

    // generate SInt32 channelMap
    self->channelMapSize = (int) PyTuple_Size(channel_map);

    self->channelMap = (SInt32 *) malloc(sizeof(SInt32) * self->channelMapSize);

    if (self->channelMap == NULL) {
      PyErr_SetString(PyExc_SystemError, "Out of memory");
      _pyAudio_MacOSX_hostApiSpecificStreamInfo_cleanup(self);
      return -1;
    }

    PyObject *element;
    int i;
    for (i = 0; i < self->channelMapSize; ++i) {
      element = PyTuple_GetItem(channel_map, i);
      if (element == NULL) {
	// error condition
	PyErr_SetString(PyExc_ValueError,
			"Internal error: out of bounds index");
	_pyAudio_MacOSX_hostApiSpecificStreamInfo_cleanup(self);
	return -1;
      }

      // make sure element is an integer
      if (!PyNumber_Check(element)) {
	PyErr_SetString(PyExc_ValueError,
			"Channel Map must consist of integer elements");
	_pyAudio_MacOSX_hostApiSpecificStreamInfo_cleanup(self);
	return -1;
      }

      PyObject *long_element = PyNumber_Long(element);

      // OK, looks good
      self->channelMap[i] = (SInt32) PyLong_AsLong(long_element);
      Py_DECREF(long_element);
    }
  }

  // malloc self->paMacCoreStreamInfo
  self->paMacCoreStreamInfo =
      (PaMacCoreStreamInfo *) malloc(sizeof(PaMacCoreStreamInfo));

  if (self->paMacCoreStreamInfo == NULL) {
    PyErr_SetString(PyExc_SystemError, "Out of memeory");
    _pyAudio_MacOSX_hostApiSpecificStreamInfo_cleanup(self);
    return -1;
  }

  PaMacCore_SetupStreamInfo(self->paMacCoreStreamInfo, flags);

  if (self->channelMap) {
    PaMacCore_SetupChannelMap(self->paMacCoreStreamInfo,
			      self->channelMap,
			      self->channelMapSize);
  }

  self->flags = flags;

  return 0;
}

static PyObject *
_pyAudio_MacOSX_hostApiSpecificStreamInfo_get_flags(_pyAudio_Mac_HASSI *self,
						    void *closure)
{
  return PyLong_FromLong(self->flags);
}

static PyObject *
_pyAudio_MacOSX_hostApiSpecificStreamInfo_get_channel_map(
	        _pyAudio_Mac_HASSI *self,
		void *closure)
{
  if (self->channelMap == NULL || self->channelMapSize == 0) {
    Py_INCREF(Py_None);
    return Py_None;
  }

  int i;
  PyObject *channelMapTuple = PyTuple_New(self->channelMapSize);
  for (i = 0; i < self->channelMapSize; ++i) {
    PyObject *element = PyLong_FromLong(self->channelMap[i]);
    if (!element) {
      PyErr_SetString(PyExc_SystemError, "Invalid channel map");
      return NULL;
    }

    if (PyTuple_SetItem(channelMapTuple,
			i,
			PyLong_FromLong(self->channelMap[i]))) {
      // non-zero on error
      PyErr_SetString(PyExc_SystemError, "Can't create channel map.");
      return NULL;
    }
  }
  return channelMapTuple;
}

static int
_pyAudio_MacOSX_hostApiSpecificStreamInfo_antiset(_pyAudio_Mac_HASSI *self,
						  PyObject *value,
						  void *closure)
{
  /* read-only: do not allow users to change values */
  PyErr_SetString(PyExc_AttributeError,
		  "Fields read-only: cannot modify values");
  return -1;
}

static PyGetSetDef _pyAudio_MacOSX_hostApiSpecificStreamInfo_getseters[] = {
  {"flags",
   (getter) _pyAudio_MacOSX_hostApiSpecificStreamInfo_get_flags,
   (setter) _pyAudio_MacOSX_hostApiSpecificStreamInfo_antiset,
   "flags",
   NULL},

  {"channel_map",
   (getter) _pyAudio_MacOSX_hostApiSpecificStreamInfo_get_channel_map,
   (setter) _pyAudio_MacOSX_hostApiSpecificStreamInfo_antiset,
   "channel map",
   NULL},

  {NULL}
};

static PyTypeObject _pyAudio_MacOSX_hostApiSpecificStreamInfoType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_portaudio.PaMacCoreStreamInfo", /*tp_name*/
    sizeof(_pyAudio_MacOSX_hostApiSpecificStreamInfo),   /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    /*tp_dealloc*/
    (destructor) _pyAudio_MacOSX_hostApiSpecificStreamInfo_dealloc,
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    0,                         /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT,        /*tp_flags*/
    "Mac OS X Specific HostAPI configuration",       /* tp_doc */
    0,  /* tp_traverse */
    0,  /* tp_clear */
    0,  /* tp_richcompare */
    0,  /* tp_weaklistoffset */
    0,  /* tp_iter */
    0,  /* tp_iternext */
    0,  /* tp_methods */
    0,  /* tp_members */
    _pyAudio_MacOSX_hostApiSpecificStreamInfo_getseters,  /* tp_getset */
    0,  /* tp_base */
    0,  /* tp_dict */
    0,  /* tp_descr_get */
    0,  /* tp_descr_set */
    0,  /* tp_dictoffset */
    (int (*)(PyObject*, PyObject*, PyObject*))_pyAudio_MacOSX_hostApiSpecificStreamInfo_init,  /* tp_init */
    0,  /* tp_alloc */
    0,  /* tp_new */
};
#endif


/*************************************************************
 * Stream Wrapper Python Object
 *************************************************************/

typedef struct {
  PyObject *callback;
  long main_thread_id;
  unsigned int frame_size;
} PyAudioCallbackContext;

typedef struct {
  PyObject_HEAD
  PaStream *stream;
  PaStreamParameters *inputParameters;
  PaStreamParameters *outputParameters;

  /* include PaStreamInfo too! */
  PaStreamInfo *streamInfo;

  /* context for callback */
  PyAudioCallbackContext *callbackContext;

  int is_open;
} _pyAudio_Stream;

static int
_is_open(_pyAudio_Stream *obj) {
  return (obj) && (obj->is_open);
}

static void
_cleanup_Stream_object(_pyAudio_Stream *streamObject)
{
  if (streamObject->stream != NULL) {
    Pa_CloseStream(streamObject->stream);
    streamObject->stream = NULL;
  }

  if (streamObject->streamInfo)
    streamObject->streamInfo = NULL;

  if (streamObject->inputParameters != NULL) {
    free(streamObject->inputParameters);
    streamObject->inputParameters = NULL;
  }

  if (streamObject->outputParameters != NULL) {
    free(streamObject->outputParameters);
    streamObject->outputParameters = NULL;
  }

  if (streamObject->callbackContext != NULL) {
    Py_XDECREF(streamObject->callbackContext->callback);
    free(streamObject->callbackContext);
    streamObject->callbackContext = NULL;
  }

  /* designate the stream as closed */
  streamObject->is_open = 0;
}

static void
_pyAudio_Stream_dealloc(_pyAudio_Stream* self)
{
  /* deallocate memory if necessary */
  _cleanup_Stream_object(self);

  /* free the object */
  Py_TYPE(self)->tp_free((PyObject*) self);
}


static PyObject *
_pyAudio_Stream_get_structVersion(_pyAudio_Stream *self,
				  void *closure)
{
  /* sanity check */
  if (!_is_open(self)) {
    PyErr_SetObject(PyExc_IOError,
		    Py_BuildValue("(s,i)",
				  "Stream closed",
				  paBadStreamPtr));
    return NULL;
  }

  if ((!self->streamInfo)) {
    PyErr_SetObject(PyExc_IOError,
		    Py_BuildValue("(s,i)",
				  "No StreamInfo available",
				  paBadStreamPtr));
    return NULL;
  }

  return PyLong_FromLong(self->streamInfo->structVersion);
}

static PyObject *
_pyAudio_Stream_get_inputLatency(_pyAudio_Stream *self,
				 void *closure)
{
  /* sanity check */
  if (!_is_open(self)) {
    PyErr_SetObject(PyExc_IOError,
		    Py_BuildValue("(s,i)",
				  "Stream closed",
				  paBadStreamPtr));
    return NULL;
  }

  /* sanity check */
  if ((!self->streamInfo)) {
    PyErr_SetObject(PyExc_IOError,
		    Py_BuildValue("(s,i)",
				  "No StreamInfo available",
				  paBadStreamPtr));
    return NULL;
  }

  return PyFloat_FromDouble(self->streamInfo->inputLatency);
}

static PyObject *
_pyAudio_Stream_get_outputLatency(_pyAudio_Stream *self,
				  void *closure)
{
  /* sanity check */
  if (!_is_open(self)) {
    PyErr_SetObject(PyExc_IOError,
		    Py_BuildValue("(s,i)",
				  "Stream closed",
				  paBadStreamPtr));
    return NULL;
  }

  /* sanity check */
  if ((!self->streamInfo)) {
    PyErr_SetObject(PyExc_IOError,
		    Py_BuildValue("(s,i)",
				  "No StreamInfo available",
				  paBadStreamPtr));
    return NULL;
  }

  return PyFloat_FromDouble(self->streamInfo->outputLatency);
}

static PyObject *
_pyAudio_Stream_get_sampleRate(_pyAudio_Stream *self,
			       void *closure)
{
  /* sanity check */
  if (!_is_open(self)) {
    PyErr_SetObject(PyExc_IOError,
		    Py_BuildValue("(s,i)",
				  "Stream closed",
				  paBadStreamPtr));
    return NULL;
  }

  /* sanity check */
  if ((!self->streamInfo)) {
    PyErr_SetObject(PyExc_IOError,
		    Py_BuildValue("(s,i)",
				  "No StreamInfo available",
				  paBadStreamPtr));
    return NULL;
  }

  return PyFloat_FromDouble(self->streamInfo->sampleRate);
}

static int
_pyAudio_Stream_antiset(_pyAudio_Stream *self,
			PyObject *value,
			void *closure)
{
  /* read-only: do not allow users to change values */
  PyErr_SetString(PyExc_AttributeError,
		  "Fields read-only: cannot modify values");
  return -1;
}

static PyGetSetDef _pyAudio_Stream_getseters[] = {
  {"structVersion",
   (getter) _pyAudio_Stream_get_structVersion,
   (setter) _pyAudio_Stream_antiset,
   "struct version",
   NULL},

  {"inputLatency",
   (getter) _pyAudio_Stream_get_inputLatency,
   (setter) _pyAudio_Stream_antiset,
   "input latency",
   NULL},

  {"outputLatency",
   (getter) _pyAudio_Stream_get_outputLatency,
   (setter) _pyAudio_Stream_antiset,
   "output latency",
   NULL},

  {"sampleRate",
   (getter) _pyAudio_Stream_get_sampleRate,
   (setter) _pyAudio_Stream_antiset,
   "sample rate",
   NULL},

  {NULL}
};

static PyTypeObject _pyAudio_StreamType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_portaudio.Stream",       /*tp_name*/
    sizeof(_pyAudio_Stream),         /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor) _pyAudio_Stream_dealloc, /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    0,                         /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT,        /*tp_flags*/
    "Port Audio Stream",       /* tp_doc */
    0,  /* tp_traverse */
    0,  /* tp_clear */
    0,  /* tp_richcompare */
    0,  /* tp_weaklistoffset */
    0,  /* tp_iter */
    0,  /* tp_iternext */
    0,  /* tp_methods */
    0,  /* tp_members */
    _pyAudio_Stream_getseters, /* tp_getset */
    0,  /* tp_base */
    0,  /* tp_dict */
    0,  /* tp_descr_get */
    0,  /* tp_descr_set */
    0,  /* tp_dictoffset */
    0,  /* tp_init */
    0,  /* tp_alloc */
    0,  /* tp_new */
};

static _pyAudio_Stream *
_create_Stream_object(void)
{
  _pyAudio_Stream *obj;

  /* don't allow subclassing? */
  obj = (_pyAudio_Stream *) PyObject_New(_pyAudio_Stream,
					 &_pyAudio_StreamType);
  return obj;
}


/************************************************************
 *
 * III. PortAudio Method Implementations
 *
 ************************************************************/

/*************************************************************
 * Version Info
 *************************************************************/

static PyObject *
pa_get_version(PyObject *self, PyObject *args)
{
  if (!PyArg_ParseTuple(args, ""))
    return NULL;

  return PyLong_FromLong(Pa_GetVersion());
}

static PyObject *
pa_get_version_text(PyObject *self, PyObject *args)
{
  if (!PyArg_ParseTuple(args, ""))
    return NULL;

  return PyUnicode_FromString(Pa_GetVersionText());
}

/*************************************************************
 * Initialization/Termination
 *************************************************************/

static PyObject *
pa_initialize(PyObject *self, PyObject *args)
{
  int err;
  err = Pa_Initialize();
  if (err != paNoError) {
    Pa_Terminate();
#ifdef VERBOSE
    fprintf(stderr, "An error occured while using the portaudio stream\n");
    fprintf(stderr, "Error number: %d\n", err);
    fprintf(stderr, "Error message: %s\n", Pa_GetErrorText(err));
#endif
    PyErr_SetObject(PyExc_IOError,
		    Py_BuildValue("(s,i)",
				  Pa_GetErrorText(err), err));
    return NULL;
  }

  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *
pa_terminate(PyObject *self, PyObject *args)
{
  Pa_Terminate();
  Py_INCREF(Py_None);
  return Py_None;
}

/*************************************************************
 * HostAPI
 *************************************************************/

static PyObject *
pa_get_host_api_count(PyObject *self, PyObject *args)
{
  PaHostApiIndex count;

  if (!PyArg_ParseTuple(args, ""))
    return NULL;

  count = Pa_GetHostApiCount();

  if (count < 0) {

#ifdef VERBOSE
    fprintf(stderr, "An error occured while using the portaudio stream\n");
    fprintf(stderr, "Error number: %d\n", count);
    fprintf(stderr, "Error message: %s\n", Pa_GetErrorText(count));
#endif

    PyErr_SetObject(PyExc_IOError,
		    Py_BuildValue("(s,i)",
				  Pa_GetErrorText(count), count));
    return NULL;
  }

  return PyLong_FromLong(count);
}

static PyObject *
pa_get_default_host_api(PyObject *self, PyObject *args)
{
  PaHostApiIndex index;

  if (!PyArg_ParseTuple(args, ""))
    return NULL;

  index = Pa_GetDefaultHostApi();

  if (index < 0) {

#ifdef VERBOSE
    fprintf(stderr, "An error occured while using the portaudio stream\n");
    fprintf(stderr, "Error number: %d\n", index);
    fprintf(stderr, "Error message: %s\n", Pa_GetErrorText(index));
#endif

    PyErr_SetObject(PyExc_IOError,
		    Py_BuildValue("(s,i)",
				  Pa_GetErrorText(index), index));
    return NULL;
  }

  return PyLong_FromLong(index);
}

static PyObject *
pa_host_api_type_id_to_host_api_index(PyObject *self, PyObject *args)
{
  PaHostApiTypeId typeid;
  PaHostApiIndex index;

  if (!PyArg_ParseTuple(args, "i", &typeid))
    return NULL;

  index = Pa_HostApiTypeIdToHostApiIndex(typeid);

  if (index < 0) {

#ifdef VERBOSE
    fprintf(stderr, "An error occured while using the portaudio stream\n");
    fprintf(stderr, "Error number: %d\n", index);
    fprintf(stderr, "Error message: %s\n", Pa_GetErrorText(index));
#endif

    PyErr_SetObject(PyExc_IOError,
		    Py_BuildValue("(s,i)",
				  Pa_GetErrorText(index), index));
    return NULL;
  }

  return PyLong_FromLong(index);
}

static PyObject *
pa_host_api_device_index_to_device_index(PyObject *self, PyObject *args)
{
  PaHostApiIndex apiIndex;
  int hostApiDeviceindex;
  PaDeviceIndex devIndex;


  if (!PyArg_ParseTuple(args, "ii", &apiIndex, &hostApiDeviceindex))
    return NULL;

  devIndex = Pa_HostApiDeviceIndexToDeviceIndex(apiIndex, hostApiDeviceindex);
  if (devIndex < 0) {

#ifdef VERBOSE
    fprintf(stderr, "An error occured while using the portaudio stream\n");
    fprintf(stderr, "Error number: %d\n", devIndex);
    fprintf(stderr, "Error message: %s\n", Pa_GetErrorText(devIndex));
#endif

    PyErr_SetObject(PyExc_IOError,
		    Py_BuildValue("(s,i)",
				  Pa_GetErrorText(devIndex), devIndex));
    return NULL;
  }

  return PyLong_FromLong(devIndex);
}

static PyObject *
pa_get_host_api_info(PyObject *self, PyObject *args)
{
  PaHostApiIndex index;
  PaHostApiInfo* _info;
  _pyAudio_paHostApiInfo* py_info;

  if (!PyArg_ParseTuple(args, "i", &index))
    return NULL;

  _info = (PaHostApiInfo *) Pa_GetHostApiInfo(index);

  if (!_info) {
    PyErr_SetObject(PyExc_IOError,
		    Py_BuildValue("(s,i)",
				  "Invalid host api info",
				  paInvalidHostApi));
    return NULL;
  }

  py_info = _create_paHostApiInfo_object();
  py_info->apiInfo = _info;

  return (PyObject *) py_info;
}

/*************************************************************
 * Device API
 *************************************************************/

static PyObject *
pa_get_device_count(PyObject *self, PyObject *args)
{
  PaDeviceIndex count;

  if (!PyArg_ParseTuple(args, ""))
    return NULL;

  count = Pa_GetDeviceCount();
  if (count < 0) {

#ifdef VERBOSE
    fprintf(stderr, "An error occured while using the portaudio stream\n");
    fprintf(stderr, "Error number: %d\n", count);
    fprintf(stderr, "Error message: %s\n", Pa_GetErrorText(count));
#endif

    PyErr_SetObject(PyExc_IOError,
		    Py_BuildValue("(s,i)",
				  Pa_GetErrorText(count), count));
    return NULL;
  }

  return PyLong_FromLong(count);
}

static PyObject *
pa_get_default_input_device(PyObject *self, PyObject *args)
{
  PaDeviceIndex index;

  if (!PyArg_ParseTuple(args, ""))
    return NULL;

  index = Pa_GetDefaultInputDevice();
  if (index == paNoDevice) {
    PyErr_SetString(PyExc_IOError, "No Default Input Device Available");
    return NULL;
  } else if (index < 0) {

#ifdef VERBOSE
    fprintf(stderr, "An error occured while using the portaudio stream\n");
    fprintf(stderr, "Error number: %d\n", index);
    fprintf(stderr, "Error message: %s\n", Pa_GetErrorText(index));
#endif

    PyErr_SetObject(PyExc_IOError,
		    Py_BuildValue("(s,i)",
				  Pa_GetErrorText(index), index));
    return NULL;
  }

  return PyLong_FromLong(index);
}

static PyObject *
pa_get_default_output_device(PyObject *self, PyObject *args)
{
  PaDeviceIndex index;

  if (!PyArg_ParseTuple(args, ""))
    return NULL;

  index = Pa_GetDefaultOutputDevice();
  if (index == paNoDevice) {
    PyErr_SetString(PyExc_IOError, "No Default Output Device Available");
    return NULL;
  } else if (index < 0) {

#ifdef VERBOSE
    fprintf(stderr, "An error occured while using the portaudio stream\n");
    fprintf(stderr, "Error number: %d\n", index);
    fprintf(stderr, "Error message: %s\n", Pa_GetErrorText(index));
#endif

    PyErr_SetObject(PyExc_IOError,
		    Py_BuildValue("(s,i)",
				  Pa_GetErrorText(index), index));
    return NULL;
  }

  return PyLong_FromLong(index);
}

static PyObject *
pa_get_device_info(PyObject *self, PyObject *args)
{
  PaDeviceIndex index;
  PaDeviceInfo* _info;
  _pyAudio_paDeviceInfo* py_info;

  if (!PyArg_ParseTuple(args, "i", &index))
    return NULL;

  _info = (PaDeviceInfo *) Pa_GetDeviceInfo(index);

  if (!_info) {
    PyErr_SetObject(PyExc_IOError,
		    Py_BuildValue("(s,i)",
				  "Invalid device info", paInvalidDevice));
    return NULL;
  }

  py_info = _create_paDeviceInfo_object();
  py_info->devInfo = _info;
  return (PyObject *) py_info;
}

/*************************************************************
 * Stream Open / Close / Supported
 *************************************************************/

int
_stream_callback_cfunction(const void *input,
                           void *output,
                           unsigned long frameCount,
                           const PaStreamCallbackTimeInfo *timeInfo,
                           PaStreamCallbackFlags statusFlags,
                           void *userData)
{
  int return_val = paAbort;
  PyGILState_STATE _state = PyGILState_Ensure();

#ifdef VERBOSE
  if (statusFlags != 0) {
    printf("Status flag set: ");
    if (statusFlags & paInputUnderflow) {
      printf("input underflow!\n");
    }
    if (statusFlags & paInputOverflow) {
      printf("input overflow!\n");
    }
    if (statusFlags & paOutputUnderflow) {
      printf("output underflow!\n");
    }
    if (statusFlags & paOutputUnderflow) {
      printf("output overflow!\n");
    }
    if (statusFlags & paPrimingOutput) {
      printf("priming output!\n");
    }
  }
#endif

  PyAudioCallbackContext *context = (PyAudioCallbackContext *)userData;
  PyObject *py_callback = context->callback;
  unsigned int bytes_per_frame = context->frame_size;
  long main_thread_id = context->main_thread_id;

  PyObject *py_frame_count = PyLong_FromUnsignedLong(frameCount);
  PyObject *py_time_info = Py_BuildValue("{s:d,s:d,s:d}",
                                         "input_buffer_adc_time",
                                         timeInfo->inputBufferAdcTime,
                                         "current_time",
                                         timeInfo->currentTime,
                                         "output_buffer_dac_time",
                                         timeInfo->outputBufferDacTime);
  PyObject *py_status_flags = PyLong_FromUnsignedLong(statusFlags);
  PyObject *py_input_data = Py_None;

  if (input) {
    py_input_data = PyBytes_FromStringAndSize(input,
                                              bytes_per_frame * frameCount);
  }

  PyObject *py_result;
  py_result = PyObject_CallFunctionObjArgs(py_callback,
                                           py_input_data,
                                           py_frame_count,
                                           py_time_info,
                                           py_status_flags,
                                           NULL);

  if (py_result == NULL) {
#ifdef VERBOSE
    fprintf(stderr, "An error occured while using the portaudio stream\n");
    fprintf(stderr, "Error message: Could not call callback function\n");
#endif
    PyObject *err = PyErr_Occurred();

    if (err) {
        PyThreadState_SetAsyncExc(main_thread_id, err);

        // Print out a stack trace to help debugging.
        // TODO: make VERBOSE a runtime flag so users can control
        // the amount of logging.
        PyErr_Print();
    }

    goto end;
  }

  const char *pData;
  int output_len;

  if (!PyArg_ParseTuple(py_result,
                        "z#i",
                        &pData,
                        &output_len,
                        &return_val)) {
#ifdef VERBOSE
    fprintf(stderr, "An error occured while using the portaudio stream\n");
    fprintf(stderr, "Error message: Could not parse callback return value\n");
#endif

    PyObject *err = PyErr_Occurred();

    if (err) {
        PyThreadState_SetAsyncExc(main_thread_id, err);

        // Print out a stack trace to help debugging.
        // TODO: make VERBOSE a runtime flag so users can control
        // the amount of logging.
        PyErr_Print();
    }

    Py_XDECREF(py_result);
    return_val = paAbort;
    goto end;
  }

  Py_DECREF(py_result);

  if ((return_val != paComplete) &&
      (return_val != paAbort) &&
      (return_val != paContinue)) {
      PyErr_SetString(PyExc_ValueError,
                      "Invalid PaStreamCallbackResult from callback");
      PyThreadState_SetAsyncExc(main_thread_id, PyErr_Occurred());
      PyErr_Print();

      // Quit the callback loop
      return_val = paAbort;

      goto end;
  }

  // Copy bytes for playback only if this is an output stream:

  if (output) {
      char *output_data = (char*)output;
      memcpy(output_data, pData, min(output_len, bytes_per_frame * frameCount));

      // Pad out the rest of the buffer with 0s if callback returned
      // too few frames (and assume paComplete).
      if (output_len < (frameCount * bytes_per_frame)) {
          memset(output_data + output_len,
                 0,
                 (frameCount * bytes_per_frame) - output_len);
          return_val = paComplete;
      }
  }

 end:

  if (input) {
    // Decrement this at the end, after memcpy, in case the user
    // returns py_input_data back for playback.
    Py_DECREF(py_input_data);
  }

  Py_XDECREF(py_frame_count);
  Py_XDECREF(py_time_info);
  Py_XDECREF(py_status_flags);

  PyGILState_Release(_state);
  return return_val;
}

static PyObject *
pa_open(PyObject *self, PyObject *args, PyObject *kwargs)
{
  int rate, channels;
  int input, output, frames_per_buffer;
  int input_device_index = -1;
  int output_device_index = -1;
  PyObject *input_device_index_arg = NULL;
  PyObject *output_device_index_arg = NULL;
  PyFunctionObject *stream_callback = NULL;
  PaSampleFormat format;
  PaError err;

#ifdef MACOSX
  _pyAudio_MacOSX_hostApiSpecificStreamInfo *inputHostSpecificStreamInfo =
      NULL;
  _pyAudio_MacOSX_hostApiSpecificStreamInfo *outputHostSpecificStreamInfo =
      NULL;
#else
  /* mostly ignored...*/
  PyObject *inputHostSpecificStreamInfo = NULL;
  PyObject *outputHostSpecificStreamInfo = NULL;
#endif

  /* default to neither output nor input */
  input = 0;
  output = 0;
  frames_per_buffer = DEFAULT_FRAMES_PER_BUFFER;

  /* pass in rate, channel, width */
  static char *kwlist[] = {"rate",
			   "channels",
			   "format",
			   "input",
			   "output",
			   "input_device_index",
			   "output_device_index",
			   "frames_per_buffer",
			   "input_host_api_specific_stream_info",
			   "output_host_api_specific_stream_info",
                           "stream_callback",
			   NULL};

  if (!PyArg_ParseTupleAndKeywords(args, kwargs,
#ifdef MACOSX
				   "iik|iiOOiO!O!O!",
#else
				   "iik|iiOOiOOO!",
#endif
				   kwlist,
				   &rate, &channels, &format,
				   &input, &output,
				   &input_device_index_arg,
				   &output_device_index_arg,
				   &frames_per_buffer,
#ifdef MACOSX
				   &_pyAudio_MacOSX_hostApiSpecificStreamInfoType,
#endif
				   &inputHostSpecificStreamInfo,
#ifdef MACOSX
				   &_pyAudio_MacOSX_hostApiSpecificStreamInfoType,
#endif
				   &outputHostSpecificStreamInfo,
                   &PyFunction_Type,
                   &stream_callback))

    return NULL;


  /* check to see if device indices were specified */
  if ((input_device_index_arg == NULL) ||
      (input_device_index_arg == Py_None)) {

#ifdef VERBOSE
    printf("Using default input device\n");
#endif

    input_device_index = -1;

  } else {
    // Support both Python 2 and Python 3 by using PyNumber_Check
    if (!PyNumber_Check(input_device_index_arg)) {
      PyErr_SetString(PyExc_ValueError,
		      "input_device_index must be integer (or None)");
      return NULL;
    }

    PyObject *input_device_index_long =
      PyNumber_Long(input_device_index_arg);

    input_device_index = (int) PyLong_AsLong(input_device_index_long);
    Py_DECREF(input_device_index_long);

#ifdef VERBOSE
    printf("Using input device index number: %d\n", input_device_index);
#endif
  }

  if ((output_device_index_arg == NULL) ||
      (output_device_index_arg == Py_None)) {

#ifdef VERBOSE
    printf("Using default output device\n");
#endif

    output_device_index = -1;

  } else {
    // Support both Python 2 and Python 3 by using PyNumber_Check
    if (!PyNumber_Check(output_device_index_arg)) {
      PyErr_SetString(PyExc_ValueError,
		      "output_device_index must be integer (or None)");
      return NULL;
    }

    PyObject *output_device_index_long =
      PyNumber_Long(output_device_index_arg);
    output_device_index = (int) PyLong_AsLong(output_device_index_long);
    Py_DECREF(output_device_index_long);

#ifdef VERBOSE
    printf("Using output device index number: %d\n", output_device_index);
#endif
  }

  /* sanity checks */
  if (input == 0 && output == 0) {
    PyErr_SetString(PyExc_ValueError, "Must specify either input or output");
    return NULL;
  }

  if (channels < 1) {
    PyErr_SetString(PyExc_ValueError, "Invalid audio channels");
    return NULL;
  }

  PaStreamParameters *outputParameters = NULL;
  PaStreamParameters *inputParameters = NULL;

  if (output) {
    outputParameters =
      (PaStreamParameters *) malloc(sizeof(PaStreamParameters));


    if (output_device_index < 0)
      /* default output device */
      outputParameters->device = Pa_GetDefaultOutputDevice();
    else
      outputParameters->device = output_device_index;

    /* final check -- ensure that there is a default device */
    if (outputParameters->device < 0 ||
        outputParameters->device >= Pa_GetDeviceCount()) {
      free(outputParameters);
      PyErr_SetObject(PyExc_IOError,
		      Py_BuildValue("(s,i)",
				    "Invalid output device "
				    "(no default output device)",
				    paInvalidDevice));
      return NULL;
    }

    outputParameters->channelCount = channels;
    outputParameters->sampleFormat = format;
    outputParameters->suggestedLatency =
      Pa_GetDeviceInfo(outputParameters->device)->defaultLowOutputLatency;
    outputParameters->hostApiSpecificStreamInfo = NULL;

#ifdef MACOSX
    if (outputHostSpecificStreamInfo) {
      outputParameters->hostApiSpecificStreamInfo =
	outputHostSpecificStreamInfo->paMacCoreStreamInfo;
    }
#endif

  }

  if (input) {
    inputParameters =
      (PaStreamParameters *) malloc(sizeof(PaStreamParameters));

    if (input_device_index < 0) {
      /* default output device */
      inputParameters->device = Pa_GetDefaultInputDevice();
    } else {
      inputParameters->device = input_device_index;
    }

    /* final check -- ensure that there is a default device */
    if (inputParameters->device < 0) {
      free(inputParameters);
      PyErr_SetObject(PyExc_IOError,
		      Py_BuildValue("(s,i)",
				    "Invalid input device "
				    "(no default output device)",
				    paInvalidDevice));
      return NULL;
    }

    inputParameters->channelCount = channels;
    inputParameters->sampleFormat = format;
    inputParameters->suggestedLatency =
      Pa_GetDeviceInfo(inputParameters->device)->defaultLowInputLatency;
    inputParameters->hostApiSpecificStreamInfo = NULL;

#ifdef MACOSX
    if (inputHostSpecificStreamInfo) {
      inputParameters->hostApiSpecificStreamInfo =
	inputHostSpecificStreamInfo->paMacCoreStreamInfo;
    }
#endif

  }

  PaStream *stream = NULL;
  PaStreamInfo *streamInfo = NULL;
  PyAudioCallbackContext *context = NULL;

  // Handle callback mode:
  if (stream_callback) {
    Py_INCREF(stream_callback);
    context = (PyAudioCallbackContext *) malloc(sizeof(PyAudioCallbackContext));
    context->callback = (PyObject *) stream_callback;
    context->main_thread_id = PyThreadState_Get()->thread_id;
    context->frame_size = Pa_GetSampleSize(format) * channels;
  }

  err = Pa_OpenStream(&stream,
		      /* input/output parameters */
		      /* NULL values are ignored */
		      inputParameters,
		      outputParameters,
		      /* Samples Per Second */
		      rate,
		      /* allocate frames in the buffer */
		      frames_per_buffer,
		      /* we won't output out of range samples
			 so don't bother clipping them */
		      paClipOff,
		      /* callback, if specified */
		      (stream_callback)?(_stream_callback_cfunction):(NULL),
		      /* callback userData, if applicable */
		      context);

  if (err != paNoError) {

#ifdef VERBOSE
    fprintf(stderr, "An error occured while using the portaudio stream\n");
    fprintf(stderr, "Error number: %d\n", err);
    fprintf(stderr, "Error message: %s\n", Pa_GetErrorText(err));
#endif

    PyErr_SetObject(PyExc_IOError,
		    Py_BuildValue("(s,i)",
				  Pa_GetErrorText(err), err));
    return NULL;
  }

  streamInfo = (PaStreamInfo *) Pa_GetStreamInfo(stream);
  if (!streamInfo) {
    /* Pa_Terminate(); */
    PyErr_SetObject(PyExc_IOError,
		    Py_BuildValue("(s,i)",
 				  "Could not get stream information",
				  paInternalError));
    return NULL;
  }

  _pyAudio_Stream *streamObject = _create_Stream_object();
  streamObject->stream = stream;
  streamObject->inputParameters = inputParameters;
  streamObject->outputParameters = outputParameters;
  streamObject->is_open = 1;
  streamObject->streamInfo = streamInfo;
  streamObject->callbackContext = context;

  return (PyObject *) streamObject;
}

static PyObject *
pa_close(PyObject *self, PyObject *args)
{
  PyObject *stream_arg;
  _pyAudio_Stream *streamObject;

  if (!PyArg_ParseTuple(args, "O!", &_pyAudio_StreamType, &stream_arg))
    return NULL;

  streamObject = (_pyAudio_Stream *) stream_arg;

  _cleanup_Stream_object(streamObject);

  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *
pa_get_sample_size(PyObject *self, PyObject *args)
{
  PaSampleFormat format;
  int size_in_bytes;

  if (!PyArg_ParseTuple(args, "k", &format))
    return NULL;

  size_in_bytes = Pa_GetSampleSize(format);

  if (size_in_bytes < 0) {
    PyErr_SetObject(PyExc_ValueError,
		    Py_BuildValue("(s,i)",
				  Pa_GetErrorText(size_in_bytes),
				  size_in_bytes));
    return NULL;
  }

  return PyLong_FromLong(size_in_bytes);
}


static PyObject *
pa_is_format_supported(PyObject *self, PyObject *args,
		       PyObject *kwargs)
{
  /* pass in rate, channel, width */
  static char *kwlist[] = {
      "sample_rate",
      "input_device",
      "input_channels",
      "input_format",
      "output_device",
      "output_channels",
      "output_format",
      NULL
  };

  int input_device, input_channels;
  int output_device, output_channels;
  float sample_rate;
  PaStreamParameters inputParams;
  PaStreamParameters outputParams;
  PaSampleFormat input_format, output_format;
  PaError error;

  input_device = input_channels =
    output_device = output_channels = -1;

  input_format = output_format = -1;

  if (!PyArg_ParseTupleAndKeywords(args, kwargs, "f|iikiik", kwlist,
				   &sample_rate,
				   &input_device,
				   &input_channels,
				   &input_format,
				   &output_device,
				   &output_channels,
				   &output_format))
    return NULL;

  if (!(input_device < 0)) {
    inputParams.device = input_device;
    inputParams.channelCount = input_channels;
    inputParams.sampleFormat = input_format;
    inputParams.suggestedLatency = 0;
    inputParams.hostApiSpecificStreamInfo = NULL;
  }

  if (!(output_device < 0)) {
    outputParams.device = output_device;
    outputParams.channelCount = output_channels;
    outputParams.sampleFormat = output_format;
    outputParams.suggestedLatency = 0;
    outputParams.hostApiSpecificStreamInfo = NULL;
  }

  error = Pa_IsFormatSupported((input_device < 0) ? NULL : &inputParams,
			       (output_device < 0) ? NULL : &outputParams,
			       sample_rate);

  if (error == paFormatIsSupported) {
    Py_INCREF(Py_True);
    return Py_True;
  } else {
    PyErr_SetObject(PyExc_ValueError,
		    Py_BuildValue("(s,i)",
				  Pa_GetErrorText(error),
				  error));
    return NULL;
  }
}

/*************************************************************
 * Stream Start / Stop / Info
 *************************************************************/

static PyObject *
pa_start_stream(PyObject *self, PyObject *args)
{
  int err;
  PyObject *stream_arg;
  _pyAudio_Stream *streamObject;

  if (!PyArg_ParseTuple(args, "O!", &_pyAudio_StreamType, &stream_arg))
    return NULL;

  streamObject = (_pyAudio_Stream *) stream_arg;

  if (!_is_open(streamObject)) {
    PyErr_SetObject(PyExc_IOError,
		    Py_BuildValue("(s,i)",
				  "Stream closed",
				  paBadStreamPtr));
    return NULL;
  }

  PaStream *stream = streamObject->stream;

  if ( ((err = Pa_StartStream(stream)) != paNoError) &&
       (err != paStreamIsNotStopped)) {
    _cleanup_Stream_object(streamObject);

#ifdef VERBOSE
    fprintf(stderr, "An error occured while using the portaudio stream\n");
    fprintf(stderr, "Error number: %d\n", err);
    fprintf(stderr, "Error message: %s\n", Pa_GetErrorText(err));
#endif

    PyErr_SetObject(PyExc_IOError,
		    Py_BuildValue("(s,i)",
				  Pa_GetErrorText(err),
				  err));
    return NULL;
  }

  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *
pa_stop_stream(PyObject *self, PyObject *args)
{

  int err;
  PyObject *stream_arg;
  _pyAudio_Stream *streamObject;

  if (!PyArg_ParseTuple(args, "O!", &_pyAudio_StreamType, &stream_arg))
    return NULL;

  streamObject = (_pyAudio_Stream *) stream_arg;

  if (!_is_open(streamObject)) {
    PyErr_SetString(PyExc_IOError, "Stream not open");
    return NULL;
  }

  PaStream *stream = streamObject->stream;

  if ( ((err = Pa_StopStream(stream)) != paNoError)  &&
       (err != paStreamIsStopped)) {

    _cleanup_Stream_object(streamObject);

#ifdef VERBOSE
    fprintf(stderr, "An error occured while using the portaudio stream\n");
    fprintf(stderr, "Error number: %d\n", err);
    fprintf(stderr, "Error message: %s\n", Pa_GetErrorText(err));
#endif

    PyErr_SetObject(PyExc_IOError,
		    Py_BuildValue("(s,i)",
				  Pa_GetErrorText(err),
				  err));
    return NULL;
  }

  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *
pa_abort_stream(PyObject *self, PyObject *args)
{
  int err;
  PyObject *stream_arg;
  _pyAudio_Stream *streamObject;

  if (!PyArg_ParseTuple(args, "O!", &_pyAudio_StreamType, &stream_arg))
    return NULL;

  streamObject = (_pyAudio_Stream *) stream_arg;

  if (!_is_open(streamObject)) {
    PyErr_SetString(PyExc_IOError, "Stream not open");
    return NULL;
  }

  PaStream *stream = streamObject->stream;

  if ( ((err = Pa_AbortStream(stream)) != paNoError) &&
       (err != paStreamIsStopped)) {
    _cleanup_Stream_object(streamObject);

#ifdef VERBOSE
    fprintf(stderr, "An error occured while using the portaudio stream\n");
    fprintf(stderr, "Error number: %d\n", err);
    fprintf(stderr, "Error message: %s\n", Pa_GetErrorText(err));
#endif

    PyErr_SetObject(PyExc_IOError,
		    Py_BuildValue("(s,i)",
				  Pa_GetErrorText(err),
				  err));
    return NULL;
  }

  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *
pa_is_stream_stopped(PyObject *self, PyObject *args)
{
  int err;
  PyObject *stream_arg;
  _pyAudio_Stream *streamObject;

  if (!PyArg_ParseTuple(args, "O!", &_pyAudio_StreamType, &stream_arg))
    return NULL;

  streamObject = (_pyAudio_Stream *) stream_arg;

  if (!_is_open(streamObject)) {
    PyErr_SetObject(PyExc_IOError,
		    Py_BuildValue("(s,i)",
				  "Stream closed",
				  paBadStreamPtr));
    return NULL;
  }

  PaStream *stream = streamObject->stream;

  if ((err = Pa_IsStreamStopped(stream)) < 0) {
    _cleanup_Stream_object(streamObject);

#ifdef VERBOSE
    fprintf(stderr, "An error occured while using the portaudio stream\n");
    fprintf(stderr, "Error number: %d\n", err);
    fprintf(stderr, "Error message: %s\n", Pa_GetErrorText(err));
#endif

    PyErr_SetObject(PyExc_IOError,
		    Py_BuildValue("(s,i)",
				  Pa_GetErrorText(err),
				  err));
    return NULL;
  }

  if (err) {
    Py_INCREF(Py_True);
    return Py_True;
  }

  Py_INCREF(Py_False);
  return Py_False;
}

static PyObject *
pa_is_stream_active(PyObject *self, PyObject *args)
{

  int err;
  PyObject *stream_arg;
  _pyAudio_Stream *streamObject;

  if (!PyArg_ParseTuple(args, "O!", &_pyAudio_StreamType, &stream_arg))
    return NULL;

  streamObject = (_pyAudio_Stream *) stream_arg;

  if (!_is_open(streamObject)) {
    PyErr_SetString(PyExc_IOError, "Stream not open");
    return NULL;
  }

  PaStream *stream = streamObject->stream;

  if ((err = Pa_IsStreamActive(stream)) < 0) {
    _cleanup_Stream_object(streamObject);

#ifdef VERBOSE
    fprintf(stderr, "An error occured while using the portaudio stream\n");
    fprintf(stderr, "Error number: %d\n", err);
    fprintf(stderr, "Error message: %s\n", Pa_GetErrorText(err));
#endif

    PyErr_SetObject(PyExc_IOError,
		    Py_BuildValue("(s,i)",
				  Pa_GetErrorText(err),
				  err));
    return NULL;
  }

  if (err) {
    Py_INCREF(Py_True);
    return Py_True;
  }

  Py_INCREF(Py_False);
  return Py_False;
}

static PyObject *
pa_get_stream_time(PyObject *self, PyObject *args)
{
  double time;
  PyObject *stream_arg;
  _pyAudio_Stream *streamObject;

  if (!PyArg_ParseTuple(args, "O!", &_pyAudio_StreamType, &stream_arg))
    return NULL;

  streamObject = (_pyAudio_Stream *) stream_arg;

  if (!_is_open(streamObject)) {
    PyErr_SetObject(PyExc_IOError,
		    Py_BuildValue("(s,i)",
				  "Stream closed",
				  paBadStreamPtr));
    return NULL;
  }

  PaStream *stream = streamObject->stream;

  if ((time = Pa_GetStreamTime(stream)) == 0) {
    _cleanup_Stream_object(streamObject);
    PyErr_SetObject(PyExc_IOError,
		    Py_BuildValue("(s,i)",
				  "Internal Error",
				  paInternalError));
    return NULL;
  }

  return PyFloat_FromDouble(time);
}

static PyObject *
pa_get_stream_cpu_load(PyObject *self, PyObject *args)
{
  PyObject *stream_arg;
  _pyAudio_Stream *streamObject;

  if (!PyArg_ParseTuple(args, "O!", &_pyAudio_StreamType, &stream_arg))
    return NULL;

  streamObject = (_pyAudio_Stream *) stream_arg;

  if (!_is_open(streamObject)) {
    PyErr_SetObject(PyExc_IOError,
		    Py_BuildValue("(s,i)",
				  "Stream closed",
				  paBadStreamPtr));
    return NULL;
  }

  PaStream *stream = streamObject->stream;
  return PyFloat_FromDouble(Pa_GetStreamCpuLoad(stream));
}


/*************************************************************
 * Stream Read/Write
 *************************************************************/

static PyObject *
pa_write_stream(PyObject *self, PyObject *args)
{
  const char *data;
  int total_size;
  int total_frames;
  int err;
  int should_throw_exception = 0;

  PyObject *stream_arg;
  _pyAudio_Stream *streamObject;

  if (!PyArg_ParseTuple(args, "O!s#i|i",
			&_pyAudio_StreamType,
			&stream_arg,
			&data,
			&total_size,
			&total_frames,
			&should_throw_exception))
    return NULL;

  /* make sure total frames is larger than 0 */
  if (total_frames < 0) {
    PyErr_SetString(PyExc_ValueError,
		    "Invalid number of frames");
    return NULL;
  }

  streamObject = (_pyAudio_Stream *) stream_arg;

  if (!_is_open(streamObject)) {
    PyErr_SetObject(PyExc_IOError,
		    Py_BuildValue("(s,i)",
				  "Stream closed",
				  paBadStreamPtr));
    return NULL;
  }

  PaStream *stream = streamObject->stream;

  Py_BEGIN_ALLOW_THREADS
  err = Pa_WriteStream(stream, data, total_frames);
  Py_END_ALLOW_THREADS

  if (err != paNoError) {
    if (err == paOutputUnderflowed) {
      if (should_throw_exception)
	goto error;
    } else
      goto error;
  }

  Py_INCREF(Py_None);
  return Py_None;

 error:
  /* cleanup */
  _cleanup_Stream_object(streamObject);

#ifdef VERBOSE
  fprintf(stderr, "An error occured while using the portaudio stream\n");
  fprintf(stderr, "Error number: %d\n", err);
  fprintf(stderr, "Error message: %s\n", Pa_GetErrorText(err));
#endif

  PyErr_SetObject(PyExc_IOError,
		  Py_BuildValue("(s,i)",
				Pa_GetErrorText(err),
				err));
  return NULL;
}

static PyObject *
pa_read_stream(PyObject *self, PyObject *args)
{
  int err;
  int total_frames;
  short *sampleBlock;
  int num_bytes;
  PyObject *rv;

  PyObject *stream_arg;
  _pyAudio_Stream *streamObject;

  if (!PyArg_ParseTuple(args, "O!i",
			&_pyAudio_StreamType,
			&stream_arg,
			&total_frames))
    return NULL;

  /* make sure value is positive! */
  if (total_frames < 0) {
    PyErr_SetString(PyExc_ValueError, "Invalid number of frames");
    return NULL;
  }

  streamObject = (_pyAudio_Stream *) stream_arg;

  if (!_is_open(streamObject)) {
    PyErr_SetObject(PyExc_IOError,
		    Py_BuildValue("(s,i)",
				  "Stream closed",
				  paBadStreamPtr));
    return NULL;
  }

  PaStream *stream = streamObject->stream;
  PaStreamParameters *inputParameters = streamObject->inputParameters;
  num_bytes = (total_frames) * (inputParameters->channelCount) *
    (Pa_GetSampleSize(inputParameters->sampleFormat));

#ifdef VERBOSE
  fprintf(stderr, "Allocating %d bytes\n", num_bytes);
#endif

  rv = PyBytes_FromStringAndSize(NULL, num_bytes);
  sampleBlock = (short *) PyBytes_AsString(rv);

  if (sampleBlock == NULL) {
    PyErr_SetObject(PyExc_IOError,
		    Py_BuildValue("(s,i)",
				  "Out of memory",
				  paInsufficientMemory));
    return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  err = Pa_ReadStream(stream, sampleBlock, total_frames);
  Py_END_ALLOW_THREADS

  if (err != paNoError) {

    /* ignore input overflow and output underflow */
    if (err & paInputOverflowed) {

#ifdef VERBOSE
      fprintf(stderr, "Input Overflow.\n");
#endif

    } else if (err & paOutputUnderflowed) {

#ifdef VERBOSE
      fprintf(stderr, "Output Underflow.\n");
#endif

    } else {
      /* clean up */
      _cleanup_Stream_object(streamObject);
    }

    /* free the string buffer */
    Py_XDECREF(rv);

    PyErr_SetObject(PyExc_IOError,
		    Py_BuildValue("(s,i)",
				  Pa_GetErrorText(err), err));
    return NULL;
  }

  return rv;
}

static PyObject *
pa_get_stream_write_available(PyObject *self, PyObject *args)
{
  signed long frames;
  PyObject *stream_arg;
  _pyAudio_Stream *streamObject;

  if (!PyArg_ParseTuple(args, "O!", &_pyAudio_StreamType, &stream_arg))
    return NULL;

  streamObject = (_pyAudio_Stream *) stream_arg;

  if (!_is_open(streamObject)) {
    PyErr_SetObject(PyExc_IOError,
		    Py_BuildValue("(s,i)",
				  "Stream closed",
				  paBadStreamPtr));
    return NULL;
  }

  PaStream *stream = streamObject->stream;
  frames = Pa_GetStreamWriteAvailable(stream);
  return PyLong_FromLong(frames);
}

static PyObject *
pa_get_stream_read_available(PyObject *self, PyObject *args)
{
  signed long frames;
  PyObject *stream_arg;
  _pyAudio_Stream *streamObject;

  if (!PyArg_ParseTuple(args, "O!", &_pyAudio_StreamType, &stream_arg))
    return NULL;

  streamObject = (_pyAudio_Stream *) stream_arg;

  if (!_is_open(streamObject)) {
    PyErr_SetObject(PyExc_IOError,
		    Py_BuildValue("(s,i)",
				  "Stream closed",
				  paBadStreamPtr));
    return NULL;
  }

  PaStream *stream = streamObject->stream;
  frames = Pa_GetStreamReadAvailable(stream);
  return PyLong_FromLong(frames);
}


/************************************************************
 *
 * IV. Python Module Init
 *
 ************************************************************/

#if PY_MAJOR_VERSION >= 3
#define ERROR_INIT NULL
#else
#define ERROR_INIT /**/
#endif

#if PY_MAJOR_VERSION >= 3
static struct PyModuleDef moduledef = {
  PyModuleDef_HEAD_INIT,
  "_portaudio",
  NULL,
  -1,
  paMethods,
  NULL,
  NULL,
  NULL,
  NULL
};
#endif

PyMODINIT_FUNC
#if PY_MAJOR_VERSION >= 3
PyInit__portaudio(void)
#else
init_portaudio(void)
#endif
{
  PyObject* m;

  PyEval_InitThreads();

  _pyAudio_StreamType.tp_new = PyType_GenericNew;
  if (PyType_Ready(&_pyAudio_StreamType) < 0)
    return ERROR_INIT;

  _pyAudio_paDeviceInfoType.tp_new = PyType_GenericNew;
  if (PyType_Ready(&_pyAudio_paDeviceInfoType) < 0)
    return ERROR_INIT;

  _pyAudio_paHostApiInfoType.tp_new = PyType_GenericNew;
  if (PyType_Ready(&_pyAudio_paHostApiInfoType) < 0)
    return ERROR_INIT;

#ifdef MACOSX
  _pyAudio_MacOSX_hostApiSpecificStreamInfoType.tp_new = PyType_GenericNew;
  if (PyType_Ready(&_pyAudio_MacOSX_hostApiSpecificStreamInfoType) < 0)
    return ERROR_INIT;
#endif

#if PY_MAJOR_VERSION >= 3
  m = PyModule_Create(&moduledef);
#else
  m = Py_InitModule("_portaudio", paMethods);
#endif

  Py_INCREF(&_pyAudio_StreamType);
  Py_INCREF(&_pyAudio_paDeviceInfoType);
  Py_INCREF(&_pyAudio_paHostApiInfoType);

#ifdef MACOSX
  Py_INCREF(&_pyAudio_MacOSX_hostApiSpecificStreamInfoType);
  PyModule_AddObject(m, "paMacCoreStreamInfo",
		     (PyObject *)
		     &_pyAudio_MacOSX_hostApiSpecificStreamInfoType);
#endif

  /* Add PortAudio constants */

  /* host apis */
  PyModule_AddIntConstant(m, "paInDevelopment", paInDevelopment);
  PyModule_AddIntConstant(m, "paDirectSound", paDirectSound);
  PyModule_AddIntConstant(m, "paMME", paMME);
  PyModule_AddIntConstant(m, "paASIO", paASIO);
  PyModule_AddIntConstant(m, "paSoundManager", paSoundManager);
  PyModule_AddIntConstant(m, "paCoreAudio", paCoreAudio);
  PyModule_AddIntConstant(m, "paOSS", paOSS);
  PyModule_AddIntConstant(m, "paALSA", paALSA);
  PyModule_AddIntConstant(m, "paAL", paAL);
  PyModule_AddIntConstant(m, "paBeOS", paBeOS);
  PyModule_AddIntConstant(m, "paWDMKS", paWDMKS);
  PyModule_AddIntConstant(m, "paJACK", paJACK);
  PyModule_AddIntConstant(m, "paWASAPI", paWASAPI);
  PyModule_AddIntConstant(m, "paNoDevice", paNoDevice);

  /* formats */
  PyModule_AddIntConstant(m, "paFloat32", paFloat32);
  PyModule_AddIntConstant(m, "paInt32", paInt32);
  PyModule_AddIntConstant(m, "paInt24", paInt24);
  PyModule_AddIntConstant(m, "paInt16", paInt16);
  PyModule_AddIntConstant(m, "paInt8", paInt8);
  PyModule_AddIntConstant(m, "paUInt8", paUInt8);
  PyModule_AddIntConstant(m, "paCustomFormat", paCustomFormat);

  /* error codes */
  PyModule_AddIntConstant(m, "paNoError", paNoError);
  PyModule_AddIntConstant(m, "paNotInitialized", paNotInitialized);
  PyModule_AddIntConstant(m, "paUnanticipatedHostError",
			  paUnanticipatedHostError);
  PyModule_AddIntConstant(m, "paInvalidChannelCount",
			  paInvalidChannelCount);
  PyModule_AddIntConstant(m, "paInvalidSampleRate",
			  paInvalidSampleRate);
  PyModule_AddIntConstant(m, "paInvalidDevice", paInvalidDevice);
  PyModule_AddIntConstant(m, "paInvalidFlag", paInvalidFlag);
  PyModule_AddIntConstant(m, "paSampleFormatNotSupported",
			  paSampleFormatNotSupported);
  PyModule_AddIntConstant(m, "paBadIODeviceCombination",
			  paBadIODeviceCombination);
  PyModule_AddIntConstant(m, "paInsufficientMemory",
			  paInsufficientMemory);
  PyModule_AddIntConstant(m, "paBufferTooBig", paBufferTooBig);
  PyModule_AddIntConstant(m, "paBufferTooSmall", paBufferTooSmall);
  PyModule_AddIntConstant(m, "paNullCallback", paNullCallback);
  PyModule_AddIntConstant(m, "paBadStreamPtr", paBadStreamPtr);
  PyModule_AddIntConstant(m, "paTimedOut", paTimedOut);
  PyModule_AddIntConstant(m, "paInternalError", paInternalError);
  PyModule_AddIntConstant(m, "paDeviceUnavailable", paDeviceUnavailable);
  PyModule_AddIntConstant(m, "paIncompatibleHostApiSpecificStreamInfo",
			  paIncompatibleHostApiSpecificStreamInfo);
  PyModule_AddIntConstant(m, "paStreamIsStopped", paStreamIsStopped);
  PyModule_AddIntConstant(m, "paStreamIsNotStopped", paStreamIsNotStopped);
  PyModule_AddIntConstant(m, "paInputOverflowed", paInputOverflowed);
  PyModule_AddIntConstant(m, "paOutputUnderflowed", paOutputUnderflowed);
  PyModule_AddIntConstant(m, "paHostApiNotFound", paHostApiNotFound);
  PyModule_AddIntConstant(m, "paInvalidHostApi", paInvalidHostApi);
  PyModule_AddIntConstant(m, "paCanNotReadFromACallbackStream",
			  paCanNotReadFromACallbackStream);
  PyModule_AddIntConstant(m, "paCanNotWriteToACallbackStream",
			  paCanNotWriteToACallbackStream);
  PyModule_AddIntConstant(m, "paCanNotReadFromAnOutputOnlyStream",
			  paCanNotReadFromAnOutputOnlyStream);
  PyModule_AddIntConstant(m, "paCanNotWriteToAnInputOnlyStream",
			  paCanNotWriteToAnInputOnlyStream);
  PyModule_AddIntConstant(m, "paIncompatibleStreamHostApi",
			  paIncompatibleStreamHostApi);

  /* callback constants */
  PyModule_AddIntConstant(m, "paContinue", paContinue);
  PyModule_AddIntConstant(m, "paComplete", paComplete);
  PyModule_AddIntConstant(m, "paAbort", paAbort);

  /* callback status flags */
  PyModule_AddIntConstant(m, "paInputUnderflow", paInputUnderflow);
  PyModule_AddIntConstant(m, "paInputOverflow", paInputOverflow);
  PyModule_AddIntConstant(m, "paOutputUnderflow", paOutputUnderflow);
  PyModule_AddIntConstant(m, "paOutputOverflow", paOutputOverflow);
  PyModule_AddIntConstant(m, "paPrimingOutput", paPrimingOutput);

#ifdef MACOSX
  PyModule_AddIntConstant(m, "paMacCoreChangeDeviceParameters",
			  paMacCoreChangeDeviceParameters);
  PyModule_AddIntConstant(m, "paMacCoreFailIfConversionRequired",
			  paMacCoreFailIfConversionRequired);
  PyModule_AddIntConstant(m, "paMacCoreConversionQualityMin",
			  paMacCoreConversionQualityMin);
  PyModule_AddIntConstant(m, "paMacCoreConversionQualityMedium",
			  paMacCoreConversionQualityMedium);
  PyModule_AddIntConstant(m, "paMacCoreConversionQualityLow",
			  paMacCoreConversionQualityLow);
  PyModule_AddIntConstant(m, "paMacCoreConversionQualityHigh",
			  paMacCoreConversionQualityHigh);
  PyModule_AddIntConstant(m, "paMacCoreConversionQualityMax",
			  paMacCoreConversionQualityMax);
  PyModule_AddIntConstant(m, "paMacCorePlayNice",
			  paMacCorePlayNice);
  PyModule_AddIntConstant(m, "paMacCorePro",
			  paMacCorePro);
  PyModule_AddIntConstant(m, "paMacCoreMinimizeCPUButPlayNice",
			  paMacCoreMinimizeCPUButPlayNice);
  PyModule_AddIntConstant(m, "paMacCoreMinimizeCPU",
			  paMacCoreMinimizeCPU);
#endif

#if PY_MAJOR_VERSION >= 3
  return m;
#endif
}
