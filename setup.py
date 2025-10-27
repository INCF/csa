#!/usr/bin/env python

from distutils.core import setup

# ugly hack to prevent matplotlib from creating a configuration file
# outside of the EasyInstall sandbox
import os
os.environ['MPLCONFIGDIR'] = "."

# read version without actually importing the module
import re
from pathlib import Path

def read_version(path: str) -> str:
    text = Path(path).read_text(encoding="utf-8")
    m = re.search(r"^__version__\s*=\s*\"(.+?)\"", text, flags=re.M)
    if not m:
        raise RuntimeError(f"Unable to find __version__ in {path}")
    return m.group(1)

__version__ = read_version("csa/version.py")

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
    #...
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
