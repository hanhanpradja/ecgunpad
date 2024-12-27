from django.db import models

# Create your models here.
class Pasien(models.Model):
    id_pasien = models.AutoField(primary_key=True)
    nik = models.CharField(max_length=16, unique=True)
    nama = models.CharField(max_length=100)
    umur = models.IntegerField()
    riwayat_penyakit = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.nama} ({self.nik})"
    



    