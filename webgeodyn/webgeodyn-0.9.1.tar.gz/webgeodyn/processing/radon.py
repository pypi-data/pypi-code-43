""" Radon Transform as described in Birkfellner, Wolfgang. Applied Medical Image Processing: A Basic Course. [p. 344] """
from scipy import misc
import numpy as np
import matplotlib.pyplot as plt
from skimage.transform import radon

def discrete_radon_transform(array2D,steps):
    B = np.ones((array2D.shape))
    q = np.linspace(-90., 90., steps, endpoint=True)
    H = radon(array2D, theta=q, circle=False)
    C = radon(B, theta=q, circle=False)
    Cm = np.sum(C**2,axis=0)	#normalization fn
    S = np.sum(H**2,axis=0)/Cm
    return H,S,q

def TL_radon_power_diagram(measure, time, components=["th","ph"]): #par défault components = ["th","ph"] sauf si j'appelle autre chose...
    rE = 6371.2
    rC = 3485.0

    # définir theta ici...
    
    # si realisations, irealisations<0 => prend la moyenne
    # griddata = dictionnaire qui contient les components appelées
    griddata = measure.computeRThetaPhiData(rC,measure.th,measure.ph,components=components,computeallrealisation=False,irealisation=-1)
    output_dict = {}

    radon_steps = 180; #griddata[component].shape[2]
    th1 = measure.th
    lat1 = np.pi/2. - th1
    lat_max=70.*np.pi/180.
    jj=np.argwhere(abs(lat1)<=lat_max)[::5]
    th2 = measure.th[jj]
    nth2 = max(th2.shape)
    print(nth2)
    print("!! normalised radon transform !!")

    for component in components:
        meantimephi = np.mean(griddata[component],axis=(0,2))
        print(component)
        output_dict[component] = np.zeros((nth2,radon_steps))
#        for ith,th in enumerate(measure.th): # boucle sur les colatitudes (theta)
        for ith2,th in enumerate(th2): # boucle sur les colatitudes (theta)
            ith = jj[ith2,0]
            array2D = griddata[component][:,ith,:]
            print(ith2,ith,th*180/np.pi,measure.th[ith]*180/np.pi)
            array2D=array2D-meantimephi[ith]
            [H,S,q] = discrete_radon_transform(array2D,radon_steps)
            rms_array2D = np.linalg.norm(array2D)
#            output_dict[component][ith2,:] = S[:]
            output_dict[component][ith2,:] = S[:]/rms_array2D



    # sortie: dictionnaire de tout le monde

    return output_dict, q, th2
