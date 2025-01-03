# Generated by Django 5.1.4 on 2024-12-10 03:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("dashboard", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="RekamanEKG",
            fields=[
                ("id_rekaman", models.AutoField(primary_key=True, serialize=False)),
                ("tanggal", models.IntegerField()),
                ("bulan", models.IntegerField()),
                ("tahun", models.IntegerField()),
                ("klasifikasi", models.CharField(max_length=100)),
                (
                    "id_pasien",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="dashboard.pasien",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="IntervalData",
            fields=[
                ("id_interval", models.AutoField(primary_key=True, serialize=False)),
                ("interval_rr", models.FloatField()),
                ("interval_pr", models.FloatField()),
                ("interval_qrs", models.FloatField()),
                ("interval_qt", models.FloatField()),
                ("interval_st", models.FloatField()),
                ("bpm", models.FloatField()),
                ("rs_ratio", models.FloatField()),
                (
                    "id_rekaman",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="record.rekamanekg",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="SinyalData",
            fields=[
                ("id_sinyal", models.AutoField(primary_key=True, serialize=False)),
                ("sinyal_ekg_10s", models.JSONField()),
                (
                    "id_rekaman",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="record.rekamanekg",
                    ),
                ),
            ],
        ),
    ]
