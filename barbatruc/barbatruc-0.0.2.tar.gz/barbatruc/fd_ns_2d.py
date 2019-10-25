"""Module to solve 2D Naviers stokes equations.

The interactive module 12 steps to Navier-Stokes is one of several
components of the Computational Fluid Dynamics class taught by Professor
Lorena Barba in Boston university between 2009 and 2013.

The following code is started from step12
See https://nbviewer.jupyter.org/github/barbagroup/CFDPython/tree/master/lessons/
for futher reading

Dom here after isthe FluidDomain object of barbatruc
"""

import numpy as np
from barbatruc.fd_operators import (grad_2, scnd_der_2)



CFL_MAX = 0.699
FOU_MAX = 0.099
OBS_GAIN = -20.

__all__ = ["ns_iteration"]


def mini_ns_delta_t(dom):
    """ Define the mai iteration of the temporal loop.
    """
    u_max = max(np.max(np.hypot(
        dom.fields["vel_u"],
        dom.fields["vel_v"])), 1.e-8)
    delta_t_cfl = CFL_MAX*dom.delta_x/u_max
    delta_t_fou = FOU_MAX/dom.nu_*dom.delta_x**2
    delta_t = min(delta_t_cfl, delta_t_fou)
    return delta_t


def ns_iteration(
        dom,
        time_step,
        ns_fields=None, obs_immersed=0.0):
    """Major iteration."""
    time = 0.
    if ns_fields is None:
        ns_fields = dict()
        ns_fields["obs_force_x"] = np.zeros(dom.shape)
        ns_fields["obs_force_y"] = np.zeros(dom.shape)
        ns_fields["temporal"] = dict()
        for key in dom.fields:
            ns_fields["temporal"][key] = list()

    while time < time_step:
        delta_t = min(mini_ns_delta_t(dom), time_step-time)
        time += delta_t
        dom.fields = ns_sub_iteration(dom, ns_fields, delta_t, obs_immersed)
        for key in dom.fields:
            ns_fields["temporal"][key].append(dom.fields[key].mean())

    return ns_fields


def ns_sub_iteration(dom, ns_fields, delta_t, obs_immersed):
    """Sub iteration of Naviers stokes."""

    periox, perioy = dom.perio_xy()

    fields_new = dict()
    grad_x, grad_y, ggrad_x, ggrad_y = compute_derivatives(dom, periox, perioy)

    # compute pressure term
    fields_new["press"] = pressure_poisson(
        dom,
        delta_t,
        periox,
        perioy)

    if obs_immersed > 0.0:
        ns_fields["obs_force_x"] += obs_immersed*dom.obstacle*dom.fields["vel_u"]
        ns_fields["obs_force_y"] += obs_immersed*dom.obstacle*dom.fields["vel_v"]

    sce_term = dict()
    sce_term["vel_u"] = (
        dom.source["vel_u"]
        - grad_x["press"] / (2. * dom.rho)
        + ns_fields["obs_force_x"])
    sce_term["vel_v"] = (
        dom.source["vel_v"]
        - grad_y["press"] / (2. * dom.rho)
        + ns_fields["obs_force_y"])
    sce_term["scal"] = dom.source["scal"]

    for field in ["vel_u", "vel_v", "scal"]:
        fields_new[field] = dom.fields[field] + delta_t * (
            - (dom.fields["vel_u"] * grad_x[field] + dom.fields["vel_v"] * grad_y[field])
            + sce_term[field]
            + dom.nu_ * (ggrad_x[field] + ggrad_y[field])
            )

    apply_bc_dirichlet(dom, fields_new)

    if obs_immersed == 0.0:
        for field in ["vel_u", "vel_v"]:
            fields_new[field] = dom.nullify_on_obstacle(fields_new[field])

    return fields_new


def compute_derivatives(dom, periox, perioy):
    """Compute the derivatives of fields."""
    grad_x = dict()
    grad_y = dict()
    ggrad_x = dict()
    ggrad_y = dict()
    for field in ["vel_u", "vel_v", "scal", "press"]:
        grad_x[field], grad_y[field] = grad_2(
            dom.fields[field],
            dom.delta_x,
            periox=periox,
            perioy=perioy
            )
        ggrad_x[field], ggrad_y[field] = scnd_der_2(
            dom.fields[field],
            dom.delta_x,
            periox=periox,
            perioy=perioy)

    apply_bc_neumann(dom, grad_x, grad_y)
    return grad_x, grad_y, ggrad_x, ggrad_y


def apply_bc_dirichlet(dom, fields):
    """Apply boundary condituons with a crude manner."""
    if dom.bc_xmin_type == "dirichlet":
        for key in dom.bc_xmin_values.keys():
            fields[key][:, 0] = dom.bc_xmin_values[key]
    if dom.bc_xmax_type == "dirichlet":
        for key in dom.bc_xmax_values.keys():
            fields[key][:, -1] = dom.bc_xmax_values[key]
    if dom.bc_ymin_type == "dirichlet":
        for key in dom.bc_ymin_values.keys():
            fields[key][0, :] = dom.bc_ymin_values[key]
    if dom.bc_ymax_type == "dirichlet":
        for key in dom.bc_ymax_values.keys():
            fields[key][-1, :] = dom.bc_ymax_values[key]


def apply_bc_neumann(dom, derivx, derivy):
    """Apply boundary condituons with a crude manner."""
    if dom.bc_xmin_type == "neumann":
        for key in dom.bc_xmin_values.keys():
            derivx[key][:, 0] = dom.bc_xmin_values[key]
    if dom.bc_xmax_type == "neumann":
        for key in dom.bc_xmax_values.keys():
            derivx[key][:, -1] = dom.bc_xmax_values[key]
    if dom.bc_ymin_type == "neumann":
        for key in dom.bc_ymin_values.keys():
            derivy[key][0, :] = dom.bc_ymin_values[key]
    if dom.bc_ymax_type == "neumann":
        for key in dom.bc_ymax_values.keys():
            derivy[key][-1, :] = dom.bc_ymax_values[key]


def pressure_poisson(dom, delta_t, periox, perioy):
    """Define Pressure Poisson iterative ffields["vel_u"]_oldction.

    here ggrad_p_x and ggrad_p_y are terms comming from the pressure laplacian
    u_term is the pressure term coming from div_u
    """
    b_press = press_from_div_u(dom, delta_t, periox, perioy)
    eps_old = 1.
    press = dom.fields["press"].copy()
    norm_ref = np.linalg.norm(press)
    for _ in range(40):
        p_old = press.copy()
        ggrad_p_x, ggrad_p_y = scnd_der_2(
            p_old,
            dom.delta_x,
            periox=periox,
            perioy=perioy,
            no_center=True)
        press = (ggrad_p_x + ggrad_p_y - b_press) * dom.delta_x**2 / 4.0
        eps = np.linalg.norm(press-p_old)/norm_ref
        if eps < 1e-3:
            break
        if eps_old > eps:
            break
        eps_old = eps
    press -= press.mean()
    return press


def press_from_div_u(dom, delta_t, periox, perioy):
    """Compute the presure term from velocity divengence."""
    b_press = np.zeros_like(dom.fields["vel_u"])
    gux, guy = grad_2(
        dom.fields["vel_u"],
        dom.delta_x,
        periox=periox,
        perioy=perioy)
    gvx, gvy = grad_2(
        dom.fields["vel_v"],
        dom.delta_x,
        periox=periox,
        perioy=perioy)
    b_press = dom.rho * ((gux + gvy)/delta_t - (gux**2 + 2.0*guy*gvx + gvy**2))
    return b_press
