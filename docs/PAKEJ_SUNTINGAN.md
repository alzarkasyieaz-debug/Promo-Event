# Pakej Suntingan — Video Promo BRISKWALK MASJID BERSAMA GEN Z 2026

**Anjuran:** Masjid As-Siddiq Seri Iskandar  
**Format:** 9:16 · 1080×1920 · 30 fps · 74.5 saat · H.264 + AAC 48 kHz · −14 LUFS  
**Muzik:** 132 BPM (1 beat = 0.4545 s, 1 bar = 1.818 s). Semua potongan scene jatuh tepat pada bar.

---

## 1. Fail yang dihasilkan (`output/`)

| Fail | Kegunaan |
|---|---|
| `BRISKWALK_GenZ2026_Promo_9x16_noVO.mp4` | **Master utama.** Muzik + SFX, muzik sudah diturunkan −4 dB pada slot VO. Rakam VO lelaki sebenar dan letak di atasnya. |
| `BRISKWALK_GenZ2026_Promo_9x16_guideVO.mp4` | Versi lengkap dengan **VO panduan (suara TTS sintetik)** + ducking −10 dB. Untuk semakan timing / draf sahaja. |
| `subtitles_BM.srt` | Subtitle BM bertimestamp (frasa pendek, sepadan 100% dengan skrip VO). |
| `qr_pendaftaran.png` | Kod QR → `https://forms.gle/b9Hx6iZRGFn2xLuS6` (diuji: boleh dibaca dari frame video). |
| `stems/music.wav`, `stems/sfx.wav`, `stems/vo_guide.wav`, `stems/clip_voice.wav` | Stem berasingan (termasuk suara asli ustaz yang telah dibersihkan) untuk mix semula. |

> **Sumber visual:** (1) **Rakaman sebenar** daripada video Drive — ucapan YB Ustaz Ismi di scene 4; (2) **motion graphics maklumat** dibina daripada fakta poster rasmi (poster itu sendiri **tidak dipaparkan**); (3) logo Masjid As-Siddiq (dipotong dari poster, tidak diubah) dan potongan gambar masjid/peserta sebagai B-roll kad; (4) latar emerald asli dengan jalur sukan emas. **Tiada footage AI** digunakan.
>
> **Nota rakaman Drive:** video asal (4:04, 464×832) dirakam di depan **poster lama** yang menyebut *Yuran RM15*, *5KM*, *Cabutan Bertuah* dan *17 & 18 (Okt)* — butiran yang **tiada dalam poster rasmi**. Seluruh latar belakang klip **dikaburkan melalui segmentasi orang** (hanya penceramah tajam), jadi poster lama tidak terbaca.
>
> **Ucapan yang dimasukkan = semua audio ucapan yang wujud dalam fail**, kecuali 0:03–0:12: salam (0:00–0:02.9) + jemputan penuh (3:52.6–4:01.05). Analisis isyarat menunjukkan **0:12–3:52 tiada suara langsung** (hanya dengung ~−50 dB, tiada harmonik pertuturan) walaupun beliau kelihatan bercakap — kemungkinan audio terputus semasa rakaman/eksport. Bahagian 0:03–0:12 tidak dimasukkan kerana menyebut "5 km"/larian (tiada dalam poster rasmi) dan sukar difahami.
> **Muzik & SFX:** dijana secara sintetik dari kod (`src/build_audio.py`) — karya asli, bebas hak cipta untuk TikTok/FB/IG/WhatsApp.

---

## 2. Skrip VO (lelaki, BM, mesra & yakin, ~150–160 patah perkataan/minit)

| # | Masa VO | Skrip (ejaan muktamad) | Nota lakonan |
|---|---|---|---|
| 1 | 00:00.35 – 00:04.27 | Warga Seri Iskandar! Dah bersedia untuk bergerak bersama? | Bertenaga, macam hos acara. Tekan "Seri Iskandar". |
| 2 | 00:05.90 – 00:13.15 | Jom sertai Briskwalk Masjid Bersama Gen Z 2026 di Masjid As-Siddiq Seri Iskandar! | "Briskwalk" sebut *brisk-wok*; "Gen Z" sebut *jen zed*; "2026" = dua ribu dua puluh enam. |
| 3 | 00:14.65 – 00:23.48 | Bukan sekadar berjalan! Inilah peluang untuk aktif, mengeratkan ukhuwah dan mencipta kenangan bersama keluarga serta rakan-rakan! | Senyum dalam suara. Jeda kecil selepas "berjalan!". |
| ★1 | 00:23.76 – 00:26.62 | *(Suara asli YB Ustaz Ismi, Ahli Parlimen Parit)* "Assalamualaikum warahmatullahi wabarakatuh." | Rakaman sebenar — bukan VO. |
| ★2 | 00:26.83 – 00:35.08 | *(Suara asli, jump-cut)* "Sesama kita, saya jemput orang ramai pada hujung minggu depan pada 21 bulan November. Terima kasih." | Rakaman sebenar — bukan VO. |
| — | — | *(VO "Catat tarikh! … Bertempat di Masjid As-Siddiq Seri Iskandar" digugurkan untuk memberi ruang kepada ucapan penuh; tarikh, hari & lokasi dipaparkan di panel skrin sepanjang ucapan dan disebut dalam VO 2 & 6.)* | |
| 5 | 00:36.96 – 00:46.76 | Pendaftaran masih dibuka! Tapi ingat, tarikh tutup ialah Selasa, 17 November 2026, tepat jam 12 tengah hari! | **Penekanan maksimum** pada "17 November" dan "12 tengah hari". |
| 6 | 00:49.54 – 00:56.88 | Nak daftar? Mudah sahaja! Isi Google Form atau daftar terus di kaunter Masjid As-Siddiq Seri Iskandar. | Nada membantu, mudah. |
| 7 | 01:00.50 – 01:10.21 | Jangan tunggu lagi! Ajak keluarga, bawa sahabat dan daftar sekarang! Kita jumpa di Briskwalk Masjid Bersama Gen Z 2026! | Klimaks, paling bersemangat. Berakhir sebelum hit muzik terakhir (01:12.7). |

*Nota ejaan:* brief menulis "ukhwah"; ejaan baku DBP ialah **"ukhuwah"** dan itulah yang digunakan dalam VO, subtitle dan teks skrin (konsisten dengan "ERATKAN UKHUWAH!").

**Rakaman VO sebenar:** rakam setiap baris sebagai klip berasingan (WAV 48 kHz), letak bermula pada masa "Masa VO" di atas. Jika lebih panjang, baris mesti tamat sebelum scene seterusnya bermula (lihat jadual timeline).

---

## 3. Timeline edit terperinci

| Scene | Masa | Visual (sebenar dalam video) | Teks skrin | SFX |
|---|---|---|---|---|
| **1 Hook** | 0:00.00–0:05.45 | Latar emerald gelap, sinar emas berputar laju, garisan laju (speed lines), **tapak kasut emas melangkah ikut beat**, smash cut 3 kad B-roll poster (peserta → masjid → close-up peserta) setiap 2 beat. Shake + flash pada 0:00 & 0:03.64. | "SERI ISKANDAR," (putih 3D, slam) → "ARE YOU READY?" (emas 3D) → 0:03.64 "JOM" + "BRISKWALK!" (emas, light sweep, ledakan partikel) | Boom impact 0:00, tapak kaki ×8 ikut beat, whoosh, impact 0:03.64 |
| **2 Acara** | 0:05.45–0:14.55 | Whip pan masuk. **Dynamic logo reveal**: logo Masjid As-Siddiq pop + cincin emas mengembang + ledakan partikel + light sweep; "JOM SERTAI!" slam. Pada 0:08.85 logo bergerak ke atas, diikuti kad masjid "aerial-style" (zoom-out perlahan) → kad peserta (pan parallax). | "JOM SERTAI!" → 3D bertingkat ikut beat: "BRISKWALK" (hijau/emas) · "MASJID BERSAMA" · "GEN Z 2026" | Riser → whoosh → impact, shutter ×2 |
| **3 Tarikan** | 0:14.55–0:23.64 | Montaj kad poster (peserta pelbagai generasi, close-up, masjid) bertukar setiap 4 beat, zoom-in/zoom-out berselang, beat pulse zoom. | Berurutan setiap 5 beat dengan ikon animasi: "AKTIFKAN DIRI!" ⚡ / "AJAK SAHABAT!" 👥 / "ERATKAN UKHUWAH!" ❤ / "SATUKAN GENERASI!" 👨‍👩‍👦 | Whoosh setiap slogan, tapak kaki, sorakan sintetik lembut |
| **4 Ucapan YB Ustaz Ismi (rakaman sebenar)** | 0:23.64–0:36.36 | **0:23.76–0:35.13 ucapan** (2 segmen disambung jump-cut + flash/shutter; latar dikaburkan melalui segmentasi; push-in perlahan; grade hangat). Panel emerald-emas kanan atas: kalendar 21 NOV SABTU · 2026 · MASJID AS-SIDDIQ SERI ISKANDAR (light sweep semasa "21 bulan November"). Tag "JEMPUTAN KHAS"; **lower-third "YB Ustaz Ismi" / "Ahli Parlimen Parit"**. 0:35.13 slam pantas kad masjid + pin lokasi. | (subtitle ucapan) → "MASJID AS-SIDDIQ" · "SERI ISKANDAR" | Shutter pada jump-cut, whoosh, impact; muzik di-duck −13 dB semasa ucapan |
| **5 Urgency** | 0:36.36–0:49.09 | Latar gelap + **vignette merah berdenyut** ikut beat. Slam "PENDAFTARAN / MASIH DIBUKA!" → kalendar flip countdown 1→**17** + jam berputar ke **12.00** → slam kotak merah-emas dengan shake. Ikon amaran bergoyang. | "PENDAFTARAN MASIH DIBUKA!" · "TARIKH TUTUP PENDAFTARAN" · **"17 NOVEMBER 2026"** · "SELASA • 12.00 TENGAH HARI" | Jam berdetik 1/8, impact besar 0:41.8, bass berdenyut 16th |
| **6 Cara daftar** | 0:49.09–1:00.00 | Telefon dengan animasi borang digital generik (medan diisi → HANTAR ✓) → grafik kaunter pendaftaran → ringkasan 2 pill + **QR code**. | "CARA DAFTAR" · "ONLINE" "GOOGLE FORM" → "OFFLINE" "KAUNTER MASJID" → "ONLINE — GOOGLE FORM" / "OFFLINE — KAUNTER MASJID" · **URL kekal di skrin 0:50.0–1:00.0 (≈10 s)** · "IMBAS QR ATAU TAIP PAUTAN" | Bunyi tap ×5 |
| **7 CTA akhir** | 1:00.00–1:14.55 | Push-in dramatik ke peserta + speed lines → **freeze-frame** (flash, desaturate→warna, condong) → lockup logo + tajuk → **kad info motion graphics** (1:10.3): logo, BRISKWALK / MASJID BERSAMA GEN Z 2026, kemudian 4 baris info masuk berselang kiri/kanan (📅 Tarikh program · 📍 Lokasi · ⏰ Tarikh tutup [merah] · 👥 Cara daftar), QR, URL, butang "DAFTAR SEKARANG!" berdenyut. Hit muzik + ledakan partikel pada 1:12.7. | "JANGAN TUNGGU LAGI!" → "DAFTAR SEBELUM 17 NOVEMBER!" → "BRISKWALK MASJID BERSAMA GEN Z 2026" + "21 NOVEMBER 2026 \| MASJID AS-SIDDIQ" → kad info: "SABTU • 21 NOVEMBER 2026" / "MASJID AS-SIDDIQ SERI ISKANDAR" / "SELASA • 17 NOV 2026 • 12.00 TENGAH HARI" / "ONLINE: GOOGLE FORM \| OFFLINE: KAUNTER MASJID" / URL | Sorakan, impact, boom akhir + shutter, fade out muzik |

**Safe area:** semua teks dalam x 60–980 px, y 150–1500 px (paksi tengah x = 520 untuk mengelak butang kanan TikTok/Reels). Subtitle berpusat pada y ≈ 1395 px.

---

## 4. Subtitle (ringkasan — fail penuh `output/subtitles_BM.srt`)

Gaya: Inter Display Black 60 px, putih, outline hitam 7 px + bayang lembut, **kata penting kuning (#FFD60A)**, perkataan muncul satu-satu (pop ke atas 0.15 s). Kata yang di-highlight:

1. **Warga Seri Iskandar!** / Dah **bersedia** / untuk bergerak bersama?
2. **Jom sertai** / **Briskwalk Masjid** Bersama / **Gen Z 2026** / di **Masjid As-Siddiq** / Seri Iskandar!
3. Bukan sekadar **berjalan!** / Inilah peluang untuk **aktif,** / mengeratkan **ukhuwah** / dan mencipta **kenangan** / bersama **keluarga** / serta **rakan-rakan!**
4. *(YB Ustaz Ismi)* **Assalamualaikum** / warahmatullahi wabarakatuh. / **Sesama kita,** / saya jemput **orang ramai** / pada **hujung minggu depan** / pada **21 bulan November.** / **Terima kasih.**
5. **Pendaftaran masih dibuka!** / Tapi ingat, **tarikh tutup** ialah / **Selasa, 17 November 2026,** / tepat jam **12 tengah hari!**
6. Nak **daftar?** / **Mudah** sahaja! / Isi **Google Form** / atau daftar terus di **kaunter** / **Masjid As-Siddiq** Seri Iskandar.
7. **Jangan tunggu lagi!** / Ajak **keluarga,** / bawa **sahabat** / dan **daftar sekarang!** / Kita jumpa di / **Briskwalk Masjid Bersama Gen Z 2026!**

Jika VO sebenar berbeza tempo, import SRT ke CapCut (*Text → Captions → Import*) dan seret blok mengikut gelombang suara, atau guna *Auto Captions* lalu salin ejaan dari jadual ini.

---

## 5. Senarai B-roll

**Rakaman sebenar digunakan:** ucapan **YB Ustaz Ismi, Ahli Parlimen Parit** (video Drive, 0:00–0:02.9 + 3:52.6–4:01.05).

**Digunakan dalam video (dari poster rasmi):** kad peserta berjalan (lebar), close-up peserta lelaki & pakcik, peserta wanita bertudung, kumpulan kanan, Masjid As-Siddiq (menara + dewan solat), logo masjid.

**Disyorkan jika ada rakaman sebenar (tukar kad poster dengan footage ini):**
1. Close-up kasut sukan melangkah atas jalan berturap (slow-mo 60 fps → speed ramp).
2. Drone/tinggi: Masjid As-Siddiq Seri Iskandar waktu pagi.
3. Belia & keluarga (pakaian sopan, tudung, baju sukan hijau) berjalan pantas, ketawa, high-five.
4. Kumpulan pelbagai generasi berjalan menuju kamera (untuk scene 7 freeze-frame).
5. Tangan memegang telefon membuka borang (skrin boleh diganti dengan rakaman skrin Google Form sebenar).
6. Kaunter pendaftaran di masjid.

Footage program **tahun lepas** (jika ada) boleh dipakai dengan label kecil "Gambar hiasan: program terdahulu".

---

## 6. Prompt penjanaan footage AI (pilihan)

> Wajib: jika footage AI digunakan, letak label kecil **"Visual hiasan dijana AI"** di penjuru atas kiri (putih 60% opacity, 28 px) sepanjang klip itu, dan **jangan** gunakan footage AI yang menunjukkan papan tanda/banner acara sebenar.

Gaya asas untuk semua prompt: `vertical 9:16, cinematic sports commercial, morning golden light, emerald green and gold color grade, Malaysian suburban setting, modest clothing, women in hijab, men in t-shirts and track pants, shallow depth of field, 4K, 30fps, no text, no logos`

| Scene | Prompt |
|---|---|
| 1 | `Extreme close-up of running shoes briskly walking on asphalt, low tracking camera moving fast alongside, dust particles in sunlight, then quick tilt up to a smiling Malaysian teenage boy in a green sports t-shirt, energetic, speed ramp` |
| 2 | `Aerial drone shot slowly pulling back from a Malaysian mosque with red tiered roofs and a white minaret, palm trees, early morning sky, a group of young people and families walking briskly on the road in front, warm golden hour` |
| 3 | `Montage-style shot: diverse Malaysian youths, parents and grandparents briskwalking together in a park beside a mosque, laughing, giving high-fives, hijab-wearing women and men in matching green sports tees, handheld energetic camera, lens flare` |
| 4 | `Slow cinematic dolly shot of a Malaysian mosque entrance gate in morning light, empty clean road, birds flying, peaceful and welcoming` |
| 5 | (Tiada footage — motion graphics sahaja: kalendar, jam, kotak amaran merah-emas.) |
| 6 | `Close-up of a young Malaysian woman in hijab holding a smartphone, tapping the screen and smiling, blurred mosque courtyard background, soft daylight` (screen kosong/hijau untuk diganti) |
| 7 | `Group of multi-generational Malaysians in green sports t-shirts briskwalking directly toward the camera, smiling confidently, slow push-in, background mosque, triumphant mood, freeze-ready final frame` |

---

## 7. Motion graphics (spesifikasi)

- **Palet:** Emerald `#0B5D3B` / gelap `#04281C` · Emas `#F4B400` / cerah `#FFE282` · Kuning highlight `#FFD60A` · Merah amaran `#D62028` · Putih.
- **Teks 3D:** Inter Display Black Italic, muka gradien (emas: `#FFF6C4→#FFD44D→#E3960A`), extrusion 10–19 lapisan ke kanan-bawah (coklat-emas gelap / hijau gelap), outline hijau gelap, **golden glow** blur ≈ saiz/7.
- **Animasi masuk:** *Slam* (skala 2.8→1.0 dalam 0.22 s, ease-out cubic), *Pop* (0.3→1.0 ease-out-back), *Slide* kiri/kanan 900 px, *Drop* (pin), keluar = skala 1→1.35 + fade 0.2 s.
- **Light sweep:** jalur putih pepenjuru (25°) merentasi teks 0.8–1.0 s selepas masuk.
- **Partikel:** 70 bokeh emas terapung ke atas; ledakan radial pada "JOM BRISKWALK!" dan hit akhir.
- **Transisi:** whip pan 0.24 s (motion blur mendatar) + flash putih 0.16 s + camera shake 0.35 s pada setiap potongan scene.
- **Beat pulse:** zoom 1.8% pada setiap kick (scene 1, 3, 7).
- **URL:** JetBrains Mono ExtraBold 40 px, hijau gelap atas pill putih berbingkai emas (fon mono supaya `i`, `Z`, `L`, `6` tidak tertukar).

---

## 8. Muzik & SFX

- **Muzik:** asli, 132 BPM, C major (I–V–vi–IV: C–G–Am–F). Kick four-on-the-floor + sidechain, clap 2 & 4, hi-hat 8th/16th, bass off-beat, supersaw stabs, pad, arpeggio pluck, riser sebelum setiap scene. Scene 5 ditapis (low-pass) dengan bass 16th berdenyut untuk ketegangan; scene 7 tenaga penuh + chord akhir.
- **SFX:** boom impact, whoosh, tapak kaki, camera shutter, jam berdetik, sorakan & tepukan (sintetik), tap telefon.
- **Ducking:** muzik turun −10 dB (versi guideVO) / −4 dB (versi noVO) semasa VO, attack 0.12 s, release 0.35 s.
- **Mastering:** −14 LUFS integrated, true peak −1 dBTP (sesuai TikTok/IG/FB).

Alternatif berlesen jika mahu muzik lain: YouTube Audio Library, CapCut Commercial Music (tanda "Commercial use"), Pixabay Music — cari "sport energetic 130 bpm".

---

## 9. Arahan CapCut (VO sebenar)

1. Import `BRISKWALK_GenZ2026_Promo_9x16_noVO.mp4` ke projek 9:16.
2. *Audio → Record* (atau import WAV): rakam 7 baris VO, letak setiap klip pada masa dalam Seksyen 2.
3. Pilih klip video → *Audio → Volume* kekal 100%; pilih VO → *Enhance voice* ON, *Noise reduction* ON, Volume +2 dB.
4. Jika mahu ducking lebih dalam: *Split audio* video → pada slot VO turunkan 'keyframe' volume −6 dB lagi.
5. *Text → Captions → Import* `subtitles_BM.srt` (atau gunakan subtitle terbina dalam video — sudah ada; jangan duplikasi).
6. *Export*: 1080p, 30 fps, Bitrate "Higher", format MP4.

## 10. Arahan Premiere Pro

1. Sequence 1080×1920, 30 fps. Import master noVO (V1/A1) atau stems (`music.wav` A2, `sfx.wav` A3).
2. Rakam/import VO di A4; *Essential Sound → Dialogue*. Pada A2 *Music → Ducking* (Duck against Dialogue, −10 dB, sensitivity 6, fade 350 ms) → *Generate Keyframes*.
3. Subtitle: *File → Import* SRT → *Captions* track, gaya ikut Seksyen 4 (atau abaikan kerana sudah dibakar dalam video).
4. Export H.264, *Match Source – High bitrate*, Loudness Normalization ITU BS.1770-3 −14 LUFS, TP −1.

---

## 11. Senarai semak fakta (disahkan dengan poster)

- [x] Nama: BRISKWALK MASJID BERSAMA GEN Z 2026
- [x] Penganjur/Lokasi: Masjid As-Siddiq Seri Iskandar
- [x] Tarikh program: 21 November 2026 (Sabtu)
- [x] Tutup pendaftaran: 17 November 2026, Selasa, 12.00 tengah hari
- [x] Online: Google Form — `https://forms.gle/b9Hx6iZRGFn2xLuS6` (QR diuji)
- [x] Offline: Kaunter pendaftaran Masjid As-Siddiq Seri Iskandar
- [x] Tiada hadiah, yuran, slot, jarak, masa mula/berkumpul atau aktiviti tambahan direka
- [x] Tiada dakwaan "slot hampir habis"
- [x] Poster rasmi tidak dipaparkan; hanya maklumat penting dijadikan motion graphics. Logo tidak diubah.
- [x] Poster lama dalam rakaman Drive (RM15 / 5KM / Cabutan Bertuah / 17 & 18 Okt) dikaburkan — tidak terbaca
- [ ] **Semak:** ustaz menyebut "hujung minggu depan" — tepat jika video disiar 14–15 Nov 2026; selepas itu tarikh di skrin tetap jelas (21 Nov)

## 12. Bina semula

```bash
pip install numpy scipy pillow qrcode opencv-python-headless
apt-get install -y espeak-ng ffmpeg
# letak video Drive di footage/drive_video.mp4
cd src && python3 build_audio.py && python3 prep_clip.py && python3 render_video.py
# kemudian mux: lihat README.md
```
