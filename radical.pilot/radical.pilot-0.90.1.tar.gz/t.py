#!/usr/bin/env python

import radical.pilot as rp


# ------------------------------------------------------------------------------
#
if __name__ == '__main__':

    ps =      1024
    un =  1 * 1024
    us =         1

    try:
        pd_init = {'resource'      : 'local.localhost',
                   'runtime'       : 15,
                   'exit_on_error' : True,
                   'cores'         : ps,
                  }

        cd_init = {'executable'    : '/bin/date',
                   'cpu_processes' : us,
                  }

        session = rp.Session()
        pmgr    = rp.PilotManager(session)
        pdesc   = rp.ComputePilotDescription(pd_init)
        umgr    = rp.UnitManager(session)
        cuds    = [rp.ComputeUnitDescription(cd_init) for _ in range(0, un)]
        pilot   = pmgr.submit_pilots(pdesc)

        umgr.add_pilots(pilot)
        umgr.submit_units(cuds)
        umgr.wait_units()

    finally:
        session.close(download=True)


# ------------------------------------------------------------------------------

