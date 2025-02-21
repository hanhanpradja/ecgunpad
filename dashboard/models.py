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
    
class Userlogin(models.Model):
    id_user = models.AutoField(primary_key=True)
    nip = models.CharField(max_length=36, unique=True)
    nama = models.CharField(max_length=200)
    email = models.EmailField(max_length=256, unique=True)
    password = models.CharField(max_length=200)

    def __str__(self):
        return f'{self.id_user}-{self.nip}'
    