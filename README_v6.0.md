# 🖼️ Image Tools PRO v6.0.0

Aplikasi desktop berbasis GUI modern (menggunakan CustomTkinter) yang komprehensif untuk mengelola, mengompresi, mengonversi format gambar, serta melakukan berbagai operasi file PDF secara instan dan aman.

---

## 📋 Daftar Isi
1. [Fitur Utama](#-fitur-utama)
2. [Struktur File](#-struktur-file)
3. [Panduan Penggunaan Quick Start](#-panduan-penggunaan-quick-start)
4. [Persyaratan Sistem & Dependensi](#-persyaratan-sistem--dependensi)
5. [Troubleshooting & Catatan Penting](#-troubleshooting--catatan-penting)
6. [Informasi Migrasi dari v5.0](#-migrasi-dari-v50)
7. [Hubungi & Dukungan](#-hubungi--dukungan)

---

## ✨ Fitur Utama

### 1. 🖼️ Tab Kompresi Gambar
* **Kustomisasi Kualitas & Ukuran**: Pengaturan slider untuk kompresi kualitas (0-100%) dan pengubahan ukuran/resize gambar (0-100%).
* **Banyak Format Didukung**: Mendukung JPG, PNG, ICO, BMP, GIF, TIFF, WEBP, dan konversi dasar SVG.
* **Pelestarian Metadata EXIF**: Menjaga data kamera dan metadata penting pada gambar (opsional).
* **Backup Otomatis**: Membuat backup file asli sebelum operasi sehingga Anda dapat melakukan **Undo** kapan saja (Ctrl+Z).

### 2. 🔄 Tab Konversi Format
* Mengonversi banyak format gambar sekaligus secara bulk ke format JPG, PNG, ICO, BMP, GIF, TIFF, dan WEBP dengan pengaturan resize independen.

### 3. 📄 Tab Utilitas PDF
* **Gambar ke PDF**: Mengubah koleksi gambar menjadi file PDF (satu halaman per gambar).
* **Gabung PDF**: Menggabungkan beberapa file PDF secara berurutan menjadi satu file PDF utuh.
* **Kompres PDF**: Mengurangi ukuran file PDF menggunakan PyPDF2.
* **PDF ke Gambar**: Mengekstrak halaman PDF menjadi file gambar (jika modul pendukung aktif).

### 4. 📊 Riwayat & Logging
* **Riwayat Operasi**: Log aktivitas terakhir yang disimpan otomatis ke `history.json`.
* **Log Kompresi Lengkap**: Catatan log performa kompresi mendetail di `compression_log.txt`.

### 5. ⚙️ Pengaturan & Kustomisasi
* **Tema UI Modern**: Mendukung mode warna System, Light, dan Dark secara dinamis.
* **Kustomisasi Output**: Ubah lokasi penyimpanan folder hasil proses sesuka Anda.

---

## 📁 Struktur File

Berikut penjelasan isi folder aplikasi ini:

* 📂 **`dist/`** -> Berisi file executable siap pakai.
  * 📄 `Image Tools PRO v6.0.0.exe` -> **File aplikasi utama**. Cukup double-click file ini untuk menggunakan aplikasi tanpa perlu menginstal Python.
* 📄 **`image tools pro v6.py`** -> Source code Python utama (untuk keperluan pengembangan/debugging).
* 📄 **`Image Tools PRO v6.0.0.spec`** -> Konfigurasi PyInstaller untuk mem-build kode Python menjadi file `.exe`.
* 📄 **`image-tools.ico`** -> Icon resmi aplikasi.
* 📄 **`settings.json`** -> Menyimpan preferensi konfigurasi tema dan folder output Anda.
* 📄 **`history.json`** -> Menyimpan riwayat aktivitas operasi aplikasi secara lokal.
* 📖 **`UPDATE_GUIDE.md`** -> Panduan pengguna lengkap dan user-friendly (sangat disarankan dibaca terlebih dahulu!).
* 📖 **`UPDATE_DOCUMENTATION.md`** -> Dokumentasi teknis terperinci untuk developer.

---

## 🚀 Panduan Penggunaan (Quick Start)

### A. Untuk Pengguna Umum (Tanpa Install Python)
1. Buka folder `dist`.
2. Double-click file `Image Tools PRO v6.0.0.exe`.
3. Aplikasi siap digunakan! Baca `UPDATE_GUIDE.md` untuk panduan visual lengkap.

### B. Untuk Developer (Menjalankan / Mengembangkan Source Code)
1. **Install Dependensi**:
   Buka terminal/command prompt pada direktori ini, kemudian instal paket-paket Python yang dibutuhkan:
   ```bash
   pip install customtkinter pillow fpdf PyPDF2
   ```
2. **Jalankan Aplikasi**:
   ```bash
   python "image tools pro v6.py"
   ```
3. **Kompilasi Menjadi File `.exe` Baru**:
   Jika Anda melakukan modifikasi kode dan ingin membuat file `.exe` baru:
   ```bash
   python -m PyInstaller --clean "Image Tools PRO v6.0.0.spec"
   ```

---

## 🛠️ Persyaratan Sistem & Dependensi

* **Sistem Operasi**: Windows 10/11 (direkomendasikan) 64-bit.
* **Python Version**: Python 3.10 ke atas (khusus untuk Developer).
* **Library Utama**:
  * `customtkinter` (Modern UI)
  * `pillow` (Pemrosesan Gambar)
  * `fpdf` (Pembuatan PDF dari Gambar)
  * `PyPDF2` (Kompresi & Penggabungan PDF)

---

## 🔧 Troubleshooting & Catatan Penting

* **Konversi SVG lambat / gagal**: Konversi SVG opsional memerlukan pustaka `cairosvg`. Jika tidak terinstal atau tidak kompatibel dengan Windows DLL Anda, konversi SVG akan dilewati secara aman.
* **Window Tidak Muncul**: Jika file `.exe` tidak terbuka, pastikan antivirus Anda tidak memblokir aplikasi baru yang belum dikenal (pilih "Run anyway" jika muncul smartscreen Windows).
* **Pintasan Keyboard (Shortcuts)**:
  * `Ctrl + O`: Memilih file gambar masukan.
  * `Ctrl + S`: Menyimpan pengaturan saat ini.
  * `Ctrl + Z`: Undo (membatalkan) operasi kompresi/konversi terakhir.
  * `F1`: Menampilkan jendela bantuan.

---

## 🔄 Migrasi dari v5.0

* **Migrasi Pengaturan**: Konfigurasi tema dan folder output dari versi 5.0 akan langsung dideteksi dan diimpor secara otomatis ke versi 6.0 tanpa konfigurasi ulang.
* **Backup Aman**: File riwayat dan cadangan pemrosesan lama dipindahkan secara aman ke folder `update_backup/` agar tidak menimpa data baru Anda.

---

## 📞 Hubungi & Dukungan

* **Panduan Lengkap**: Baca `UPDATE_GUIDE.md`
* **Dokumentasi Teknis**: Baca `UPDATE_DOCUMENTATION.md`
* **Saweria Dukungan**: Hubungi Developer melalui tombol donasi di aplikasi (Saweria Habib Frambudi)

---
**Versi:** v6.0.0  
**Tanggal Rilis:** Mei 2026  
**Developer:** Habib Frambudi  
