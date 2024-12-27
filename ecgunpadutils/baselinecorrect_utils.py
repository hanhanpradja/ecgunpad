import numpy as np
import scipy.signal as signal
import pywt
import matplotlib.pyplot as plt
from scipy.datasets import electrocardiogram


def remove_baseline_wander_highpass(ecg_signal, fs, cutoff=0.5):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = signal.butter(1, normal_cutoff, btype='high', analog=False)
    filtered_signal = signal.filtfilt(b, a, ecg_signal)
    return filtered_signal

def remove_baseline_wander_median(ecg_signal, window_size):
    baseline = signal.medfilt(ecg_signal, kernel_size=window_size)
    corrected_signal = ecg_signal - baseline
    return corrected_signal

def remove_baseline_wander_wavelet(ecg_signal, wavelet='db4', level=5):
    coeffs = pywt.wavedec(ecg_signal, wavelet, level=level)
    coeffs[0] = np.zeros_like(coeffs[0])  # Setkan koefisien level terendah (trend) ke nol
    corrected_signal = pywt.waverec(coeffs, wavelet)
    return corrected_signal

def remove_baseline_wander_wavelet_new(ecg_signal, wavelet='db4', level=9, threshold_min=0, threshold_max=1, sampling_rate=360):
    # Dekomposisi sinyal menggunakan wavelet
    coeffs = pywt.wavedec(ecg_signal, wavelet, level=level)

    # Menghitung frekuensi yang sesuai dengan level aproksimasi
    approx_level = level  # level yang digunakan untuk aproksimasi baseline wander (misal cA8)
    freq_level = sampling_rate / (2 ** approx_level)  # Frekuensi yang sesuai dengan cA8
    
    # Atur koefisien aproksimasi untuk frekuensi baseline wander (0 hingga 0.49 Hz)
    if freq_level < threshold_max:
        coeffs[0] = np.where(np.abs(coeffs[0]) < threshold_max, coeffs[0], 0)

    # Rekonstruksi sinyal tanpa komponen baseline wander
    corrected_signal = pywt.waverec(coeffs, wavelet)

    return corrected_signal