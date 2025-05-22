# Real-Time Web-Based ECG Signal Classification Using DNN

> Sistem deteksi aritmia berbasis web secara real-time menggunakan Deep Neural Network (DNN), Discrete Wavelet Transform (DWT), dan biopeaks.

## 📑 Deskripsi

Proyek ini merupakan implementasi sistem klasifikasi sinyal EKG (Elektrokardiogram) secara real-time melalui platform web. Sinyal diambil dari perangkat **smart holter portable**, diproses di sisi server menggunakan **DWT** untuk denoising dan **biopeaks** untuk deteksi puncak, lalu diklasifikasikan menggunakan **DNN (Deep Neural Network)** menjadi empat kelas:
- Normal
- Abnormal
- Berpotensi Aritmia
- Sangat Berpotensi Aritmia

Sistem ini dikembangkan menggunakan stack berikut:
- **Backend**: Django + TensorFlow
- **Frontend**: JavaScript + Bootstrap
- **Real-time communication**: Pusher WebSocket
- **Database**: Django ORM (PostgreSQL/MySQL)

## 🖼️ Arsitektur Sistem

> Letakkan diagram arsitektur sistem di bawah ini

![System Architecture](assets/system_architecture.png)

## 🧠 Arsitektur Model DNN

Model DNN dibangun dengan struktur sebagai berikut:
- Input: 7 fitur (RR, PR, QRS, QT, ST, Heart Rate, Rasio R/S)
- Dense Layer 1: 128 neuron + BatchNorm + Dropout(0.4)
- Dense Layer 2: 64 neuron + Dropout(0.3)
- Dense Layer 3: 32 neuron + Dropout(0.2)
- Output Layer: Softmax (4 kelas)
- Optimizer: Adam + Learning Rate Scheduler
- Regularization: L2

## 🧪 Dataset & Labeling

Data pelatihan berasal dari:
- PTB-XL v1.0.3
- MIT-BIH Arrhythmia Dataset v1.0.0

Label disederhanakan menjadi 4 kelas berdasarkan kondisi medis dan literatur.

## 🖥️ Fitur Web

- Dashboard pemantauan klasifikasi real-time
- Perekaman data EKG dengan kontrol dari browser
- Penyimpanan otomatis hasil abnormal ke riwayat pasien
- Visualisasi sinyal EKG & fitur yang terdeteksi
- Panel administrator & referensi data

## ⚙️ Teknologi

| Komponen        | Teknologi               |
|----------------|--------------------------|
| Backend        | Django, TensorFlow       |
| Frontend       | Bootstrap, JavaScript    |
| Database       | Django ORM, PostgreSQL/MySQL |
| Real-time Comm | Pusher WebSocket         |
| Data Processing| NeuroKit2, PyWavelets    |

## 🗃️ Struktur Database

> Letakkan diagram ERD (Entity Relationship Diagram) database di bawah ini

![Database Schema](assets/database_erd.png)

### Tabel utama:
- `Pasien`: menyimpan data identitas
- `RekamanEKG`: menyimpan metadata rekaman
- `SinyalData`: sinyal mentah untuk grafik
- `IntervalData`: fitur-fitur hasil ekstraksi (RR, PR, dst.)

## 🚀 Cara Menjalankan

```bash
# Clone repository
git clone https://github.com/your-username/your-project.git
cd your-project

# Install dependencies (gunakan virtualenv)
pip install -r requirements.txt

# Jalankan server
python manage.py runserver

Pastikan .env Anda sudah dikonfigurasi untuk akses database dan API Pusher.
```

## 📈 Hasil & Evaluasi
- Akurasi: 91% (dataset), 90% (data real-time)
- Precision, Recall, F1-score: ~90%
- Performa Web (Google Lighthouse): Skor 96
