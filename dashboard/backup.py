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