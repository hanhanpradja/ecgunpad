from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.http import JsonResponse
from dashboard.models import Pasien
from .models import RekamanEKG, SinyalData, IntervalData
import json
# Create your views here.

def search_page(request):
    pasien_data = list(Pasien.objects.values('id_pasien', 'nik', 'nama'))
    context = {
        'jumlah_pasien':len(pasien_data)
    }
    return render(request, 'record/main.html', context)

def search(request):
    pasien_data = list(Pasien.objects.values('id_pasien', 'nik', 'nama'))  # Mengambil id, NIK, dan nama pasien
    return JsonResponse(pasien_data, safe=False)

def patient_record(request):
    id_pasien = request.GET.get('id_pasien')
    bulan_filter = request.GET.get('bulan', 'all')
    rows_per_page = request.GET.get('rows_per_page', 10)

    if not id_pasien:
        return render(request, 'record/index.html', {'error':'TERDAPAT MASALAH!'})
    
    # Filter berdasarkan ID pasien
    rekaman_queryset = RekamanEKG.objects.filter(id_pasien=id_pasien).order_by('-id_rekaman')

    # Filter berdasarkan bulan jika dipilih
    if bulan_filter != 'all':
        rekaman_queryset = rekaman_queryset.filter(bulan=bulan_filter)

    # Pagination
    paginator = Paginator(rekaman_queryset, rows_per_page)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Kirim context ke template
    context = {
        'id_pasien': id_pasien,
        'rekaman_data': page_obj,  # Data rekaman per halaman
        'paginator': paginator,   # Objek paginator untuk kontrol navigasi
        'current_page': page_obj.number,  # Halaman saat ini
        'rows_per_page': rows_per_page,   # Jumlah baris per halaman
        'bulan_filter': bulan_filter,     # Filter bulan aktif
    }

    return render(request, 'record/index.html', context)

def detail(request):
    id_rekaman = request.GET.get('id_rekaman')  # Ambil ID rekaman dari query parameter
    id_pasien = request.GET.get('id_pasien')

    # Filter data berdasarkan ID rekaman
    detail_interval_data = IntervalData.objects.filter(id_rekaman=id_rekaman).first()
    if not detail_interval_data:
        print("Data Interval tidak ditemukan.")

    sinyal_ekg_data = SinyalData.objects.filter(id_rekaman=id_rekaman).values('sinyal_ekg_10s')

    # Parsing sinyal EKG
    sinyal_ekg_parsed = [
        json.loads(item['sinyal_ekg_10s']) for item in sinyal_ekg_data
    ]

    context = {
        'detail_interval_data': detail_interval_data,
        'sinyal_ekg_data': sinyal_ekg_parsed,
        'id_pasien' : id_pasien
    }

    return render(request, 'record/detail.html', context)

def get_signal(request):
    id_rekaman = request.GET.get('id_rekaman')

    sinyal_ekg_data = SinyalData.objects.filter(id_rekaman=id_rekaman).values('sinyal_ekg_10s')
    sinyal_ekg_parsed = [
        json.loads(item['sinyal_ekg_10s']) for item in sinyal_ekg_data
    ]

    return JsonResponse(sinyal_ekg_parsed, safe=False)

