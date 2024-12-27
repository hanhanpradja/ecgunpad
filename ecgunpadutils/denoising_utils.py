import numpy as np
import pywt
import scipy.signal
import matplotlib.pyplot as plt
from skimage.restoration import estimate_sigma
import math

def filter_ecg_signal(ecg_signal, sampling_rate, cutoff_frequency=4.0, stopband_attenuation=60.0, butterworth_order=4):
    """
    Apply Butterworth and FIR filters to denoise an ECG signal.

    Parameters:
    - ecg_signal (array-like): The input ECG signal.
    - sampling_frequency (float): Sampling frequency of the ECG signal.
    - cutoff_frequency (float): Cutoff frequency for the FIR filter (default: 4.0 Hz).
    - stopband_attenuation (float): Desired attenuation in the stopband for the FIR filter (default: 60.0 dB).
    - butterworth_order (int): Order of the Butterworth filter (default: 4).

    Returns:
    - filtered_signal (array): The filtered ECG signal.
    """
    # Apply Butterworth filter

    ecg_signal = scipy.signal.detrend(ecg_signal, axis=-1, type='linear', bp=0, overwrite_data=False)
    nyquist_frequency = 0.5 * sampling_rate
    normalized_cutoff_frequency = 0.6
    butterworth_b, butterworth_a = scipy.signal.butter(butterworth_order, normalized_cutoff_frequency, 'low')
    butterworth_filtered_signal = scipy.signal.filtfilt(butterworth_b, butterworth_a, ecg_signal)
    
    # Determine FIR filter parameters
    min_sampling_frequency = 2 * cutoff_frequency
    fir_sampling_frequency = max(sampling_rate, min_sampling_frequency)
    fir_nyquist_rate = fir_sampling_frequency / 2
    transition_width = 5.0 / fir_nyquist_rate
    
    # Calculate FIR filter parameters
    fir_order, kaiser_beta = scipy.signal.kaiserord(stopband_attenuation, transition_width)
    if fir_order % 2 == 0:  # Ensure the filter order is odd
        fir_order += 1
    fir_filter_coefficients = scipy.signal.firwin(
        fir_order, 
        cutoff_frequency / fir_nyquist_rate, 
        window=('kaiser', kaiser_beta), 
        pass_zero=False
    )
    
    # Apply FIR filter to the Butterworth-filtered signal
    filtered_signal = scipy.signal.lfilter(fir_filter_coefficients, 1.0, butterworth_filtered_signal)
    
    return filtered_signal



def dwt_denoise(signal, 
                wavelet='sym8', 
                level=5, 
                thresholding_method='soft', 
                sigma_scale=1.0):
    
    """
    Applies denoising to a given signal using Discrete Wavelet Transform (DWT) with adjustable thresholding methods.

    Parameters:
        signal (array-like): The input signal to be denoised.
        wavelet (str): The type of wavelet to be used for transformation. Default is 'sym8'.
        level (int): The number of decomposition levels for the wavelet transform. Default is 5.
        thresholding_method (str): The type of thresholding to apply to the wavelet coefficients.
            Available options: 'hard', 'soft', 'less', 'greater', 'garrote'. Default is 'soft'.
        sigma_scale (float): Scaling factor for computing the threshold value. Default is 1.0.

    Returns:
        array-like: The denoised signal reconstructed using the inverse wavelet transform.
    
    Description:
        This function uses DWT to decompose the input signal into different levels of coefficients using the specified
        wavelet type. It estimates the noise level using the Median Absolute Deviation (MAD) on the finest scale
        coefficients, and computes a universal threshold scaled by `sigma_scale`. The coefficients are thresholded
        according to the specified method ('hard', 'soft', 'less', 'greater', or 'garrote'). The approximation
        coefficients (coeffs[0]) are set to zero to focus on denoising the detail coefficients. Finally, the modified
        coefficients are reconstructed back into the denoised signal using the inverse wavelet transform.
    """

    coeffs = pywt.wavedec(signal, wavelet, level=level)
    #coeffs[0] = np.zeros_like(coeffs[0])
    sigma = np.median(np.abs(coeffs[-1] - np.median(coeffs[-1]))) / 0.6745  # MAD estimation
    sigma *= sigma_scale
    uthresh = sigma * np.sqrt(2 * np.log(len(signal)))

    if thresholding_method == 'hard':
        coeffs[1:] = [pywt.threshold(c, value=uthresh, mode='hard') for c in coeffs[1:]]
    elif thresholding_method == 'soft':
        coeffs[1:] = [pywt.threshold(c, value=uthresh, mode='soft') for c in coeffs[1:]]
    elif thresholding_method == 'less':
        coeffs[1:] = [pywt.threshold(c, value=uthresh, mode='less') for c in coeffs[1:]]
    elif thresholding_method == 'greater':
        coeffs[1:] = [pywt.threshold(c, value=uthresh, mode='greater') for c in coeffs[1:]]
    elif thresholding_method == 'garrote':
        coeffs[1:] = [pywt.threshold(c, value=uthresh, mode='garrote') for c in coeffs[1:]]

    return pywt.waverec(coeffs, wavelet)


# def kaiser_denoise(signal, sampling_rate):

#     b, a = scipy.signal.butter(4, 0.6, 'low')
#     tempf_butter = scipy.signal.filtfilt(b, a, signal)

#     cut_off = 4
#     nyquist = sampling_rate/2
#     width = 5/nyquist
#     ripple = 60
#     O, beta = scipy.signal.kaiserord(ripple, width)
#     if O % 2 == 0:
#         O += 1
#     else:
#         O, beta = scipy.signal.kaiserord(ripple, width)
    
#     taps = scipy.signal.firwin(O, cut_off/nyquist, window=('kaiser', beta), pass_zero=False)
#     denoised = scipy.signal.lfilter(taps, 1.0, tempf_butter)

#     return denoised
    

# def SURE(lam, x):
#     n = len(x)
#     term1 = n
#     term2 = np.sum(np.minimum(np.abs(x), lam)**2)
#     term3 = -2 * len(x[x < lam])  # Corrected cardinality term
#     return term1 + term2 + term3

# def optimal_lambda(x):
#     n = len(x)
#     lam_values = np.linspace(0, np.sqrt(2 * np.log(n)), 1000)
#     SURE_values = [SURE(lam, x) for lam in lam_values]
#     return lam_values[np.argmin(SURE_values)]

# def shureshrink(x, n, lambda_star, s=1):
#     """
#     Fungsi untuk melakukan thresholding pada array x menggunakan metode ShureShrink.

#     Parameters
#     ----------
#     x : numpy array
#         Array input sinyal.
#     n : int
#         Jumlah elemen dalam sinyal (panjang sinyal).
#     s : float
#         Parameter sparsity.
#     lambda_star : float
#         Threshold awal.

#     Returns
#     -------
#     x_thresholded : numpy array
#         Array hasil thresholding berdasarkan ShureShrink.
#     """

#     # Hitung sparsity ν_s(x)
#     sum_term = 0
#     for i in range(n):
#         sum_term += (x[i] ** 2 - 1)
    
#     nu_s_x = (s ** (-1/2)) * (sum_term / np.log2(n ** (3/2)))

#     # Tentukan nilai threshold λ_ShureShrink(x)
#     if nu_s_x <= 1:
#         lambda_ShureShrink = np.sqrt(2 * np.log(n))
#     else:
#         lambda_ShureShrink = lambda_star

#     # Terapkan thresholding pada setiap elemen array x
#     x_thresholded = np.where(np.abs(x) > lambda_ShureShrink, x, 0)

#     return x_thresholded


# def dwt_denoise_sure(signal, wavelet='sym8', level=5):
#     # Dekomposisi DWT
#     coeffs = pywt.wavedec(signal, wavelet, level=level)
    
#     # Proses thresholding SURE untuk setiap level koefisien detail menggunakan MAD
#     for i in range(1, len(coeffs)):  # Lewati koefisien level 0 (approximation coefficients)
#         # Threshold berdasarkan SURE dan MAD
#         uthresh = optimal_lambda(coeffs[-1])
#         coeffs[i] = shureshrink(x=coeffs[i], n=len(coeffs[i]), 
#                                 lambda_star=uthresh)
        
#     # Rekonstruksi sinyal
#     return pywt.waverec(coeffs, wavelet)






# def dwt_denoise_auto(signal, wavelet=None, thresholding_method='soft'):
#     # 1. Pilih wavelet secara otomatis berdasarkan panjang sinyal
#     if wavelet is None:
#         # Pilih wavelet yang cocok untuk sinyal bio (misal ekg), 'db' atau 'sym' sering digunakan
#         wavelet = 'db6' if len(signal) > 1000 else 'sym4'

#     # 2. Menentukan level dekomposisi berdasarkan panjang sinyal
#     max_level = pywt.dwt_max_level(len(signal), pywt.Wavelet(wavelet).dec_len)
#     # Batasi level agar tidak terlalu besar untuk sinyal pendek
#     level = min(max_level, 6)

#     # 3. Decomposisi sinyal menggunakan wavelet
#     coeffs = pywt.wavedec(signal, wavelet, level=level)
    
#     # 4. Estimasi noise level menggunakan MAD (Median Absolute Deviation)
#     sigma = np.median(np.abs(coeffs[-1])) / 0.6745

#     # 5. Ubah threshold menjadi otomatis sesuai dengan panjang sinyal
#     uthresh = sigma * np.sqrt(2 * np.log(len(signal)))
    
#     # 6. Terapkan thresholding
#     if thresholding_method == 'hard':
#         coeffs[1:] = [pywt.threshold(c, value=uthresh, mode='hard') for c in coeffs[1:]]
#     elif thresholding_method == 'soft':
#         coeffs[1:] = [pywt.threshold(c, value=uthresh, mode='soft') for c in coeffs[1:]]
#     elif thresholding_method == 'less':
#         coeffs[1:] = [pywt.threshold(c, value=uthresh, mode='less') for c in coeffs[1:]]
#     elif thresholding_method == 'greater':
#         coeffs[1:] = [pywt.threshold(c, value=uthresh, mode='greater') for c in coeffs[1:]]
#     elif thresholding_method == 'garrote':
#         coeffs[1:] = [pywt.threshold(c, value=uthresh, mode='garrote') for c in coeffs[1:]]
    
#     # 7. Rekonstruksi sinyal
#     return pywt.waverec(coeffs, wavelet)


# def denoise_ecg_signal(data, wavelet_type='sym11', sub_coeff_of_decomp=2, decision_type='soft'):
#     wavelet_type = wavelet_type
#     w = pywt.Wavelet(wavelet_type)
#     maxlev = pywt.dwt_max_level(len(data), w.dec_len) - sub_coeff_of_decomp # maximum useful level of decomposition
#     coeffs = pywt.wavedec(data, wavelet_type, level=maxlev) # wavelet decomposition of the signal

#     for i in range(1, len(coeffs)):
#         M = len(coeffs[i])
#         lambda_val = math.sqrt(2*math.log(M)) # Threshold for filtering, SureShrink method
#         coeffs[i] = pywt.threshold(coeffs[i], lambda_val, decision_type) # Filter the noise using a soft decision
#         datarec = pywt.waverec(coeffs, wavelet_type) # Wavelet reconstruction of the signal

#     return datarec