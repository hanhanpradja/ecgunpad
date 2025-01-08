from django.shortcuts import render
from django.http import JsonResponse
from datetime import datetime
from ecgunpadutils.denoising_utils import dwt_denoise, filter_ecg_signal
from ecgunpadutils.baselinecorrect_utils import remove_baseline_wander_wavelet
from ecgunpadutils.device_record import record_bluetooth_data
from ecgunpadutils.pqst_utils import detect_pqrst, calculate_features
from ecgunpadutils.myutils import ExceptionThread
from pusher import Pusher
from django.views.decorators.csrf import csrf_exempt
from .models import Pasien
from record.models import RekamanEKG, IntervalData, SinyalData
import json
import neurokit2 as nk
import tensorflow as tf
import joblib
from sklearn.preprocessing import StandardScaler
import threading
import traceback
import random
import numpy as np
import pandas as pd

# Status
status_data = {'status':'idle', 'error': None}

def get_process_status(request):
    global status_data
    return JsonResponse(status_data)


# Event config.
stop_event = threading.Event()

# Pusher config.
pusher_client = Pusher(
    app_id="1908865",
    key="7d3db4cc20408e453e6f",
    secret="7c5e9c53a4b629689364",
    cluster="ap1",
    ssl=True
)

# Model config.
model = tf.keras.models.load_model('dashboard/static/dashboard/other/my_model15.h5')
scaler = joblib.load('dashboard/static/dashboard/other/scaler15.pkl')
class_map = {
    0: 'NORMAL',
    1: 'ABNORMAL',
    2: 'BERPOTENSI ARITMIA',
    3: 'SANGAT BERPOTENSI ARITMIA'
}

# Create your views here.
def index(request):
    return render(request, "dashboard/index.html")

@csrf_exempt
def new_pasien_rekam(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            nama = data.get('nama')
            nik = data.get('nik')
            umur = data.get('umur')

            if not nama or not nik or not umur:
                return JsonResponse({"error": "Data tidak lengkap."}, status=400)

            # Validasi apakah NIK sudah ada
            if Pasien.objects.filter(nik=nik).exists():
                return JsonResponse({"error": "NIK sudah terdaftar."}, status=400)

            # Simpan pasien baru
            pasien = Pasien.objects.create(
                nama=nama,
                nik=nik,
                umur=umur
            )
            return JsonResponse({"message": "Pasien baru disimpan.", "id": pasien.id_pasien}, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request"}, status=400)


def process_data(stop_event, data, pasien_id, ports):
    global status_data
    try:
        status_data = {'status':'process', 'error':None}
        while not stop_event.is_set():
            if stop_event.is_set():
                raise Exception('Perekaman dihentikan')
            
            # cek pasien
            pasien_check = Pasien.objects.filter(id_pasien=pasien_id).first()
            if not pasien_check:
                raise Exception('Pasien tidak ditemukan')
            
            # koneksi ke device
            result = record_bluetooth_data(port=ports)

            # validasi data
            if not result or not isinstance(result, dict):
                raise Exception(f'port bluetooth {ports} sepertinya belum di bind!')
            
            try:
                # denoising
                sampling_rate = int(len(result['I']) / 10)
                column = list(result.keys())
                all_channel_cleaned = {}
                for i in column:
                    channel = np.array(result[i])
                    to_mv = channel * (2.4 / ((2**24))) * 1000
                    blw = remove_baseline_wander_wavelet(to_mv, 'db4')
                    denoised = dwt_denoise(blw, wavelet='sym8', level=3)
                    # denoised = filter_ecg_signal(to_mv, sampling_rate)
                    all_channel_cleaned[i] = list(denoised)
                
                # deteksi puncak r
                r_peaks = {}
                for i in column:
                    _, r = nk.ecg_peaks(np.array(all_channel_cleaned[i]), sampling_rate)
                    r_peaks[i] = r['ECG_R_Peaks']

                # fitur ekstraksi
                ch_features = {}
                for i in column:
                    features = calculate_features(np.array(all_channel_cleaned[i]), detect_pqrst(np.array(all_channel_cleaned[i]), r_peaks[i], sampling_rate=sampling_rate), sampling_rate=sampling_rate)
                    ch_features[i] = features

                # Prediksi menggunakan model TensorFlow
                features_for_model = [
                    ch_features[column[1]]['RR'],
                    ch_features[column[1]]['PR'],
                    ch_features[column[1]]['QS'],
                    ch_features[column[1]]['QTc'],
                    ch_features[column[0]]['ST'],
                    ch_features[column[2]]['RS_ratio'],
                    ch_features[column[2]]['BPM']
                ]

                features_array = np.array(features_for_model).reshape(1, -1)
                features_scaled = scaler.transform(features_array)
                prediction = model.predict(features_scaled)
                predicted_class = np.argmax(prediction, axis=1)
                classification_result = pd.Series(predicted_class).map(class_map).values[0]
                print(classification_result)

                # Simpan data ke database jika hasil tidak NORMAL
                rekaman = RekamanEKG.objects.create(
                    id_pasien_id=pasien_id,
                    tanggal=datetime.now().day,
                    bulan=datetime.now().month,
                    tahun=datetime.now().year,
                    klasifikasi=classification_result
                )
                IntervalData.objects.create(
                    id_rekaman=rekaman,
                    interval_rr=round(features_for_model[0], 1),
                    interval_pr=round(features_for_model[1], 1),
                    interval_qrs=round(features_for_model[2], 1),
                    interval_qt=round(features_for_model[3], 1),
                    interval_st=round(features_for_model[4], 1),
                    rs_ratio=round(features_for_model[5], 1),
                    bpm=round(features_for_model[6], 1)
                )
                SinyalData.objects.create(
                    id_rekaman=rekaman,
                    sinyal_ekg_10s=json.dumps(all_channel_cleaned)
                )
                    
                # Kirim data ke Pusher
                pusher_client.trigger('ecg-comm-unpad', 'new-ekg-data', {
                    'id': pasien_id,
                    'nama': pasien_check.nama,
                    'umur': pasien_check.umur,
                    'klasifikasi': classification_result,
                    'record-date': datetime.now().isoformat(),
                    'device_status': 'Online',
                })

            except:
                pusher_client.trigger('ecg-comm-unpad', 'new-ekg-data', {
                    'id': pasien_id,
                    'nama': pasien_check.nama,
                    'umur': pasien_check.umur,
                    'klasifikasi': 'UNKNOWN',
                    'record-date': datetime.now().isoformat(),
                    'device_status': 'Online',
                })
                continue

            print("Proses selesai untuk iterasi ini.")
    
    except Exception as e:
        status_data = {"status": "stopped", "error":f'PERIKSA KONEKSI ALAT ATAU PENEMPATAN ELEKTODA!!\n\nLebih lanjut:\n{str(e)}\n{traceback.format_exc()}'}
        raise




def process_in_background(stop_event, data, pasien_id):
    while not stop_event.is_set():
        try:
            if stop_event.is_set():
                break


            # Cek apakah pasien ada di database
            pasien_check = Pasien.objects.filter(id_pasien=pasien_id).first()
            if not pasien_check:
                print("Pasien tidak ditemukan.")
                continue

            # Log informasi awal
            print(f"Memulai perekaman untuk pasien ID: {pasien_id}")

            # Simulasi pemrosesan data (record_bluetooth_data)
            try:
                result = record_bluetooth_data(port='COM8')  # Pastikan port benar
            except Exception as e:
                print(f"Gagal membaca data dari perangkat: {str(e)}")
                continue

            # Validasi hasil data
            if not result or not isinstance(result, dict):
                print("Data yang diterima tidak valid.")
                continue

            classification_result = random.choice(list(class_map.values()))

            # Simpan data ke database jika hasil tidak NORMAL
            if classification_result != 'NORMAL':
                try:
                    rekaman = RekamanEKG.objects.create(
                        id_pasien_id=pasien_id,
                        tanggal=datetime.now().day,
                        bulan=datetime.now().month,
                        tahun=datetime.now().year,
                        klasifikasi=classification_result
                    )
                    IntervalData.objects.create(
                        id_rekaman=rekaman,
                        interval_rr=random.randint(1, 10),
                        interval_pr=random.randint(1, 10),
                        interval_qrs=random.randint(1, 10),
                        interval_qt=random.randint(1, 10),
                        interval_st=random.randint(1, 10),
                        rs_ratio=random.randint(1, 10),
                        bpm=random.randint(1, 10)
                    )
                    SinyalData.objects.create(
                        id_rekaman=rekaman,
                        sinyal_ekg_10s=json.dumps(result)
                    )
                except Exception as e:
                    print(f"Gagal menyimpan data ke database: {str(e)}\n{traceback.format_exc()}")
                    continue

            # Kirim data ke Pusher
            try:
                pusher_client.trigger('ecg-comm-unpad', 'new-ekg-data', {
                    'id': pasien_id,
                    'nama': pasien_check.nama,
                    'umur': pasien_check.umur,
                    'klasifikasi': classification_result,
                    'record-date': datetime.now().isoformat(),
                    'device_status': 'Online',
                })
            except Exception as e:
                print(f"Gagal mengirim data ke Pusher: {str(e)}\n{traceback.format_exc()}")

            print("Proses selesai untuk iterasi ini.")
        except Exception as e:
            print(f"Kesalahan tidak terduga: {str(e)}\n{traceback.format_exc()}")

@csrf_exempt
def test_process_data(request):
    global stop_event, status_data

    if request.method == "POST":
        stop_event.clear()

        try:
            # Parse JSON data
            data = json.loads(request.body)
            pasien_id = data.get('id_pasien')
            ports = data.get('ports')
            

            if not pasien_id:
                raise Exception('id pasien tidak diberikan')

            if not ports:
                raise Exception('ports tidak dimasukkan')

            # Mulai thread untuk proses latar belakang
            process_thread = ExceptionThread(target=process_data, args=(stop_event, data, pasien_id, ports))
            process_thread.daemon = True  # Agar thread berhenti saat server dimatikan
            process_thread.start()

            return JsonResponse({"message": "Proses telah dimulai di latar belakang."}, status=200)

        except Exception as e:
            stop_event.set()
            print(traceback.format_exc())
            return JsonResponse({'error':f'terjadi kesalahan {str(e)}\nPERIKSA ALAT ATAU PENEMPATAN ELEKTRODA!'}, status=400)

    return JsonResponse({"error": "Invalid request method. Use POST to start or DELETE to stop."}, status=405)


@csrf_exempt
def check_nik(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            nik = data.get("nik")  # Make sure key matches JavaScript

            if not nik:
                return JsonResponse({"error": "NIK tidak diberikan."}, status=400)

            pasien = Pasien.objects.filter(nik=nik).first()
            if not pasien:
                return JsonResponse({"error": "NIK tidak ditemukan."}, status=404)

            return JsonResponse({"message": "Pasien ditemukan.", "id": pasien.id_pasien}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request"}, status=400)


def get_registered_niks(request):
    # Ambil semua NIK dari model Pasien
    registered_niks = Pasien.objects.values_list('nik', flat=True)
    # Kembalikan NIK dalam format JSON
    return JsonResponse(list(registered_niks), safe=False)

@csrf_exempt
def stop_process(request):
    if request.method == "POST":
        try:
            # Menghentikan perekaman dengan mengatur stop_event
            stop_event.set()  # Memberikan sinyal untuk menghentikan perekaman
            
            # Kembalikan response JSON untuk menunjukkan bahwa perekaman sudah dihentikan
            return JsonResponse({
                "message": "Perekaman dihentikan."
            }, status=200)
        
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request"}, status=400)