# -*- coding: utf-8 -*-
"""
Created on Sun Jan 27 17:35:59 2019

@author: jazzn
"""

import IPython as ip
from plotly.offline import  iplot
from scipy.io import wavfile
from scipy import fftpack as fft
from scipy import signal
import numpy as np
import plotly.graph_objs as go
from plotly.offline import  iplot

class Sound():
    def __init__(self,duree=1.,data=None,samplerate=11025.,info=''):
        self.duree=duree
        self.data=data
        self.sr=samplerate
        self.info="pas d'info particuliere"
        #if (self.data==None) or (len(self.data)<5):
        #    self.data=np.zeros(self.get_samplecount())
        self.verify()
    
    def verify(self):
        self.sr=max(min(self.sr,44100.),3000.)
        self.duree=max(min(self.duree,13.),0.1)
            
    def get_samplecount(self):
        return int(self.sr*self.duree)
    
    def define_tone(self,freq=440.,amp=1.,duree=1.,sr=11025):
        """ 
       Méthode un son possedant les frequences freq associées aux amplitudes amp
        Arguments:
            * freq (float): fréquences ou liste de fréquences
            * amp (float): amplitudes ou liste d'amplitudes
            * duree (float): durée du son.
            * sampleRate (float/int): fréquence d'échantillonage en Hz (nb d'échantillon par seconde) comprise entre 3000 et 44100 Hz

        * retourne : dictionnaire contenant le temps 't', le signal 'data' et la frequence d'échantillonnage 'sr'

        Exemple : pour générer un son (nommé 'un_son') possédant les frequences/amplitudes suivantes
                    (440 Hz,2) ; (800Hz,3) qui dure 8s avec un echantillonnage de 8000 ech/s
                >un_son=f_tone(freq=[440,800],amp=[2,3],duree=8,samplerate=8000)
        """
        if not isinstance(freq,list):
            freq=[freq]
        if not isinstance(amp,list):
            amp=[amp]
        if len(amp) != len(freq):
            print(f'Rien ne va : vous avez {len(freq)} fréquences et {len(amp)} amplitudes')
            return None
        freq=[float(i) for i in freq]
        amp=[float(i) for i in amp]
        self.sr=sr
        self.duree=duree
        self.verify()
        nb = self.get_samplecount()
        data = np.zeros(nb)
        t=np.linspace(0,self.duree,nb)
        for f,A in zip(freq,amp):
            data += A * np.sin(2*np.pi*f*t)
        self.data = data
        return self
    
    def define_sweep(self,duree=1.,samplerate=11025,fmin=440.,fmax=500.,amp=1.):
        fmin=min(max(fmin,10),44100)
        fmax=min(max(fmax,10),44100)
        if fmax<fmin:
            fmin,fmax = fmax,fmin
        self.duree=duree
        self.sr=samplerate
        self.verify()
        t=np.linspace(0,self.duree,self.duree*self.sr)
        f=fmin+t*(fmax-fmin)/(2*duree)
        Y=2*amp*np.sin(2*np.pi*f*t)
        self.data=Y
        return self

    def define_sawtooth(self,freq=440.,amp=1.,duree=1.,samplerate=11025):
        """
        """
        self.duree=duree
        self.sr=int(samplerate)
        self.verify()
        t=np.linspace(0,self.duree,self.duree*self.sr)
        Y = signal.sawtooth(2*np.pi*freq*t)
        self.data = Y
        return self
        
    def define_harmonic(self,freq=440.,amp=1.,duree=1.,samplerate=11025):
        """ 
        retourne un son (Sound) harmonieux de fréquence fondamentale freq et d'amplitudes amp
        Arguments:
            * freq (float): fréquences fondamentale
            * amp (float): amplitudes ou liste d'amplitudes
            * duree (float): durée du son.
            * sampleRate (float/int): fréquence d'échantillonage en Hz (nb d'échantillon par seconde) comprise entre 3000 et 44100 Hz

            * retourne : un son (Sound)

        Exemple : pour générer un son (nommé 'un_son') de fondamentale 440 Hz et 3 harmoniques d'amplitudes (1,5,3.5,4) (la première valeur correspond
                à la fondamentale) qui dure 2s avec 22050 ech/s
                >un_son=f_tone(freq=440],amp=[1,5,3.5,4],duree=2,samplerate=22050)
        """
        if not isinstance(amp,list):
            amp=[amp]
        self.sr=samplerate
        self.duree=duree
        self.verify()
        nb=self.get_samplecount()
        data = np.zeros(nb) 
        t=np.linspace(0,self.duree,nb)
        for i,A in enumerate(amp):
            data += A*np.sin(2*np.pi*freq*(i+1)*t) 
        self.data=data
        return self
    
    def read_from_wav(self,fichier):
        """
            fonction qui retourne un dictionnaire contenant la table des temps 't' , celle des amplitudes 'data' et la valeur de la 
            fréquence d'échantillonnage 'sr' (pour samplerate)
            Arguments:
                * fichier (wav) : chemin d'un fichier son
                * typ (str): si typ='tuple' la fonction retourne le tuple (t,data,sr) ; si typ='dict' la fonction retourne une dictionnaire
                    ayant pour clé 't','data' et 'sr' (samplerate)
                    Defaut typ='dict'

            Exemple : lire un fichier son "c:/user/truc.wav"
                    > f_read_wav("c:/user/truc.wav")
        """
        rate,data = wavfile.read(fichier)
        self.sr=rate
        self.duree = len(data) / rate
        self.verify()
        self.info=fichier
        self.data=data[0:self.get_samplecount()]
        return self
    
    def sound_plot(self,other_sound=None,titre='Courbe sans titre!!!',xlabel='t(s)'):
        """
        m"thode qui retourne un graphique
        Arguments:
            * son (dict): son audio ou liste de sons dont on veux tracer la (les) courbe(s)
            * titre (str): titre du tracé - Defaut 'Courbe sans titre!!!'
            * xlabel (str): nom de l'axe des absisses - Defaut 't(s)'

        Exemple : Soient son1 et son2 des sons, pour tracer leurs évolutions temporelles
                > f_plot2(son=[son1,son2],titre='un super titre',xlabel='t_s')
        """
        son=[self]
        if not isinstance(other_sound,list):
            son.append(other_sound)
        else:
            for elem in other_sound:
                son.append(elem)
        courbes=[]
        for elem in son:
            if isinstance(elem,Sound):
                try:
                    info = elem.info
                except:
                    info = "pas d'info"
                t = np.linspace(0,elem.duree,elem.get_samplecount())
                courbes.append(go.Scatter(x=t,y=elem.data,mode='lines',name=info))
        layout = go.Layout(title= titre,xaxis= dict(title= xlabel),yaxis=dict(title= 'signal'))
        fig = go.Figure(data=courbes, layout=layout)
        return iplot(fig,filename=titre)  
    
    def band_filter(self,freq=100,largeur=20):
        """
        Méthode qui retourne un son dont on aura retirer quelques fréquences
        Arguments:
            * freq (float): fréquence ou liste de fréquences en Hertz (ex [150,140,552]) - Défaut 100
            * largeur (float): largeur de l intervalle de suppression en Hertz (ex si freq=150Hz et largeur=20Hz alors toutes les fréquences
            entre 130 et 170 seront supprimées) - Défaut 20
        """
        if not isinstance(freq,list):
            freq=[freq]
        dataFreq = fft.fftshift(fft.fft(self.data))
        sampleRate =  self.sr
        n = len(self.data)
       # w = n*largeur/sampleRate
        for f in freq:
            deb = int(n/2 + n*(f-largeur)/sampleRate )
            fin=int(n/2 + n*(f+largeur)/sampleRate)
            dataFreq[deb : fin] = 0
            deb = int(n/2 - n*(f+largeur)/sampleRate )
            fin=int(n/2 - n*(f-largeur)/sampleRate)
            dataFreq[deb :fin ] = 0
        resultat = np.real(fft.ifft(fft.fftshift(dataFreq)))
        duree = len(resultat)/sampleRate
        #print(resultat)
        return Sound(duree=duree,data=resultat,samplerate=sampleRate)

        
    def mean_amp(self):
        return np.sqrt((self.data**2).mean())
    
    def max_amp(self):
        return self.data.max()
    
    def band_amplifier(self,freq=440.,largeur=20.,factor=10.):
        """
        Méthode qui retourne un son dont on aura amplifier quelques fréquences
        Arguments:
            * freq (float): fréquence ou liste de fréquences en Hertz (ex [150,140,552]) - Défaut 100
            * largeur (float): largeur de l intervalle de suppression en Hertz (ex si freq=150Hz et largeur=20Hz alors toutes les fréquences
            entre 130 et 170 seront amplifiées) - Défaut 20
            * factor (float) : facteur d'amplification compris entre 1 et 50 - Défaut 10
        """
        factor=min(max(factor,1),50)
        if not isinstance(freq,list):
            freq=[freq]
        dataFreq = fft.fftshift(fft.fft(self.data))
        sampleRate =  self.sr
        n = len(self.data)
        w = n*largeur/sampleRate
        for f in freq:
            deb = int(n/2 + n*(f-largeur)/sampleRate )
            fin=int(n/2 + n*(f+largeur)/sampleRate)
            dataFreq[deb : fin] = factor * dataFreq[deb : fin]
            deb = int(n/2 - n*(f+largeur)/sampleRate )
            fin=int(n/2 - n*(f-largeur)/sampleRate)
            dataFreq[deb :fin ] = factor * dataFreq[deb :fin ]
            resultat = np.real(fft.ifft(fft.fftshift(dataFreq)))
        duree = len(resultat)/sampleRate
        return Sound(duree=duree,data=resultat,samplerate=sampleRate)
    
    def set_info(self,txt):
        self.info=txt
    
    def __add__(self,other):
        if self.sr != other.sr:
            print("vos 2 sons n'ont pas la même fréquence d'échantillonage")
            return None
        self_data=self.data[:]
        other_data=other.data[:]
        if len(self_data) > len(other_data):
            other_data.resize(self_data.shape)
        else:
            self_data.resize(other_data.shape)
        duree_com = len(self_data)/self.sr
        data = self_data + other_data
        return Sound(duree=duree_com,data=data,samplerate=self.sr,info=f'{self.info} + {other.info}')
        
    def play(self):
        """
        fonction qui permet de lire un son
        Arguments:
            * son (dict): est un son
            * t (série numpy) optionnel: tableau des temps
            * data (série numpy) optionnel : tableau des amplitudes
            * file (str): nom du fichier avec son chemin
            * rate (int) : valeur de la fréquence d'échantillonnage

        Exemple 1: Lire un fichier son "c:/user/truc.wav"
                > f_play_audio(file="c:/user/truc.wav",rate=44100)
        Exemple 2: Pour lire une variable son nommé 'un_son'
                > f_play_audio(son=un_son)
        """
        return ip.display.Audio(data=self.data,rate=self.sr)     
    
    def f_plot(self,t,y,titre='Courbe sans titre!!!',xlabel='t(s)'):
        """
        fonction qui retourne un graphique
        Arguments:
            * t (série numpy): nom de l'absisse
            * y (série numpy): nom des l'ordonnées (ex y=['y1','y2'])
            * titre (str): titre du tracé - Defaut 'Courbe sans titre!!!'
            * xlabel (str): nom de l'axe des absisses - Defaut 't(s)'

        Exemple : Soient y1, y2 et t des séries numpy de taille identique, pour tracer y1=f(t) et y2=f(t)
                > plot(t,y=[y1,y2],titre='y1=f(t) et y2=f(t)')
        """
        if isinstance(y,np.ndarray):
            y=[y]
        courbes=[]
        for i,elem in enumerate(y):
            label=f'courbe n°{i}'
            courbes.append(go.Scatter(x=t,y=elem,mode='lines',name=label))
        layout = go.Layout(title= titre,xaxis= dict(title= xlabel),yaxis=dict(title= 'signal'))
        fig = go.Figure(data=courbes, layout=layout)
        return iplot(fig,filename=titre)
    
    def fft_plot(self,other_sound=None,titre='Il faut mettre un titre',**d):
        """
        fonction qui retourne le graphique du spectre (fft) d'un son
        Arguments:
            * other_sound (Sound): un son au format Sound
            * titre (str): titre du tracé - Defaut 'Courbe sans titre!!!'

        Exemple : Soit un son nommé 'un_son', pour tracer son spectre
                > plot_fft(son=un_son,titre='Spectre de un_son')
        """ 
        dataF=[self]
        if not isinstance(other_sound,list):
            other_sound=[other_sound]
        for s in other_sound:
            dataF.append(s)
        courbes=[]
        plt.ioff()
        for s in dataF:
            if isinstance(s,Sound):
                dataFreq,freq,_=plt.magnitude_spectrum(s.data,Fs=s.sr,**d)
                courbes.append(go.Scatter(x=freq,y=dataFreq,mode='lines',name=s.info))
        layout = go.Layout(title= titre,xaxis= dict(title= 'f(Hz)'),yaxis=dict(title= 'Amplitude'))
        fig = go.Figure(data=courbes, layout=layout)
        return iplot(fig,filename=titre) 
    
    def __str__(self):
        return f'info={self.info} \nduree={self.duree} s \nsamplerate={self.sr} ech/s \nnb_ech={self.get_samplecount()} \ndata={self.data} '
    
    def __repr__(self):
        return  f'info={self.info} \nduree={self.duree} s \nsamplerate={self.sr} ech/s \nnb_ech={self.get_samplecount()} \ndata={self.data} '