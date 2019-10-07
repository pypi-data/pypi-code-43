#!/usr/bin/env python

__copyright__ = 'Copyright 2013-2014, http://radical.rutgers.edu'
__license__   = 'MIT'

import os
import random

import radical.pilot as rp

PWD = os.getcwd()


# ------------------------------------------------------------------------------
#
if __name__ == '__main__':

    session = rp.Session()

    try:

        pmgr    = rp.PilotManager(session=session)
        pd_init = {'resource'      : 'local.localhost',
                   'runtime'       : 60,
                   'exit_on_error' : True,
                   'cores'         : 2  # 2300 * 1 * 42
                  }
        pdesc = rp.ComputePilotDescription(pd_init)
        pilot = pmgr.submit_pilots(pdesc)
        umgr  = rp.UnitManager(session=session)
        umgr.add_pilots(pilot)

        n = 4  # 1024 * 1
        cuds = list()
        for i in range(0, n):

            cud = rp.ComputeUnitDescription()
            cud.executable       = '%s/examples/lm_task.sh' % PWD
            cud.arguments        = 5         # [random.randint(5, 10) * 1]
            cud.cpu_threads      = 1         # random.randint(1, 8)
            cud.cpu_processes    = 1         # random.randint(1, 41) * 10
            cud.gpu_processes    = 0         # [0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 4] \
                                             # [random.randint(0, 10)]
            cud.gpu_process_type = rp.POSIX  # rp.MPI
            cud.cpu_process_type = rp.POSIX  # rp.MPI
            cud.cpu_thread_type  = rp.POSIX
            cuds.append(cud)

        umgr.submit_units(cuds)
        umgr.wait_units()
        session.close(download=True)

    except:
        session.close(download=False)
        raise


# ------------------------------------------------------------------------------

