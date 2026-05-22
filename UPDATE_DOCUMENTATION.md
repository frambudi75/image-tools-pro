# Image Tools PRO v6.0 - Update Documentation

## 📋 Overview
Image Tools PRO telah diperbarui ke versi 6.0 dengan fitur **Update Otomatis** yang lengkap dan perbaikan UI pada tab Pengaturan.

## 🚀 Fitur Baru

### 1. Update Otomatis
- **Pengaturan Update Otomatis**: Pengguna dapat mengaktifkan/nonaktifkan update otomatis
- **Frekuensi Update**: Pilihan frekuensi cek update:
  - Saat startup aplikasi
  - Harian
  - Mingguan
- **Notifikasi Update**: Notifikasi otomatis saat ada versi baru tersedia
- **Download & Install Otomatis**: Opsi untuk download dan install update secara otomatis
- **Backup Otomatis**: Backup file penting (qris.jpeg, settings.json, history.json) sebelum update
- **Restart Otomatis**: Prompt untuk restart aplikasi setelah update berhasil

### 2. Perbaikan UI Tab Pengaturan
- **Hapus Scrollable Frame**: Tab Pengaturan sekarang menampilkan semua elemen tanpa scroll
- **Layout Tetap**: Semua pengaturan terlihat dalam satu tampilan
- **Responsivitas**: UI lebih responsif dan mudah diakses

## 🔧 Perubahan Teknis

### File yang Dimodifikasi
- `gambar-kompres.py`: Penambahan fitur update otomatis dan perbaikan UI

### Konstanta Baru
```python
# Auto-update settings
AUTO_UPDATE_ENABLED = False
AUTO_UPDATE_FREQUENCY = "startup"  # startup, daily, weekly
LAST_UPDATE_CHECK = None
UPDATE_CHECK_THREAD = None
```

### Metode Baru
- `initialize_auto_update()`: Inisialisasi fitur update otomatis
- `toggle_auto_update()`: Toggle aktif/nonaktif update otomatis
- `change_update_frequency()`: Ubah frekuensi cek update
- `schedule_auto_update_check()`: Jadwalkan cek update otomatis
- `perform_auto_update_check()`: Lakukan cek update di background
- `show_update_notification()`: Tampilkan notifikasi update
- `download_and_install_update()`: Download dan install update
- `show_restart_prompt()`: Tampilkan prompt restart

### Perubahan UI
- Tab Pengaturan tidak menggunakan `CTkScrollableFrame` lagi
- Semua frame pengaturan menggunakan padding standar
- Tombol support developer selalu terlihat

## 📊 Cara Kerja Update Otomatis

### 1. Inisialisasi
- Saat aplikasi startup, load pengaturan update dari `settings.json`
- Jika update otomatis aktif, jadwalkan cek update berdasarkan frekuensi

### 2. Cek Update
- Menggunakan GitHub API untuk cek versi terbaru
- URL: `https://api.github.com/repos/{GITHUB_REPO}/releases/latest`
- Bandingkan versi saat ini dengan versi terbaru

### 3. Notifikasi Update
- Jika ada versi baru, tampilkan dialog notifikasi
- Opsi: Download otomatis, buka halaman download, atau lewati

### 4. Download & Install
- Download file update dari GitHub releases
- Backup file penting ke folder `update_backup`
- Replace file lama dengan yang baru
- Restore file penting dari backup
- Prompt untuk restart aplikasi

## ⚙️ Pengaturan Update

### Aktivasi Update Otomatis
1. Buka tab "Pengaturan"
2. Centang "Aktifkan update otomatis"
3. Pilih frekuensi cek update

### Frekuensi Update
- **Saat startup**: Cek update setiap kali aplikasi dibuka
- **Harian**: Cek update sekali sehari
- **Mingguan**: Cek update sekali seminggu

## 🔒 Keamanan & Backup

### File yang Di-backup
- `qris.jpeg`: Gambar QRIS untuk support developer
- `settings.json`: Pengaturan aplikasi
- `history.json`: Riwayat operasi

### Proses Backup
1. Buat folder `update_backup` di direktori aplikasi
2. Copy file penting ke folder backup
3. Lakukan update
4. Restore file penting dari backup
5. Hapus folder backup setelah berhasil

## 🐛 Troubleshooting

### Update Gagal
- Pastikan koneksi internet stabil
- Cek apakah file aplikasi tidak sedang digunakan
- Restart aplikasi dan coba lagi

### Notifikasi Tidak Muncul
- Pastikan update otomatis aktif
- Cek pengaturan frekuensi
- Restart aplikasi untuk menerapkan pengaturan

### Backup Gagal
- Pastikan folder aplikasi memiliki permission write
- Cek apakah file backup tidak terkunci

## 📝 Catatan Pengembang

### Dependencies
- `requests`: Untuk HTTP requests ke GitHub API
- Sudah ada dalam requirements.txt

### GitHub Repository
- Pastikan `GITHUB_REPO` diatur dengan benar
- Format: `username/repository-name`

### Versioning
- Versi aplikasi disimpan dalam `CURRENT_VERSION`
- Update versi di kode setelah release

## 🎯 Testing Checklist

### Fitur Update Otomatis
- [ ] Aktivasi/nonaktifkan update otomatis
- [ ] Perubahan frekuensi update
- [ ] Cek update manual
- [ ] Notifikasi update muncul
- [ ] Download & install otomatis
- [ ] Backup & restore file penting
- [ ] Restart aplikasi setelah update

### UI Tab Pengaturan
- [ ] Semua elemen terlihat tanpa scroll
- [ ] Tombol support developer terlihat
- [ ] Responsivitas UI
- [ ] Layout tetap saat resize window

## 📈 Performance Impact

### CPU/Memory
- Cek update berjalan di background thread
- Minimal impact pada performa aplikasi utama

### Network
- Request ke GitHub API hanya saat diperlukan
- Timeout 10 detik untuk menghindari hanging

### Storage
- Backup temporary menggunakan storage minimal
- Cleanup otomatis setelah update selesai

## 🔄 Rollback Plan

### Jika Update Gagal
1. Gunakan file backup di folder `update_backup`
2. Restore file penting secara manual
3. Restart aplikasi
4. Nonaktifkan update otomatis jika diperlukan

### Recovery Steps
1. Close aplikasi
2. Copy file dari `update_backup` ke folder utama
3. Delete folder `update_backup`
4. Restart aplikasi

## 📞 Support

Untuk bantuan atau laporan bug:
- Email: [kontak.habibframbudi.my.id](https://kontak.habibframbudi.my.id)
- GitHub Issues: [Repository Issues](https://github.com/frambudi75/jpg-to-pdf-convert/issues)

---

**Dibuat oleh:** Habib Frambudi
**Versi:** 6.0
**Tanggal:** 2024
