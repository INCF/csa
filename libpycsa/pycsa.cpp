/*
 *  pycsa.cpp
 *
 *  This file is part of libneurosim.
 *
 *  Copyright (C) 2013, 2018 INCF
 *
 *  libneurosim is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  libneurosim is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *
 */

#include "pycsa.h"

#include <neurosim/pyneurosim.h>

#include <string>
#include <iostream>

#if PY_MAJOR_VERSION >= 3
#define PYINT_ASLONG PyLong_AsLong
#define PYINT_FROMLONG PyLong_FromLong
#else
#define PYINT_ASLONG PyInt_AsLong
#define PYINT_FROMLONG PyInt_FromLong
#endif

static PyObject* pMask = 0;
static PyObject* pConnectionSet = 0;
static PyObject* pCSAClasses = 0;
static PyObject* pArity = 0;
static PyObject* pCross = 0;
static PyObject* pPartition = 0;
static PyObject* pParse = 0;
static PyObject* pParseString = 0;


static void
error (std::string errstring)
{
  PYGILSTATE_ENSURE (gstate);
  PyErr_SetString (PyExc_RuntimeError, errstring.c_str ());
  PYGILSTATE_RELEASE (gstate);
}


static bool
CSAimported ()
{
  if (!Py_IsInitialized ())
    Py_Initialize ();
  return PyMapping_HasKeyString (PyImport_GetModuleDict (), (char*)"csa");
}


static bool
loadCSA ()
{
  PYGILSTATE_ENSURE (gstate);
  PyObject* pModule = PyMapping_GetItemString (PyImport_GetModuleDict (), (char*)"csa");

  pMask = PyObject_GetAttrString (pModule, "Mask");
  if (pMask == NULL)
    {
      Py_DECREF (pModule);
      PYGILSTATE_RELEASE (gstate);
      error ("Couldn't find the Mask class in the CSA library");
      return false;
    }

  pConnectionSet = PyObject_GetAttrString (pModule, "ConnectionSet");
  if (pConnectionSet == NULL)
    {
      Py_DECREF (pModule);
      PYGILSTATE_RELEASE (gstate);
      error ("Couldn't find the ConnectionSet class in the CSA library");
      return false;
    }

  pArity = PyObject_GetAttrString (pModule, "arity");
  pCross = PyObject_GetAttrString (pModule, "cross");
  pPartition = PyObject_GetAttrString (pModule, "partition");

  pParse = PyObject_GetAttrString (pModule, "parse");
  pParseString = PyObject_GetAttrString (pModule, "parseString");

  Py_DECREF (pModule);
  if (pArity == NULL)
    {
      PYGILSTATE_RELEASE (gstate);
      error ("Couldn't find the arity function in the CSA library");
      return false;
    }

  pCSAClasses = PyTuple_Pack (2, pMask, pConnectionSet);
  PYGILSTATE_RELEASE (gstate);
  return true;
}


static bool
tryLoadCSA ()
{
  if (pCSAClasses == 0)
    {
      if (!CSAimported ())
	PyRun_SimpleString ("import csa\n"); //*fixme* error handling

      // load CSA library
      bool status = loadCSA ();
      if (!status)
	return false;
    }
}


namespace PyCSA {

  PyCSAGenerator::PyCSAGenerator (PyObject* obj)
    : pCSAObject (obj), pPartitionedCSAObject (NULL), pIterator (NULL)
  {
    PYGILSTATE_ENSURE (gstate);
    Py_INCREF (pCSAObject);
    PyObject* a = PyObject_CallFunctionObjArgs (pArity, pCSAObject, NULL);
    arity_ = PYINT_ASLONG (a);
    Py_DECREF (a);
    PYGILSTATE_RELEASE (gstate);
  }


  PyCSAGenerator::~PyCSAGenerator ()
  {
    PYGILSTATE_ENSURE (gstate);
    Py_XDECREF (pIterator);
    Py_XDECREF (pPartitionedCSAObject);
    Py_DECREF (pCSAObject);
    PYGILSTATE_RELEASE (gstate);
  }


  int
  PyCSAGenerator::arity ()
  {
    return arity_;
  }


  PyObject*
  PyCSAGenerator::makeIntervals (IntervalSet& iset)
  {
    PyObject* ivals = PyList_New (0);
    if (iset.skip () == 1)
      {
	for (IntervalSet::iterator i = iset.begin (); i != iset.end (); ++i)
	  PyList_Append (ivals,
			 PyTuple_Pack (2,
				       PYINT_FROMLONG (i->first),
				       PYINT_FROMLONG (i->last)));
      }
    else
      {
	for (IntervalSet::iterator i = iset.begin (); i != iset.end (); ++i)
	  {
	    int last = i->last;
	    for (int j = i->first; j < last; j += iset.skip ())
	      PyList_Append (ivals,
			     PyTuple_Pack (2,
					   PYINT_FROMLONG (j),
					   PYINT_FROMLONG (j)));
	  }
      }
    return ivals;
  }


  void
  PyCSAGenerator::setMask (std::vector<Mask>& masks, int local)
  {
    PYGILSTATE_ENSURE (gstate);
    PyObject* pMasks = PyList_New (masks.size ());
    for (size_t i = 0; i < masks.size (); ++i)
      {
	PyObject* pMask
	  = PyObject_CallFunctionObjArgs (pCross,
					  makeIntervals (masks[i].sources),
					  makeIntervals (masks[i].targets),
					  NULL);
	PyList_SetItem (pMasks, i, pMask);
      }

    Py_XDECREF (pPartitionedCSAObject);
    pPartitionedCSAObject = PyObject_CallFunctionObjArgs (pPartition,
							  pCSAObject,
							  pMasks,
							  PYINT_FROMLONG (local),
							  NULL);
    if (pPartitionedCSAObject == NULL)
      {
	PYGILSTATE_RELEASE (gstate);
	std::cerr << "Failed to create masked CSA object" << std::endl;
	return;
      }
    Py_INCREF (pPartitionedCSAObject); //*fixme* check if necessary!
    PYGILSTATE_RELEASE (gstate);
  }


  int
  PyCSAGenerator::size ()
  {
    PYGILSTATE_ENSURE (gstate);
    int size = PySequence_Size (pCSAObject);
    PYGILSTATE_RELEASE (gstate);
    return size;
  }


  void
  PyCSAGenerator::start ()
  {
    if (pPartitionedCSAObject == NULL)
      {
	error ("CSA connection generator not properly initialized");
	return;
      }
    PYGILSTATE_ENSURE (gstate);
    Py_XDECREF (pIterator);
    pIterator = PyObject_GetIter (pPartitionedCSAObject);
    PYGILSTATE_RELEASE (gstate);
  }


  bool
  PyCSAGenerator::next (int& source, int& target, double* value)
  {
    if (pIterator == NULL)
      {
	error ("Must call start() before next()");
	return false;
      }

    PYGILSTATE_ENSURE (gstate);
    PyObject* tuple = PyIter_Next (pIterator);
    PyObject* err = PyErr_Occurred ();
    if (err)
      {
	PYGILSTATE_RELEASE (gstate);
	return false;
      }

    if (tuple == NULL)
      {
	Py_DECREF (pIterator);
	pIterator = NULL;
	PYGILSTATE_RELEASE (gstate);
	return false;
      }

    source = PYINT_ASLONG (PyTuple_GET_ITEM (tuple, 0));
    target = PYINT_ASLONG (PyTuple_GET_ITEM (tuple, 1));
    for (int i = 0; i < arity_; ++i)
      {
	PyObject* v = PyTuple_GET_ITEM (tuple, i + 2);
	if (!PyFloat_Check (v))
	  {
	    Py_DECREF (tuple);
	    PYGILSTATE_RELEASE (gstate);
	    error ("NEST cannot handle non-float CSA value sets");
	    return false;
	  }
	value[i] = PyFloat_AsDouble (v);
      }

    Py_DECREF (tuple);
    PYGILSTATE_RELEASE (gstate);
    return true;
  }

  static bool
  isPyCSAGenerator (PyObject* obj)
  {
    if (pCSAClasses == 0)
      {
	if (!CSAimported ())
	  return false;

	// load CSA library
	bool status = loadCSA ();
	if (!status)
	  return false;
      }

    return PyObject_IsInstance (obj, pCSAClasses);
  }


  static ConnectionGenerator*
  unpackPyCSAGenerator (PyObject* pObj)
  {
    if (isPyCSAGenerator (pObj))
      return new PyCSAGenerator (pObj);
    else
      return 0;
  }

  static ConnectionGenerator*
  parseString (std::string xml)
  {
    if (!tryLoadCSA ())
      return 0;
    PYGILSTATE_ENSURE (gstate);
    PyObject* pyXML = PyUnicode_FromString (xml.c_str ());
    PyObject* cg = PyObject_CallFunctionObjArgs (pParseString, pyXML, NULL);
    Py_DECREF (pyXML);
    PYGILSTATE_RELEASE (gstate);
    return new PyCSAGenerator (cg);
  }

  static ConnectionGenerator*
  parseFile (std::string fname)
  {
    if (!tryLoadCSA ())
      return 0;
    PYGILSTATE_ENSURE (gstate);
    PyObject* pyfname = PyUnicode_FromString (fname.c_str ());
    PyObject* cg = PyObject_CallFunctionObjArgs (pParseString, pyfname, NULL);
    Py_DECREF (pyfname);
    PYGILSTATE_RELEASE (gstate);
    return new PyCSAGenerator (cg);
  }

  // Publicly visible in PyCSA namespace
  void
  init ()
  {
    registerConnectionGeneratorLibrary ("libpycsa",
					parseString,
					parseFile,
					0,
					0);
    PNS::registerConnectionGeneratorType (isPyCSAGenerator,
					  unpackPyCSAGenerator);
  }

}

namespace {
  struct initializer {
    initializer() {
      PyCSA::init ();
    }
  };
  static initializer i;
}
