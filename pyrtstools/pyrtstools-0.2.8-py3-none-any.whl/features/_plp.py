import numpy as np

class PLP_Features:
    
    def __init__(self, sample_rate, frame_length, hamming=True):
        self.sample_rate = sample_rate
        self.frame_length = frame_length
        self._window_fun = np.hamming(frame_length) if hamming else None
        self.barkfbank = bark_bands(1024,sample_rate)
        self.barkfbank.resize((512, len(self.barkfbank)))
    
    def process_frame(self, frame,
            num_filter,
            dorasta=True):

        # Window_fun
        if self._window_fun is not None:
            frame = frame * self._window_fun
        # Power spectrum
        pow_spect = power_spectrum(frame)[1:]

        # Bark filterbank
        c_spectrum = np.matmul(self.barkfbank, pow_spect)

        # Rasta
        if dorasta:
            #smoke weed everyday
            pass

        #Equal loudness - pre emphasis

    def process(self, signal):
        pass


def bark_bands(fft_length, fs, nfilts = 0, band_width = 1, min_freq = 0, max_freq = 0):
    if max_freq == 0:
        max_freq = fs / 2
        
    min_bark = hz2bark(min_freq)
    nyqbark = hz2bark(max_freq) - min_bark
    
    if nfilts == 0 :
        nfilts = int(np.ceil(nyqbark) + 1)
    
    wts = np.zeros((nfilts, fft_length))
    
    step_barks = nyqbark / (nfilts - 1)
    binbarks = hz2bark(np.arange(0, fft_length / 2 + 1) * fs / fft_length)
    
    for i in range (nfilts):
        f_bark_mid = min_bark + (i * step_barks)
        lof = (binbarks - f_bark_mid) - 0.5
        hif = (binbarks - f_bark_mid) + 0.5
        wts[i, 0 : fft_length // 2 + 1] = np.power(10, np.minimum(0, np.divide(np.minimum(hif, -2.5 * lof), band_width)))
    return wts

def power_spectrum(frame: np.ndarray, fft_size=512):
        """Calculates power spectrogram"""
        fft = np.fft.rfft(frame, n=fft_size)
        return (fft.real ** 2 + fft.imag ** 2) / fft_size

def hz2bark(freq):
    return 6 * np.arcsinh(freq / 600)

def bark2hz(bark):
    return 600 * np.sinh(bark / 6)