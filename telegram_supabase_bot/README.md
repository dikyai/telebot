# Telegram → Supabase bot

Bot Python ini menerima pesan Telegram melalui long polling dan menyimpan isi
teks/caption serta metadata pesan ke tabel `public.telegram_messages`. Media
disimpan sebagai jenis pesan dan caption; file media tidak diunduh.

## 1. Siapkan tabel di Supabase

Di Supabase, buka **SQL Editor**, jalankan isi `schema.sql`, lalu pastikan
tabel `telegram_messages` berhasil dibuat. Row Level Security aktif dan tidak
ada policy publik.

## 2. Siapkan bot Telegram

Buat bot melalui [@BotFather](https://t.me/BotFather), lalu simpan token bot
sebagai Replit Secret dengan nama `TELEGRAM_BOT_TOKEN`.

Untuk grup, bot Telegram dengan pengaturan privasi standar hanya menerima
perintah dan pesan yang menyebut bot. Jika bot perlu menyimpan semua pesan grup,
ubah Group Privacy melalui BotFather dan tambahkan bot ke grup.

## 3. Konfigurasi Secrets

Tambahkan tiga nilai ini di **Replit Secrets** (jangan tempel ke kode atau
commit ke Git):

- `TELEGRAM_BOT_TOKEN` — token dari BotFather.
- `SUPABASE_URL` — URL project, misalnya `https://<project-ref>.supabase.co`.
- `SUPABASE_SERVICE_ROLE_KEY` — service role key dari pengaturan API Supabase.

Service role key memiliki akses luas dan melewati RLS. Script hanya memakai
key tersebut di sisi server; jangan pernah mengirimkannya ke browser atau
membagikannya.

## 4. Instal dan jalankan

Dari direktori project:

```bash
python -m pip install -r telegram_supabase_bot/requirements.txt
python telegram_supabase_bot/bot.py
```

Kirim `/start` atau pesan lain ke bot. Pesan pribadi mendapat balasan setelah
tersimpan. Pesan grup disimpan tanpa membalas agar tidak memenuhi grup. Hentikan
bot dengan `Ctrl+C`.

Script memakai Telegram update ID sebagai kunci unik, sehingga update yang
dikirim ulang Telegram tidak membuat baris duplikat. Jalankan hanya satu
instance bot polling dengan token yang sama.