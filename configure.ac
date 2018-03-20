dnl Process this file with autoconf to produce configure.
AC_INIT(csa, 0.1.6)
AM_INIT_AUTOMAKE
AM_CONFIG_HEADER([config.h])
AM_MAINTAINER_MODE

#
# Use libneurosim?
#
AC_CHECK_LIB(neurosim, libneurosim_version, HAVE_LIBNEUROSIM="auto", HAVE_LIBNEUROSIM="no")
if test "x$HAVE_LIBNEUROSIM" = xauto; then
   LIBNEUROSIM_LIBS="-lneurosim"
   LIBNEUROSIM_PY_LIBS="-lpyneurosim"
   LIBNEUROSIM_INCLUDE=""
fi
AC_ARG_WITH(libneurosim, [  --with-libneurosim[[=directory]]       Request the use of libneurosim. Optionally give the directory, where libneurosim is installed],
  [
    if test "$withval" != "no"; then
      if test "$withval" != "yes"; then
    	LIBNEUROSIM_LIBS="-L${withval}/lib -lneurosim"
	LIBNEUROSIM_PY_LIBS="-lpyneurosim"
	LIBNEUROSIM_INCLUDE="-I${withval}/include"
      fi
      HAVE_LIBNEUROSIM="yes"
    else
      HAVE_LIBNEUROSIM="no"
    fi
  ])

if test "x$HAVE_LIBNEUROSIM" != xno; then
  AC_DEFINE(HAVE_LIBNEUROSIM, 1, [libneurosim support enabled?])
fi

AC_ARG_WITH([python],
    [AS_HELP_STRING([--without-python], [ignore the presence of Python and disable libpycsa])])

AS_IF([test "x$with_python" != "xno"],
      [AM_PATH_PYTHON([2.6], [have_python=yes], [have_python=no])],
      [have_python=no])

AS_IF([test "x$have_python" = "xyes"], [
    PYTHON_INC=`$PYTHON -c 'import sys; from distutils import sysconfig; sys.stdout.write(sysconfig.get_python_inc())'`
    AC_CHECK_FILE(["${PYTHON_INC}/Python.h"], [LIBPYCSA_CPPFLAGS="-I${PYTHON_INC}"], [have_python=no])
])

AC_MSG_CHECKING([whether to build libpycsa])
AS_IF([test "x$have_python" = "xyes"], [],
      [AS_IF([test "x$with_python" = "xyes"],
             [AC_MSG_ERROR([Libpycsa requested, but Python not found])])])
AC_MSG_RESULT([$have_python])

AX_CHECK_COMPILE_FLAG([-fno-strict-aliasing],
                      [LIBPYCSA_CXXFLAGS="-fno-strict-aliasing"], [])

# FIXME: this means that --without-python make will not recurse into libpycsa subdir
if test "x$have_python" = "xyes"; then
    LIBPYCSA_SUBDIR="libpycsa"
else
    LIBPYCSA_SUBDIR=""
fi

AM_CONDITIONAL([HAVE_PYTHON], [test "x$have_python" = "xyes"])

AC_SUBST([HAVE_PYTHON])
AC_SUBST([LIBPYCSA_SUBDIR])

AC_SUBST([PYTHON])
AC_SUBST([PYTHON_VERSION])

AC_SUBST([LIBPYCSA_CPPFLAGS])
AC_SUBST([LIBPYCSA_CXXFLAGS])

AC_LANG(C++)

AC_PROG_CXX
AC_PROG_LIBTOOL

AC_SUBST(LIBNEUROSIM_LIBS)
AC_SUBST(LIBNEUROSIM_PY_LIBS)
AC_SUBST(LIBNEUROSIM_INCLUDE)

AC_CONFIG_FILES([
  Makefile
  csa/__init__.py
  libpycsa/Makefile
])

AC_OUTPUT

dnl Local Variables:
dnl comment-start: "dnl "
dnl comment-end: ""
dnl comment-start-skip: "\\bdnl\\b\\s *"
dnl End:
