# Generated by Django 5.1.4 on 2024-12-10 03:02

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Pasien",
            fields=[
                ("id_pasien", models.AutoField(primary_key=True, serialize=False)),
                ("nik", models.CharField(max_length=16, unique=True)),
                ("nama", models.CharField(max_length=100)),
                ("umur", models.IntegerField()),
                ("riwayat_penyakit", models.TextField(blank=True, null=True)),
            ],
        ),
    ]
