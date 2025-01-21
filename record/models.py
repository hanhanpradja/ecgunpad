from django.db import models
from dashboard.models import Pasien
# Create your models here.

class RekamanEKG(models.Model):
    id_rekaman = models.AutoField(primary_key=True)  # Primary Key
    id_pasien = models.ForeignKey(Pasien, on_delete=models.CASCADE)  # Referensi ke tabel Pasien
    tanggal = models.IntegerField()  # Tanggal perekaman
    bulan = models.IntegerField()  # Bulan perekaman
    tahun = models.IntegerField()  # Tahun perekaman
    waktu = models.TimeField() # Waktu perekaman WIB
    klasifikasi = models.CharField(max_length=100)  # hasil klasifikasi model DNN

    def __str__(self):
        return f"Rekaman {self.id_rekaman} - {self.id_pasien.nama}"


class IntervalData(models.Model):
    id_interval = models.AutoField(primary_key=True)  # Primary Key
    id_rekaman = models.ForeignKey(RekamanEKG, on_delete=models.CASCADE)  # Referensi ke RekamanEKG

    # Data interval
    interval_rr = models.FloatField()  # Interval RR dalam ms
    interval_pr = models.FloatField()  # Interval PR dalam ms
    interval_qrs = models.FloatField()  # Interval QRS dalam ms
    interval_qt = models.FloatField()  # Interval QT dalam ms
    interval_st = models.FloatField()  # Interval ST dalam ms
    bpm = models.FloatField()  # Beats Per Minute (detak jantung)
    rs_ratio = models.FloatField()  # R/S Ratio

    def __str__(self):
        return f"Interval Data {self.id_interval} - Rekaman {self.id_rekaman.id_rekaman}"
    

class SinyalData(models.Model):
    id_sinyal = models.AutoField(primary_key=True)  # Primary Key
    id_rekaman = models.ForeignKey(RekamanEKG, on_delete=models.CASCADE)  # Referensi ke RekamanEKG

    # Data sinyal
    sinyal_ekg_10s = models.JSONField()  # Data sinyal dalam rentang 10 detik (format JSON)

    def __str__(self):
        return f"Sinyal Data {self.id_sinyal} - Rekaman {self.id_rekaman.id_rekaman}"