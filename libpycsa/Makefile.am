## Process this file with Automake to create Makefile.in

ACLOCAL = $(top_srcdir)/aclocal.sh

lib_LTLIBRARIES = libpycsa.la

libpycsa_la_SOURCES = pycsa.h pycsa.cpp

libpycsa_la_HEADERS = pycsa.h
libpycsa_la_CPPFLAGS = @LIBPYCSA_CPPFLAGS@ @LIBNEUROSIM_INCLUDE@
libpycsa_la_CXXFLAGS = @LIBPYCSA_CXXFLAGS@
libpycsa_la_LIBADD = @LIBNEUROSIM_PY_LIBS@ @LIBNEUROSIM_LIBS@ @PYTHONLIB@
libpycsa_la_LDFLAGS = \
	-version-info 1:0:0 -export-dynamic -Wl,-z,defs
libpycsa_ladir = $(includedir)

MKDEP = gcc -M $(DEFS) $(INCLUDES) $(CPPFLAGS) $(CFLAGS)
