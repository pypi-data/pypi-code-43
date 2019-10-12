#!/usr/bin/env python

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
                   'cores'         : 1024 * 8,
                  }
        pdesc = rp.ComputePilotDescription(pd_init)
        pilot = pmgr.submit_pilots(pdesc)
        umgr  = rp.UnitManager(session=session)
        umgr.add_pilots(pilot)

        n = 1024 * 4
        cuds = list()
        for i in range(0, n):
            cud = rp.ComputeUnitDescription()
            cud.executable       = '/bin/sleep'
            cud.arguments        = [random.randint(5, 20)]
            cud.cpu_processes    =  random.choice([1, 2, 4, 16, 32])
            cud.cpu_threads      =  random.choice([1, 2, 4])
            cud.cpu_process_type =  rp.MPI
            cuds.append(cud)

        umgr.submit_units(cuds)
        umgr.wait_units()

    finally:
        session.close(download=True)


# ------------------------------------------------------------------------------

