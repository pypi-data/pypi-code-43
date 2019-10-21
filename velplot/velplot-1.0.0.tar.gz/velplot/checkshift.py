import matplotlib.pyplot as plt
from matplotlib import re

def check_shift(i,dv,table1,table2,header,comment):
    '''
    Check applied shifts, zero or continuum levels in input model.
    '''
    left  = table1[i][2]
    right = table1[i][3]
    
    shift,cont,slope,z,zero = 0,1,0,0,0

    for j in range(len(table2)):

        val = table2[j][0]
        N   = float(re.compile(r'[^\d.-]+').sub('',table2[j][1]))
        z   = float(re.compile(r'[^\d.-]+').sub('',table2[j][2]))
        b   = float(re.compile(r'[^\d.-]+').sub('',table2[j][3]))
        reg = table2[j][4]
        if val==">>" and (reg==i+1 or (reg==0 and left<1215.6701*(z+1)<right)):
            t = plt.text(-.5*dv,-.43,'>> %.5f km/s'%b,color='blue',fontsize=5)
            t.set_bbox(dict(color='white', alpha=0.5, edgecolor=None))        
            shift = -b
        if val=="<>" and (reg==i+1 or (reg==0 and left<1215.6701*(z+1)<right)):
            t = plt.text(-.5*dv,-.28,'<> %.5f'%N,color='blue',fontsize=5)
            t.set_bbox(dict(color='white', alpha=0.5, edgecolor=None))        
            cont  = N
            slope = b
            z     = z
        if val=="__" and (reg==i+1 or (reg==0 and left<1215.6701*(z+1)<right)):
            t = plt.text(-.27*dv,-.28,'__ %.5f'%N,color='blue',fontsize=5)
            t.set_bbox(dict(color='white', alpha=0.5, edgecolor=None))        
            zero = -N

    ''' Insert comments in figure '''

    t1 = plt.text(-.97*dv,-.4,str(header[i,0])+' '+str('%.2f'%float(header[i,1])),color='blue',fontsize=10,ha='left')
    t2 = plt.text(-.1*dv,-.28,' f = %.4f'%float(header[i,2]),color='blue',fontsize=5,ha='left')
    t3 = plt.text(.1*dv,-.28,' $\chi^2_{\mathrm{abs}}$ = '+header[i,-4],color='blue',fontsize=5,ha='left')
    t5 = plt.text(.1*dv,-.43,'npix = '+header[i,-2],color='blue',fontsize=5,ha='left')
    t4 = plt.text(.35*dv,-.28,' $\chi^2_{\mathrm{red}}$ = '+header[i,-3],color='blue',fontsize=5,ha='left')
    t6 = plt.text(.35*dv,-.43,'ndf  = '+header[i,-1],color='blue',fontsize=5,ha='left')
    t7 = plt.text(.97*dv,-.4,str(i+1)+' - '+str(table1[i][0].split('/')[-1]),color='blue',fontsize=7,ha='right')
    for t in [t1,t2,t3,t4,t5,t6,t7]:
        t.set_bbox(dict(color='white', alpha=0.5, edgecolor=None))

    if header[i,4]!='0':
        t = plt.text(-.1*dv,-.43,'q = %.0f'%float(header[i,4]),color='blue',fontsize=5,ha='left')
        t.set_bbox(dict(color='white', alpha=0.5, edgecolor=None))        
    if 'overlap' in comment[i,0]:
        t = plt.text(.97*dv,.3,'Overlapping system:\n'+comment[i,1],color='darkorange',weight='bold',fontsize=6,horizontalalignment='right')
        t.set_bbox(dict(color='white', alpha=0.5, edgecolor=None))        
    if 'external' in comment[i,0]:
        t = plt.text(.97*dv,.3,'External system:\n'+comment[i,1],color='darkorange',weight='bold',fontsize=6,horizontalalignment='right')
        t.set_bbox(dict(color='white', alpha=0.5, edgecolor=None))        
        
    return shift,cont,slope,z,zero
