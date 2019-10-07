#!/usr/bin/env python

__copyright__ = 'Copyright 2013-2014, http://radical.rutgers.edu'
__license__   = 'MIT'

import os
import time
import sys
import random

import radical.pilot as rp
import radical.utils as ru


import threading as mt

ucount = 0

glyphs = {rp.DONE    : '+',
          rp.FAILED  : '-',
          rp.CANCELED: '?'}


# ------------------------------------------------------------------------------
#
def unit_state_cb (unit, state):

    global ucount

    if state in rp.FINAL:
        ucount += 1
        sys.stdout.write(glyphs[state])
        sys.stdout.flush()


# ------------------------------------------------------------------------------
#
if __name__ == '__main__':

    session = rp.Session()

    try:

        pmgr    = rp.PilotManager(session=session)
        pd_init = {'resource'      : 'local.localhost',
                   'runtime'       : 60,
                   'exit_on_error' : True,
                   'cores'         : 50,
                  }
        pdesc = rp.ComputePilotDescription(pd_init)
        pilot = pmgr.submit_pilots(pdesc)
        umgr  = rp.UnitManager(session=session)
        umgr.add_pilots(pilot)
        umgr.register_callback(unit_state_cb)

        n       = 1000
        nchunks = 100
        chunkn  = n / nchunks
        chunks  = list()

        for i in range(nchunks):
            chunks.append(list())

        for i in range(0, n):

            cud = rp.ComputeUnitDescription()
            cud.executable    = '/home/merzky/radical/radical.pilot.devel/examples/lm_task.sh'
            cud.arguments     = 1
            cud.cpu_processes = 1

            chunk_id = i % nchunks
            chunks[chunk_id].append(cud)

        chunk_idx = 0
        umgr.submit_units(chunks.pop())
        while chunks:
            time.sleep(1)
            if ucount > chunk_idx * chunkn + chunkn / 2:
                umgr.submit_units(chunks.pop())
                chunk_idx += 1

        print
        umgr.wait_units()

        session.close(download=True)


    except:
        session.close(download=False)
        raise


# ------------------------------------------------------------------------------
