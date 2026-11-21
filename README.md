# Musik

Pemutar musik lokal dengan tampilan ala Spotify. Aplikasi membaca lagu dari folder di komputer Anda, menampilkan judul, artis, dan sampul secara otomatis, dan menampilkan lirik yang bergerak mengikuti lagu. Tidak perlu login dan tidak ada data yang dikirim ke internet.

## Fitur

- Daftar lagu terisi otomatis dari folder; tidak ada input manual
- Judul, artis, album, durasi, dan sampul dibaca dari tag file
- Panel lirik dengan sorotan baris aktif (format `.lrc`) atau lirik teks biasa
- Klik baris lirik untuk lompat ke bagian itu
- Putar, jeda, sebelumnya, berikutnya, acak, ulangi (semua / satu lagu)
- Slider progress dan volume yang bisa diklik atau digeser
- Lagu disukai, pencarian judul atau artis
- Tambah lagu lewat seret-dan-lepas atau tombol Pilih file
- Pintasan keyboard dan dukungan tombol media sistem
- Warna panel mengikuti sampul lagu yang sedang diputar

## Kebutuhan

- Python 3.8 atau lebih baru
- Browser modern (Chrome, Edge, Firefox, Safari)
- Mutagen (opsional, disarankan)

Tanpa Mutagen, aplikasi tetap berjalan: judul dan artis diambil dari nama file, sedangkan sampul dan durasi di daftar tidak tampil.

## Instalasi

```bash
pip install mutagen
```

Susunan folder:

```
project/
  main.py
  index.html
  Weird_Genius_-_Sweet_Scar.mp3     (boleh di sini)
  musik/                            (atau di sini; subfolder ikut dipindai)
    Lagu Lain.mp3
```

## Menjalankan

```bash
python main.py
```

Browser terbuka otomatis di `http://127.0.0.1:8765`. Jika port itu terpakai, aplikasi memakai port berikutnya dan menampilkan alamatnya di terminal. Tekan Ctrl+C di terminal untuk berhenti.

## Menambah lagu

Pilih salah satu cara:

1. Salin file musik ke folder `musik/`. Daftar diperbarui otomatis dalam sekitar 5 detik.
2. Seret file ke jendela aplikasi.
3. Klik tombol plus di Pustaka atau Pilih file.

Dua cara terakhir menyimpan file ke folder `musik/`. Format yang didukung: MP3, M4A, FLAC, OGG, dan WAV. Sampul dan lirik tertanam hanya dibaca dari MP3 (tag ID3); format yang bisa diputar juga bergantung pada browser Anda.

Jika tag kosong, judul dan artis diambil dari nama file dengan pola `Artis - Judul.mp3`. Garis bawah diubah menjadi spasi.

## Lirik

### Cara memuat lirik

Aplikasi mencari file lirik dengan nama yang sama persis dengan file musik, di folder yang sama atau di `musik/`:

| File musik | File lirik |
|---|---|
| `Weird_Genius_-_Sweet_Scar.mp3` | `Weird_Genius_-_Sweet_Scar.lrc` atau `.txt` |

- Jika ada `.lrc` dan `.txt`, yang dipakai adalah `.lrc`.
- File lirik yang kosong diabaikan.
- Jika tidak ada file lirik, aplikasi memakai lirik tertanam di tag MP3 (USLT) bila ada.

### Menambah atau mengubah lirik dari aplikasi

1. Putar lagu, lalu klik ikon mikrofon di player untuk membuka panel lirik.
2. Klik Tambah lirik (atau Ubah lirik jika sudah ada).
3. Tempel lirik, lalu klik Simpan lirik.

Lirik disimpan di samping file musik. Jika teks mengandung penanda waktu, file disimpan sebagai `.lrc`; jika tidak, sebagai `.txt`.

### Format `.lrc`

Setiap baris diawali waktu `[menit:detik.persen]`:

```
[00:12.30] teks baris pertama
[00:16.80] teks baris kedua
```

Lirik berformat ini bergerak dan menyorot baris yang sedang dinyanyikan. Lirik teks biasa hanya tampil statis. Satu baris boleh punya beberapa waktu, misalnya `[00:20.00][01:05.50] teks` untuk bagian yang berulang.

Aplikasi ini tidak menyertakan lirik apa pun. Anda menyediakan liriknya sendiri.

## Akses dari perangkat lain di Wi-Fi yang sama

Secara bawaan aplikasi hanya bisa dibuka dari komputer yang menjalankannya. Untuk mendengarkan dari ponsel atau laptop lain yang tersambung ke Wi-Fi yang sama:

```bash
python main.py --lan
```

Terminal menampilkan alamat seperti `http://192.168.x.x:8765`. Buka alamat itu di perangkat lain.

- Perangkat lain hanya bisa mendengarkan dan melihat lirik. Tambah lagu dan ubah lirik hanya bisa dilakukan dari komputer yang menjalankan aplikasi, lewat `http://127.0.0.1:8765`.
- Aplikasi tidak bisa diakses dari internet; hanya perangkat di jaringan yang sama.
- Jika Windows menampilkan peringatan firewall, pilih Izinkan untuk jaringan pribadi.
- Beberapa Wi-Fi kampus memblokir komunikasi antarperangkat. Jika alamat tidak bisa dibuka, sambungkan semua perangkat ke hotspot ponsel.
- Hentikan dengan Ctrl+C setelah selesai, dan jalankan tanpa `--lan` untuk pemakaian pribadi.

## Kontrol

| Aksi | Cara |
|---|---|
| Putar lagu | Klik nomor baris lagu, atau klik 2x barisnya |
| Putar atau jeda | Tombol putar di player, atau Spasi |
| Maju atau mundur 5 detik | Panah kanan atau kiri |
| Lompat ke posisi | Klik atau geser slider progress |
| Sebelumnya | Tombol sebelumnya (jika lagu sudah berjalan lebih dari 3 detik, kembali ke awal lagu) |
| Acak dan ulangi | Tombol acak dan ulangi; ulangi berganti antara mati, semua, dan satu lagu |
| Volume dan bisukan | Slider volume dan ikon speaker |
| Sukai lagu | Ikon hati di baris lagu |
| Lihat lagu disukai | Pilih Disukai di Pustaka |
| Cari | Kolom Cari judul atau artis |
| Buka atau tutup lirik | Ikon mikrofon, atau tombol Tutup di panel lirik |

Daftar lagu disukai dan level volume disimpan di browser (localStorage), jadi tetap ada saat aplikasi dibuka lagi di browser yang sama.

## Struktur proyek

| File | Peran |
|---|---|
| `main.py` | Server lokal (hanya pustaka standar Python): memindai folder, membaca tag, mengirim audio dengan dukungan seek, serta menyimpan lirik dan file unggahan |
| `index.html` | Seluruh antarmuka: tampilan, pemutar, lirik, dan pustaka dalam satu file |

Endpoint server (secara bawaan hanya dapat diakses dari komputer Anda sendiri, `127.0.0.1`):

| Endpoint | Fungsi |
|---|---|
| `GET /api/info` | Status akses (hanya-dengar atau penuh) |
| `GET /api/library` | Daftar lagu beserta metadata |
| `GET /audio/<id>` | Audio, mendukung Range request |
| `GET /cover/<id>` | Sampul dari tag MP3 |
| `GET /api/lyrics/<id>` | Teks lirik |
| `POST /api/lyrics/<id>` | Simpan lirik |
| `PUT /api/upload?name=...` | Simpan file ke folder `musik/` |

## Pemecahan masalah

| Masalah | Solusi |
|---|---|
| Daftar kosong | Pastikan file musik ada di folder `main.py` atau di `musik/`, lalu tunggu beberapa detik |
| Judul berupa nama file, sampul tidak muncul | Jalankan `pip install mutagen` lalu mulai ulang aplikasi; sampul hanya terbaca dari MP3 yang punya gambar tertanam |
| Lirik tidak muncul | Nama file lirik harus sama persis dengan nama file musik, dan isinya tidak boleh kosong |
| Lirik tampil tetapi tidak bergerak | Lirik berformat teks biasa; ubah ke `.lrc` dengan penanda waktu |
| Lagu tidak bisa diputar | Format file mungkin tidak didukung browser; coba MP3 |
| Tidak ada suara | Periksa slider volume dan volume sistem |
| Alamat lain muncul di terminal | Port 8765 sedang dipakai; buka alamat yang tertulis di terminal |

## Catatan

- Aplikasi berjalan di komputer Anda; tidak ada akun, penyimpanan awan, atau pelacakan. Akses dari perangkat lain hanya terbuka jika Anda menjalankan `--lan`.
- Selain daftar lagu disukai dan volume, tidak ada pengaturan lain yang disimpan; semua lagu berasal dari isi folder.
- Hapus lagu dengan menghapus filenya dari folder.