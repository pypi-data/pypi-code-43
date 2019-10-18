#quanternion converter
#$Id$
import numpy
PI = 3.14159265358979323846
def qtom3(q): #quaternion to 3x3 non-homogeneous rotation matrix
    M = numpy.zeros((3,3),'d')
    s = 2.0/((q[0]*q[0])+(q[1]*q[1])+(q[2]*q[2])+(q[3]*q[3]));
    xs = q[1]*s;
    ys = q[2]*s;
    zs = q[3]*s;
    wx = q[0]*xs;
    wy = q[0]*ys;
    wz = q[0]*zs;
    xx = q[1]*xs;
    xy = q[1]*ys;
    xz = q[1]*zs;
    yy = q[2]*ys;
    yz = q[2]*zs;
    zz = q[3]*zs;

    M[0,0] = 1.0-yy-zz;
    M[0,1] = xy-wz;
    M[0,2] = xz+wy;
    M[1,0] = xy+wz;
    M[1,1] = 1.0-xx-zz;
    M[1,2] = yz-wx;
    M[2,0] = xz-wy;
    M[2,1] = yz+wx;
    M[2,2] = 1.0-xx-yy;
    return(M);
def m3toe(M):
    e = numpy.zeros((3,),'d')
    EPSILON = 0.00001
    sy = -M[2,0];
    cy = 1-(sy*sy);
    if cy > EPSILON:
        cy = numpy.sqrt(cy);
        cx = M[2,2]/cy;
        sx = M[2,1]/cy;
        cz = M[0,0]/cy;
        sz = M[1,0]/cy;
    else:
        cy = 0.0;
        cx = M[1,1];
        sx = -M[1,2];
        cz = 1.0;
        sz = 0.0;

    e[0] = numpy.arctan2(sx, cx);
    e[1] = numpy.arctan2(sy, cy);
    e[2] = numpy.arctan2(sz, cz);
    return(e)
def qtoe(q):
    if q[0]==0:
        e=numpy.zeros(3,'d')
        return(e);
    M = qtom3(q);
    e = m3toe(M);
#    e = e*180.0/PI #convert from radian to degree
    return(e)
#Eulor to M3
def etom3(e):
    M = numpy.zeros((3,3),'d')
    #E0,1,2 = yaw, pitch, roll
    cosmat = numpy.array([numpy.cos(e[2]),numpy.cos(e[1]),numpy.cos(e[0])])
    sinmat = numpy.array([numpy.sin(e[2]),numpy.sin(e[1]),numpy.sin(e[0])])
    
    M[0,0] = cosmat[0]*cosmat[1]
    M[0,1] = cosmat[0]*sinmat[1]*sinmat[2] - sinmat[0]*cosmat[2]
    M[0,2] = cosmat[0]*sinmat[1]*cosmat[2] + sinmat[0]*sinmat[2]
    M[1,0] = sinmat[0]*cosmat[1]
    M[1,1] = sinmat[0]*sinmat[1]*sinmat[2] + cosmat[0]*cosmat[2]
    M[1,2] = sinmat[0]*sinmat[1]*cosmat[2] - cosmat[0]*sinmat[2]
    M[2,0] = - sinmat[1]
    M[2,1] = cosmat[1]*sinmat[2]
    M[2,2] = cosmat[1]*cosmat[2]
    return M
