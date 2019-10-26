c = 299792.458
outliers = ['J194454+770552/2.84330/HIRES_sargent',
            'J220852-194400/1.01720/HIRES_sargent',
            'J220852-194400/2.07620/HIRES_sargent',
            'J000448-415728/1.54190/UVES_squader']

#home        = os.getenv('HOME')+'/ASTRO/analysis/alpha'
#home        = os.getenv('HOME')+'/Volumes/ASTRO_HOME/ASTRO/analysis/alpha' if '--server'   in sys.argv else home
#home        = '/media/removable/ASTRO/analysis/alpha'                      if '--external' in sys.argv else home
#home        = '/short/gd5/ASTRO/analysis/alpha'                            if '--raijin'   in sys.argv else home
#alphapath   = '/home/561/vxd561/ASTRO/code/'                               if '--raijin'   in sys.argv else ''
#vpfitpath   = '/home/561/vxd561/ASTRO/code/vpfit10/'                       if '--raijin'   in sys.argv else ''
#fitdir      = home+'/systems/'
#wdrep       = home+'/systems/G191-B2B/'
#Crep        = home+'/dipole/'
#Rrep        = home+'/alpha_analysis/'
#rundir      = home+'/runs/'
#uveshead    = home+'/headers/'
#compdir     = home+'/multiplots/compare/'
#here        = os.getenv('PWD')
#pathdata    = os.path.abspath(__file__).rsplit('/',1)[0] + '/data/'
#pathdata    = os.path.dirname(os.path.realpath(__file__)) + '/data/'
#skipabs     = []
#discard     = []
#keck        = ['HIRES_churchill','HIRES_sargent','HIRES_prochaska','HIRES_outram']
#vlt         = ['UVES_squader']
#murphy      = ['HIRES_murphy_A','HIRES_murphy_B1','HIRES_murphy_B2','HIRES_murphy_C']
#degensys    = ['J111113-080402/3.60770/UVES_squader',
#                 'J034943-381031/3.02470/HIRES_prochaska']
#badwhit     = ['J200324-325145/2.03290/UVES_squader']
#clippeduves = ['J104032-272749/1.38610/UVES_squader',
#                 'J010311+131617/2.30920/UVES_squader',
#                 'J234628+124900/2.17130/UVES_squader',
#                 'J010311+131617/1.79750/UVES_squader',
#                 'J044017-433308/2.04820/UVES_squader',
#                 'J055246-363727/1.74750/UVES_squader',
#                 'J040718-441014/2.59480/UVES_squader']
#done       = False
#alphara    = 17.3
#alphadec   = -61
#uvesblue   = 3900.
#uvesred    = 5800.
#zsample    = 'all'
#zcut       = 1.6
#wd_slope   = numpy.arange(-15,15.1,0.1)
#hires_amp  = numpy.arange(0,400,50)
#args         = numpy.array(sys.argv, dtype='str')
#slope      = 0    if '--slope'    not in sys.argv else float(args[numpy.where(args=='--slope'   )[0][0]+1])
#minslope   = None if '--minslope' not in sys.argv else float(args[numpy.where(args=='--minslope')[0][0]+1])
#maxslope   = None if '--maxslope' not in sys.argv else float(args[numpy.where(args=='--maxslope')[0][0]+1])
#step       = None if '--step'     not in sys.argv else float(args[numpy.where(args=='--step'    )[0][0]+1])
#operation  = None if len(sys.argv)==1 else sys.argv[1]
#clean      = '--clean'     in sys.argv
#compress   = '--compress'  in sys.argv
#constrain  = '--constrain' in sys.argv
#display    = '--display'   in sys.argv
#display2   = '--display2'  in sys.argv
#expind     = '--expind'    in sys.argv  
#fit        = '--fit'       in sys.argv
#fit2       = '--fit2'      in sys.argv
#loop       = '--loop'      in sys.argv
#mgisotope  = '--mgisotope' in sys.argv
#murphy     = '--murphy'    in sys.argv
#newatom    = '--newatom'   in sys.argv
#noalpha    = '--noalpha'   in sys.argv
#original   = '--original'  in sys.argv
#previous   = '--previous'  in sys.argv
#reset      = '--reset'     in sys.argv
#show       = '--show'      in sys.argv
#tbs        = '--tbs'       in sys.argv
#whitmore   = '--whitmore'  in sys.argv
#binning    = 12          if '--bin'        not in sys.argv else   int(args[numpy.where(args=='--bin'       )[0][0]+1])
#order      = 3           if '--order'      not in sys.argv else   int(args[numpy.where(args=='--order'     )[0][0]+1])
#repeat     = 1           if '--repeat'     not in sys.argv else   int(args[numpy.where(args=='--repeat'    )[0][0]+1])
#ntrans     = 5           if '--ntrans'     not in sys.argv else   int(args[numpy.where(args=='--ntrans'    )[0][0]+1])
#stdev      = 0           if '--stdev'      not in sys.argv else float(args[numpy.where(args=='--stdev'     )[0][0]+1])
#chisq      = 1.E-5       if '--chisq'      not in sys.argv else float(args[numpy.where(args=='--chisq'     )[0][0]+1])
#snr        = None        if '--snr'        not in sys.argv else float(args[numpy.where(args=='--snr'       )[0][0]+1])
#threshold  = None        if '--threshold'  not in sys.argv else float(args[numpy.where(args=='--threshold' )[0][0]+1])
#wmin       = None        if '--wmin'       not in sys.argv else float(args[numpy.where(args=='--wmin'      )[0][0]+1])
#wmax       = None        if '--wmax'       not in sys.argv else float(args[numpy.where(args=='--wmax'      )[0][0]+1])
#xmin       = None        if '--xmin'       not in sys.argv else float(args[numpy.where(args=='--xmin'      )[0][0]+1])
#xmax       = None        if '--xmax'       not in sys.argv else float(args[numpy.where(args=='--xmax'      )[0][0]+1])
#ymin       = None        if '--ymin'       not in sys.argv else float(args[numpy.where(args=='--ymin'      )[0][0]+1])
#ymax       = None        if '--ymax'       not in sys.argv else float(args[numpy.where(args=='--ymax'      )[0][0]+1])
#mode       = None        if '--mode'       not in sys.argv else   str(args[numpy.where(args=='--mode'      )[0][0]+1])
#compare    = None        if '--compare'    not in sys.argv else   str(args[numpy.where(args=='--compare'   )[0][0]+1])
#custom     = None        if '--custom'     not in sys.argv else   str(args[numpy.where(args=='--custom'    )[0][0]+1])
#sample     = None        if '--sample'     not in sys.argv else   str(args[numpy.where(args=='--sample'    )[0][0]+1])
#tarfile    = None        if '--include'    not in sys.argv else   str(args[numpy.where(args=='--include'   )[0][0]+1])
#instrument = None        if '--instrument' not in sys.argv else   str(args[numpy.where(args=='--instrument')[0][0]+1])
#simulation = None        if '--simulation' not in sys.argv else   str(args[numpy.where(args=='--simulation')[0][0]+1])
#model      = None        if '--model'      not in sys.argv else   str(args[numpy.where(args=='--model'     )[0][0]+1])
#system     = None        if '--system'     not in sys.argv else   str(args[numpy.where(args=='--system'    )[0][0]+1])
#selection  = None        if '--selection'  not in sys.argv else   str(args[numpy.where(args=='--selection' )[0][0]+1])
#path       = '.'         if '--path'       not in sys.argv else   str(args[numpy.where(args=='--path'      )[0][0]+1])
#plot       = 'all'       if '--plot'       not in sys.argv else   str(args[numpy.where(args=='--plot'      )[0][0]+1])
#vpversion  = '10'        if '--vpfit'      not in sys.argv else   str(args[numpy.where(args=='--vpfit'     )[0][0]+1])
#arm        = None        if '--arm'        not in sys.argv else   str(args[numpy.where(args=='--arm'       )[0][0]+1])
#shape      = 'slope'     if '--shape'      not in sys.argv else   str(args[numpy.where(args=='--shape'     )[0][0]+1])
#vpcommand  = vpfitpath + 'vpfit' + vpversion
#vpfsetup   = 'vp_setup_king.dat' if vpversion=='9.5-king' else 'vp_setup_hires.dat' if instrument=='hires' else 'vp_setup_uves.dat'
#vpfsetup   = numpy.loadtxt(pathdata+vpfsetup,dtype=str,delimiter='\n',comments='!')
#vpfsetup   = numpy.hstack((vpfsetup,['chisqthres %.E 2 %.E'%(chisq,chisq)])) if vpversion!='9.5-king' else vpfsetup
#distortion = '0.000' if round(slope,3)==0 else 'm%.3f'%abs(slope) if slope<0 else 'p%.3f'%abs(slope)
#deviation  = '%.2f'%stdev if expind else '0.00'
##test       = 'v' + vpversion + '_chisq%.E'%chisq
##test       = test+'_'+arm            if instrument=='uves'  and '--simulation' not in sys.argv    else test
##test       = test+'_'+shape          if instrument=='hires' and (slope!=0 or distsep!=0)      else test
##test       = test+'_step%.E'%distsep if distsep!=0                                                else test
##test       = test+'_prev'              if '--previous'   in sys.argv and (slope!=0 or distsep!=0) else test
##test       = test+'_jw'                if '--whitmore'   in sys.argv and (slope!=0 or distsep!=0) else test
##test       = test+'_null'              if '--simulation' not in sys.argv and '--noalpha' in sys.argv  else test
##test       = test+'_new'               if '--newatom'    in sys.argv                                  else test
##test       = test+'_murphy'            if '--murphy'     in sys.argv                                  else test
##test       = test+'_mg'                if '--mgisotope'  in sys.argv                                  else test
##test = test+'_noalpha'         if '--noalpha'     in sys.argv    else test
##test = test+'_colfix'          if '--colfix'      in sys.argv    else test
##test = test+'_fddhires'        if '--fdd'         in sys.argv    else test
##test = test+'_fddhires2'       if '--fdd2'        in sys.argv    else test
##test = test+'_final'           if '--finalmodel'  in sys.argv    else test
#modflag = ''
##modflag = modflag+'_'+str(totrep)+'-0'            if totrep!=0 and sys.argv[1]=='run' else modflag
##modflag = modflag+'_'+str(totrep)+'-'+str(totrep) if totrep!=0 and sys.argv[1]!='run' else modflag
#if '--test' in sys.argv:
#    k = numpy.where(args=='--test')[0][0]
#    test = args[k+1]
#if os.getenv('HOME')=='/home/561/vxd561':
#    curlist = numpy.genfromtxt(pathdata+'allsys.dat',names=True,dtype=object,comments='!')
#    distres = numpy.genfromtxt(pathdata+'sims.dat',names=True,dtype=object,comments='!')
