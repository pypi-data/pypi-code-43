"""
This file provides information of how to build and configure pythia packet:

TODO en this point

"""

import os
import subprocess
from ejpm.engine.commands import run, workdir, env


def install_pythia(context):
    """Install pythia according to Context"""

    os.environ['CONTAINER_ROOT'] = '/home/romanov/jleic/test'
    os.environ['PYTHIA_VERSION'] = '8230'
    os.environ['pythia_tgz'] = 'pythia${PYTHIA_VERSION}.tgz'

    result = subprocess.run(

    """wget http://home.thep.lu.se/~torbjorn/pythia8/$pythia_tgz \
    && tar xzf $pythia_tgz \
    && rm -f $pythia_tgz \
    && cd pythia${PYTHIA_VERSION} \
    && ./configure --with-python --with-python-include=/usr/include/python2.7 --prefix=$CONTAINER_ROOT/app/pythia/pythia${PYTHIA_VERSION} \
    && make -j $NBUILD_THREADS install \
    && cd .. \
    && rm -rf pythia${PYTHIA_VERSION} \
    && yum remove -y python-devel \
    && mkdir -p $EIC_ROOT/app/pythia \
    && ln -s $CONTAINER_ROOT/app/pythia/pythia${PYTHIA_VERSION} $EIC_ROOT/app/pythia/pythia${PYTHIA_VERSION} \
    && ln -s pythia${PYTHIA_VERSION} $EIC_ROOT/app/pythia/PRO
    """)
    print(result)


if __name__ == '__main__':
    install_pythia(None)
