import numpy as np
from pymatgen.core.lattice import Lattice

eV2GPa = 160.217
GPa2eV = 1.0/eV2GPa

"""
Scripts to compute LJ energy and force
"""

def get_neighbors(struc, i, rcut):
    """
    script to get the neighbors info for an atom in the struct
    """
    lat = struc.lattice_matrix
    center = struc.cart_coords[i]
    c1 = struc.frac_coords[i]
    fcoords = struc.frac_coords
    r, dists, inds, images = Lattice(lat).get_points_in_sphere(
            fcoords, center=center, r=rcut, zip_results=False)
    ids = np.where(dists>1e-2)
    r = r[ids] 
    r = np.dot(r, lat) - center
    return dists[ids]**2, r


class LJ():
    """
    LJ model for 3D crystals, maybe extended to 0D, 1D, 2D later
    """
    def __init__(self, epsilon=1.0, sigma=1.0, rcut=8.0):
        """
        passing the parameter to LJ model
        - epsilon
        - sigma
        - rcut
        """

        self.epsilon = epsilon
        self.sigma = sigma
        self.rcut = rcut

    def calc(self, struc, press=1e-4):
        pos = struc.cart_coords
        lat = struc.lattice_matrix
        volume = np.linalg.det(lat)

        # initiate the energy, force, stress
        energy = 0
        force = np.zeros([len(pos), 3])
        stress = np.zeros([3, 3])
        sigma6 = self.sigma**6
        sigma12 = sigma6*sigma6

        # calculating the energy/force, needs to update sigma/epsilons
        for i, pos0 in enumerate(pos):
            [r2, r] = get_neighbors(struc, i, self.rcut)
            r6 = np.power(r2, 3)     
            r12 = np.power(r6, 2)
            energy += np.sum(4.0*self.epsilon*(sigma12/r12 - sigma6/r6))
            f = (24*self.epsilon*(2.0*sigma12/r12-sigma6/r6)/r2)[:, np.newaxis] * r
            force[i] = f.sum(axis=0)
            stress += np.dot(f.T, r)

        energy = 0.5*energy    
        enthalpy = energy + press*volume*GPa2eV
        force = force
        stress = -0.5*stress/volume*eV2GPa
        #print(force)
        return energy, enthalpy, force, stress

if __name__ == "__main__":
    from pyxtal.crystal import random_crystal
    """
    A test on the Argon fcc crystal
    from gulp 
    lennard
    Ar Ar 100298.645 64.3565 0.0 10.0 
    the reference energy is -0.34294999 eV

    our output is -0.3428445828199249
    This is perhaps due to the conversion of units
    """
    L = 5.265420
    crystal = random_crystal(19, ['C'], [4], 1.0)
    crystal.lattice_matrix = np.eye(3)*L
    crystal.frac_coords = np.array([[0,0,0],[0.5,0.5,0],[0.5,0,0.5],[0,0.5,0.5]])
    crystal.cart_coords = L*np.array([[0,0,0],[0.5,0.5,0],[0.5,0,0.5],[0,0.5,0.5]])

    energy, enthalpy, force, stress = LJ(epsilon=0.010320394, sigma=3.405, rcut=10.0).calc(crystal)
    print(energy)

