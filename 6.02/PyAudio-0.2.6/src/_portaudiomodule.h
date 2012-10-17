/**
 * PyAudio : Python Bindings for PortAudio.
 *
 * PyAudio : API Header File
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

#ifndef __PAMODULE_H__
#define __PAMODULE_H__

/* version */
static PyObject *
pa_get_version(PyObject *self, PyObject *args);

static PyObject *
pa_get_version_text(PyObject *self, PyObject *args);

/* framework init */
static PyObject *
pa_initialize(PyObject *self, PyObject *args);

static PyObject *
pa_terminate(PyObject *self, PyObject *args);

/* host api */
static PyObject *
pa_get_host_api_count(PyObject *self, PyObject *args);

static PyObject *
pa_get_default_host_api(PyObject *self, PyObject *args);

static PyObject *
pa_host_api_type_id_to_host_api_index(PyObject *self, PyObject *args);

static PyObject *
pa_host_api_device_index_to_device_index(PyObject *self, PyObject *args);

static PyObject *
pa_get_host_api_info(PyObject *self, PyObject *args);

/* device api */
static PyObject *
pa_get_device_count(PyObject *self, PyObject *args);

static PyObject *
pa_get_default_input_device(PyObject *self, PyObject *args);

static PyObject *
pa_get_default_output_device(PyObject *self, PyObject *args);

static PyObject *
pa_get_device_info(PyObject *self, PyObject *args);

/* stream open/close */

static PyObject *
pa_open(PyObject *self, PyObject *args, PyObject *kwargs);

static PyObject *
pa_close(PyObject *self, PyObject *args);

static PyObject *
pa_get_sample_size(PyObject *self, PyObject *args);

static PyObject *
pa_is_format_supported(PyObject *self, PyObject *args,
		       PyObject *kwargs);

/* stream start/stop/info */

static PyObject *
pa_start_stream(PyObject *self, PyObject *args);

static PyObject *
pa_stop_stream(PyObject *self, PyObject *args);

static PyObject *
pa_abort_stream(PyObject *self, PyObject *args);

static PyObject *
pa_is_stream_stopped(PyObject *self, PyObject *args);

static PyObject *
pa_is_stream_active(PyObject *self, PyObject *args);

static PyObject *
pa_get_stream_time(PyObject *self, PyObject *args);

static PyObject *
pa_get_stream_cpu_load(PyObject *self, PyObject *args);

/* stream write/read */

static PyObject *
pa_write_stream(PyObject *self, PyObject *args);

static PyObject *
pa_read_stream(PyObject *self, PyObject *args);

static PyObject *
pa_get_stream_write_available(PyObject *self, PyObject *args);

static PyObject *
pa_get_stream_read_available(PyObject *self, PyObject *args);

#endif
