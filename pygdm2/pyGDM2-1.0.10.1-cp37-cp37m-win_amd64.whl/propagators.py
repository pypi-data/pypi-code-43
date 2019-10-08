# encoding: utf-8
#
#Copyright (C) 2019, P. R. Wiecha
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
"""
python implementations of the propagators, accelerated using `numba`
"""
from __future__ import print_function
from __future__ import absolute_import

import copy

import numpy as np
import math
import cmath
import numba
from numba import cuda


# =============================================================================
# numba compatible propagators (CPU)
# =============================================================================
## --- free space propagator
@numba.njit(cache=True)
def G0(R1, R2, lamda, cnorm, step, eps):
    Dx = R2[0] - R1[0]
    Dy = R2[1] - R1[1]
    Dz = R2[2] - R1[2]
    lR = np.sqrt(Dx**2 + Dy**2 + Dz**2)
    
    if lR == 0:
        ## --- "self" term
        xx = cnorm
        yy = cnorm
        zz = cnorm
        xy = 0
        xz = 0
        yz = 0
    else:
        ## --- coupling 2 dipoles
        k = 2*np.pi / lamda
        cn2 = np.sqrt(eps)
        ck0 = -1j * k * cn2
        k2 = k*k*eps
        
        r25 = np.power((Dx*Dx+Dy*Dy+Dz*Dz), 2.5)
        r2 = np.power((Dx*Dx+Dy*Dy+Dz*Dz), 2.0)
        r15 = np.power((Dx*Dx+Dy*Dy+Dz*Dz), 1.5)
        
#!C-------------------------------------------------------------------
        T1XX = (2*Dx*Dx-Dy*Dy-Dz*Dz) / r25
        T2XX = (2*Dx*Dx-Dy*Dy-Dz*Dz) / r2
        T3XX = -1*(Dy*Dy+Dz*Dz) / r15
#!C-------------------------------------------------------------------
        T1XY = 3*Dx*Dy / r25
        T2XY = 3*Dx*Dy / r2
        T3XY = Dx*Dy / r15
#!C-------------------------------------------------------------------
        T1XZ = 3*Dx*Dz / r25
        T2XZ = 3*Dx*Dz / r2
        T3XZ = Dx*Dz / r15
#!C-------------------------------------------------------------------
        T1YY = (2*Dy*Dy-Dx*Dx-Dz*Dz) / r25
        T2YY = (2*Dy*Dy-Dx*Dx-Dz*Dz) / r2
        T3YY = -(Dx*Dx+Dz*Dz) / r15
#!C-------------------------------------------------------------------
        T1YZ = 3*Dy*Dz / r25
        T2YZ = 3*Dy*Dz / r2
        T3YZ = Dy*Dz / r15
#!C------------------------------------------------------------------
        T1ZZ = (2*Dz*Dz-Dx*Dx-Dy*Dy) / r25
        T2ZZ = (2*Dz*Dz-Dx*Dx-Dy*Dy) / r2
        T3ZZ = -(Dx*Dx+Dy*Dy) / r15
        
        CFEXP = np.exp(1j*k*cn2*lR)
        
        xx = CFEXP*(T1XX+ck0*T2XX-k2*T3XX)/eps
        yy = CFEXP*(T1YY+ck0*T2YY-k2*T3YY)/eps
        zz = CFEXP*(T1ZZ+ck0*T2ZZ-k2*T3ZZ)/eps
        
        xy = CFEXP*(T1XY+ck0*T2XY-k2*T3XY)/eps
        xz = CFEXP*(T1XZ+ck0*T2XZ-k2*T3XZ)/eps
        
        yz = CFEXP*(T1YZ+ck0*T2YZ-k2*T3YZ)/eps
        
    yx = xy
    zx = xz
    zy = yz
    
    return xx, yy, zz, xy, xz, yx, yz, zx, zy


## --- "1-2-3" slab propagator, via method of mirror charges for 2 surfaces
@numba.njit(cache=True)
def Gs123(R1, R2, lamda, step, eps1, eps2, eps3, spacing):
    Dx = R2[0] - R1[0]
    Dy = R2[1] - R1[1]
    Dz = R2[2] + R1[2]
    
    cdelta12 = (eps1-eps2)/(eps1+eps2)
    cdelta23 = (eps3-eps2)/(eps3+eps2)
    
#!************* Interface: (1,2) *******************************
    r25 = np.power((Dx*Dx+Dy*Dy+Dz*Dz), 2.5)
     
    SXX12 = cdelta12*(Dz*Dz+Dy*Dy-2*Dx*Dx) / r25
    SYY12 = cdelta12*(Dz*Dz+Dx*Dx-2*Dy*Dy) / r25
    SZZ12 = cdelta12*(2*Dz*Dz-Dx*Dx-Dy*Dy) / r25
    SXY12 = cdelta12*(-3*Dx*Dy) / r25
    SXZ12 = cdelta12*(3*Dx*Dz) / r25
    SYZ12 = cdelta12*(3*Dy*Dz) / r25

#!************* Interface: (2,3) *******************************
    GZ = Dz - 2*spacing
    rgz25 = np.power((Dx*Dx+Dy*Dy+GZ*GZ), 2.5)
    
    SXX23 = cdelta23*(GZ*GZ+Dy*Dy-2*Dx*Dx) / rgz25
    SYY23 = cdelta23*(GZ*GZ+Dx*Dx-2*Dy*Dy) / rgz25
    SZZ23 = cdelta23*(2*GZ*GZ-Dx*Dx-Dy*Dy) / rgz25
    SXY23 = cdelta23*(-3*Dx*Dy) / rgz25
    SXZ23 = cdelta23*(3*Dx*GZ) / rgz25
    SYZ23 = cdelta23*(3*Dy*GZ) / rgz25
#!**************************************************************
    
    xx = SXX12+SXX23
    yy = SYY12+SYY23
    zz = SZZ12+SZZ23
    
    xy = SXY12+SXY23
    xz = SXZ12+SXZ23
    
    yx = xy
    yz = SYZ12+SYZ23
    
    zx = -1*xz
    zy = -1*yz
    
    return xx, yy, zz, xy, xz, yx, yz, zx, zy


## --- the propagator: vacuum + surface term
@numba.njit(cache=True)
def G(R1, R2, lamda, cnorm, step, eps1, eps2, eps3, spacing):
    xx, yy, zz, xy, xz, yx, yz, zx, zy = G0(R1, R2, lamda, cnorm, step, eps2)
    xxs,yys,zzs,xys,xzs,yxs,yzs,zxs,zys = Gs123(R1, R2, lamda, step, 
                                                eps1, eps2, eps3, spacing)
    
    return xx+xxs, yy+yys, zz+zzs, \
           xy+xys, xz+xzs, yx+yxs, \
           yz+yzs, zx+zxs, zy+zys


## --- coupling matrix generator
@numba.njit(parallel=True, cache=True)
def t_sbs(geo, lamda, cnorm, step, eps1, eps2, eps3, spacing, alpha, M):
    for i in numba.prange(len(geo)):    # explicit parallel loop
        R1 = geo[i]
        for j in range(len(geo)):
            R2 = geo[j]
            aj = alpha[j]
            xx, yy, zz, xy, xz, yx, yz, zx, zy = G(R1, R2, lamda, 
                                       cnorm, step, eps1, eps2, eps3, spacing)
            
            ## return invertible matrix:  delta_ij*1 - G[i,j] * alpha[j]
            M[3*i+0, 3*j+0] = -1*(xx*aj[0,0] + xy*aj[1,0] + xz*aj[2,0])
            M[3*i+1, 3*j+1] = -1*(yx*aj[0,1] + yy*aj[1,1] + yz*aj[2,1])
            M[3*i+2, 3*j+2] = -1*(zx*aj[0,2] + zy*aj[1,2] + zz*aj[2,2])
            M[3*i+1, 3*j+0] = -1*(xx*aj[0,1] + xy*aj[1,1] + xz*aj[2,1])
            M[3*i+2, 3*j+0] = -1*(xx*aj[0,2] + xy*aj[1,2] + xz*aj[2,2])
            M[3*i+0, 3*j+1] = -1*(yx*aj[0,0] + yy*aj[1,0] + yz*aj[2,0])
            M[3*i+2, 3*j+1] = -1*(yx*aj[0,2] + yy*aj[1,2] + yz*aj[2,2])
            M[3*i+0, 3*j+2] = -1*(zx*aj[0,0] + zy*aj[1,0] + zz*aj[2,0])
            M[3*i+1, 3*j+2] = -1*(zx*aj[0,1] + zy*aj[1,1] + zz*aj[2,1])
            if i==j:
                M[3*i+0, 3*j+0] += 1
                M[3*i+1, 3*j+1] += 1
                M[3*i+2, 3*j+2] += 1




# =============================================================================
# CUDA compatible versions of propagators
# =============================================================================
## --- free space propagator
@numba.njit(cache=True)
def G0_cuda(R1, R2, lamda, cnorm, step, eps):
    Dx = R2[0] - R1[0]
    Dy = R2[1] - R1[1]
    Dz = R2[2] - R1[2]
    lR = math.sqrt(Dx**2 + Dy**2 + Dz**2)
    
    if lR == 0:
        ## --- "self" term
        xx = cnorm
        yy = cnorm
        zz = cnorm
        xy = 0
        xz = 0
        yz = 0
    else:
        ## --- coupling 2 dipoles
        k = 2*np.pi / lamda
        cn2 = cmath.sqrt(eps)
        ck0 = -1j * k * cn2
        k2 = k*k*eps
        
        r25 = math.pow((Dx*Dx+Dy*Dy+Dz*Dz), 2.5)
        r2 = math.pow((Dx*Dx+Dy*Dy+Dz*Dz), 2.0)
        r15 = math.pow((Dx*Dx+Dy*Dy+Dz*Dz), 1.5)
        
#!C-------------------------------------------------------------------
        T1XX = (2*Dx*Dx-Dy*Dy-Dz*Dz) / r25
        T2XX = (2*Dx*Dx-Dy*Dy-Dz*Dz) / r2
        T3XX = -1*(Dy*Dy+Dz*Dz) / r15
#!C-------------------------------------------------------------------
        T1XY = 3*Dx*Dy / r25
        T2XY = 3*Dx*Dy / r2
        T3XY = Dx*Dy / r15
#!C-------------------------------------------------------------------
        T1XZ = 3*Dx*Dz / r25
        T2XZ = 3*Dx*Dz / r2
        T3XZ = Dx*Dz / r15
#!C-------------------------------------------------------------------
        T1YY = (2*Dy*Dy-Dx*Dx-Dz*Dz) / r25
        T2YY = (2*Dy*Dy-Dx*Dx-Dz*Dz) / r2
        T3YY = -(Dx*Dx+Dz*Dz) / r15
#!C-------------------------------------------------------------------
        T1YZ = 3*Dy*Dz / r25
        T2YZ = 3*Dy*Dz / r2
        T3YZ = Dy*Dz / r15
#!C------------------------------------------------------------------
        T1ZZ = (2*Dz*Dz-Dx*Dx-Dy*Dy) / r25
        T2ZZ = (2*Dz*Dz-Dx*Dx-Dy*Dy) / r2
        T3ZZ = -(Dx*Dx+Dy*Dy) / r15
        
        CFEXP = cmath.exp(1j*k*cn2*lR)
        
        xx = CFEXP*(T1XX+ck0*T2XX-k2*T3XX)/eps
        yy = CFEXP*(T1YY+ck0*T2YY-k2*T3YY)/eps
        zz = CFEXP*(T1ZZ+ck0*T2ZZ-k2*T3ZZ)/eps
        
        xy = CFEXP*(T1XY+ck0*T2XY-k2*T3XY)/eps
        xz = CFEXP*(T1XZ+ck0*T2XZ-k2*T3XZ)/eps
        
        yz = CFEXP*(T1YZ+ck0*T2YZ-k2*T3YZ)/eps
        
    yx = xy
    zx = xz
    zy = yz
    
    return xx, yy, zz, xy, xz, yx, yz, zx, zy



## --- "1-2-3" slab propagator, via method of mirror charges for 2 surfaces
@numba.njit(cache=True)
def Gs123_cuda(R1, R2, lamda, step, eps1, eps2, eps3, spacing):
    Dx = R2[0] - R1[0]
    Dy = R2[1] - R1[1]
    Dz = R2[2] + R1[2]
    
    cdelta12=(eps1-eps2)/(eps1+eps2)
    cdelta23=(eps3-eps2)/(eps3+eps2)
    
    r25 = math.pow((Dx*Dx+Dy*Dy+Dz*Dz), 2.5)
     
#!************* Interface: (1,2) *******************************
    SXX12 = cdelta12*(Dz*Dz+Dy*Dy-2*Dx*Dx) / r25
    SYY12 = cdelta12*(Dz*Dz+Dx*Dx-2*Dy*Dy) / r25
    SZZ12 = cdelta12*(2*Dz*Dz-Dx*Dx-Dy*Dy) / r25
    SXY12 = cdelta12*(-3*Dx*Dy) / r25
    SXZ12 = cdelta12*(3*Dx*Dz) / r25
    SYZ12 = cdelta12*(3*Dy*Dz) / r25

#!************* Interface: (2,3) *******************************
    GZ = Dz - 2*spacing
    rgz25 = math.pow((Dx*Dx+Dy*Dy+GZ*GZ), 2.5)
    
    SXX23 = cdelta23*(GZ*GZ+Dy*Dy-2*Dx*Dx) / rgz25
    SYY23 = cdelta23*(GZ*GZ+Dx*Dx-2*Dy*Dy) / rgz25
    SZZ23 = cdelta23*(2*GZ*GZ-Dx*Dx-Dy*Dy) / rgz25
    SXY23 = cdelta23*(-3*Dx*Dy) / rgz25
    SXZ23 = cdelta23*(3*Dx*GZ) / rgz25
    SYZ23 = cdelta23*(3*Dy*GZ) / rgz25
#!**************************************************************
    
    xx = SXX12+SXX23
    yy = SYY12+SYY23
    zz = SZZ12+SZZ23
    
    xy = SXY12+SXY23
    xz = SXZ12+SXZ23
    
    yx = xy
    yz = SYZ12+SYZ23
    
    zx = -1*xz
    zy = -1*yz
    
    return xx, yy, zz, xy, xz, yx, yz, zx, zy


## --- the propagator: vacuum + surface term
@numba.njit(cache=True)
def G_cuda(R1, R2, lamda, cnorm, step, eps1, eps2, eps3, spacing):
    xx, yy, zz, xy, xz, yx, yz, zx, zy = G0_cuda(R1, R2, lamda, cnorm, step, eps2)
    xxs,yys,zzs,xys,xzs,yxs,yzs,zxs,zys = Gs123_cuda(R1, R2, lamda, step, 
                                                eps1, eps2, eps3, spacing)
    
    return xx+xxs, yy+yys, zz+zzs, \
           xy+xys, xz+xzs, yx+yxs, \
           yz+yzs, zx+zxs, zy+zys


