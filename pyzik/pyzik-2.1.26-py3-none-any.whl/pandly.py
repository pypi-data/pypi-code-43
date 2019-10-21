__autor__ = 'FJ'
import pandas as pd
import numpy as np
import plotly.graph_objs as go
from plotly import figure_factory as ff
from plotly.offline import  iplot
from plotly import tools
from scipy import stats
from scipy.io import wavfile
from scipy.fftpack import fft, fftfreq, fftshift
from scipy.optimize import curve_fit
import IPython as ip
from uncertainties import ufloat
from time import sleep,time
import datetime
from colorama import Fore, Back, Style
from inspect import signature,getsource
from astroquery.jplhorizons import Horizons
from sklearn.metrics import r2_score
from prettytable import PrettyTable
import codecs
import traceback
import pip  
import inspect
import urllib.request
import requests
import base64
import sys
import os
from websocket import create_connection
from json import loads, dumps
from sjcl import SJCL, sjcl
MAGIC = "XXMOJOXX"
CHUNK_SIZE = 2*1000*1000

def fram_upload(filepath, url='https://framadrop.org/', delay=None, del_at_first_view=False):
    f1=open(filepath,'r')
    f2=open('_'+filepath,'w')
    for line in f1.readlines() :
        f2.write(line)
    f1.close()
    f2.close()
    filepath = '_' + filepath
    key = base64.b64encode(sjcl.get_random_bytes(32))
    size = os.path.getsize(filepath)
    (e, r) = divmod(size, CHUNK_SIZE)
    totalparts = e + [0, 1][r > 0]
    meta = {"name": filepath.split("/")[-1],
            "size": size,
            "total": totalparts,
            "i": 0,
            "del_at_first_view": del_at_first_view}
    f = open(filepath, "rb")
    wsurl = url.replace("http", "ws")+"upload/"
    ws = create_connection(wsurl)
    for (i, data) in enumerate(iter(lambda: f.read(CHUNK_SIZE), b"")):
        meta["part"] = i
        data = SJCL().encrypt(base64.b64encode(data), key)  # b64 is unnecessary be kept for compatibility
        for k in data.keys():
            if isinstance(data[k], bytes):  # b64encode produces bytes
                data[k] = data[k].decode("ascii")
        ws.send(payload=dumps(meta)+MAGIC+dumps(dumps(data)))  # second dumps is unnecessary be kept for compatibility
        result = ws.recv()
        print(result, file=sys.stderr)
        result = loads(result)
        meta["id"] = result["short"]
    ws.close()
    f.close()
    d={"download_url ":url+"r/"+meta["id"]+"#"+key.decode("ascii"),
       "delete_url ":url+"d/"+meta["id"]+"/"+result["token"]}
    return d


def fram_load(url):
    [url, key] = url.split('#')
    url = url.replace("http", "ws").replace("/r/", "/download/")
    ws = create_connection(url)
    p = 0
    t = 1
    while p < t:
        ws.send('{"part":%d}' % p)
        result = ws.recv()
        idx = result.find(MAGIC)
        meta = loads(result[0:idx])
        print(meta, file=sys.stderr)
        data = loads(loads(result[idx+len(MAGIC):]))  # second loads is unnecessary be kept for compatibility
        t = meta["total"]
        filepath = meta["name"].split("/")[-1]
        f = open(filepath, "ab")
        f.write(base64.b64decode(SJCL().decrypt(data, key)))  # b64 is unnecessary be kept for compatibility
        p += 1
    ws.close()
    f.close()
    f = open(filepath)
    data = f.read()
    f.close()
    try:
        os.remove(filepath)
    except:
        print('unable to delete '+filepath)
    return data
     
    

def install_pack(*package,proxy=None,option=None):
    print(f"version pip={pip.__version__}")
    if int(pip.__version__.split('.')[0])>9:
        from pip._internal import main
    else:
        from pip import main
    for p in package:
        print(f"\n********************** installation de {p} *************\n")
        if (proxy == None):
            if (option==None):
                try:
                    main(['install', p])
                except:
                    print(f">>> non installé")
            elif (option in ['pb','PB','PBayle','pbayle']):
                try:
                    main(['install','--proxy==192.168.224.254:3128', p])
                except:
                    print(f">>> non installé")
        else:
            try:
                main(['install',f'--proxy=={proxy}', p])
            except:
                print(f">>> non installé")

SPY = []
SPY_KEY = 9 #clé pour l'utilisation de check_graph ou check_op ou ...
__version__ = '19.8.2'

def exfw(tmp_url='',url_type="gd",glob_var=None):
    d = eval(requests.get(tmp_url).text)
    url = d['id_py']
    url0 = "https://drive.google.com/uc?export=download&id="+url if url_type == "gd" else url
    txt = requests.get(url0).text
    txt +='\n'*5
    key = d['id_code']
    credo = encrypt(d['id_cred'], key)
    urlo = encrypt(d['id_gs'], key)
    txtb = f"\ns=Gsheet({urlo},{credo},{key})"
    return exec(txt+txtb,glob_var)

def set_spy(func):
    def search_traceback(t,k,fname,name):
        try:
            t0 = t.replace(' ','')
            t0=t0.lstrip(t0[:t0.index(k)]).rstrip(")")
            x= t0[t0.index(k)+len(k)+1]
            if x=='[':
                result = t0[t0.index(k)+len(k)+2:t0.index(']')].split(',')
                result.sort()
            else:
                result = t0.split(",")[0].split("=")[1]
            return result
        except:
            return None

    def modif(*args, **kwargs):
        fname = func.__name__
        if fname == "scatter2D":
            keys = {'x':0,'y':0,'ortho':0,'other_df':1}
            kwargs['y'] = format_to_valid_y(kwargs['y'])
        elif fname == "scatter3D":
           keys = {'x':0,'y':0,'z':0,'other_df':1}
        elif fname == "vector3D":
            keys = {'x':0,'y':0,'z':0,'ux':0,'uy':0,'uz':0}
        elif fname == "vector":
            keys = {'x':0,'y':0,'ux':0,'uy':0}
        elif fname == 'histogram':
            keys = {'x':0,'histnorm':0}
        elif fname == 'scatterPolar':
            keys = {'theta':0,'r':0,'other_df':1}
            kwargs['r'] = format_to_valid_y(kwargs['r'])
        elif fname == 'regression':
            keys = {'x':0,'y':0,'degre':1}
        elif fname == 'draw_vectors':
            keys = {'point':0,'vector':0}
        elif fname == 'scatter1D':
            keys = {'x':0 }
        (_,_,_,text)=traceback.extract_stack()[-2]
        def_name = text[:text.find('.'+fname)].strip()
        if (def_name == 'self') and (fname=='scatter2D'):
            ret = func(*args, **kwargs)
            return ret
        spy_elem = {}
        spy_elem['name']=def_name
        spy_elem['method']=fname
        for k,v in keys.items():
            if k in kwargs: 
                if v == 0:
                    spy_elem[k]=kwargs[k]
                elif v == 1:
                    spy_elem[k]=search_traceback(text,k,fname,def_name)
            else:
                spy_elem[k] = get_default_args(func)[k]
        SPY.append(spy_elem)
        ret = func(*args, **kwargs)
        return ret
        
    return modif

def enable_plotly_in_cell():    
  """
  fonction a mettre pour afficher un graphique plotly uniquement sur google.colab
  """
  import IPython
  from plotly.offline import init_notebook_mode
  display(IPython.core.display.HTML('''<script src="/static/components/requirejs/require.js"></script>'''))
  init_notebook_mode(connected=False)

def reset_spy():
    SPY = []

@ set_spy
def scatterPolar(self,other_df=None, theta='theta', r='R', titre="",
              unsur=1, style_tracer='o',
              color='auto', quadril_r=0, quadril_theta=0):
    couleur=['red', 'blue', 'green', 'grey', 'darkgrey', 'gold', 'black',
             'pink', 'darkturquoise', 'lightblue', 'purple', 'maroon', 'violet', 'mistyrose']
    datf = [self]
    r = format_to_valid_y(r)
    if not isinstance(other_df, list):
        other_df = [other_df]
    for elem in other_df:
        if isinstance(elem, pd.DataFrame):
            datf.append(elem)
    courbes = []
    i = 0
    for data in datf:
        if not check_info(data):
            print(f"Avertissement - dataframe sans nom\nEcrire ma_dataframe.info='quelque chose'")
            data.info = "sans info"
        nom = data.info
        for ordonnee in r:
            a_virer = False
            if isinstance(ordonnee,(float, int)):
                a_virer = True
                txt=f'_val={ordonnee:.3e}'
                data[txt] = pd.Series(np.ones(len(data)) * float(ordonnee))
                ordonnee = txt
                r[i] = txt
            xyz=go.Scatterpolar(theta=data[theta][::unsur],r=data[ordonnee][::unsur],
                               name=f"{ordonnee}/({nom})")
            mode_symbol_dask = marker_to_plotly_marker(style_tracer)
            xyz['mode'] = mode_symbol_dask['mode']
            if 'markers' in xyz['mode']:
                xyz['marker']['symbol'] = mode_symbol_dask['symbol']
            if 'lines' in xyz['mode']:
                xyz['line']['shape']='spline'
                xyz['line']['dash'] = mode_symbol_dask['dash']
            if color=='auto':
                xyz['marker']['color']=couleur[i]
            elif color=='rainbow':
                xyz['marker']['color']=data[ordonnee][::unsur]
            else:
                xyz['marker']['color']=color
            courbes.append(xyz)
            i = (i + 1)%len(couleur)
            if a_virer:
                data.drop(columns=[txt],inplace=True)
    i = (i + 1)%len(couleur)
    if titre=="":
        try:
            titre="Courbe(s) relative(s) à "+" ; ".join([data.info for data in datf])
            tit_ok = True
        except:
            titre="Pas de titre"
            tit_ok = False
    layout= go.Layout(title= titre)
    fig = go.Figure(data=courbes, layout=layout)
    return iplot(fig,filename=titre)

@ set_spy
def histogram(self,x=None,titre='pas de titre',orientation='vertical',histnorm=""):
   """
   Trace un histogramme de la grandeur 'x'
   Arguments:
       * x (str ou [str]): Nom de la ou des colonnes dont on veux l'histogramme
       * titre (str) : titre de l'histogramme
       * orientation (str) : indique l'orientation de l'histogramme 
           > 'vertical' (défaut) ou 'horizontal' 
       * histnorm (str): Normalise l'histogramme
           > "" (défaut) : pas de normalisation
           > "percent" : normalisation en pourcentage
    Exemple:
        'x' et 'y' sont des noms de colonnes de la dataframe df. Pour tracer
        les histogrammes de 'x' et 'y'
        >df.histogram(x=['x','y'])
   """
   if x == None:
       x = list(self.columns)
   x = format_to_valid_y(x)
   courbes=[]
   for elem in x:
       if orientation.lower()=='vertical':
           his = go.Histogram(x=self[elem],name=elem,histnorm=histnorm)
       else:
           his = go.Histogram(y=self[elem],name=elem,histnorm=histnorm)
       his['opacity'] = 0.75 if len(x)>1 else 1
       courbes.append(his)
   layout = go.Layout(barmode='overlay')
   fig = go.Figure(data=courbes, layout=layout)
   return iplot(fig,filename='overlaid histogram')         

def get_default_args(func):
    signature = inspect.signature(func)
    return {
        k: v.default
        for k, v in signature.parameters.items()
        if v.default is not inspect.Parameter.empty
    }


def wavelength_to_rgb(wavelength, gamma=0.8):

    '''This converts a given wavelength of light to an 
    approximate RGB color value. The wavelength must be given
    in nanometers in the range from 380 nm through 750 nm
    (789 THz through 400 THz).

    Based on code by Dan Bruton
    http://www.physics.sfasu.edu/astro/color/spectra.html
    '''

    wavelength = float(wavelength)
    if wavelength >= 400 and wavelength <= 440:
        attenuation = 0.3 + 0.7 * (wavelength - 400) / (440 - 400)
        R = ((-(wavelength - 440) / (440 - 380)) * attenuation) ** gamma
        G = 0.0
        B = (1.0 * attenuation) ** gamma
    elif wavelength >= 440 and wavelength <= 490:
        R = 0.0
        G = ((wavelength - 440) / (490 - 440)) ** gamma
        B = 1.0
    elif wavelength >= 490 and wavelength <= 510:
        R = 0.0
        G = 1.0
        B = (-(wavelength - 510) / (510 - 490)) ** gamma
    elif wavelength >= 510 and wavelength <= 580:
        R = ((wavelength - 510) / (580 - 510)) ** gamma
        G = 1.0
        B = 0.0
    elif wavelength >= 580 and wavelength <= 645:
        R = 1.0
        G = (-(wavelength - 645) / (645 - 580)) ** gamma
        B = 0.0
    elif wavelength >= 645 and wavelength <= 800:
        attenuation = 0.3 + 0.7 * (800 - wavelength) / (800 - 645)
        R = (1.0 * attenuation) ** gamma
        G = 0.0
        B = 0.0
    else:
        R = 0.0
        G = 0.0
        B = 0.0
    R *= 255
    G *= 255
    B *= 255
    return f"rgb({int(R)},{int(G)},{int(B)})"


@ set_spy
def scatter1D(self,x='lamb',titre='',xlabel='',other_df=None,style_tracer='|',**d):
    gamma = d.get('gamma',0.4)
    self['__color'] = [wavelength_to_rgb(xi,gamma=gamma) for xi in self[x]]
    self['__y'] = 0
    self['__uy'] = 1
    line_shapes = [{'type':'line','x0':xx,'y0':0,'x1':xx,'y1':1,'line':{'color':cc,'width':3}} for xx,cc in zip(self[x],self['__color'])]
    xyz=go.Scatter(x=self[x],y=self['__y'],marker={'size':7,'color':self['__color']},mode='markers')
    xx_label = xlabel if xlabel=='' else x
    layout= go.Layout(title= titre,xaxis= dict(title=xx_label),yaxis=dict(title= ''),shapes=line_shapes)
    fig = go.Figure(data=xyz, layout=layout)
    self.drop(columns=['__color','__y','__uy'],inplace=True)
    return iplot(fig, filename='LO')

def marker_to_plotly_marker(markers):
    if markers in [None,'']:
        return
    symbol, s = ["circle","circle-open","square","square-open","diamond","diamond-open","cross","x"], list(r'oO[<>+x')
    marker_typ = {k:v for k,v in zip(s,symbol)}
    #mode = lines;markers;lines+markers
    #dash => "solid", "dot", "dash", "longdash", "dashdot", or "longdashdot"
    #symbol => yen a plein
    #symbol 3D "circle" | "circle-open" | "square" | "square-open" | "diamond" | "diamond-open" | "cross" | "x"  
    line_typ = {':':'dot','.':'dash',';':'longdash','-':'solid'}
    result = {'mode':'markers','symbol':'xxx','dash':'xxx'} #default result
    #check if lines.
    mar,lin = '',''
    #check if lines.
    for k,v in line_typ.items():
        if k in markers:
            lin = 'lines'
            result['dash'] = v
            break
   #check if markers:
    for k,v in marker_typ.items():
       if k in markers:
           mar = 'markers'
           result['symbol']=v
           break
    if (lin == 'lines') and (mar == 'markers'):
        result['mode'] = 'lines+markers'
    elif (lin == '') and ( mar == 'markers'):
        result['dash']=''
        result['mode'] = 'markers'
    elif (lin == 'lines') and (mar == ''):
        result['symbol'] = ''
        result['mode'] = 'lines'
    assert result['symbol'] != 'xxx',f"marker symbol must be in {marker_typ.keys()} or None"
    assert result['dash'] != 'xxx',f"marker dash must be in {line_typ.keys()} or None"
    return result
               
@ set_spy           
def scatter2D(self, other_df=None, x='t', y='X', titre="",
              ortho='auto', unsur=1, style_tracer='o',
              color='auto', shape=None, origin_df=None, quadril_x=0, quadril_y=0,
              subplots=False, fill='', xlabel='', ylabel='',xorder='normal'):
    """
        Méthode appliquée à une dataframe -> retourne un graphique plotly en 2D
        Arguments, significations et valeurs par defaut        
        * x (str): Nom unique de l'abcisse (ex x='t') - Défaut x='t'
        * y (str ou [str]): Nom(s) de la/des ordonnées (ex y=['X','Y',85.6]) 
                                accepte les valeurs (ex 8.31) - Défaut y='X'
        * titre (str): titre du graphique - Défaut titre=''
        * x_label, y_label (str) : Noms des axes x et y - Défaut ''
        * ortho ('ortho' ou 'auto') : repère normé => ortho='ortho' 
                    sinon ortho='auto' (Défaut ortho='auto')
        * unsur (int): Affiche 1 point sur unsur - Défaut unsur=1
        * style_tracer (str): Défini le style du tracé parmis 'o','-o','--'
                        Défaut style_tracer='o'
        * color (str) : Défini la couleur - Défaut color='auto'
                        Spécial 'rainbow'
        * quadril_x, quadril_y (int): définie la densité de la grille (max=50)
        * shape [dict]: Permet d'inserer une forme géométrique sur le graphique
                        Défaut shape=None
               ex pour tracer le soleil de rayon 600000 km=> 
          shape=dict(type='circle',x0=-300000,x1=300000,y0=-300000,y1=300000) 
        * other_df (dataframe): Nom d'une autre dataframe à tracer possédant les mêmes colonnes.
        * subplots (booleen) : Si True, organise vos graphiques en plusieurs sous_graphiques. Défaut = False
        * fill (str) : Permet de colorier en dessous d'une courbe depuis y=0 ('tozeroy') ou entre 2 courbes ('tonexty') - Défaut ''
        * secondary_y (bool) : Affiche une seconde graduation à la courbe Defaut=False
                               Valable uniquement s'il n'y a que 2 grandeurs y a tracer.
                               Pratique pour tracer pH=f(V) et dpH/dV = f(V) sur un même graphique 
        * origin_df (dataFrame): définie la dataframe qui sera l'origine du tracé, 
                - conditions : origin_df et la dataframe (self) doivent avoir la même colonne de temps, elles doivent être
                synchrone. Elles doivent avoir des colonnes positions x,y ayant les mêmes noms.
                - Par défaut c'est le repère ou l'on a définie la dataframe (self)
        Exemple 1 : 'mars' et 'phobos' sont des dataframes  possédant 'x' et 'y' comme colonnes. Pour tracer y=f(x) de Mars
                  et de son satellite Phobos
                  >mars.scatter2D(x='x',y='y',other_df=phobos,ortho='ortho',color='rainbow')      
                  
        Exemple 2 : 'ballon' est une dataframe (mouvement d'un ballon) possédant 't','x' et 'y' comme colonnes - Pour tracer
                  les courbes x=f(t), y=f(t):
                  >ballon.scatter2D(x='t',y=['x','y'],titre='équations horaires du mouvement')
        
        Exemple 3 : 'io', 'calisto' et 'jupyter' sont des dataframes synchrones dans le temps et ayant des noms de colonnes identiques - Pour 
                    tracer la trajectoire de io et callisto dans le référentiel jovien:
                    >io.scatter2D(other_df=callisto,origin_df=jupiter,x='x',y='y',titre='trajectoire de io par rapport à Jupyter')
            
    """
    couleur=['red', 'blue', 'green', 'grey', 'darkgrey', 'gold', 'black',
             'pink', 'darkturquoise', 'lightblue', 'purple', 'maroon', 'violet', 'mistyrose']
    datf = [self]
    y = format_to_valid_y(y)
    if not isinstance(other_df, list):
        other_df = [other_df]
    for elem in other_df:
        if isinstance(elem, pd.DataFrame):
            datf.append(elem)
    origin = False
    if isinstance(origin_df, pd.DataFrame):
        origin = True
    courbes = []
    i = 0
    #symbol, s = ["circle",17,3,4,29,29,23,24,10,11,15], list(r'o*+x[]<>/\%')
    for data in datf:
        if not check_info(data):
            print(f"Avertissement - dataframe sans nom\nEcrire ma_dataframe.info='quelque chose'")
            data.info = "sans info"
        nom = data.info
        for num,ordonnee in enumerate(y):
            a_virer = False
            if isinstance(ordonnee,(float, int)):
                a_virer = True
                txt=f'_val={ordonnee:.3e}'
                data[txt] = pd.Series(np.ones(len(data)) * float(ordonnee))
                ordonnee = txt
                y[i] = txt
            if not origin:
                xyz=go.Scatter(x=data[x][::unsur],y=data[ordonnee][::unsur],marker=dict(size=4),
                               name=f"{ordonnee}/({nom})"[:50])
            else:
                xyz=go.Scatter(x=data[x][::unsur]-origin_df[x][::unsur],y=data[ordonnee][::unsur]-origin_df[ordonnee][::unsur],
                                   marker=dict(size=4),name=f"{ordonnee}({nom})"[:50])
                xyz_origin = go.Scatter(x=np.zeros(1),y=np.zeros(1),marker=dict(size=4),name=f"{origin_df.info}"[:50])
            mode_symbol_dask = marker_to_plotly_marker(style_tracer)
            xyz['mode'] = mode_symbol_dask['mode']
            if 'markers' in xyz['mode']:
                xyz['marker']['symbol'] = mode_symbol_dask['symbol']
            if 'lines' in xyz['mode']:
                xyz['line']['shape']='spline'
                xyz['line']['dash'] = mode_symbol_dask['dash']
            if color=='auto':
                xyz['marker']['color']=couleur[i]
            elif color=='rainbow':
                xyz['marker']['color']=data[ordonnee][::unsur]
            else:
                xyz['marker']['color']=color
            if fill != '':
                xyz['fill'] = fill
            courbes.append(xyz)
            if origin:
               courbes.append(xyz_origin) 
            i = (i + 1)%len(couleur)
            if a_virer:
                data.drop(columns=[txt],inplace=True)
    if titre=="":
        try:
            titre="Courbe(s) relative(s) à "+" ; ".join([data.info for data in datf])
            tit_ok = True
        except:
            titre="Pas de titre"
            tit_ok = False
    else:
        tit_ok = True
    x_label = x if xlabel == '' else xlabel
    y_label = " | ".join(y) if ylabel == '' else ylabel
    quadril_x = int(max(min(quadril_x,50),0))
    quadril_x = int(max(min(quadril_x,50),0))
    autorange = True if xorder == 'normal' else "reversed"
    layout= go.Layout(title= titre,xaxis= dict(autorange=autorange,title = x_label,nticks=quadril_x),yaxis=dict(nticks=quadril_y,title=y_label ))
    if ortho=='ortho':
        layout['xaxis']['constrain'] ='domain'
        layout['yaxis']['scaleanchor']='x'
    if shape != None:
        if not isinstance(shape,list):
            shape=[shape]
        layout['shapes']=shape
    if subplots:
        nb_rows = len(courbes) // 2 + len(courbes) % 2
        if tit_ok:
            titres = tuple([tit for tit in titre.split('+')][1:])
        fig = tools.make_subplots(rows=nb_rows, cols=2, subplot_titles=titres)
        for idx,curve in enumerate(courbes):
            fig.append_trace(curve, 1+int(idx/2), 1+idx%2)
            fig['layout'][f"xaxis{1+idx}"].update(title = x)
            fig['layout'][f"yaxis{1+idx}"].update(title = f"{curve['name']}")
    else:
        fig = go.Figure(data=courbes, layout=layout)
    return iplot(fig,filename=titre)

@ set_spy
def scatter3D(self, other_df=None, x='X', y='Y', z='Z', titre="un titre", unsur=1,color='auto',origin_df=None,style_tracer='o',xlabel='',ylabel='',zlabel=''):
    """
        Méthode/Fonction appliquée à une dataframe -> retourne un graphique plotly en 3D
        Arguments, signification et valeurs par defauts
        Par convention : on appelle 'self' la dataframe qui appele la méthode. 
        * x,y,z (str): Noms des coordonnées uniques x,y,z qui sont des colonnes de la dataframe self  - Défauts x='X',y='Y',z='Z'
        * titre (str): titre du graphique - Défaut titre='un titre'
        * unsur (int): Affiche 1 point sur unsur - Défaut unsur=1
        * style_tracer (str): Défini le style du tracé parmis 'o','-o','--' - Défaut style_tracer='o'
        * color (str): Défini la couleur - Défaut color='auto' - Spécial 'rainbow'
        * other_df (dataframe): Nom d'une autre dataframe qui possède les mêmes colonnes x,y,z
        * origin_df (dataFrame): définie la dataframe qui sera l'origine du tracé, 
                - conditions : origin_df et la dataframe (self) doivent avois la même colonne de temps, elles doivent être
                synchrones. Elles doivent avoir des colonnes positions x,y,z ayant les mêmes noms.
                - Par défaut l'origine est le repère ou l'on a définie le mvt de la dataframe (self)
        
        Exemple 1  : 'mars' et 'phobos' sont des dataframes possédant 'x','y','z' comme colonnes - Pour tracer la trajectoire de Mars
                  >mars.scatter3D(x='x',y='y',z='z',titre='un super titre')    
        Exemple 2 :  'triton' et 'uranus' sont des dataframes possédant 'x','y','z' comme coordonnées de positions et 
                    synchrone sur 't'. Pour tracer la trajectoire de triton dans le repère d'uranus.
                  >triton.scatter3D(x='x',y='y',z='z',origin_df=uranus)

    """
    
    symbol, s = ['circle', 'circle-open', 'square', 'square-open','diamond', 'diamond-open', 'cross', 'x'],list(r'oO[]<>/x')
    datf = [self]
    if not isinstance(other_df, list):
        other_df = [other_df]
    for elem in other_df:
        if isinstance(elem, pd.DataFrame):
            datf.append(elem)
    trace = []
    couleur = ['red', 'blue','green' , 'grey','darkgrey','gold','black',
             'pink','darkturquoise','lightblue','purple','maroon','violet','mistyrose']
    origin = False
    if isinstance(origin_df,pd.DataFrame):
        origin = True
    for i, df in enumerate(datf):
        if not check_info(df):
            df.info = "pas d'info"
        if not origin:
            xyz=go.Scatter3d(x=df[x][::unsur], y=df[y][::unsur], z=df[z][::unsur],name=df.info)
        else:
            xyz=go.Scatter3d(x=df[x][::unsur]-origin_df[x][::unsur], y=df[y][::unsur]-origin_df[y][::unsur],
                             z=df[z][::unsur]-origin_df[z][::unsur],name=df.info)
            xyz_origin = go.Scatter3d(x=np.zeros(1), y=np.zeros(1),
                             z=np.zeros(1), mode='markers', marker=dict(size=5), name=origin_df.info)
        mode_symbol_dask = marker_to_plotly_marker(style_tracer)
        xyz['mode'] = mode_symbol_dask['mode']
        if 'markers' in mode_symbol_dask['mode']:
                #print("**************************jai un marker")
                xyz['marker']['symbol'] = mode_symbol_dask['symbol']
                xyz['marker']['size'] = 2
                if color == 'auto':
                    xyz['marker']['color'] = couleur[i]
                elif color == 'rainbow':
                    xyz['marker']['color'] = df[x]
                else:
                    xyz['marker']['color'] = color
        if 'lines' in mode_symbol_dask['mode']:
            xyz['line']['dash'] = mode_symbol_dask['dash']
        trace.append(xyz)
        if origin:
            trace.append(xyz_origin) 
    titx = xlabel if xlabel != '' else x
    tity = xlabel if ylabel != '' else y
    titz = xlabel if zlabel != '' else z
    layout = go.Layout(title=titre,margin=dict(l=0,r=0,b=0,t=0),showlegend=True,
                       scene = dict(aspectmode='data',xaxis = dict(title=titx), 
                                    yaxis = dict(title=tity), zaxis=dict(title=titz)))
    fig = go.Figure(data=trace, layout=layout)
#    (_,_,_,text)=traceback.extract_stack()[-2]
#    df_name = text[:text.index('.scatter3D')].strip()
#    SPY.append({'method': 'scatter3D','x':x,'y':y,'z':z,'name':df_name})
    return iplot(fig, filename=titre)

def arrondir_cs(x,cs = 1):
    """
    Fonction -> retourne l'arrondi supérieur d'une valeur x avec cs chiffres significatifs (float)
    Arguments:
    * x (float): Valeur à arrondir
    * cs (int): nombre de chiffres significatifs - Défaut cs=1
    """
    cs = min(max(cs, 1), 10)
    parts = ("%e" % x).split('e') 
    exposant = int(parts[1])
    mantisse = np.ceil(float(parts[0])*10**(cs-1))/10**(cs-1)
    return (mantisse*10**exposant)

def get_student_k(n,percent):
    x = 1-(1 - percent)/2 #2tails
    return stats.t.ppf(x,n-1)

def display_U(self,grandeur,cs=1,percent=0.95):
    """
    Fonction ou méthode appliquée à une dataframe -> retourne l'incertitude d'une grandeur U(grandeur) contenue dans une 
    dataframe avec cs chiffres significatifs sous forme d'un texte (str)
    Arguments:
    grandeur (str): nom de la colonne de la dataframe dont on veux l'incertitude (ex: grandeur='R')
    * cs (int): nombre de chiffres significatif - Défaut cs=1
    * perdent (float): niveau de confiance - Défaut 0.95 dsoit 95%
    """

    cs=int(min(max(cs, 1),2))
    moy=self[grandeur].mean()
    std=self[grandeur].std()
    nb=self[grandeur].count()
    k = get_student_k(nb,percent)
    u0=std*k/np.sqrt(nb)
    u=arrondir_cs(u0,cs)
    x=ufloat(moy,u)
    relat=np.abs(arrondir_cs(u/moy,2)*100)
    if cs==1:
        txt=f'grandeur/incertitude \n{grandeur}={x:.1u} à {100*percent}% avec k={k:.4}'
    elif cs==2:
        txt=f'grandeur/incertitude \n{grandeur}={x:.2u} à {100*percent}% avec k={k:.4}'
    txt+='\n'+f'incertitude relative = {relat:.2}%'
    txt+="\nsans arrondi :"
    txt+=f'{grandeur}={moy} et U({grandeur})={u:}'
    txt+='\n\n'
    return txt

@ set_spy
def draw_vectors(self,point=('&','&'),vector=('vx','vy'),style_tracer='o',unsur=1,scalvect=1,titre="sans titre",quadril_x=0,quadril_y=0,**d):
    if (point == ('&','&')) and len(vector)==3:
        point = ('&','&','&')
    if len(point) == len(vector) == 2:
        x,y = point
        ux,uy = vector
        xlabel,ylabel = d.get('xlabel',''),d.get('ylabel','')
        self.vector(x=x,y=y,ux=ux,uy=uy,unsur=unsur,scalvect=scalvect,titre=titre,quadril_x=quadril_x,quadril_y=quadril_y,xlabel=xlabel,ylabel=ylabel,style_tracer=style_tracer)
    elif len(point) == len(vector) == 3:
        x,y,z = point
        ux,uy,uz = vector
        xlabel,ylabel,zlabel = d.get('xlabel',''),d.get('ylabel',''),d.get('zlabel','')
        self.vector3D(x=x,y=y,z=z,ux=ux,uy=uy,uz=uz,unsur=unsur,scalvect=scalvect,titre=titre,quadril_x=quadril_x,quadril_y=quadril_y,xlabel=xlabel,ylabel=ylabel,zlabel=zlabel,style_tracer=style_tracer)
    else:
        print(f'votre point={point} et vector={vector} ne conviennent pas')
  
def vector_by_norm_and_direction(self,vector_norm,direction='centripetal',x='&',y='&',unsur=1,scalvect=1,titre="sans titre",quadril_x=0,quadril_y=0,**d):
    """
        Méthode/Fonction appliquée à une dataframe -> retourne la trajectoire avec des vecteurs.
        Conditions d'utilisation :
        
        Arguments, signification et valeurs par défauts:
        * x,y (str) : Noms des points d'applications des vecteurs - défaut 'x' et 'y'
        * vector_norm (str) : Nom de la coordonnée représentant la norme du vecteur à tracer (ex vector_norm='F')
        * direction (str) : représente l'orientation du vecteur:
            >si 'centripetal'(defaut) le vecteur de norme u est représenté vers le centre de la trajectoire
            >si 'centrifugal' le vecteur de norme u est représenté vers l'extérieure de la trajectoire
            
            
        * titre (str): titre du graphique - Défaut titre='un titre'
        * unsur (int): Affiche 1 vecteur sur unsur - Défaut unsur=1
        * scalvect (float): echelle de tracé des vecteurs - Défaut scalvect=1.0
        * quadril_x,quadril_y (int) : Densité du quadrillage (défaut 0,0)
    Exemple 1: Utilisation pour visualiser le vecteur Force de gravitation de norme 'F' de la planètes Mars (dataFrameMars)
        >dataFrameMars.vector(vector_norm='F',direction='centripetal',unsur=2)
    """     
    xx,yy='',''
    #recherche du x,y par defaut
    if (x=='&' and y=='&'):
        list_x='x','X','x_mod','X_mod' #valeurs préalablement testées
        list_y='y','Y','y_mod','Y_mod'
        for lx in list_x:
            if lx in list(self):
                xx=lx
                break
        for ly in list_y:
            if ly in list(self):
                yy=ly
                break
    if (x in self) and (y in self):
        xx, yy = x, y
    if xx=='' or yy=='':
        print(f"'X ou x' ou 'Y ou y' ne sont pas des colonnes de votre dataFrame, il faut spécifier une origine à vos vecteurs en utilisant x='**' et y='**' ou ** sont parmis\n{self.columns}")
        return None
    self['__r'] =self.norme(xx,yy)
    if direction.lower()=='centripetal':
        self['__vect_x']=-self[vector_norm]*self[xx]/self['__r']
        self['__vect_y']=-self[vector_norm]*self[yy]/self['__r']
    elif direction.lower()=='centrifugal':
        self['__vect_x']=self[vector_norm]*self[xx]/self['__r']
        self['__vect_y']=self[vector_norm]*self[yy]/self['__r']
    else:
        print("under construct...")
        return None
    result = self.vector(ux='__vect_x',uy='__vect_y',x=xx,y=yy,unsur=unsur,scalvect=scalvect,titre=titre,quadril_x=quadril_x,quadril_y=quadril_y,**d)
    self.del_columns('__r','__vect_x','__vect_y')
    return result

def vector_by_norm_and_direction3D(self,vector_norm,direction='centripetal',x='&',y='&',z='&',unsur=1,scalvect=1,titre="sans titre",quadril_x=0,quadril_y=0,**d):
    """
        Méthode/Fonction appliquée à une dataframe -> retourne la trajectoire avec des vecteurs en 3D.
        Conditions d'utilisation :
        
        Arguments, signification et valeurs par défauts:
        * x,y,z (str) : Noms des points d'applications des vecteurs - défaut 'x' , 'y' et 'z'
        * vector_norm (str) : Nom de la coordonnée représentant la norme du vecteur à tracer (ex vector_norm='F')
        * direction (str) : représente l'orientation du vecteur:
            >si 'centripetal'(defaut) le vecteur de norme u est représenté vers le centre de la trajectoire
            >si 'centrifugal' le vecteur de norme u est représenté vers l'extérieure de la trajectoire
            
            
        * titre (str): titre du graphique - Défaut titre='un titre'
        * unsur (int): Affiche 1 vecteur sur unsur - Défaut unsur=1
        * scalvect (float): echelle de tracé des vecteurs - Défaut scalvect=1.0
        * quadril_x,quadril_y (int) : Densité du quadrillage (défaut 0,0)
    Exemple: Utilisation pour visualiser le vecteur Force de gravitation de norme 'F' de la planètes Mars (dataFrameMars)
        >dataFrameMars.vector(vector_norm='F',direction='centripetal',unsur=2)
    """     
    xx,yy,zz='','',''
    #recherche du x,y par defaut
    if (x=='&' and y=='&' and z=='&'):
        list_x='x','X','x_mod','X_mod' #valeurs préalablement testées
        list_y='y','Y','y_mod','Y_mod'
        list_z='z','Z','z_mod','Z_mod'
        for lx in list_x:
            if lx in list(self):
                xx=lx
                break
        for ly in list_y:
            if ly in list(self):
                yy=ly
                break
        for lz in list_z:
            if lz in list(self):
                zz=lz
                break
    if (x in self) and (y in self) and (z in self):
        xx, yy, zz = x, y, z
    if xx=='' or yy=='' or zz=='':
        print(f"'X ou x' ou 'Y ou y' ou 'Z ou z' ne sont pas des colonnes de votre dataFrame, il faut spécifier un point d'application à vos vecteurs en utilisant x='**' et y='**' ou ** sont parmis\n{self.columns}")
        return None
    self['__r'] =self.norme(xx,yy,zz)
    if direction.lower()=='centripetal':
        self['__vect_x']=-self[vector_norm]*self[xx]/self['__r']
        self['__vect_y']=-self[vector_norm]*self[yy]/self['__r']
        self['__vect_z']=-self[vector_norm]*self[zz]/self['__r']
    elif direction.lower()=='centrifugal':
        self['__vect_x']=self[vector_norm]*self[xx]/self['__r']
        self['__vect_y']=self[vector_norm]*self[yy]/self['__r']
        self['__vect_z']=self[vector_norm]*self[zz]/self['__r']
    else:
        print("under construct...")
        return None
    result = self.vector3D(ux='__vect_x',uy='__vect_y',uz='__vect_z',x=xx,y=yy,z=zz,unsur=unsur,scalvect=scalvect,titre=titre,quadril_x=quadril_x,quadril_y=quadril_y)
    self.del_columns('__r','__vect_x','__vect_y','__vec_z')
    return result


def vector(self,ux,uy,x='&',y='&',unsur=1,style_tracer='o',scalvect=1,titre="sans titre",quadril_x=0,quadril_y=0,xlabel='',ylabel='',**d):
    """
        Méthode/Fonction appliquée à une dataframe -> retourne la trajectoire avec des vecteurs.
        Conditions d'utilisation :
        
        Arguments, signification et valeurs par défauts:
        * x,y (str) : Noms des points d'applications des vecteurs - défaut 'x' et 'y'
        * ux,uy (str) : Noms des coordonnées uniques du vecteur à tracer (ex ux='AX', uy='AY')
        * titre (str): titre du graphique - Défaut titre='un titre'
        * unsur (int): Affiche 1 vecteur sur unsur - Défaut unsur=1
        * scalvect (float): echelle de tracé des vecteurs - Défaut scalvect=1.0
        * quadril_x,quadril_y (int) : Densité du quadrillage (défaut 0,0)
    Exemple 1: Utilisation pour visualiser le vecteur vitesse (VX,VY) de la planètes Mars (dataFrameMars)
        >dataFrameMars.vector(ux='VX',uy='VY',unsur=2)
        >ballon.vector(ux='ax',uy='ay')
    """
    xx,yy='',''
    #recherche du x,y par defaut
    if (x=='&' and y=='&'):
        list_x='x','X','x_mod','X_mod' #valeurs préalablement testées
        list_y='y','Y','y_mod','Y_mod'
        for lx in list_x:
            if lx in list(self):
                xx=lx
                break
        for ly in list_y:
            if ly in list(self):
                yy=ly
                break
    if (x in self) and (y in self):
        xx, yy = x, y
    if xx=='' or yy=='':
        print(f"'X ou x' ou 'Y ou y' ne sont pas des colonnes de votre dataFrame, il faut spécifier une origine à vos vecteurs en utilisant x='**' et y='**' ou ** sont parmis\n{self.columns}")
        return None
    scal_espace=np.abs((self[xx].max()+self[yy].max())/(self[ux].max()+self[uy].max()))
    quiver_fig = ff.create_quiver(self[xx][::unsur],self[yy][::unsur], self[ux][::unsur], self[uy][::unsur],
                       scale=scal_espace*scalvect,
                       arrow_scale=0.08, # Sets arrow scale
                       name=f'vecteur ({ux},{uy})',
                       angle=np.pi/12,
                       line=dict(width=1))
    points = go.Scatter(x=self[xx],y=self[yy],name=f"Point ({xx},{yy})")
    mode_symbol_dask = marker_to_plotly_marker(style_tracer)
    points['mode'] = mode_symbol_dask['mode']
    if 'markers' in points['mode']:
        points['marker']['symbol'] = mode_symbol_dask['symbol']
    if 'lines' in points['mode']:
        points['line']['shape']='spline'
        points['line']['dash'] = mode_symbol_dask['dash']
    xlab = xx if xlabel =='' else xlabel
    ylab = yy if ylabel =='' else ylabel
    layout= go.Layout(title= titre,xaxis= dict(constrain='domain',title= xlab,nticks=quadril_x),yaxis=dict(scaleanchor='x',title= ylab,nticks=quadril_y))
    quiver_fig.add_trace(points)
    quiver_fig['layout'].update(layout)
#    (_,_,_,text)=traceback.extract_stack()[-2]
#    df_name = text[:text.index('.vector')].strip()
#    SPY.append({'method': 'vector','ux':ux,'uy':uy,'x':xx,'y':yy,'name':df_name})
    return iplot(quiver_fig, filename='vecteur')


def vector3D(self,ux,uy,uz,x='&',y='&',z='&',unsur=1,scalvect=1,titre="sans titre",quadril_x=0,quadril_y=0,quadril_z=0,xlabel='',ylabel='',zlabel='',style_tracer='o'):
    """
        Méthode/Fonction appliquée à une dataframe -> retourne la trajectoire avec des vecteurs.
        
        Arguments, signification et valeurs par défauts:
        * x,y,z (str) : Noms des points d'applications des vecteurs
        * ux,uy,uz (str) : Noms des coordonnées uniques du vecteur à tracer (ex ux='AX', uy='AY', uz='AZ')
        * titre (str): titre du graphique - Défaut titre='un titre'
        * unsur (int): Affiche 1 vecteur sur unsur - Défaut unsur=1
        * scalvect (float): echelle de tracé des vecteurs - Défaut scalvect=1.0
    Exemple:  Utilisation pour visualiser le vecteur vitesse (VX,VY,VZ) de la planètes Mars (dataFrameMars)
                dont les points d'application ont pour coordonnées les colonnes 'X','Y','Z' 
        >dataFrameMars.vector3D(x='X',y='Y',z='Z',ux='VX',uy='VY',uz='VZ',unsur=2)
    """
    xx,yy,zz='','',''
    #recherche du x,y par defaut
    if (x=='&' and y=='&' and z=='&'):
        list_x='x','X','x_mod','X_mod' #valeurs préalablement testées
        list_y='y','Y','y_mod','Y_mod'
        list_z='z','Z','z_mod','Z_mod'
        for lx in list_x:
            if lx in list(self):
                xx=lx
                break
        for ly in list_y:
            if ly in list(self):
                yy=ly
                break
        for lz in list_z:
            if lz in list(self):
                zz=lz
                break
    if (x in self) and (y in self) and (z in self):
        xx, yy, zz = x, y, z
    if xx=='' or yy=='' or zz=='':
        print(f"'X ou x' ou 'Y ou y' ou 'Z ou z' ne sont pas des colonnes de votre dataFrame, il faut spécifier un point d'application à vos vecteurs en utilisant x='**' et y='**' ou ** sont parmis\n{self.columns}")
        return None
    scal=scalvect*np.abs((self[xx].max()+self[yy].max()+self[zz].max())/(self[ux].max()+self[uy].max()+self[uz].max()))
    xyz=go.Scatter3d(x=self[xx], y=self[yy], z=self[zz], name=self.info)
    mode_symbol_dask = marker_to_plotly_marker(style_tracer)
    xyz['mode'] = mode_symbol_dask['mode']
    if 'markers' in xyz['mode']:
        xyz['marker']['symbol'] = mode_symbol_dask['symbol']
    if 'lines' in xyz['mode']:
        #xyz['line']['shape']='spline'
        xyz['line']['dash'] = mode_symbol_dask['dash']
    xyz['marker']['colorscale']='Rainbow'
    xyz['marker']['size']=3
    trace = []
    trace.append(xyz)
    for i,coordonnees in enumerate(zip(self[xx][::unsur],self[yy][::unsur],self[zz][::unsur],self[ux][::unsur],self[uy][::unsur],self[uz][::unsur])):
        vec_x=[coordonnees[0],coordonnees[0]+scal*coordonnees[3]]
        vec_y=[coordonnees[1],coordonnees[1]+scal*coordonnees[4]]
        vec_z=[coordonnees[2],coordonnees[2]+scal*coordonnees[5]]
        vector=go.Scatter3d(x=vec_x,y=vec_y,z=vec_z,marker = dict( size = 1),line = dict(width = 2),name='')
        trace.append(vector)
    xlab = xx if xlabel =='' else xlabel
    ylab = yy if ylabel =='' else ylabel
    zlab = zz if ylabel =='' else ylabel
    layout = go.Layout(title=titre,margin=dict(l=0,r=0,b=0,t=0),
                       scene = dict(aspectmode='data',xaxis= dict(title= xlab,nticks=quadril_x),
                        yaxis=dict(title= ylab,nticks=quadril_y),
                        zaxis=dict(title= zlab,nticks=quadril_z)),showlegend=False)
    fig = go.Figure(data=trace, layout=layout)
#    (_,_,_,text)=traceback.extract_stack()[-2]
#    def_name = text[:text.find('.vector3D')].strip()
#    SPY.append({'method': 'vector3D','ux':ux,'uy':uy,'uz':uz,'x':xx,'y':yy,'z':zz,'name':def_name})
    return iplot(fig, filename='vecteur3D')

def get_kinematic(self,xyzt,**d):
    xyzt = format_to_valid_y(xyzt)
    dt = xyzt[-1]
    option = d.get('opt',(1,0))
    #create velocity
    txt_v,txt_a, txt_r = '','',''
    for elem in xyzt[:len(xyzt)-1]:
        self[f"v{elem}"] = self.derive(elem,dt,opt=option)
        txt_v += f"v{elem}**2 +"
    txt_v = txt_v[:-1]
    for elem in xyzt[:len(xyzt)-1]:
        self[f"a{elem}"] = self.derive(f"v{elem}",dt,opt=option)
        txt_a += f"a{elem}**2 +"
    txt_a = txt_a[:-1]
    for elem in xyzt[:len(xyzt)-1]:
        txt_r += f"{elem}**2 +"
    txt_r = txt_r[:-1]
    self['r']=self.eval(f'({txt_r})**(1/2)')
    self["v"]=self.eval(f"({txt_v})**(1/2)")
    self["a"]=self.eval(f"({txt_a})**(1/2)")
    return self.head()

def compute_ntc_model(self,temp='T',resistor='R',**d):
    T0=298.15
    print(f"compute log{resistor} and inverse 1/{temp} ..\n")
    self['__invT']=1/(273.15+self[temp])
    self['__lnR']=np.log(self[resistor])
    anim_bar(100,8,0.25)
    print('\n')
    print("compute regression ...\n")
    anim_bar(100,10,0.3)
    print('\n')
    idx = np.isfinite(self['__invT']) & np.isfinite(self['__lnR'])
    resultat = np.polyfit(self['__invT'][idx],self['__lnR'][idx],1)
    #print(f"résultat .. ln(R)={resultat[0]}*(1/T)+{resultat[1]}")
    beta = resultat[0]
    R0 = np.exp(resultat[1]+beta/T0)
    print(f'characteristics of the resistor NTC ... \nBeta={resultat[0]:.1f}\tR0={R0:.1f} Ohm  @{T0-273.15} °C')
    self['__R_mod']=R0*np.exp(beta*(1/(273.15+self[temp])-1/T0))
    print("\ngraphic of regression")
    self.scatter2D(x=temp,y=[resistor,'__R_mod'],**d)
    self.del_columns('__invT','__lnR','__R_mod') 

def derive(self,df,dt,opt=(1,0)):
    a,b = opt[0],opt[1]
    return (self[df].shift(-a)-self[df].shift(b))/(self[dt].shift(-a)-self[dt].shift(b))

def delta(self,df,opt=(1,0)):
    a,b = opt[0],opt[1]
    return (self[df].shift(-a)-self[df].shift(b))

def norme(self,*args):
    return np.sqrt(sum(self[arg]**2 for arg in args))

def del_columns(self,*y,**kwarg):
    y=list(y)
    y_elim = []
    display = kwarg.get('display',True)
    for elem in y:
        if elem not in list(self):
                if display:
                    print(f"... La colonne {elem} n'existe pas")
        else:
            y_elim.append(elem)
    if y_elim:
        self.drop(columns=y_elim,inplace=True)
    return self.head()

       
def nonlinear_regression(self,x,y,ym='--',func = lambda x,A,w,phy:A*np.sin(w*x+phy),ajout_col=False,tracer_courbe=False):
    if (x not in list(self.columns)) or (y not in list(self.columns)):
        print(f"la colonne {x} ou {y} n'existe pas dans votre dataframe")
        return self.columns
    idx = np.isfinite(self[x]) & np.isfinite(self[y])
    popt, _ = curve_fit(func, self[x][idx], self[y][idx])
    a = getsource(func)
    ok = False
    if "lambda" in a:
        ok = True
        i_deb = a.find(":",a.index("lambda"))+1
        i_fin = a.find(",",i_deb)
        a[i_deb:i_fin]
    list_arg = str(signature(func)).strip('(').strip(')').split(',')[1:]
    txt = ''
    for arg,val in zip(list_arg,popt):
        txt += f'{arg}={val}\n'
    if ym == '--':
        ym = y+'_mod'
    print(f"les paramètres de votre modèle {y}={a[i_deb:i_fin] if ok else ''} sont:\n{txt}")
    if tracer_courbe or ajout_col:
        self[ym] = func(self[x],*popt) 
        #calculate r**2
        r2 = r2_score(self[ym],self[y])
        print(f"coef de détermination R²={r2}")
    if tracer_courbe:
        self.scatter2D(x=x,y=[y,ym],style_tracer='-o')
    if not ajout_col:
        self.del_columns(ym)

@ set_spy
def regression(self,x,y,ym='--',degre=1,ajout_col=False,tracer_courbe=True,**d):
    """ 
    Méthode/Fonction appliqué à une dataframe -> retourne une modélisation.
    
    Regression permet d'obtenir une modélisation entre 2 colonnes d'une dataframe df (courbe de tendance)
    * x (str): nom de la colonne correspondant à l'abcisse Ex : x='t(s)'
    * y (str): nom de la colonne correspondant à l'ordonnée, c'est la grandeur qui sera modélisée Ex: y='VX'
    * ym (str): nom de l'ordonnée modélisée Ex: y='VX_mod'
    * degre (0, 1 ou 2): est le depré du polynome (degre=1 pour une regression linéaire)
    * ajout_col (booleen): permet de creer une nouvelle colonne nommée ym dans la dataframe self (défaut ajout_col=False)
    * tracer_courbe : Si True, affiche la courbe y=f(x) et y_mod=f(x)
    
    Exemple : On veux modéliser par une relation linéaire la colonne 'V' en fonction de 'R' de la dataframe venus sans 
    creer une nouvelle colonne
    >venus.regression(x='V',y='R',degre=1) 
    
    résultat :
    meilleur modèle linéaire entre V et R est :
    V = 121558311055.52502 x R - 4.5721051617156645
    """
    if (x not in list(self.columns)) or (y not in list(self.columns)):
        print(f"la colonne {x} ou {y} n'existe pas dans votre dataframe")
        return self.columns
    degre = int(f_borne(degre,0,3))
    idx = np.isfinite(self[x]) & np.isfinite(self[y])
    resultat = np.polyfit(self[x][idx],self[y][idx],degre)
    p=np.poly1d(resultat,variable=x)
    if ym == '--':
        ym = y+'_mod'
    if tracer_courbe or ajout_col:
        self[ym] = np.poly1d(resultat)(self[x])
    print(f'meilleur modèle de degré {degre} entre {x} et {y} est :')
    print(y+'=')
    print(p)
    #calculate r**2
    r2 = r2_score(self[ym][idx],self[y][idx])
    txt0 = ' ... le modèle est très bon !!!' if r2>0.999 else ''
    print(f"coef de détermination R²={r2}")
    if tracer_courbe:
        self.scatter2D(x=x,y=[y,ym],**d)
    if not ajout_col:
        self.del_columns(ym)
#    (_,_,_,text)=traceback.extract_stack()[-2]
#    df_name = text[:text.index('.reg')].strip()
#    SPY.append({'method':'regression','x':x,'y':y,'degre':degre,'name':df_name})


def f_read_wav(fichier,typ='tuple'):
    """
    fonction qui retourne la table des temps et celle des amplitudes (série numpy)
    Arguments:
        * fichier (wav) : chemin d'un fichier son
        * typ (str): si typ='tuple' la fonction retourne la tuple t,data ; si typ='dict' la fonction retourne un dictionnaire
            ayant pour clé 't','data' et 'sr' (samplerate)
    """
    rate,data = wavfile.read(fichier)
    nb_data = len(data)
    tmax = nb_data / rate
    t = np.linspace(0,tmax,nb_data)
    if typ == 'tuple':
        return t,data
    return {'t':t, 'data':data, 'sr':rate}

def f_plot(x, y, titre='Courbe sans titre!!!', labels=[], xlabel='pas de nom', ylabel='pas de nom', quadril_x=0, quadril_y=0):
    """
    fonction qui retourne un graphique
    Arguments:
        * x (série numpy): nom de l'absisse
        * y (série numpy): nom des l'ordonnées (ex y=['y1','y2'])
        * titre (str): titre du tracé - Defaut 'Courbe sans titre!!!'
        * labels (list): liste des labels des ordonnées y
        * xlabel (str): nom de l'axe des absisses - Defaut 't(s)'
        * ylabel (str): nom de l'axe des ordonnées
    
    Exemple : Soient y1, y2 et t des séries numpy de taille identique, pour tracer y1=f(t) et y2=f(t)
            > plot(t,y=[y1,y2],titre='y1=f(t) et y2=f(t)')
    """
    if isinstance(y,np.ndarray):
        y=[y]
    courbes=[]
    if len(labels)<len(y):
        labels += [f'courbe n°{i}' for i in range(len(y)-len(courbes))]
    for elem,label in zip(y,labels):
        if isinstance(elem,np.ndarray):
            courbes.append(go.Scatter(x=x, y=elem, mode='lines', name=label))
        else:
            print(f"L'argument n°{i} n'est pas une série numpy")
    layout = go.Layout(title= titre,xaxis= dict(nticks=quadril_x,title= xlabel),yaxis=dict(nticks=quadril_y,title= ylabel))
    fig = go.Figure(data=courbes, layout=layout)
    return iplot(fig,filename=titre)

def f_plot2(son=None,titre='Courbe sans titre!!!',xlabel='t(s)'):
    """
    fonction qui retourne un graphique
    Arguments:
        * son (dict): son audio ou liste de sons dont on veux tracer la (les) courbe(s)
        * titre (str): titre du tracé - Defaut 'Courbe sans titre!!!'
        * xlabel (str): nom de l'axe des absisses - Defaut 't(s)'
    
    Exemple : Soient son1 et son2 des sons, pour tracer leurs évolutions temporelles
            > f_plot2(son=[son1,son2],titre='un super titre',xlabel='t_s')
    """
    if not isinstance(son,list):
        son=[son]
    courbes=[]
    for i,elem in enumerate(son):
        if isinstance(elem,dict):
            if ('t' in elem) and ('data' in elem) and ('sr' in elem):
                courbes.append(go.Scatter(x=elem['t'],y=elem['data'],mode='lines',name=f'courbe n°{i}'))
    layout = go.Layout(title= titre,xaxis= dict(title= xlabel),yaxis=dict(title= 'signal'))
    fig = go.Figure(data=courbes, layout=layout)
    return iplot(fig,filename=titre)   
 
def f_plot_fft(son = None,x = None,y = None,titre='Courbe sans titre!!!'):
    """
    fonction qui retourne le graphique du spectre (fft) d'un son
    Arguments:
        * t (série numpy): nom de l'absisse
        * y (série numpy): nom de l'ordonnée
        * titre (str): titre du tracé - Defaut 'Courbe sans titre!!!'
        * son (dict) (oprionnel) : dictionnaire contenant t et data
    Exemple : Soient y et t des séries numpy de taille identique, pour tracer le spectre de y
            > plot_fft(t,y,titre='Spectre de y')
    """
    t = x
    data = y
    if isinstance(son,dict) and ('t' in son) and ('data' in son) and ('sr' in son):
        Y=np.abs(fft(son['data']))
        t=son['t']
        freq = fftfreq(len(son['data']), t[1] - t[0])
        data=None
    if isinstance(t,np.ndarray) and isinstance(data,np.ndarray):
        Y = np.abs(fft(data))
        freq = fftfreq(len(data), t[1] - t[0])
    f_plot(freq,Y,titre=titre,xlabel='f (Hz)')
    return {'freq':freq,'fft':Y}

def f_play_audio(son=None,t=None,data=None,file=None,rate=None):
    if isinstance(son,dict):
        return ip.display.Audio(data=son['data'],rate=son['sr'],autoplay=True)
    if isinstance(t,np.ndarray) and isinstance(data,np.ndarray):
        f_ech = len(t)/t.max()
        return ip.display.Audio(data=data,rate=f_ech,autoplay=True)
    if isinstance(file,str):
        return ip.display.Audio(filename=file,rate=rate,autoplay=True)

def f_delete_freq(son=None,freq=100,largeur=20):
    """
    Fonction qui retourne un son dont on aura retirer quelques fréquences
    Arguments:
        * son (dict clés 't','data','sr'): son à traiter
        * freq (float): fréquence ou liste de fréquences en Hertz (ex [150,140,552]) - Défaut 100
        * largeur (float): largeur de l intervalle de suppression en Hertz (ex si freq=150Hz et largeur=20Hz alors toutes les fréquences
        entre 130 et 170 seront supprimées) - Défaut 20
    """
    if not isinstance(freq,list):
        freq=[freq]
    dataFreq = fftshift(fft.fft(son['data']))
    sampleRate = son['sr']
    n = len(son['data'])
    w = largeur
    for f in freq:
        dataFreq[n/2 + n*f/sampleRate - w : n/2 + n*f/sampleRate + w] = 0
        dataFreq[n/2 - n*f/sampleRate - w : n/2 - n*f/sampleRate + w] = 0
    resultat = fft.ifft(fft.fftshift(dataFreq))
    return {'t':son['t'],'data':resultat,'sr':son['sr']}

def animation():
    anim = r"-/|\o"
    for i in range(20):
        sleep(0.05)
        print(anim[i % len(anim)],end='\r',flush=True)


def normalize(self,y,limit=(1,100),inplace=True):
    """
    normalise une la colonne y dans le limite de limit
    arguments:
        y (str) : nom de la colonne à normaliser
        limit (tuple ou list): limites de la normalisation
    Exemple:
        'x' est une colonne de la dataframe df variant de 0 à 527.
        pour normaliser la colonne 'x' et la faire varier de 0 à 100
        >df.normalize('x',limit=(0,100))
    """
    if isinstance(limit,(tuple,list)):
        limit = limit[:2]
    elif isinstance(limit,(int,float)):
        limit = [0,limit]
    elif isinstance(limit,str):
        if limit in self.columns:
            limit=[self[limit].dropna().min(),self[limit].dropna().max()]
        else:
            print(f"column {limit} does not exist ... limit fixed to [0,100]")
            limit = [0,100]
    else:
        limit = [0,100]
    y_min=self[y].dropna().min()
    y_max=self[y].dropna().max()
    if inplace:
        self[y] = self[y].apply(lambda y: (y- y_min)/(y_max-y_min)*(max(limit)-min(limit))+min(limit))
    else:
        return self[y].apply(lambda y: (y- y_min)/(y_max-y_min)*(max(limit)-min(limit))+min(limit))
        


def check_info(df):
    return False if "bound method DataFrame.info" in str(df.info) else True
    
def dict_compare(d1, d2):
    d1_keys = set(d1.keys())
    d2_keys = set(d2.keys())
    intersect_keys = d1_keys.intersection(d2_keys)
    same = set(o for o in intersect_keys if d1[o] == d2[o])
    return  same



def get_SPY():
    return SPY


def give_me_crypto(levels=0):
    if not isinstance(levels,(list,tuple)):
        levels = [levels]
    for level in levels:
        d = str(SPY[-level-1])
        dc = f_crypt(d,SPY_KEY,"crypt")
        txt = f"level={level}||{d}||'{dc}'"
        return txt

def f_crypt(y,key,option="crypt"):
    clair = sorted(r"ABCDEFGHIJKLMNOPQRSTUVWXYZ abcdefghijklmnopqrstuvwxyz0123456789²&é'(-è_çà)#{[|^@]}?,;.:/!§*+µ$£%=",key=str.lower)
    clair = "".join(clair)
    crypte = "".join([clair[(key+i)%len(clair)] for i,_ in enumerate(clair)])
    if option == "crypt":
        return "".join([crypte[clair.find(i)] for i in y])
    else:
        clair = "".join([crypte[(-key+i)%len(crypte)] for i,_ in enumerate(crypte)])
        return "".join([clair[crypte.find(i)] for i in y])
       
def f_input(txt='',output='float',limit=None,choice=None,sep=',',**d):
    #sep_list = list(r"-,;:_/\")
    sep_list = "/\\,;:-"
    if sep not in sep_list:
        print(f"Err: delimiter sep='{sep}' must be in ({sep_list})")
        return None
    output_list = ["float","float_list","int","int_float","str"]
    if output not in output_list:
        print(f"Err: argument output={output} must be in {output_list}")
        return None
    if isinstance(choice,(tuple,list)):
        affichage = f"choice={choice}"
        option = 'choice'
    elif isinstance(limit,(tuple,list)):
        limit = limit[:2]
        affichage = f"limit={limit}"
        option = 'limit'
    else:
        affichage = '*'
        option = ''
    while True:
        res = input(f"{txt} [{Fore.GREEN}{output}{Style.RESET_ALL}][{Fore.RED}{affichage}{Style.RESET_ALL}]>")
        if res.lower() == "_exit":
            break
        if output == 'float':
            try:
                resultat = float(res)
                if option == 'limit':
                    if (max(limit)>=resultat>=min(limit)):
                        break
                    else:
                        print(f"Err: input {resultat} out of range {limit}")
                elif option == 'choice':
                    if resultat in choice:
                        break
                    else:
                        print(f"Err: input {resultat} not in choice {choice}")
                else:
                    break
            except:
                print("Result isnt float")
        elif output == 'int':
            try:
                resultat = int(res)
                if option == 'limit':
                    if (max(limit)>=resultat>=min(limit)):
                        break
                    else:
                        print(f"Err: input {resultat} out of range {limit}")
                elif option == 'choice':
                    if resultat in choice:
                        break
                    else:
                        print(f"Err: input {resultat} not in choice {choice}")
                else:
                    break
            except:
                print("Err:Result isnt integer") 
        elif output == "float_list":
            try:
                resultat = [float(i) for i in res.split(sep)]
                if option == 'limit':
                    if all([(max(limit)>=i>=min(limit)) for i in resultat]):
                        break
                    else:
                        print(f"Err: input {resultat} out of range {limit}")
                elif option=='choice':
                    if all([i in choice for i in resultat]):
                        break
                    else:
                        print(f"Err: input {resultat} not in choice {choice}")
                else:
                    break
            except:
                print(f"les valeurs données ne sont pas des floats")
        elif output == "int_list":
            try:
                resultat = [int(i) for i in res.split(sep)]
                if option == 'limit':
                    if all([(max(limit)>=i>=min(limit)) for i in resultat]):
                        break
                    else:
                        print(f"Err: input {resultat} out of range {limit}")
                elif option == 'choice':
                    if all([i in choice for i in resultat]):
                        break
                    else:
                        print(f"Err: input {resultat} not in choice {choice}")
                else:
                    break
            except:
                print(f"il y a un probleme")
        elif output == 'str':
            resultat = res
            if option == 'choice':
                if resultat in choice:
                    break
                else:
                    print(f"Err: input {resultat} not in choice {choice}")
            else:
                break
         
    return resultat

def f_input_list(txt, limit=None, sep=','):
    result = []
    result_txt = f_input(txt,opt='str')
    try:
        result = [float(i) for i in result_txt.split(sep)]
    except:
        print(f'il y a un problème dans vos valeurs :\n{result_txt}')
        return None
    if limit != None:
        result = [f_borne(i,limit[0],limit[1]) for i in result]    
    return result
          
def f_borne(x,xmin,xmax):
    return max(xmin,min(xmax,x))             

def f_sin(x):
    """
    calcule le sinus de x ou x est en degré
    """
    x = x/180*np.pi
    return np.sin(x)

def f_cos(x):
    """
    calcule le sinus de x ou x est en degré
    """
    x = x/180*np.pi
    return np.cos(x)
    
def f_arcsin(x):
    """
    calcule le sinus d'arc de x et retourne la valeur en degré
    """
    return np.arcsin(x)/np.pi*180

def draw_refrac(i1,i2,n1='',n2='',d = 10.0):
    trace0 = go.Scatter(x=[0,d/2,-d/2],y=[0,d/2,-d/2],text=['normale',f"n1={n1:.4f}",f"n2={n2:.4f}"],mode='text')
    data = [trace0]
    layout = {'xaxis': {'range': [-d, d],'constrain':'domain'},'yaxis': {'range': [-d, d],'scaleanchor':'x'},
    'shapes': [ {'type': 'line','x0': 0,'y0': 0,'x1': -d*f_sin(i1),'y1': d*f_cos(i1),
                 'line': {'color': 'rgb(55, 128, 191)','width': 3,}},
                {'type': 'line','x0': 0,'y0': 0,'x1': d*f_sin(i2),'y1': -d*f_cos(i2),
                 'line': {'color': 'rgb(50, 171, 96)','width': 4}},
                 {'type':'rect','x0':-d,'y0':-d,'x1':d,'y1':0,'fillcolor': 'rgba(128, 0, 128, 0.7)','opacity':0.5}]}
    fig = {'data': data,'layout': layout}
    return iplot(fig, filename='shapes-lines')
 
def f_test(func,result,*arg,ecart = 1e-4):
    r = func(*arg)
    if isinstance(r,float):
        resul_test =  np.abs(r-result)/r<ecart
    if isinstance(r,int):
        resul_test = (r == result)
    if resul_test:
        print(f"{Fore.GREEN}le test de la fonction {func.__name__} à réussi .. {Style.RESET_ALL}")
    else:
        print((f"{Fore.RED}le test de la fonction {func.__name__} est un echec{Style.RESET_ALL} .. il faut recommencer "))

def y_to_str(y):
    if isinstance(y,str) and '/' in y:
        return '/'.join(sorted(y.split('/'),key=str.lower))
    if isinstance(y,str) and '/' not in y:
        return y
    if isinstance(y,list):
        return '/'.join(sorted(y,key=str.lower))
    return None

def format_to_valid_y(y):
    if isinstance(y,str) and '/' in y:
        return y.split('/')
    if isinstance(y,str) and '/' not in y:
        return [y]
    if isinstance(y,list):
        return y
    if isinstance(y,tuple):
        return list(y)

def Nasa_horizons_query(id='3',id_type='majorbody', origin='@sun',epochs=dict(start='2016-10-01',stop='2017-10-02',step='10d'),**d):
    print("connect to NASA JPL Horizons ...\r",end='\r')
    obj = Horizons(id=id,id_type=id_type,location=origin,epochs=epochs).vectors().to_pandas()
    astre = obj['targetname'][0]
    if d.get('display_log',True) == True:
        print(f"query of {astre} ..... start={epochs['start']}..end={epochs['stop']}.... finish")
    if d.get('keep_r',False):
        obj.rename({'range':'r'}, axis=1, inplace=True)
        obj['r'] = 1.496e+11*obj['r']
    if not d.get('keep_date',False):
        obj.del_columns('datetime_str',display=False)
    else:
        obj['datetime_str']=pd.to_datetime(obj['datetime_str'],format= 'A.D. %Y-%b-%d %H:%M:%S.0000')
        obj.rename({'datetime_str': 'date'}, axis=1, inplace=True)
    obj.del_columns('targetname', 'H', 'G',
   'vx', 'vy', 'vz', 'lighttime', 'range', 'range_rate',display=False)
    delta_t = (obj['datetime_jd'][1]-obj['datetime_jd'][0])*24*3600
    obj.del_columns('datetime_jd',display=False)
    obj['t'] = delta_t*obj.index
    #convert to m
    obj['x'] = 1.496e+11*obj['x']
    obj['y'] = 1.496e+11*obj['y']
    obj['z'] = 1.496e+11*obj['z']
    obj.info = f"{astre}"
    return obj

def Nasa_position_query(id='3',id_type='majorbody', origin='@sun',date=None):
    if date==None:
        date = str(datetime.date.today()) 
    day_after = str(datetime.datetime.strptime(date, '%Y-%m-%d')+datetime.timedelta(days=1)).strip('00:00:00').strip()   
    obj = Nasa_horizons_query(id=id,id_type=id_type,origin=origin,epochs=dict(start=date,stop=day_after,step='1d'),display_log=False)
    return obj['x'].iloc[0],obj['y'].iloc[0],obj['z'].iloc[0]

def display_progress(x, tot):
    p=int(100*x/tot)
    deb,fin='▓'*p,'░'*(100-p)
    print('|'+deb+fin+'|'+str(p)+"%",end='\r') 

def anim_bar(xmax,step,dt):
    for i in range(0,xmax,step):
        display_progress(i,xmax)
        sleep(dt)

def gd_dl_link(link):
    txt = 'https://drive.google.com/uc?export=download&id='
    x=link.find('id=')
    return txt+link[x+3:]

def get_columns_list(self,opt=None):
    def catch(func, handle=lambda e : e, *args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return "***"
    t = PrettyTable()
    cols = [col for col in self.columns]
    typs = [typ for typ in self.dtypes]
    couns = [self[c].count() for c in cols]
    t.add_column("Column",[f"'{c}'" for c in cols])
    t.add_column("Type",typs)
    t.add_column("nb",couns)
    if opt == 'add_stat':
        t.add_column('max',[catch(lambda: self[c].max()) for c in cols])
        t.add_column('min',[catch(lambda: self[c].min()) for c in cols])
        t.add_column('mean',[catch(lambda: self[c].mean()) for c in cols])
        t.add_column('std dev',[catch(lambda: self[c].std()) for c in cols])
    print(t)


def read_lab(filename,nb_mes=None,encoding=None):
    """
    fonction qui permet de lire un fichier atelier-scientifique d'extension .lab
    et retourne une dataframe (pandas) contenant les mesures.
    Remarque:
        Un fichier .lab contient bcp d'informations utiles à l'atelier scientifique.
        La fonction tente une recherche des noms des variables. 
    Arguments:
        filename (str): nom du repertoire/fichier (ex d:\toto\tutu.lab)
        nb_mes (int)  : limite le nombre de mesures (defaut None)
        encoding (str): souvent 'utf-16' ou ne rien mettre (defaut None)
    Retourne:
        Pandas dataframe
    Utilisation:
        df = pd.read_lab(r'd:\toto\tutu.lab',encoding='utf-16',nb_mes=32)
    """
    #Merci a thispointer.com pour cette fonction
    def getDuplicateColumns(df):
        '''
        Get a list of duplicate columns.
        It will iterate over all the columns in dataframe and find the columns whose contents are duplicate.
        :param df: Dataframe object
        :return: List of columns whose contents are duplicates.
        '''
        duplicateColumnNames = set()
        # Iterate over all the columns in dataframe
        for x in range(df.shape[1]):
            # Select column at xth index.
            col = df.iloc[:, x]
            # Iterate over all the columns in DataFrame from (x+1)th index till end
            for y in range(x + 1, df.shape[1]):
                # Select column at yth index.
                otherCol = df.iloc[:, y]
                # Check if two columns at x 7 y index are equal
                if col.equals(otherCol):
                    duplicateColumnNames.add(df.columns.values[y])

        return list(duplicateColumnNames)

    idxs = []
    vector_lines = []
    idx_noms=[]
    noms = []
    # recherche des grandeurs du tableur 
    if encoding != None:
        with codecs.open(filename,"r",encoding=encoding) as inpt:
            lines = inpt.readlines()
    else:
        with codecs.open(filename,"r") as inpt:
            lines = inpt.readlines()       
    for idx,line in enumerate(lines):
        if 'points = table' in line:
            idxs.append(idx)
    #recherche index des nom des grandeurs
    for idx,line in enumerate(lines):
        if 'vecteur' in line:
            idx_noms.append(idx)
    #recherche nom ou oid s'il n'y en a pas
    num_nom_inconnu = 0
    for idx in idx_noms:
        if 'nom' in lines[idx+2]:
            nom = lines[idx+2].strip().strip('nom = "').strip('"')
            if nom in noms:
                nom =f"{nom}_{num_nom_inconnu}"
                num_nom_inconnu += 1
            noms.append(nom)
        elif 'oid' in lines[idx+1]:
            noms.append(lines[idx+1].strip())
        else:
            noms.append(f"unknow_{num_nom_inconnu}")
            num_nom_inconnu += 1
    #initialisation des résultats
    resultats = {nom:[] for nom in noms}
    #recherche des valeurs

    for idx,nom in zip(idxs,noms):
        results = []
        for line in lines[idx+1:]:
            if '}' in line:
                break
            for num in line.split():
                try:
                    results.append(float(num))
                except:
                    pass
        resultats[nom]=results if nb_mes == None else results[:nb_mes]
    r = pd.DataFrame.from_dict(resultats,orient='index').transpose()
    # Delete duplicate columns
    r = r.drop(columns=getDuplicateColumns(r))
    print(r.get_columns_list())
    return r

pd.DataFrame.read_lab = read_lab
pd.DataFrame.delta = delta
pd.DataFrame.vector = vector
pd.DataFrame.vector3D = vector3D
pd.DataFrame.regression = regression
pd.DataFrame.scatter3D = scatter3D
pd.DataFrame.scatter2D = scatter2D
pd.DataFrame.scatter1D = scatter1D
pd.DataFrame.display_U = display_U
pd.DataFrame.derive = derive
pd.DataFrame.norme = norme
pd.DataFrame.del_columns = del_columns
pd.DataFrame.nonlinear_regression = nonlinear_regression
pd.DataFrame.normalize = normalize
pd.DataFrame.scatterPolar = scatterPolar
pd.DataFrame.histogram = histogram
pd.DataFrame.draw_vectors = draw_vectors
pd.DataFrame.get_kinematic = get_kinematic
pd.DataFrame.compute_ntc_model = compute_ntc_model
pd.DataFrame.vector_by_norm_and_direction = vector_by_norm_and_direction
pd.DataFrame.vector_by_norm_and_direction3D = vector_by_norm_and_direction3D
pd.DataFrame.get_columns_list = get_columns_list