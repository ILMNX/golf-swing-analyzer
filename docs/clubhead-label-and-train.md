#  Tutorial: Label clubhead + train YOLO

Panduan lengkap untuk menaikkan akurasi tracking stik. Model sekarang lemah karena pernah dilatih dari label otomatis yang salah. Yang kamu lakukan: **gambar kotak di clubhead secara manual**, lalu **train ulang**.


|        |                                                                 |
| ------ | --------------------------------------------------------------- |
| Waktu  | 1.5–3 jam label + 30–90 menit train (CPU)                       |
| Target | 200–400 kotak benar; val mAP50 **≥ 0.60**                       |
| Hasil  | file `ml-engine/yolov8n-club.pt` dipakai otomatis saat analisis |


Semua perintah di bawah dijalankan dari folder `ml-engine/`, kecuali disebut lain.

```text
cd /path/ke/golf-swing-analyzer/ml-engine
```

---



## Ringkasan alur

```text
1. Cek frame JPG di to_label/
2. Label kotak clubhead (Label Studio ATAU Roboflow)
3. Import file label .txt ke to_label/
4. Split train/val
5. Train 100 epoch → yolov8n-club.pt
6. Restart API, analisis video lagi, cek overlay
```

Pilih **satu** tool annotate: Label Studio (lokal) atau Roboflow (browser). Jangan campur dua alur di sesi yang sama.

---



## Bagian A — Aturan menggambar kotak

Ini yang paling menentukan akurasi. Salah box = train percuma.

### Yang di-box

- Hanya **kepala stik** (driver / iron / wood).
- Saat downswing: box **noda blur** clubhead, meski tidak tajam.
- Sisakan margin kecil (beberapa pixel) di luar kepala.



### Yang tidak di-box

- Shaft penuh
- Tangan / grip
- Bola (kecuali kebetulan menempel di head — tetap fokus head)
- Kaki, rumput, penonton



### Urutan frame (kerjakan yang atas dulu)

1. **Top → impact** (clubhead buram) — paling penting
2. **Address / takeaway** — supaya garis di awal video tidak jatuh lurus ke bawah
3. Follow-through — boleh belakangan

Satu file = satu JPG. Nama label harus sama: `golf_swing_front_f000690.jpg` → `golf_swing_front_f000690.txt`.

Isi `.txt` (otomatis dari tool, jangan ketik manual kecuali debug):

```text
0 0.55 0.80 0.04 0.03
```

Artinya: class `0` (clubhead), pusat x/y, lebar, tinggi — semua 0–1.

**Jangan** pakai folder `_bootstrap_bak/` dan **jangan** jalankan `bootstrap_club_labels.py`.

---



## Bagian B — Cek data yang sudah ada

```bash
ls datasets/clubhead/to_label/*.jpg | wc -l
ls datasets/clubhead/to_label/*.txt 2>/dev/null | wc -l
```

- Angka JPG: seharusnya ratusan (contoh ~183).
- Angka TXT: **0** sebelum kamu mulai label. Setelah import, harus hampir sama dengan jumlah yang sudah kamu anotasi.

Kalau JPG 0, extract dulu (Bagian G).

---



## Bagian C — Label Studio (lokal)

Gunakan ini jika kamu mau data tetap di komputer.

### C.1 Install (sekali)

Pilih salah satu:

```bash
pipx install label-studio
```

atau:

```bash
python3 -m pip install --user label-studio
```

Cek:

```bash
label-studio --version
```



### C.2 Siapkan task + environment

```bash
cd ml-engine
chmod +x scripts/start_label_studio_clubhead.sh
./scripts/start_label_studio_clubhead.sh
```

Script ini:

1. Membuat `datasets/clubhead/label_studio_tasks.json` (gambar yang belum punya `.txt`)
2. Mencetak `DOCUMENT_ROOT` dan cara start
3. Menjalankan Label Studio di `http://127.0.0.1:8080` jika `label-studio` ada di PATH

Kalau script berhenti dengan “not on PATH”, start manual **di terminal yang sama** setelah export env (copy dari output script):

```bash
export LABEL_STUDIO_LOCAL_FILES_SERVING_ENABLED=true
export LABEL_STUDIO_LOCAL_FILES_DOCUMENT_ROOT="$(pwd)/datasets/clubhead"
label-studio start --host 127.0.0.1 --port 8080
```

`DOCUMENT_ROOT` harus tepat folder `datasets/clubhead` (induk dari `to_label/`). Salah folder = gambar tidak muncul.

Buka browser: [http://127.0.0.1:8080](http://127.0.0.1:8080)

Buat akun lokal jika diminta (hanya di mesinmu).

### C.3 Buat project

1. **Create** → project baru, nama misalnya `clubhead`
2. **Settings** → **Labeling Interface** → tab **Code**
3. Hapus template default, paste seluruh isi file:
  `datasets/clubhead/label_studio_config.xml`
4. **Save**

Config itu satu class: `clubhead`, kotak persegi di atas gambar.

### C.4 Import gambar

1. **Import**
2. Pilih file: `datasets/clubhead/label_studio_tasks.json`
3. Pastikan jumlah task = jumlah JPG yang belum dilabel
4. Buka satu task: foto harus tampil. Jika rusak / 404, hentikan Label Studio, cek ulang `DOCUMENT_ROOT`, start lagi.



### C.5 Cara label di UI

1. Klik label **clubhead** (kiri / atas)
2. Drag kotak di kepala stik
3. **Submit** / **Update** (tombol utama, jangan skip kecuali frame benar-benar tidak ada clubhead)
4. Next image

Tips cepat:

- Zoom di UI jika head kecil
- Frame tanpa stik terlihat: **Skip** (jangan kotak sembarangan)
- Kerjakan dulu file yang namanya di tengah–akhir swing (blur), bukan hanya address

Target sesi pertama: **minimal ~200 Submit** yang kotaknya benar.

### C.6 Export

1. Di project: **Export**
2. Format: **JSON** (bukan COCO / YOLO dari Label Studio — kita convert sendiri)
3. Simpan file, misalnya `~/Downloads/clubhead-export.json`



### C.7 Masukkan label ke `to_label/`

```bash
cd ml-engine
./venv/bin/python scripts/import_label_studio_export.py ~/Downloads/clubhead-export.json
```

Ganti path ke file export-mu. Output contoh: `Wrote 200 YOLO labels`.

Cek:

```bash
ls datasets/clubhead/to_label/*.txt | wc -l
```

Lanjut ke **Bagian E**.

---



## Bagian D — Roboflow (browser)

Gunakan ini jika Label Studio terasa berat. Perlu akun Roboflow (gratis cukup).

### D.1 Pack gambar

```bash
cd ml-engine
./venv/bin/python scripts/pack_to_label_for_roboflow.py
```

File zip: `datasets/clubhead/roboflow_upload_to_label.zip`

Untuk hanya gambar yang belum dilabel:

```bash
./venv/bin/python scripts/pack_to_label_for_roboflow.py --skip-labeled
```



### D.2 Project di web

1. Buka [https://roboflow.com](https://roboflow.com) → login
2. **New Project**
3. Tipe: **Object Detection**
4. Nama bebas, misalnya `golf-clubhead`
5. **Upload** zip di atas, tunggu selesai
6. Saat diminta class / label: tulis persis `clubhead` (huruf kecil)



### D.3 Annotate

1. Masuk mode annotate
2. Satu kotak per gambar di **clubhead** (aturan Bagian A)
3. Selesaikan batch (target 200+)



### D.4 Export YOLO

1. **Generate** version (boleh tanpa augmentasi dulu — pipeline train kita sudah augment)
2. **Export** → format **YOLOv8**
3. Download file `.zip`



### D.5 Import ke repo

```bash
cd ml-engine
./venv/bin/python scripts/import_roboflow_yolo.py ~/Downloads/<nama-export>.zip
```

Warning `no matching JPG` artinya nama file di zip tidak sama dengan `to_label/` — jangan diabaikan jika banyak. Lanjut ke **Bagian E**.

---



## Bagian E — Split train / val

Hanya JPG yang **punya pasangan** `.txt` yang masuk training.

```bash
cd ml-engine
./venv/bin/python scripts/split_club_labels.py \
  --src datasets/clubhead/to_label \
  --dataset datasets/clubhead \
  --val-ratio 0.15
```

Contoh sukses: `Split 220 pairs → train=187, val=33`

Kalau error `No JPG+TXT pairs`: import di C.7 / D.5 belum jalan, atau `.txt` tidak di `to_label/`.

Val **minimal ~25–30** gambar. Kalau total label < 50, annotasi dulu lebih banyak.

---



## Bagian F — Train

```bash
cd ml-engine
./venv/bin/python scripts/train_clubhead.py --epochs 100 --imgsz 640
```

Opsional GPU:

```bash
./venv/bin/python scripts/train_clubhead.py --epochs 100 --imgsz 640 --device 0
```

CPU: biarkan sampai selesai (bisa 1 jam+). Jangan kill di tengah kecuali kamu sadar `best.pt` sudah ada dan mau pakai versi setengah jadi.

Selesai sukses, terminal mencetak kira-kira:

```text
Exported .../runs/clubhead/train/weights/best.pt → .../yolov8n-club.pt
```



### Baca apakah train “lulus”

Buka log train atau `runs/clubhead/train/results.csv`. Kolom penting: **mAP50**.


| mAP50 (val) | Artinya                                                                     |
| ----------- | --------------------------------------------------------------------------- |
| ≥ 0.70      | Bagus untuk overlay                                                         |
| 0.60–0.70   | Layak tes di app                                                            |
| 0.40–0.60   | Kurang; perbaiki / tambah label blur                                        |
| < 0.40      | Hampir pasti box salah atau terlalu sedikit — **jangan** cuma naikkan epoch |


Recall rendah + precision tinggi: model jarang deteksi (kurang contoh blur).  
Precision rendah: banyak false box (label kotor / background).

---



## Bagian G — Tambah frame dari video lain (opsional)

Berguna jika hanya satu sudut kamera. Tambah 1 clip DTL atau face-on lain.

1. Simpan video di `ml-engine/video/` (atau path lengkap)
2. Extract:

```bash
./venv/bin/python scripts/extract_club_frames.py \
  --videos video/golf_swing_front.mp4 video/nama_lain.mp4 \
  --out datasets/clubhead/to_label \
  --max-per-video 250
```

1. Label JPG **baru** saja:
  - Label Studio: `./venv/bin/python scripts/prepare_label_studio_tasks.py --skip-labeled` lalu import JSON task lagi
  - Roboflow: `pack_to_label_for_roboflow.py --skip-labeled`
2. Ulangi split + train

---



## Bagian H — Verifikasi di aplikasi

1. **Restart** proses ml-engine / FastAPI (agar load `yolov8n-club.pt` baru). Kalau tidak restart, bisa masih pakai weights lama di memory.
2. Analisis ulang:
  - clip `video/golf_swing_front.mp4`
  - video yang sebelumnya gagal (mis. swing teman)
3. Di halaman report, cek:
  - `yolo_enabled`: **true**
  - `method`: **line+yolo+kalman**



### Cek visual overlay merah


| Fase      | Yang benar                                           | Yang masih salah                 |
| --------- | ---------------------------------------------------- | -------------------------------- |
| Address   | Titik ujung di **kepala stik**, shaft mengikuti stik | Garis lurus ke bawah dari tangan |
| Top       | Ujung di head / smear di belakang kepala             | Ujung di penonton / udara kosong |
| Downswing | Ujung mengikuti blur                                 | Ujung di antara kaki             |


Garis merah **sengaja hilang** jika deteksi tidak yakin. Lebih baik tanpa garis daripada garis palsu. Kalau hampir semua frame tanpa garis tapi mAP50 sudah ≥ 0.6, baru itu masalah tracker — bukan langkah pertama.

---



## Troubleshooting

**Gambar Label Studio tidak muncul**  
`DOCUMENT_ROOT` bukan `datasets/clubhead`. Start ulang dengan export yang benar. Task JSON harus berisi `/data/local-files/?d=to_label/...jpg`.

**Import LS: Wrote 0 labels**  
Export bukan JSON list, atau annotasi belum Submit. Buka file JSON: harus ada `"annotations"` dengan `"rectanglelabels"`.

**Train: Need at least ~10 labeled train images**  
Split belum dijalankan, atau `images/train` kosong.

**mAP bagus, overlay tetap kacau**  
Pastikan file `ml-engine/yolov8n-club.pt` timestamp-nya baru (setelah train). Restart API.

**Saya capek di 80 gambar**  
Train boleh dicoba, tapi overlay high-speed biasanya baru layak setelah **200+** termasuk blur. 80 address-only tidak cukup.

---



## Cheat sheet perintah

```bash
cd ml-engine

# --- Label Studio ---
./scripts/start_label_studio_clubhead.sh
./venv/bin/python scripts/import_label_studio_export.py ~/Downloads/clubhead-export.json

# --- Roboflow ---
./venv/bin/python scripts/pack_to_label_for_roboflow.py
./venv/bin/python scripts/import_roboflow_yolo.py ~/Downloads/roboflow-yolov8.zip

# --- Train ---
./venv/bin/python scripts/split_club_labels.py
./venv/bin/python scripts/train_clubhead.py --epochs 100 --imgsz 640

# Restart API, lalu upload video di app
```

File terkait: `datasets/clubhead/README.md` (versi pendek), config UI `datasets/clubhead/label_studio_config.xml`.