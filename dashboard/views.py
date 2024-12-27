from django.shortcuts import render
from django.http import JsonResponse
from datetime import datetime
from ecgunpadutils.denoising_utils import dwt_denoise
from ecgunpadutils.baselinecorrect_utils import remove_baseline_wander_wavelet
from ecgunpadutils.device_record import record_bluetooth_data
from ecgunpadutils.pqst_utils import detect_pqrst, calculate_features
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


def process_data(stop_event, data, pasien_id):
    while not stop_event.is_set():
        try:
            if stop_event.is_set():
                break
            
            # cek pasien
            pasien_check = Pasien.objects.filter(id_pasien=pasien_id).first()
            if not pasien_check:
                print("Pasien tidak ditemukan.")
            
            # koneksi ke device
            try:
                result = record_bluetooth_data(port='COM7')
            except Exception as e:
                print(f"Gagal membaca data dari perangkat: {str(e)}")
            
            # validasi data
            if not result or not isinstance(result, dict):
                print("Data yang diterima tidak valid.")
            
            # denoising
            try:
                sampling_rate = int(len(result[0]) / 10)
                column = list(result.keys())
                all_channel_cleaned = {}
                for i in column:
                    channel = result[i]
                    to_mv = channel * (2.4 / ((2**24))) * 1000
                    denoised = dwt_denoise(to_mv, wavelet='sym8', level=3)
                    all_channel_cleaned[i] = denoised
            except Exception as e:
                print(f"Gagal memproses data: {str(e)}")
                
            
            # fitur ekstraksi
            try:
                ch_features = {}
                for i in column:
                    features = calculate_features(all_channel_cleaned[i], detect_pqrst(all_channel_cleaned[i], rpeaks=[], sampling_rate=sampling_rate), sampling_rate=sampling_rate)
                    ch_features[i] = features
            except Exception as e:
                print(f"Gagal mengekstrak fitur: {str(e)}")
                

            # Prediksi menggunakan model TensorFlow
            try:
                features_for_model = [
                    ch_features[column[1]]['RR'],
                    ch_features[column[1]]['PR'],
                    ch_features[column[1]]['QS'],
                    ch_features[column[1]]['QTc'],
                    ch_features[column[0]]['ST'],
                    ch_features[column[2]]['RS_ratio'],
                    ch_features[column[2]]['BPM']
                ]

                features_scaled = scaler.transform(features_for_model)
                prediction = model.predict(features_scaled)
                predicted_class = prediction[0]
                classification_result = class_map.get(predicted_class, 'Unknown')

            except Exception as e:
                print(f"Gagal memprediksi klasifikasi: {str(e)}")
                
            
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
                    print(f"Gagal menyimpan data ke database: {str(e)}")

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
                print(f"Gagal mengirim data ke Pusher: {str(e)}")

            print("Proses selesai untuk iterasi ini.")
        except Exception as e:
            print(f"Kesalahan tidak terduga: {str(e)}")


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
                    print(f"Gagal menyimpan data ke database: {str(e)}")
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
                print(f"Gagal mengirim data ke Pusher: {str(e)}")

            print("Proses selesai untuk iterasi ini.")
        except Exception as e:
            print(f"Kesalahan tidak terduga: {str(e)}")

@csrf_exempt
def test_process_data(request):
    global stop_event

    if request.method == "POST":
        stop_event.clear()
        try:
            # Parse JSON data
            try:
                data = json.loads(request.body)
                pasien_id = data.get('id_pasien')
            except json.JSONDecodeError as e:
                return JsonResponse({"error": f"JSON tidak valid: {str(e)}"}, status=400)

            if not pasien_id:
                return JsonResponse({"error": "ID pasien tidak diberikan."}, status=400)

            # Mulai thread untuk proses latar belakang
            process_thread = threading.Thread(target=process_data, args=(stop_event, data, pasien_id))
            process_thread.daemon = True  # Agar thread berhenti saat server dimatikan
            process_thread.start()

            return JsonResponse({"message": "Proses telah dimulai di latar belakang."}, status=200)

        except Exception as e:
            error_message = f"Terjadi Kesalahan: {str(e)}\n{traceback.format_exc()}"
            stop_event.set()
            print(error_message)
            return JsonResponse({"error": error_message}, status=500)

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