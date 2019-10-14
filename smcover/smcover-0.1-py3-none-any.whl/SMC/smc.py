from multiprocessing import Pool
import glob

from astropy.io import fits
from astropy.wcs import WCS
import healpy as hp
import numpy as np
import matplotlib.pyplot as plt

"""
FUTURE UPDATES:
 - Work with images that have more than four corners
 - Make pip-able
 - Better outputs
 - Make features robust for automation
 - Have a way of measuring error on the estimates
 - Ideas for other pieces of info
 - Find a way to show area covered per image and total area covered
"""

def get_corners(image):
    """
    Gets corner co-ords of the image.
    
    input: image (fits file)

    --------------------------------------

    output: array of conrner coords
    A = [R1,D1,R2,D2....]
    """

    # Try different fits compression types
    # This will need to be extended for cases that aren't these two
    try:
        H = fits.getheader(image)
        W = WCS(H)
    except:
        H = fits.open(image)[1]._header
        W = WCS(H)

    #Get coords using just the header info
    try:
        R1, D1 =  W.wcs_pix2world(0,0,0) #ZNAXIS1
        R2, D2 =  W.wcs_pix2world(H['ZNAXIS1'],0,0)
        R3, D3 =  W.wcs_pix2world(H['ZNAXIS1'],H['ZNAXIS2'],0)
        R4, D4 =  W.wcs_pix2world(0,H['ZNAXIS2'],0)
    except:
        R1, D1 =  W.wcs_pix2world(0,0,0) #ZNAXIS1
        R2, D2 =  W.wcs_pix2world(H['NAXIS1'],0,0)
        R3, D3 =  W.wcs_pix2world(H['NAXIS1'],H['NAXIS2'],0)
        R4, D4 =  W.wcs_pix2world(0,H['NAXIS2'],0)

    return([R1,D1,R2,D2,R3,D3,R4,D4])

#P = get_corners('2.fits')
#print(P)


 
def plot_coverage(images, skymap1, plot = True):
    """
    Finds the percentage sky coverage

    input: images (either array of images ["1.fits", "2.fits"...] 
                   or "diectory name")

           skymap1 (skyamp fits file)

           plot (if true will create plot of sky coverage)

    -------------------------------------------------------------

    Returns: sky area covered, percentage of probable region
    Optional: plot 
    """

    # Determine if directory or array
    if type(images) == type('string'):
        print('Going into directory '+images)
        Files = glob.glob(images+'/*.fits')
    else:
        Files = images
    ###print(Files)


    # Get corner coords of images
    with Pool(2) as p:
        corners = p.map(get_corners, Files)
        #corners is an list of lists containing
        #the corner co-ords of each input image


    # Set up skymap params 
    prob = 0
    OVERLAP = []
    skymap,  header = hp.read_map(skymap1, h= True)
    header = dict(header)
    NSIDE = header['NSIDE']
    max1 = len(skymap)
    dspp = hp.nside2pixarea(NSIDE, degrees=True) # degrees squared per pixel

    if plot == True:
    #healpy plot 
        hp.mollview(skymap, title = skymap1.replace('.fits',''), coord = 'C', cmap = 'ocean_r', notext = True, xsize = 1000, flip = 'geo')
        hp.visufunc.graticule(dpar = 15, dmer = 30)


        # This chunk exists as healpy doesn't plot an axis yet #
        PD = np.linspace(-180,180, 7) #Split of declination postions for plotting axis
        PR = np.linspace(0, 120, 9) # Split of RA pos for plotting axis
        for i in range (len(PD)-1):
            hp.visufunc.projtext(-180, PR[i], '%s  ' %int(PR[i]) , lonlat= True, fontsize = 10,  horizontalalignment = 'right')
            hp.visufunc.projtext(PD[i]-1, -8.5, '   %s' %int(PD[i]) , lonlat= True, fontsize = 10, horizontalalignment = 'center')
        
        #########

    # Use coords to find sky area and probable region
    for i in range(len(corners)):
        VERT = [hp.pix2vec(NSIDE, hp.ang2pix(NSIDE, corners[i][0], corners[i][1] , lonlat=True)),
                hp.pix2vec(NSIDE, hp.ang2pix(NSIDE, corners[i][2], corners[i][3], lonlat=True)),
                hp.pix2vec(NSIDE, hp.ang2pix(NSIDE, corners[i][4], corners[i][5], lonlat=True)),
                hp.pix2vec(NSIDE, hp.ang2pix(NSIDE, corners[i][6], corners[i][7], lonlat=True))]

        #Plots the area of the image 
        if plot == True:
            for X in range(4):
                if X+1 != 4:
                    x_lin = np.linspace(corners[i][X*2], corners[i][(X+1)*2]+0.00000000000001, 100)
                    y_lin = np.linspace(corners[i][(X*2)+1], corners[i][(X*2)+3]+0.00000000000001, 100)
                else:
                    x_lin = np.linspace(corners[i][X*2], corners[i][0]+0.00000000000001, 100)
                    y_lin = np.linspace(corners[i][(X*2)+1], corners[i][1]+0.00000000000001, 100)
                hp.visufunc.projplot([x_lin,y_lin], color = 'purple', lw=0.55, lonlat=True)
        #############


        ### Work out probability
        TMP_List = hp.query_polygon(NSIDE,VERT)
        OVERLAP.extend(TMP_List)
        if skymap1 != False:
            prob += sum(skymap[TMP_List])
            skymap[TMP_List] = 0


    prob = prob*100 #convert to percentage
    Area = len(list(set(OVERLAP))) * dspp #Total sky area covered acounting for overlap

    if plot == True:
        hp.visufunc.projtext(-15, -70 , '                                          Prob = %s %%' %round(prob*100,2),
                             color = 'black', fontsize = 15, lonlat=True)
        hp.visufunc.projtext(0 ,-90 , '                             Area = %s$°^2$ ' %round(Area,2),
                             color = 'black', fontsize = 15, lonlat=True)
        plt.savefig('sky_cover.png')
        #plt.show()




    print(Area)
    print(prob)

    # TODO #
    #return(Area, prob, sky_cover.png)

#plot_coverage('Directory', 'S190814bv.fits')
#plot_coverage(['1.fits','2.fits','3.fits','4.fits','5.fits'], 'S190814bv.fits')



    


