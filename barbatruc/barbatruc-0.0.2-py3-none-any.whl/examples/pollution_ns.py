"""Example on how to solve a pollution problem with the navier stokes solver"""

import numpy as np

from barbatruc.fluid_domain import DomainRectFluid
from barbatruc.fd_ns_2d import ns_iteration

__all__ = ["pollution_ns"]


def pollution_ns(nsave, t_end):
    """Startup computation
    solve a pollution problem with the navier stokes solver
    """
    dom = DomainRectFluid(dimx=0.82, dimy=0.61, delta_x=0.02)
    dom.fields["vel_u"] = 1. * np.ones(dom.shape)
    dom.fields["vel_v"] = 0. * np.ones(dom.shape)
    dom.add_obstacle_circle()
    dom.bcx_inlet_uv_outlet_p(val_u=1., val_v=0.0)
    dom.bcy_noslip_channel()

    time = 0.0
    time_step = t_end/nsave

    ns_fields = None
    for i in range(nsave):
        time += time_step
        ns_fields = ns_iteration(dom, time_step, ns_fields)
        print('  Max u:', np.max(dom.fields["vel_u"]))
        print('  Time :', time)
        print('  Iteration %d' % (i))

    dom.show_fields()
    dom.show_flow()

    print('Normal end of execution.')


if __name__ == "__main__":
    pollution_ns(10, 0.40)
