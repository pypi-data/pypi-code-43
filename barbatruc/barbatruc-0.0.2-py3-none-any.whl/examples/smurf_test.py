"""Example on how to solve a pollution problem.

This example uses the navier stokes solver,
add a recording structure,
and control the whole test with a dictionnary.

This example is used by Smurf for data assimilation training.
See I. Mirouze for further details.
"""

import numpy as np


from barbatruc.fluid_domain import DomainRectFluid, blur
from barbatruc.fd_ns_2d import ns_iteration

__all__ = ["smurf_test"]


def smurf_test(dof, nsave):
    """Startup computation
    solve a pollution problem with the navier stokes solver
    """
    dimx = dof["nx"] * dof["dx"]
    dimy = dof["ny"] * dof["dx"]

    dom = DomainRectFluid(
        dimx=dimx,
        dimy=dimy,
        delta_x=dof["dx"],
        rho=dof["rho"],
        nu_=dof["nu"])

    # Add an initial speed
    dom.fields["vel_u"] = np.ones(dom.shape)*dof["u_west"]
    # Add velocity BC on the left of the domain
    dom.bcx_inlet_uv_outlet_p(val_u=dof["u_west"], val_v=0.0)

    # Add a source term on scalar.
    source = np.zeros(dom.shape)
    source[dof["source"]["location"]] = dof["source"]["value"]
    for _ in range(dof["source"]["blur_it"]):
        source = blur(source)
    dom.source["scal"] = source

    # Add monitoring array
    rec_field = dict()
    rec_shape = (nsave+1, dom.shape[0], dom.shape[1])
    for field in ["vel_u", "vel_v", "scal", "press"]:
        rec_field[field] = np.zeros(rec_shape)
    time_rec = np.zeros((nsave+1))

    # record inital state
    time_rec[0] = 0
    for field in ["vel_u", "vel_v", "scal", "press"]:
        rec_field[field][0, :, :] = dom.fields[field]

    # MAIN TEMPORAL LOOP--------------------
    t_end = dof["tend"]/1000
    time = 0.0
    time_step = t_end/nsave
    for i in range(nsave):

        time += time_step
        ns_iteration(dom, time_step)
        for field in ["vel_u", "vel_v", "scal", "press"]:
            rec_field[field][i+1, :, :] = dom.fields[field]
        time_rec[i+1] = time

        print('  Max u:', np.max(dom.fields["vel_u"]))
        print('  Time :', time)
        print('  Iteration %d' % (i))

    print('Normal end of execution.')
    return rec_field, time_rec

if __name__ == "__main__":

    DOF = {
        "rho": 1.0,
        "nu": 1.0,
        "nx": 40,
        "ny": 20,
        "dx": 0.02,
        "tend": 100.,
        "u_west": 20.,
        "source": {
            "location": (10, 10),
            "value": 1.0,
            "blur_it": 0
        }

    }

    REC, TIME = smurf_test(DOF, 20)
#    plt.matshow(REC["scal"][-1, :, :])
#    plt.show()
