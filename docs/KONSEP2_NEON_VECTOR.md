# Konsep 2 — "NEON VECTOR PULSE"
**BRISKWALK MASJID BERSAMA GEN Z 2026** · 9:16 · 1080×1920 · 30 fps · 74.5 s · −14 LUFS

**Tiada sebarang imej atau keratan poster.** Semua visual ialah vector animasi yang dijana dengan kod, ditambah rakaman sebenar YB Ustaz Ismi. Latar belakang asal rakaman dibuang sepenuhnya (segmentasi orang) dan beliau diletakkan di atas latar vector dengan cahaya rim. Fakta program diambil daripada poster rasmi.

## Fail (`output/konsep2/`)
| Fail | Kegunaan |
|---|---|
| `BRISKWALK_GenZ2026_Konsep2_NeonVector_9x16_noVO.mp4` | Master: muzik + SFX + **ucapan sebenar YB Ustaz Ismi**, ruang untuk VO sebenar |
| `BRISKWALK_GenZ2026_Konsep2_NeonVector_9x16_guideVO.mp4` | Dengan VO panduan TTS (untuk semak timing sahaja) |
| `subtitles_BM_konsep2.srt` | Subtitle bertimestamp (VO + ucapan) |
| `stems/` | music, sfx, vo_guide, ucapan_YB_Ustaz_Ismi |
| `qr_pendaftaran.png` | QR → https://forms.gle/b9Hx6iZRGFn2xLuS6 (diuji pada frame video) |

## Elemen vector
- **Pejalan piktogram brisk-walk** (kitaran langkah beranimasi): belia, wanita bertudung, warga emas berkopiah dan kanak-kanak, bercahaya neon.
- **Corak bintang 8 penjuru (geometri Islamik)** berputar di latar, bersama light leak emas/teal.
- **Siluet masjid generik** dilukis dengan garisan neon emas (bukan logo masjid).
- **Teks 3D huruf demi huruf** (jatuh/pop), glitch-in, light sweep dan gelombang kejutan.
- **Cincin progres countdown** 1 → 17 dengan jam dan ikon amaran (tarikh tutup).
- **Transisi jalur pepenjuru** emas/emerald/putih pada setiap potongan scene, flash dan camera shake.
- Telefon dengan borang digital, kaunter pendaftaran, QR dan URL.

## Timeline
| Scene | Masa | Visual | Audio |
|---|---|---|---|
| 1 Hook | 0:00.0–0:04.5 | Tapak kasut neon ikut beat, pejalan gergasi melintas, streak laju. "SERI ISKANDAR, ARE YOU READY?" → gelombang kejutan + "JOM BRISKWALK!" (huruf pop) | VO1 |
| 2 Intro | 0:04.5–0:12.7 | Pill "MASJID AS-SIDDIQ • SERI ISKANDAR"; siluet masjid dilukis neon; perarakan pejalan pelbagai generasi di garis langit; "BRISKWALK" huruf jatuh, "MASJID BERSAMA", "GEN Z 2026" glitch-in | VO2 |
| 3 Ucapan (1) | 0:12.7–0:25.5 | Cutout YB Ustaz Ismi atas latar vector + cincin neon berputar; panel tarikh 21 NOV SABTU 2026 · Masjid As-Siddiq Seri Iskandar; "JEMPUTAN KHAS"; lower-third nama/jawatan | **Ucapan sebenar 0:12.9–0:25.3** |
| 4 Tarikan | 0:25.5–0:34.5 | 4 babak pejalan di atas treadmill garisan emas: AKTIFKAN DIRI! ⚡ / AJAK SAHABAT! / ERATKAN UKHUWAH! ❤ / SATUKAN GENERASI! (kanak-kanak, belia, bertudung, warga emas) | VO3 |
| 5 Ucapan (2) | 0:34.5–0:43.6 | Sama seperti scene 3 (cincin teal); panel tarikh disinari semasa "21 bulan November" | **Ucapan sebenar 0:34.8–0:43.2** |
| 6 Urgency | 0:43.6–0:54.5 | Latar merah; slam "PENDAFTARAN MASIH DIBUKA!"; cincin countdown 1→17 + gelombang kejutan; "17 NOVEMBER 2026"; "SELASA • 12.00 TENGAH HARI"; jam & ikon amaran | VO4, detik jam |
| 7 Cara daftar | 0:54.5–1:02.7 | Telefon (ONLINE — GOOGLE FORM) · ATAU · kaunter (OFFLINE — KAUNTER MASJID); **URL kekal 0:55.3–1:02.7** | VO5 |
| 8 CTA | 1:02.7–1:14.5 | Pejalan menuju kamera (perspektif) "JANGAN TUNGGU LAGI!" → cincin + kalendar 17 "DAFTAR SEBELUM 17 NOVEMBER!" → lockup tajuk + siluet masjid → **kad info**: tarikh program, lokasi, tarikh tutup, cara daftar, QR, URL, "DAFTAR SEKARANG!" | VO6, boom akhir 1:12.1 |

## Ucapan YB Ustaz Ismi (semua audio ucapan yang wujud dalam fail Drive)
Transkripsi Whisper large-v3:

1. **0:12.9** — "Assalamualaikum warahmatullahi wabarakatuh. Alhamdulillah, hari ini saya join Fun Run yang dianjurkan oleh Masjid Bandar Universiti, Fun Run 5 km oleh masjid-masjid…" *(audio dalam fail asal terputus di sini)*
2. **0:34.8** — "Sesama kita, saya jemput orang ramai pada hujung minggu depan pada 21 bulan November. Terima kasih."

Dalam fail asal, minit 0:12–3:52 tiada audio pertuturan (hanya dengung kira-kira −50 dB).

### ⚠️ Perlu disemak sebelum disiar
- Ucapan pertama menyebut **"Fun Run"**, **"5 km"** dan **"Masjid Bandar Universiti"**. Butiran ini **tidak** dinyatakan dalam poster rasmi, yang menyebut Briskwalk di Masjid As-Siddiq Seri Iskandar tanpa jarak. Ia dimasukkan kerana anda meminta semua ucapan. Pastikan ia tidak mengelirukan penonton, atau minta saya potong bahagian itu.
- Perkataan "Universiti" dan "5 km" didengar dengan yakin oleh model, tetapi sila dengar semula untuk sahkan ejaan nama masjid.
- "Hujung minggu depan" hanya tepat jika video disiar sekitar 14–15 Nov 2026.

## Bina semula
```bash
# perlu footage/drive_video.mp4 ; pip install rembg[cpu] faster-whisper
cd src && python3 build_audio2.py && python3 prep_clip2.py && python3 render_concept2.py && cd ..
for v in guideVO noVO; do
  ffmpeg -y -i build2/video_silent.mp4 -i build2/mix_$v.wav -map 0:v -map 1:a -c:v copy \
    -af "loudnorm=I=-14:TP=-1.0:LRA=11" -ar 48000 -c:a aac -b:a 256k -shortest -movflags +faststart \
    output/konsep2/BRISKWALK_GenZ2026_Konsep2_NeonVector_9x16_$v.mp4
done
```
