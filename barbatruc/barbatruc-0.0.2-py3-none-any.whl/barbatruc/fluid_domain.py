"""Module to define a fluid domain and the configurations associated"""

import numpy as np
import matplotlib.pyplot as plt


__all__ = ["DomainRectFluid", "blur"]

#pylint: disable=too-many-instance-attributes
class DomainRectFluid():
    """docstring for Domain"""

    #pylint: disable=too-many-arguments
    def __init__(
            self,
            dimx=0.82,
            dimy=0.6,
            delta_x=0.02,
            rho=1.12,
            nu_=1.0):
        """Startup class"""
        n_nodes_x = int(dimx/delta_x)
        n_nodes_y = int(dimy/delta_x)
        self.dims = (n_nodes_y*delta_x, n_nodes_x*delta_x)
        self.shape = (n_nodes_y, n_nodes_x)
        self.delta_x = delta_x

        self.fields = dict()
        self.source = dict()
        for field in ["vel_u", "vel_v", "scal"]:
            self.fields[field] = np.zeros(self.shape)
            self.source[field] = np.zeros(self.shape)

        self.fields["press"] = np.ones(self.shape)*1.0
        self.obstacle = np.zeros(self.shape)

        self.rho = rho
        self.nu_ = nu_

        self.bc_xmax_type = "Perio"
        self.bc_xmax_values = dict()
        self.bc_xmin_type = "Perio"
        self.bc_xmin_values = dict()
        self.bc_ymax_type = "Perio"
        self.bc_ymax_values = dict()
        self.bc_ymin_type = "Perio"
        self.bc_ymin_values = dict()

    def bcx_inlet_uv_outlet_p(self, val_u=20.0, val_v=0.0):
        """ set to a dirichlet vel_u, vel_v."""
        self.bc_xmin_type = "dirichlet"
        self.bc_xmin_values = {"vel_u": val_u, "vel_v": val_v, "scal": 0.}

    def bcx_perio(self):
        """ set to a x-periodic domain."""
        self.bc_xmax_type = "Perio"
        self.bc_xmax_values = dict()
        self.bc_xmin_type = "Perio"
        self.bc_xmin_values = dict()

    def bcx_closed(self):
        """ set to a x no slip wall-wall domain."""
        self.bc_xmax_type = "dirichlet"
        self.bc_xmax_values = {"vel_u": 0., "vel_v": 0.}
        self.bc_xmin_type = "dirichlet"
        self.bc_xmin_values = {"vel_u": 0., "vel_v": 0.}

    def bcy_perio(self):
        """ set to a y-periodic domain."""
        self.bc_ymax_type = "Perio"
        self.bc_ymax_values = dict()
        self.bc_ymin_type = "Perio"
        self.bc_ymin_values = dict()

    def bcy_lid_driven(self, vel_u=20.):
        """Set to lowaer y wall, and a upper y moving wall."""
        self.bc_ymax_type = "dirichlet"
        self.bc_ymax_values = {"vel_u": vel_u, "vel_v": 0.}
        self.bc_ymin_type = "dirichlet"
        self.bc_ymin_values = {"vel_u": 0., "vel_v": 0.}

    def bcy_noslip_channel(self):
        """Set to a dy noslip wall-wall."""
        self.bc_ymax_type = "dirichlet"
        self.bc_ymax_values = {"vel_u": 0., "vel_v": 0.}
        self.bc_ymin_type = "dirichlet"
        self.bc_ymin_values = {"vel_u": 0., "vel_v": 0.}

    def bcy_slip_channel(self):
        """Set to a dy slip wall-wall."""
        self.bc_ymax_type = "dirichlet"
        self.bc_ymax_values = {"vel_v": 0.}
        self.bc_ymin_type = "dirichlet"
        self.bc_ymin_values = {"vel_v": 0.}

    def perio_xy(self):
        """Return x and y Periodicities booleans."""
        if "Perio" in [self.bc_xmax_type, self.bc_xmin_type]:
            if self.bc_xmax_type != self.bc_xmax_type:
                raise RuntimeError("One mismatched perio in x-direction")

        if "Perio" in [self.bc_ymax_type, self.bc_ymin_type]:
            if self.bc_ymax_type != self.bc_ymin_type:
                raise RuntimeError("One mismatched perio in x-direction")
        periox = False
        perioy = False
        if self.bc_xmax_type == "Perio":
            periox = True
        if self.bc_ymax_type == "Perio":
            perioy = True

        return periox, perioy

    def coord_matrix(self):
        """Compute coordiantes matrix."""
        x_coor = np.ones(self.shape) * np.linspace(
            0, self.dims[1], self.shape[1])[np.newaxis, :]
        y_coor = np.ones(self.shape) * np.linspace(
            0, self.dims[0], self.shape[0])[:, np.newaxis]
        return x_coor, y_coor

    def add_obstacle_circle(self, x_c=None, y_c=None, radius=None):
        """Add cicular obstacle.

        x_c = x center in m
        y_c = y center in m
        radius = radius in meters
        """
        if x_c is None:
            x_c = 0.3 * self.dims[1]
        if y_c is None:
            y_c = 0.5 * self.dims[0]
        if radius is None:
            radius = 0.1 * self.dims[0]
        x_coor, y_coor = self.coord_matrix()
        radius_field = np.hypot(x_coor - x_c, y_coor - y_c)
        self.obstacle = np.where(radius_field < radius, 1., self.obstacle)

    def add_obstacle_rect(self, ll_x=None, ll_y=None, ur_x=None, ur_y=None):
        """Add rectangular obstacle.

        ll_x = lower left x
        ll_y = lower left y
        ll_x = upper right x
        ll_y = upper right y
        """
        if ll_x is None:
            ll_x = 0.2 * self.dims[1]
        if ll_y is None:
            ll_y = 0.4 * self.dims[0]
        if ur_x is None:
            ur_x = 0.4 * self.dims[1]
        if ur_y is None:
            ur_y = 0.6 * self.dims[0]

        x_coor, y_coor = self.coord_matrix()
        rect_field = np.ones(self.shape)

        rect_field = np.where(x_coor < ll_x, 0., rect_field)
        rect_field = np.where(x_coor > ur_x, 0., rect_field)
        rect_field = np.where(y_coor < ll_y, 0., rect_field)
        rect_field = np.where(y_coor > ur_y, 0., rect_field)

        self.obstacle = np.maximum(rect_field, self.obstacle)

    def nullify_on_obstacle(self, field):
        """Nullify a field where the obstacle is defined."""
        return np.where(self.obstacle > 0., 0., field)

    def show_fields(self):
        """Show the 4 fields in a 4 graph panel."""
        x_linp1 = np.linspace(0, self.dims[1], self.shape[1]+1)
        y_linp1 = np.linspace(0, self.dims[0], self.shape[0]+1)
        max_vel = max(
            self.fields["vel_u"].max(),
            self.fields["vel_v"].max(),
            -self.fields["vel_u"].min(),
            -self.fields["vel_v"].min(), )

        fig = plt.figure()
        ax1 = fig.add_subplot(221)
        ax1.set_title('velu')
        plt.pcolormesh(
            x_linp1,
            y_linp1,
            self.fields["vel_u"],
            vmin=-max_vel,
            vmax=max_vel,
            cmap="bwr")
        plt.colorbar()
        ax1.set_aspect('equal')
        ax2 = fig.add_subplot(222)
        ax2.set_title('velv')
        ax2.set_aspect('equal')
        plt.pcolormesh(
            x_linp1,
            y_linp1,
            self.fields["vel_v"],
            vmin=-max_vel,
            vmax=max_vel,
            cmap="bwr")
        ax3 = fig.add_subplot(223)
        ax3.set_title('press')
        ax3.set_aspect('equal')
        plt.pcolormesh(
            x_linp1,
            y_linp1,
            self.fields["press"],
            cmap="Greys")
        plt.colorbar()
        ax4 = fig.add_subplot(224)
        ax4.set_title('scal')
        ax4.set_aspect('equal')
        plt.pcolormesh(
            x_linp1,
            y_linp1,
            self.fields["scal"],
            cmap="YlGn")
        plt.colorbar()
        plt.show()

    def show_flow(self):
        """Show the flow with magnitude and streamlines."""
        magv = np.hypot(self.fields["vel_u"], self.fields["vel_v"])

        x_lin = np.linspace(0, self.dims[1], self.shape[1])
        y_lin = np.linspace(0, self.dims[0], self.shape[0])

        x_linp1 = np.linspace(0, self.dims[1], self.shape[1]+1)
        y_linp1 = np.linspace(0, self.dims[0], self.shape[0]+1)

        plt.pcolormesh(x_linp1, y_linp1, magv, cmap="jet")
        plt.colorbar()
        plt.streamplot(
            x_lin,
            y_lin,
            self.fields["vel_u"],
            self.fields["vel_v"],
            density=[0.5, 1])
        plt.show()


def blur(arr_):
    """Apply a gather scater smothing to an array.

    Probably something smarted already exists in numpy/scipy.
    If someone find ...
    """
    kernel = np.array(
        [[1.0, 2.0, 1.0],
         [2.0, 4.0, 2.0],
         [1.0, 2.0, 1.0]])
    kernel = kernel / np.sum(kernel)
    arraylist = []
    for y_i in range(3):
        temparray = np.copy(arr_)
        temparray = np.roll(temparray, y_i - 1, axis=0)
        for x_i in range(3):
            temparray_x = np.copy(temparray)
            temparray_x = np.roll(temparray_x, x_i - 1, axis=1)*kernel[y_i, x_i]
            arraylist.append(temparray_x)
    arraylist = np.array(arraylist)
    arraylist_sum = np.sum(arraylist, axis=0)
    return arraylist_sum
