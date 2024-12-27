@csrf_exempt
def process_data(request):
    if request.method == "POST":
        try:
            stop_event.clear()  # Pastikan event dihentikan sebelum memulai

            data = json.loads(request.body)
            pasien_id = data.get('id_pasien')

            if not pasien_id:
                return JsonResponse({"error": "ID pasien tidak diberikan."}, status=400)

            # Periksa apakah pasien ada di database
            pasien_check = Pasien.objects.filter(id_pasien=pasien_id).first()
            if not pasien_check:
                return JsonResponse({"error": "Pasien tidak ditemukan."}, status=404)
            
            # Perekaman dimulai
            while not stop_event.is_set():
                result = record_bluetooth_data(port='COM9')
                sampling_rate = int(len(result[0])/10)
                column = list(result.keys())
                all_channel_cleaned = {}
                for i in column:
                    channel = result[i]
                    to_mv = channel * (2.4 / ((2**24))) * 1000
                    blw = to_mv
                    denoised = dwt_denoise(blw, wavelet='sym8', level=3)
                    all_channel_cleaned[i] = denoised
                
                r_peaks = {}
                for i in column:
                    _, rpeaky = nk.ecg_peaks(all_channel_cleaned[i], sampling_rate=sampling_rate, method='neurokit2')
                    rpeak = rpeaky['ECG_R_Peaks']
                    r_peaks[i] = rpeak
                
                all_peaks = {}
                for i in column:
                    peak = detect_pqrst(all_channel_cleaned[i], rpeaks=r_peaks[i], sampling_rate=sampling_rate)
                    all_peaks[i] = peak

                # ekstraksi fitur
                ch_features = {}
                for i in column:
                    features = calculate_features(all_channel_cleaned[i], all_peaks[i], sampling_rate=sampling_rate)
                    ch_features[i] = features

                features_for_model = [
                    ch_features[column[1]]['RR'],
                    ch_features[column[1]]['PR'],
                    ch_features[column[1]]['QS'],
                    ch_features[column[1]]['QTc'],
                    ch_features[column[0]]['ST'],
                    ch_features[column[2]]['RS_ratio'],
                    ch_features[column[2]]['BPM']
                ]

                features_scaled = scaler.transform(features_for_model)  # Fit scaler dan transform data fitur

                # Prediksi menggunakan model TensorFlow
                prediction = model.predict(features_scaled)
                predicted_class = prediction[0]
                classification_result = class_map.get(predicted_class, 'Unknown')

                pasien_id = request.data.get('id_pasien')
                pasien = Pasien.objects.get(id_pasien=pasien_id)
                
                if classification_result != 'Normal':
                    rekaman = RekamanEKG.objects.create(
                        id_pasien_id=pasien_id,  # ID pasien yang sudah disimpan
                        tanggal=datetime.now().day,  # Contoh tanggal
                        bulan=datetime.now().month,  # Contoh bulan
                        tahun=datetime.now().year,  # Contoh tahun
                        klasifikasi=classification_result  # Ini bisa diperbarui dengan hasil model DNN
                    )

                    IntervalData.objects.create(
                        id_rekaman=rekaman,
                        interval_rr=ch_features[column[1]]['RR'],
                        interval_pr=ch_features[column[1]]['PR'],
                        interval_qrs=ch_features[column[1]]['QS'],
                        interval_qt=ch_features[column[1]]['QTc'],
                        interval_st=ch_features[column[0]]['ST'],
                        rs_ratio=ch_features[column[2]]['RS_ratio'],
                        bpm=ch_features[column[2]]['BPM']
                    )

                    SinyalData.objects.create(
                        id_rekaman=rekaman,
                        sinyal_ekg_10s=json.dumps(all_channel_cleaned)  # Simpan data sinyal dalam format JSON
                    )

                pusher_client.trigger('ecg-comm-unpad', 'new-ekg-data', {
                    'id':pasien.id_pasien,
                    'nama': pasien.nama,
                    'umur': pasien.umur,
                    'sinyal_ekg': all_channel_cleaned,  # Kirim data sinyal EKG 10 detik
                    'klasifikasi': classification_result,
                    'record-date': datetime.now().isoformat(),
                    'device-status': 'Online',
                })

                # Respons JSON
                return JsonResponse({
                    "message": "Data processed and pushed successfully",
                    "klasifikasi": classification_result
                }, status=200)
            
            return JsonResponse({
                "message": "Perekaman dihentikan oleh pengguna."
            }, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
        
    return JsonResponse({"error": "Invalid request"}, status=400)

@csrf_exempt
def test_process_data(request):
    if request.method == "POST":
        stop_event.clear()
        while not stop_event.is_set():
            try:
                # Parse JSON data
                try:
                    data = json.loads(request.body)
                    pasien_id = data.get('id_pasien')
                except json.JSONDecodeError as e:
                    return JsonResponse({"error": f"JSON tidak valid: {str(e)}"}, status=400)

                if not pasien_id:
                    return JsonResponse({"error": "ID pasien tidak diberikan."}, status=400)

                # Cek apakah pasien ada di database
                pasien_check = Pasien.objects.filter(id_pasien=pasien_id).first()
                if not pasien_check:
                    return JsonResponse({"error": "Pasien tidak ditemukan."}, status=404)

                # Log informasi awal
                print(f"Memulai perekaman untuk pasien ID: {pasien_id}")

                # Simulasi pemrosesan data (record_bluetooth_data)
                try:
                    result = record_bluetooth_data(port='COM8')  # Pastikan port benar
                except Exception as e:
                    return JsonResponse({"error": f"Gagal membaca data dari perangkat atau perangkat tidak terhubung: {str(e)}"}, status=500)

                # Validasi hasil data
                if not result or not isinstance(result, dict):
                    return JsonResponse({"error": "Data yang diterima tidak valid."}, status=500)

                classification_result = random.choice(list(class_map.values()))

                # Simpan data ke database
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
                        return JsonResponse({"error": f"Gagal menyimpan data ke database: {str(e)}"}, status=500)

                # Kirim data ke Pusher
                try:
                    pusher_client.trigger('ecg-comm-unpad', 'new-ekg-data', {
                        'id': pasien_id,
                        'nama': pasien_check.nama,
                        'umur': pasien_check.umur,
                        'klasifikasi': classification_result,
                        'record-date': datetime.now().isoformat(),
                        'device-status': 'Online',
                    })
             
                except Exception as e:
                    print(f"Gagal mengirim data ke Pusher: {str(e)}")

                # Respons sukses
                return JsonResponse({
                    "message": "Data processed successfully",
                    "klasifikasi": classification_result
                }, status=200)

            except Exception as e:
                # Tangkap kesalahan tak terduga
                error_message = f"Kesalahan tidak terduga: {str(e)}\n{traceback.format_exc()}"
                print(error_message)
                return JsonResponse({"error": error_message}, status=500)

    return JsonResponse({"error": "Invalid request method. Use POST."}, status=405)

