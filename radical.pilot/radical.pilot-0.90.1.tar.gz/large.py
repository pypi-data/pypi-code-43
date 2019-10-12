#!/usr/bin/env python

__copyright__ = 'Copyright 2013-2014, http://radical.rutgers.edu'
__license__   = 'MIT'

import random

import radical.pilot as rp


# ------------------------------------------------------------------------------
#
if __name__ == '__main__':

    session = rp.Session()
    try:
        pmgr = rp.PilotManager(session=session)
        pd_init = {'resource'      : 'local.localhost',
                   'runtime'       : 120,
                   'exit_on_error' : True,
                   'cores'         : 1024 * 1024
                  }
        pdesc = rp.ComputePilotDescription(pd_init)
        pilot = pmgr.submit_pilots(pdesc)
        umgr  = rp.UnitManager(session=session)
        umgr.add_pilots(pilot)

        n = 1024 * 128
        cuds = list()
        for i in range(0, n):

            cud = rp.ComputeUnitDescription()
            cud.executable       = '/bin/sleep'
          # cud.executable       = '/home/merzky/radical/radical.pilot.2/examples/hello_rp.sh'
            cud.arguments        = [random.choice([1, 2, 4, 8, 16]) * 10]
          # cud.gpu_processes    =  random.choice([1, 2, 4, 8])
            cud.cpu_processes    =  random.choice([1, 2, 4, 8, 16, 32, 64, 128])
            cud.cpu_threads      =  random.choice([1, 2, 4, 8, 16, 32, 64])
            cud.cpu_process_type = rp.MPI
            cud.cpu_thread_type  = rp.POSIX
            cuds.append(cud)

        umgr.submit_units(cuds)
        umgr.wait_units()

    finally:
        session.close(download=True)


# ------------------------------------------------------------------------------

