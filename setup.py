#!/usr/bin/env python

from distutils.core import setup

# ugly hack to prevent matplotlib from creating a configuration file
# outside of the EasyInstall sandbox
import os
os.environ['MPLCONFIGDIR'] = "."

# read version without actually importing the module
import ast
__version__ = ast.parse (open ("csa/version.py").read ()).body[0].value.s

long_description = """The CSA library provides elementary connection-sets and operators for
combining them. It also provides an iteration interface to such
connection-sets enabling efficient iteration over existing connections
with a small memory footprint also for very large networks. The CSA
can be used as a component of neuronal network simulators or other
tools."""

setup (
    name = "csa",
    version = __version__,
    packages = ['csa',],
    author = "Mikael Djurfeldt", # add your name here if you contribute to the code
    author_email = "mikael@djurfeldt.com",
    description = "The Connection-Set Algebra implemented in Python",
    long_description = long_description,
    license = "GPLv3",
    keywords = "computational neuroscience modeling connectivity",
    url = "http://software.incf.org/software/csa/",
    classifiers = ['Development Status :: 3 - Alpha',
                   'Environment :: Console',
                   'Intended Audience :: Science/Research',
                   'License :: OSI Approved :: GNU General Public License (GPL)',
                   'Natural Language :: English',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 3.4',
                   'Programming Language :: Python :: 3.5',
                   'Programming Language :: Python :: 3.6',
                   'Topic :: Scientific/Engineering'],
    install_requires = ['numpy', 'matplotlib'],
)
