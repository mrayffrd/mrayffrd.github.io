# 🎮 Pop It Game - Panduan Setup Lengkap (100% Gratis)

## Apa yang kamu dapatkan
- Game Pop-It (klik)
- Sistem login/register
- Inventori (mora, credit, gift box, banner, pet)
- Redeem kode via Spreadsheet
- 2 Gacha (Zero & Infinite) dengan rate & item yang bisa diedit di Spreadsheet
- Pet yang menghasilkan mata uang otomatis
- Banner / background profile
- Chat global (hilang setelah 3 jam)
- Data tersimpan permanen di Google Sheets (tidak hilang kalau clear browser)

---

## Langkah 1: Buat Google Spreadsheet

1. Buka [https://sheets.google.com](https://sheets.google.com)
2. Buat Spreadsheet baru, beri nama misalnya **PopIt Game Data**
3. Biarkan kosong dulu (script nanti akan otomatis membuat sheet yang dibutuhkan)

---

## Langkah 2: Pasang Google Apps Script

1. Di Spreadsheet tersebut, klik **Extensions → Apps Script**
2. Hapus semua kode yang ada di editor
3. Buka file `AppsScript.gs` yang ada di folder ini
4. **Copy seluruh isinya** dan paste ke editor Apps Script
5. Klik ikon 💾 **Save** (atau Ctrl+S)
6. Beri nama project misalnya `PopIt API`

### Deploy jadi Web App
1. Klik **Deploy → New deployment**
2. Di samping "Select type" klik ikon roda gigi → pilih **Web app**
3. Isi:
   - Description: `PopIt Game API`
   - Execute as: **Me**
   - Who has access: **Anyone**
4. Klik **Deploy**
5. Akan muncul peringatan izin → klik **Authorize access** → pilih akun Google kamu → Advanced → Go to ... (unsafe) → Allow
6. **Copy URL** yang muncul (bentuknya `https://script.google.com/macros/s/AKfycb.../exec`)

---

## Langkah 3: Hubungkan ke Frontend

1. Buka file `script.js`
2. Cari baris ini:
   ```js
   const API_URL = "https://script.google.com/macros/s/AKfycbxXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/exec";
   ```
3. Ganti dengan URL yang kamu copy tadi
4. Pastikan `SECRET` di `script.js` sama dengan yang di `AppsScript.gs` (default: `popit_secret_2026`)

---

## Langkah 4: Jalankan Game

Kamu bisa:
- Buka file `index.html` langsung di browser (double click), **atau**
- Host gratis di:
  - GitHub Pages
  - Netlify Drop (drag & drop folder)
  - Vercel
  - Cloudflare Pages

**Catatan:** Karena fetch ke Google Apps Script, lebih baik di-host (bukan file://) agar tidak kena CORS. Netlify Drop paling mudah.

---

## Struktur Spreadsheet (otomatis dibuat)

Setelah pertama kali dipanggil, akan muncul sheet:

### Users
| username | password | mora | credit | data (JSON) | lastLogin |
|----------|----------|------|--------|-------------|-----------|

### Redeem
| code | giftName | mora | credit | maxUses | usedCount |
|------|----------|------|--------|---------|-----------|
| WELCOME100 | Welcome Box | 100 | 50 | 999 | 0 |
| GIFT500 | Big Gift | 500 | 0 | 50 | 0 |

**Cara tambah kode redeem:** tinggal tambah baris baru di sheet Redeem.

### GachaZero & GachaInfinite
| id | name | type | imageUrl | chance | amount | earnType | earnAmount | intervalMinutes |
|----|------|------|----------|--------|--------|----------|------------|-----------------|

**type** bisa: `mora`, `credit`, `banner`, `pet`

**chance** = bobot peluang (semakin tinggi semakin sering muncul)

Contoh:
- chance 40 → muncul lebih sering
- chance 5 → rarer

Untuk **pet**:
- earnType = `mora` atau `credit`
- earnAmount = berapa yang dihasilkan
- intervalMinutes = setiap berapa menit

Untuk **banner**:
- imageUrl = link gambar (bisa dari Imgur, Google Drive public, Picsum, dll)

---

## Cara Edit Konten Tanpa Sentuh Coding

| Yang ingin diubah | Sheet yang diedit |
|-------------------|-------------------|
| Kode redeem + hadiah | Redeem |
| Item & rate Zero Gacha | GachaZero |
| Item & rate Infinite Gacha | GachaInfinite |
| Data user (manual) | Users (hati-hati) |

---

## Keamanan Sederhana

- Secret key (`popit_secret_2026`) mencegah orang lain sembarangan panggil API
- Password disimpan plain text (cukup untuk game kecil). Kalau mau lebih aman bisa di-hash nanti.
- Siapa saja yang punya URL Web App bisa coba, tapi tanpa secret tidak bisa.

---

## Troubleshooting

**"Gagal terhubung ke server"**
- Pastikan URL di script.js sudah benar
- Pastikan deployment "Anyone"
- Coba buka URL API di browser (harus muncul `{"success":true,"message":"Pop It API is running"}`)

**Gacha / Redeem tidak jalan**
- Pastikan sheet sudah terbuat (panggil sekali dulu lewat game)
- Cek nama sheet harus persis: `Users`, `Redeem`, `GachaZero`, `GachaInfinite`, `Chat`

**Foto profil tidak tersimpan**
- Maksimal ±500KB (karena disimpan sebagai base64 di cell)

---

## File yang ada di folder ini

```
popit-game/
├── index.html          ← Login / Register
├── Game.html           ← Game Pop-It
├── Inventori.html      ← Inventori + Redeem
├── Gacha.html          ← Zero & Infinite Gacha
├── Profile.html        ← Profile, Pet, Chat, Banner
├── style.css           ← Tampilan (ganti background di :root)
├── script.js           ← Logika + koneksi API
├── AppsScript.gs       ← Backend (paste ke Google Apps Script)
└── SETUP.md            ← Panduan ini
```

---

Selamat bermain!  
Kalau ada error atau mau tambah fitur, tinggal bilang.
