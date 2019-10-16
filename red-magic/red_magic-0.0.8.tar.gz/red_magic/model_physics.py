#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@author: misiak

"""
import numpy as np
import matplotlib.pyplot as plt

from .psd import inv_psd

def exp_heaviside(x):
    """
    to avoid exp overflow, some tweak is needed
    """
    x_aux = np.where(x>0, -np.inf, x)
    return np.exp(x_aux)


def pulse_1exp(param, time_array):
    """
    pulse = Heaviside(t-d) * a * ( exp(-(t-d)/b) - exp(-(t-d)/c) )
    """
    
    b, c, d = param
    
    x = -(time_array-d)/b
    y = -(time_array-d)/c
    pulse_array = exp_heaviside(x) - exp_heaviside(y)
    return pulse_array
    

class Model_white_noise():
    
    def __init__(self, level=1):
        
        self.level = level
    
    def psd(self, fs, wlen):
        return self.level * np.ones(int(fs*wlen/2))
    
    def sample(self, fs, wlen):
        return inv_psd(self.psd(fs, wlen), fs)
        

class Model_pulse(): 
    
    def __init__(self, model='1exp'):

        self.type = model.lower()
        
        if self.type == '1exp':
            self.function = self._model_1exp
            self.parameters_0 = [5e-2, 5e-3, 0]
        elif self.type == '2exp':
            self.function = self._model_2exp
            self.parameters_0 = [0.1, 5e-2, 20e-2, 5e-3, 0]       
        elif self.type == '3exp':
            self.function = self._model_3exp
            self.parameters_0 = [0.1, 0.1, 2e-2, 10e-2, 50e-2, 5e-3, 0]    
        else:
            raise Exception((
                    'Model \"{}\" unknown or not implemented yet.'
            ).format(self.type))
            
        self.time_array_0 = np.arange(0, 1, 1e-3)
        self.pulse_array_0 = self.function(self.parameters_0, self.time_array_0)
        self.std_array_0 = 1e-3 * np.ones(self.pulse_array_0.shape)
        self.fake_array_0 = self.fake_data(
                self.parameters_0,
                self.time_array_0,
                np.random.normal(loc=0, scale=self.std_array_0)
        )

    def _model_1exp(self, param, time_array):
        t, s, t0 = param
        if s<0:
            #print('s<0')
            s = 1e-20
        if s>t:
            #print('s>t')
            s=t
        param = [t, s, t0]
        return pulse_1exp(param, time_array)
    
    def _model_2exp(self, param, time_array):
        eps, t1, t2, s, t0 = param
        if eps>1:
            #print('eps>1')
            eps=1
        if eps<0:
            #print('eps<0')
            eps=0        
        p1 = [t1, s, t0]
        p2 = [t2, s, t0]
        pulse1 = (1-eps) * pulse_1exp(p1, time_array)
        pulse2 = eps * pulse_1exp(p2, time_array)
        return pulse1 + pulse2

    def _model_3exp(self, param, time_array):
        eps, ups, t1, t2, t3, s, t0 = param
        if eps+ups>1:
            eps=0
            ups=0
        p1 = [t1, s, t0]
        p2 = [t2, s, t0]
        p3 = [t3, s, t0]
        pulse1 = (1-eps-ups) * pulse_1exp(p1, time_array)
        pulse2 = eps * pulse_1exp(p2, time_array)
        pulse3 = ups * pulse_1exp(p3, time_array)
        return pulse1 + pulse2 + pulse3
    
    def fake_data(self, param, time_array, noise_array):
        """ Add a gaussian noise depending on the model_data.
        """
        model_array = self.function(param, time_array)
        fake_array = model_array + noise_array
        return fake_array    

    def expo_plot(self, num='Model ruo2 expo plot'):
        fig = plt.figure(num=num)
        ax = fig.subplots()
        ax.set_title(num)
        ax.plot(
                self.time_array_0, 
                self.pulse_array_0,
                color='slateblue',
                label='model parameters0\n{}'.format(self.parameters_0)
        )
        
        ax.errorbar(
                self.time_array_0,
                self.fake_array_0,
                yerr=self.std_array_0,
                ls='none',
                marker='.',
                color='k',
                label='fake data\n(0.1 relative error)'
        )
        
        ax.set_xlabel('Temperature [K]')
        ax.set_ylabel('Resistance [$\Omega$]')
        ax.legend()
        ax.grid(True)
        fig.tight_layout()
        
        return fig


