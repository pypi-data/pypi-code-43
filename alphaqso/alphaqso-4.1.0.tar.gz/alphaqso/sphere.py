import numpy,math

def dist2dip(qsoname):
    """
    Determine distance to dipole from specific quasar.

    Parameters
    ----------
    qsoname : string
      J2000 name of the quasar object
    
    Returns
    -------
    zem : float
      Emission redshift of the quasar
    ra : float
      Right Ascension
    dec : float
      Declinaison
    distance : float
      Distance to dipole from quasar object
    """
    idx = numpy.where(qsolist['name']==qsoname)[0][0]
    val = qsolist['RA\n(hh:mm:ss)'][idx].split(':')
    ra  = float(val[0])+float(val[1])/60+float(val[2])/3600         # in hours
    val = qsolist['DEC\n(dd:mm:ss)'][idx].split(':')
    if (val[0][0]=='-'):
        dec = float(val[0])-float(val[1])/60-float(val[2])/3600     # in degrees
    else:
        dec = float(val[0])+float(val[1])/60+float(val[2])/3600     # in degrees
    zem  = float(qsolist['z_em'][idx])
    # Dot product using spherical coordinates phi and theta in radians
    xdipole  = alphara*360/24.    # in degrees
    ydipole  = alphadec           # in degrees
    distance = spheredist(ra*360/24.,dec,xdipole,ydipole)
    return zem,ra,dec,distance

def spheredist(ra1,dec1,ra2,dec2):
    """
    Calculate spherical distance between 2 points.

    Parameters
    ----------
    ra1 : float
      Right ascension of the first object
    ded1 : float
      Declinaison of the first object
    ra2 : float
      Right ascension of the second object
    ded2 : float
      Declinaison of the seconds object

    Returns
    -------
    distance : float
      spherical distance between the 2 objects
    """
    theta1   = ra1*math.pi/180
    phi1     = math.pi/2-dec1*math.pi/180
    x1       = math.sin(phi1)*math.cos(theta1)
    y1       = math.sin(phi1)*math.sin(theta1)    
    z1       = math.cos(phi1)
    theta2   = ra2*math.pi/180
    phi2     = math.pi/2-dec2*math.pi/180
    x2       = math.sin(phi2)*math.cos(theta2)
    y2       = math.sin(phi2)*math.sin(theta2)    
    z2       = math.cos(phi2)
    distance = math.acos(x1*x2+y1*y2+z1*z2)
    distance = distance*180/math.pi
    return distance

