import numpy
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

def fit_parabola(x,y,xmin=None,xmax=None,ymin=None,ymax=None,plot_range=[None,None],show_text=True):
    """
    Fit parabola to the chi-square curves.
    """
    # Define plotting limits if not specified
    if plot_range==[None,None]: plot_range=[min(x),max(x)]
    # Determine in-window label position
    ymin = 0 if len(y)==0 else min(y)-1 if min(y)==max(y) else min(y) if ymin==None else ymin
    ymax = 1 if len(y)==0 else max(y)+1 if min(y)==max(y) else max(y) if ymax==None else ymax
    xpos = numpy.average(plot_range)
    ypos = ymax-0.05*(ymax-ymin)
    # Define fitting range
    imin = 0  if xmin==None else numpy.where(x>=xmin)[0][0]
    imax = -1 if xmax==None else numpy.where(x<=xmax)[0][-1]+1
    x,y  = x[imin:imax],y[imin:imax]
    x = numpy.array(x,dtype=float)
    y = numpy.array(y,dtype=float)
    # Execute parabolic fit
    A = numpy.vander(x,3)
    (coeffs, residuals, rank, sing_vals) = numpy.linalg.lstsq(A,y,rcond=None)
    f = numpy.poly1d(coeffs)
    # Define fitting variables
    xfit = numpy.arange(-100,100,0.0001)
    imid = abs(f(xfit)-min(f(xfit))).argmin()
    isig = abs(f(xfit)-(min(f(xfit))+1)).argmin()
    xmid = xfit[imid]
    xsig = abs(xfit[isig]-xfit[imid])
    xm1sig = xmid-xsig
    xp1sig = xmid+xsig
    plt.plot(xfit,f(xfit),c='red',lw=1)
    print('Slope: {0:>8}+/-{1:<8}'.format('%.4f'%xmid,'%.4f'%xsig))
    #print('Chisq: {0:>12}'.format(self.residuals))
    plt.axvline(x=xm1sig,ls='dotted',color='blue',lw=1)
    plt.axvline(x=xmid,ls='dashed',color='red',lw=1)
    plt.axvline(x=xp1sig,ls='dotted',color='blue',lw=1)
    if show_text:
        t1 = plt.text(xpos,ypos,r'$\chi^2_\mathrm{min}$ at %.4f $\pm$ %.4f'%(xmid,xsig),
                      color='red',fontsize=10,ha='center',va='top')
        t1.set_bbox(dict(color='white', alpha=0.7, edgecolor=None))
    return xmid,xsig,xm1sig,xp1sig

def fit_linear(x,y,yerr,slope,slope_error,xm1sig,xp1sig,xmin=None,xmax=None,ymin=None,ymax=None,plot_range=[None,None],show_text=True):
    """
    Do linear fit to da/a vs. distortion slope curves.
    """
    # Define plotting limits if not specified
    if plot_range==[None,None]: plot_range=[min(x),max(x)]
    # Determine in-window label position
    xpos = numpy.average(plot_range)
    ypos = ymax-0.05*(ymax-ymin)
    # Define fitting range
    imin = 0 if xmin==None else numpy.where(x>=xmin)[0][0]
    imax = -1 if xmax==None else numpy.where(x<=xmax)[0][-1]+1
    x,y,yerr = x[imin:imax],y[imin:imax],yerr[imin:imax]
    # Execute parabolic fit
    x = numpy.array(x,dtype=float)
    y = numpy.array(y,dtype=float)
    yerr = numpy.array(yerr,dtype=float)
    def func(func,a,b):
        return a + b*x
    pars,cov = curve_fit(func,x,y,sigma=yerr)
    # Define fitting variables
    xfit = numpy.arange(-100,100,0.001)
    yfit = pars[0] + pars[1]*xfit
    plt.plot(xfit,yfit,color='red',lw=1)
    imid = abs(xfit-slope).argmin()
    imin = abs(xfit-(slope-slope_error)).argmin()
    imax = abs(xfit-(slope+slope_error)).argmin()
    plt.axvline(x=xm1sig,ls='dotted',color='blue',lw=1)
    plt.axvline(x=xfit[imid],ls='dashed',color='red',lw=1)
    plt.axvline(x=xp1sig,ls='dotted',color='blue',lw=1)
    plt.axhline(y=yfit[imid],ls='dashed',color='red',lw=1)
    plt.axhline(y=yfit[imax],ls='dotted',color='blue',lw=1)
    plt.axhline(y=yfit[imin],ls='dotted',color='blue',lw=1)
    alpha      = yfit[imid]
    alpha_stat = numpy.average(yerr)
    alpha_syst = abs(yfit[imax]-yfit[imid])
    if show_text:
        t1 = plt.text(xpos,ypos,
                      r'$\Delta\alpha/\alpha$ = %.4f $\pm$ %.4f $\pm$ %.4f'%(yfit[imid],alpha_stat,alpha_syst),
                      color='red',fontsize=10,ha='center',va='top')
        t1.set_bbox(dict(color='white', alpha=0.7, edgecolor=None))
    print('Alpha: {0:>8}+/-{1:<6}+/-{2:<6}'.format('%.4f'%alpha,'%.4f'%alpha_stat,'%.4f'%alpha_syst))
