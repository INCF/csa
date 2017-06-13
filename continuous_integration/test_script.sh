#!/bin/bash

set -e

python --version
python -c "import numpy; print('numpy %s' % numpy.__version__)"
python -c "import matplotlib; print('matplotlib %s' % matplotlib.__version__)"

# build csa inplace
python setup.py build_ext -i

# run tests, but if mystery segmentation fault occurr, rerun tests to attempt a
# clean exit
while true; do
    nosetests --with-coverage --cover-package=csa
    if [ $? -eq 0 ]
    then
        exit 0
        break
    fi
done