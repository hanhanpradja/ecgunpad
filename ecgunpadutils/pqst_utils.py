import pandas as pd
import numpy as np 
import math
import neurokit2 as nk
import matplotlib.pyplot as plt
from scipy import datasets



def detect_pqrst(ecg_signal, rpeaks, sampling_rate):
    # peak acquisition
    signal_dwt, waves_dwt = nk.ecg_delineate(ecg_signal, rpeaks, sampling_rate, method='dwt')

    R = np.array(rpeaks)[np.isfinite(rpeaks)].astype(int)
    P = np.array(waves_dwt['ECG_P_Peaks'])[np.isfinite(waves_dwt['ECG_P_Peaks'])].astype(int)
    Q = np.array(waves_dwt['ECG_Q_Peaks'])[np.isfinite(waves_dwt['ECG_Q_Peaks'])].astype(int)
    S = np.array(waves_dwt['ECG_S_Peaks'])[np.isfinite(waves_dwt['ECG_S_Peaks'])].astype(int)
    T = np.array(waves_dwt['ECG_T_Peaks'])[np.isfinite(waves_dwt['ECG_T_Peaks'])].astype(int)

    P_Onsets = np.array(waves_dwt['ECG_P_Onsets'])[np.isfinite(waves_dwt['ECG_P_Onsets'])].astype(int)
    P_Offsets = np.array(waves_dwt['ECG_P_Offsets'])[np.isfinite(waves_dwt['ECG_P_Offsets'])].astype(int)
    R_Onsets = np.array(waves_dwt['ECG_R_Onsets'])[np.isfinite(waves_dwt['ECG_R_Onsets'])].astype(int)
    R_Offsets = np.array(waves_dwt['ECG_R_Offsets'])[np.isfinite(waves_dwt['ECG_R_Offsets'])].astype(int)
    T_Onsets = np.array(waves_dwt['ECG_T_Onsets'])[np.isfinite(waves_dwt['ECG_T_Onsets'])].astype(int)
    T_Offsets = np.array(waves_dwt['ECG_T_Offsets'])[np.isfinite(waves_dwt['ECG_T_Offsets'])].astype(int)

    # R = np.where(np.isfinite(rpeaks), np.array(rpeaks), 0).astype(int)
    # P = np.where(np.isfinite(waves_dwt['ECG_P_Peaks']), np.array(waves_dwt['ECG_P_Peaks']), 0).astype(int)
    # Q = np.where(np.isfinite(waves_dwt['ECG_Q_Peaks']), np.array(waves_dwt['ECG_Q_Peaks']), 0).astype(int)
    # S = np.where(np.isfinite(waves_dwt['ECG_S_Peaks']), np.array(waves_dwt['ECG_S_Peaks']), 0).astype(int)
    # T = np.where(np.isfinite(waves_dwt['ECG_T_Peaks']), np.array(waves_dwt['ECG_T_Peaks']), 0).astype(int)

    # P_Onsets = np.where(np.isfinite(waves_dwt['ECG_P_Onsets']), np.array(waves_dwt['ECG_P_Onsets']), 0).astype(int)
    # P_Offsets = np.where(np.isfinite(waves_dwt['ECG_P_Offsets']), np.array(waves_dwt['ECG_P_Offsets']), 0).astype(int)
    # R_Onsets = np.where(np.isfinite(waves_dwt['ECG_R_Onsets']), np.array(waves_dwt['ECG_R_Onsets']), 0).astype(int)
    # R_Offsets = np.where(np.isfinite(waves_dwt['ECG_R_Offsets']), np.array(waves_dwt['ECG_R_Offsets']), 0).astype(int)
    # T_Onsets = np.where(np.isfinite(waves_dwt['ECG_T_Onsets']), np.array(waves_dwt['ECG_T_Onsets']), 0).astype(int)
    # T_Offsets = np.where(np.isfinite(waves_dwt['ECG_T_Offsets']), np.array(waves_dwt['ECG_T_Offsets']), 0).astype(int)

    # R = np.array([x for x in rpeaks if math.isnan(x) is False]).astype(int)
    # P = np.array([x for x in waves_dwt['ECG_P_Peaks'] if math.isnan(x) is False]).astype(int)
    # Q = np.array([x for x in waves_dwt['ECG_Q_Peaks'] if math.isnan(x) is False]).astype(int)
    # S = np.array([x for x in waves_dwt['ECG_S_Peaks'] if math.isnan(x) is False]).astype(int)
    # T = np.array([x for x in waves_dwt['ECG_T_Peaks'] if math.isnan(x) is False]).astype(int)
    
    # P_Onsets = np.array([x for x in waves_dwt['ECG_P_Onsets'] if math.isnan(x) is False]).astype(int)
    # P_Offsets = np.array([x for x in waves_dwt['ECG_P_Offsets'] if math.isnan(x) is False]).astype(int)
    # R_Onsets = np.array([x for x in waves_dwt['ECG_R_Onsets'] if math.isnan(x) is False]).astype(int)
    # R_Offsets = np.array([x for x in waves_dwt['ECG_R_Offsets'] if math.isnan(x) is False]).astype(int)
    # T_Onsets = np.array([x for x in waves_dwt['ECG_T_Onsets'] if math.isnan(x) is False]).astype(int)
    # T_Offsets = np.array([x for x in waves_dwt['ECG_T_Offsets'] if math.isnan(x) is False]).astype(int)

    if R[0] < P_Onsets[0]:
        R = np.delete(R, 0)
    if P[0] < P_Onsets[0]:
        P = np.delete(P, 0)
    if Q[0] < P_Onsets[0]:
        Q = np.delete(Q, 0)
    if S[0] < P_Onsets[0]:
        S = np.delete(S, 0)
    if T[0] < P_Onsets[0]:
        T = np.delete(T, 0)
    if P_Offsets[0] < P_Onsets[0]:
        P_Offsets = np.delete(P_Offsets, 0)
    if R_Onsets[0] < P_Onsets[0]:
        R_Onsets = np.delete(R_Onsets, 0)
    if T_Offsets[0] < P_Onsets[0]:
        T_Offsets = np.delete(T_Offsets, 0)
    if R_Onsets[0] < P_Onsets[0]:
        R_Onsets = np.delete(R_Onsets, 0)
    if T_Onsets[0] < P_Onsets[0]:
        T_Onsets = np.delete(T_Onsets, 0)
    if R_Offsets[0] < R[0]:
        R_Offsets = np.delete(R_Offsets, 0)
    if T_Offsets[0] < R[0]:
        T_Offsets = np.delete(T_Offsets, 0)
    if T_Onsets[0] < R[0]:
        T_Onsets = np.delete(T_Onsets, 0)
    if S[0] < R[0]:
        S = np.delete(S, 0)
    if T[0] < R[0]:
        T = np.delete(T, 0)

    if ecg_signal[R][0] < ecg_signal[R][1] / 2:
        R = np.delete(R, 0)
        P = np.delete(P, 0)
        Q = np.delete(Q, 0)
        S = np.delete(S, 0)
        T = np.delete(T, 0)
        R_Onsets = np.delete(R_Onsets, 0)
        R_Offsets = np.delete(R_Offsets, 0)
        P_Onsets = np.delete(P_Onsets, 0)
        P_Offsets = np.delete(P_Offsets, 0)
        T_Onsets = np.delete(T_Onsets, 0)
        T_Offsets = np.delete(T_Offsets, 0)

    if R[len(R) - 1] > T_Offsets[len(T_Offsets) - 1]:
        R = np.delete(R, len(R) - 1)
    if P[len(P) - 1] > T_Offsets[len(T_Offsets) - 1]:
        P = np.delete(P, len(P) - 1)
    if Q[len(Q) - 1] > T_Offsets[len(T_Offsets) - 1]:
        Q = np.delete(Q, len(Q) - 1)
    if S[len(S) - 1] > T_Offsets[len(T_Offsets) - 1]:
        S = np.delete(S, len(S) - 1)
    if T[len(T) - 1] > T_Offsets[len(T_Offsets) - 1]:
        T = np.delete(T, len(T) - 1)
    if P_Onsets[len(P_Onsets) - 1] > T_Offsets[len(T_Offsets) - 1]:
        P_Onsets = np.delete(P_Onsets, len(P_Onsets) - 1)
    # if T_Offsets[len(T_Offsets) - 1] > T_Offsets[len(T_Offsets) - 1]:  # Kondisi ini tampaknya perlu dikoreksi, karena tidak logis.
    #     T_Offsets = np.delete(T_Offsets, len(T_Offsets) - 1)
    if T_Onsets[len(T_Onsets) - 1] > T_Offsets[len(T_Offsets) - 1]:
        T_Onsets = np.delete(T_Onsets, len(T_Onsets) - 1)
    if R_Onsets[len(R_Onsets) - 1] > T_Offsets[len(T_Offsets) - 1]:
        R_Onsets = np.delete(R_Onsets, len(R_Onsets) - 1)
    if R_Offsets[len(R_Offsets) - 1] > T_Offsets[len(T_Offsets) - 1]:
        R_Offsets = np.delete(R_Offsets, len(R_Offsets) - 1)

    if P[len(P) - 1] > R[len(R) - 1]:
        P = np.delete(P, len(P) - 1)
    if Q[len(Q) - 1] > R[len(R) - 1]:
        Q = np.delete(Q, len(Q) - 1)
    if P_Onsets[len(P_Onsets) - 1] > R[len(R) - 1]:
        P_Onsets = np.delete(P_Onsets, len(P_Onsets) - 1)
    if P_Offsets[len(P_Offsets) - 1] > R[len(R) - 1]:
        P_Offsets = np.delete(P_Offsets, len(P_Offsets) - 1)
    if R_Onsets[len(R_Onsets) - 1] > R[len(R) - 1]:
        R_Onsets = np.delete(R_Onsets, len(R_Onsets) - 1)

    main_dict = {
        'P':P,
        'Q':Q,
        'R':R,
        'S':S,
        'T':T,
        'P_Offsets':P_Offsets,
        'P_Onsets':P_Onsets,
        'R_Offsets':R_Offsets,
        'R_Onsets':R_Onsets,
        'T_Offsets':T_Offsets,
        'T_Onsets':T_Onsets
    }

    return main_dict

# function to calculate 7 features from ecg signal
# input dictionary must contains 7 keys (PQRST, also the onsets and offsets for PRT)
# params: dictionary, sampling_rate (int)
# return: features from ecg signal (7 total) in dictionary
def calculate_features(ecg_signal, main_dict, sampling_rate):
    # Calculate RR
    RR = []
    try:
        for i in range(len(main_dict['R']) - 1):
            RR_int = main_dict['R'][i+1] - main_dict['R'][i]
            RR_int = (RR_int / sampling_rate) * 1000
            RR.append(RR_int)
        
        RR = np.nan_to_num(RR, nan=0)
        RR_std = np.std(RR, axis=None)

        sum = 0
        count = 0
        for i in range(len(RR)):
            if np.isfinite(RR[i]):
                sum += RR[i]
                count += 1
        RR_avg = sum / count
    except:
        print('RR Interval Error')

    # Calculate PR
    PR = []
    try:
        for i in range(len(main_dict['R_Onsets'] - 1)):
            if main_dict['R_Onsets'][i] < main_dict['P_Onsets'][i]:
                PR_int = (main_dict['Q'][i] - main_dict['P_Onsets'][i])
                PR_int = ((PR_int / sampling_rate) * 1000.0)
                PR.append(PR_int)
            
            else:
                PR_int = (main_dict['R_Onsets'][i] - main_dict['P_Onsets'][i])
                PR_int = ((PR_int / sampling_rate) * 1000.0)
                PR.append(PR_int)
    except:
        print("PR Segments error")

    PR = np.nan_to_num(PR, nan=0)
    PR_std = np.std(PR, axis=None)

    sum = 0
    count = 0
    for i in range(len(PR)):
        if np.isfinite(PR[i]):
            sum += PR[i]
            count += 1
    PR_avg = sum / count

    # Calculate QS
    QS = []
    try:
        for i in range(len(main_dict['S']) - 1):
            if main_dict['S'][i] < main_dict['Q'][i]:
                QRS_complex = (main_dict['S'][i + 1] - main_dict['Q'][i])
                QRS_complex = ((QRS_complex / sampling_rate) * 1000.0)  # Convert sample distances to ms distances
                QS.append(QRS_complex)
            else:
                QRS_complex = (main_dict['S'][i] - main_dict['Q'][i])
                QRS_complex = ((QRS_complex / sampling_rate) * 1000.0)  # Convert sample distances to ms distances
                QS.append(QRS_complex)
    except:
        print("QRS width Error")

    QS = np.nan_to_num(QS, nan=0)
    QS_std = np.std(QS, axis=None)

    sum = 0
    count = 0
    for i in range(len(QS)):
        if np.isfinite(QS[i]):
            sum += QS[i]
            count += 1
    QS_avg = sum / count

    # Calculate QT
    QT = []
    try:
        for i in range(len(main_dict['T_Offsets']) - 1):
            if main_dict['T_Offsets'][i] < main_dict['R_Onsets'][i]:
                QT_int = (main_dict['T_Offsets'][i + 1] - main_dict['R_Onsets'][i])
                QT_int = ((QT_int / sampling_rate) * 1000.0)
                QT.append(QT_int)
            else:
                QT_int = (main_dict['T_Offsets'][i] - main_dict['R_Onsets'][i])
                QT_int = ((QT_int / sampling_rate) * 1000.0) 
                QT.append(QT_int)
    except:
        print("QT Interval Error")

    QT = np.nan_to_num(QT, nan=0)
    QT_std = np.std(QT, axis=None)

    sum = 0
    count = 0
    for i in range(len(QT)):
        if np.isfinite(QT[i]):
            sum += QT[i]
            count += 1
    QT_avg = sum / count
    QTc_avg = QT_avg / (math.sqrt(np.mean(RR)/ 1000))

    # Calculate BPM
    BPM = 60000 / np.mean(RR)

    # Calculate ST
    ST = []
    try:
        for i in range (len(main_dict['T_Offsets']) - 1):
            if main_dict['T_Offsets'][i] < main_dict['R_Offsets'][i]:
                ST_int = (main_dict['T_Offsets'][i+1] - main_dict['R_Offsets'][i])
                ST_int = ((ST_int / sampling_rate) * 1000.0)
                ST.append(ST_int)
                
            else:
                ST_int = (main_dict['T_Offsets'][i] - main_dict['R_Offsets'][i])
                ST_int = ((ST_int / sampling_rate) * 1000.0)
                ST.append(ST_int)
    except:
        print("ST Interval Error")

    ST = np.nan_to_num(ST, nan=0)
    ST_std = np.std(ST, axis=None)

    sum = 0
    count = 0
    for i in range(len(ST)):
        if np.isfinite(ST[i]):
            sum += ST[i]
            count += 1
    ST_avg = sum / count

    # Calculate R/S Ratio
    #RS_ratio = np.abs(np.mean(main_dict['R'])) / np.abs(np.mean(main_dict['S']))
    RS_ratio = np.mean([ecg_signal[int(i)] for i in main_dict['R']]) / np.abs(np.mean([ecg_signal[int(i)] for i in main_dict['S']])) 

    features = {'RR':RR_avg,
                #'RR_std':RR_std,
                'PR':PR_avg,
                #'PR_std':PR_std,
                'QS':QS_avg,
                #'QS_std':QS_std,
                'QT':QT_avg,
                #'QT_std':QT_std,
                'ST':ST_avg,
                #'ST_std':ST_std,
                'BPM':BPM,
                'RS_ratio':RS_ratio,
                'QTc':QTc_avg}
    
    return features
