"""KONSEP 2 — "NEON VECTOR PULSE"
Tiada sebarang imej/keratan poster. Semua visual = vector animasi + rakaman sebenar YB Ustaz Ismi
(dipotong daripada latar belakang dan diletak atas latar vector).
Fakta tetap daripada poster rasmi (lihat config.py).
"""
import os

from config import (ROOT, ASSETS, W, H, FPS, BPM, BEAT, BAR, URL, EVENT, VENUE, EVENT_DATE, EVENT_DAY,
                    CLOSE_DATE, CLOSE_DAY_TIME)

OUT = os.path.join(ROOT, "output", "konsep2")
BUILD = os.environ.get("BUILD2_DIR", os.path.join(ROOT, "build2"))
HALF = BAR / 2

# (jenis, bilangan setengah-bar)
_PLAN = [("hook", 5), ("intro", 9), ("speechA", 14), ("feature", 10), ("speechB", 10),
         ("urgency", 12), ("howto", 9), ("cta", 13)]
KINDS = [k for k, _ in _PLAN]
SCENES = []
_t = 0.0
for _k, _n in _PLAN:
    SCENES.append((_t, _t + _n * HALF))
    _t += _n * HALF
DURATION = _t   # 74.55 s

VO = [
    dict(scene=0, offset=0.30,
         text="Warga Seri Iskandar! Dah bersedia untuk bergerak bersama?",
         tts="Warga Seri Iskandar! Dah bersedia untuk bergerak bersama?"),
    dict(scene=1, offset=0.30,
         text="Jom sertai Briskwalk Masjid Bersama Gen Z 2026 di Masjid As-Siddiq Seri Iskandar!",
         tts="Jom sertai, Brisk wok Masjid Bersama, Jen Zed, dua ribu dua puluh enam, di Masjid As Siddiq, Seri Iskandar!"),
    dict(scene=3, offset=0.10,
         text="Bukan sekadar berjalan! Inilah peluang untuk aktif, mengeratkan ukhuwah dan mencipta kenangan bersama keluarga serta rakan-rakan!",
         tts="Bukan sekadar berjalan! Inilah peluang untuk aktif, mengeratkan ukhuwah, dan mencipta kenangan bersama keluarga serta rakan rakan!"),
    dict(scene=5, offset=0.40,
         text="Pendaftaran masih dibuka! Tapi ingat, tarikh tutup ialah Selasa, 17 November 2026, tepat jam 12 tengah hari!",
         tts="Pendaftaran masih dibuka! Tapi ingat, tarikh tutup ialah Selasa, tujuh belas November, dua ribu dua puluh enam, tepat jam dua belas tengah hari!"),
    dict(scene=6, offset=0.30,
         text="Nak daftar? Mudah sahaja! Isi Google Form atau daftar terus di kaunter Masjid As-Siddiq Seri Iskandar.",
         tts="Nak daftar? Mudah sahaja! Isi Gugel Form, atau daftar terus di kaunter Masjid As Siddiq, Seri Iskandar."),
    dict(scene=7, offset=0.30,
         text="Jangan tunggu lagi! Ajak keluarga, bawa sahabat dan daftar sekarang! Kita jumpa di Briskwalk Masjid Bersama Gen Z 2026!",
         tts="Jangan tunggu lagi! Ajak keluarga, bawa sahabat, dan daftar sekarang! Kita jumpa di Brisk wok Masjid Bersama Jen Zed, dua ribu dua puluh enam!"),
]
SUB_CHUNKS = [
    ["*Warga Seri Iskandar!*", "Dah *bersedia*", "untuk bergerak bersama?"],
    ["*Jom sertai*", "*Briskwalk Masjid* Bersama", "*Gen Z 2026*", "di *Masjid As-Siddiq*", "Seri Iskandar!"],
    ["Bukan sekadar *berjalan!*", "Inilah peluang untuk *aktif,*", "mengeratkan *ukhuwah*", "dan mencipta *kenangan*", "bersama *keluarga*", "serta *rakan-rakan!*"],
    ["*Pendaftaran masih dibuka!*", "Tapi ingat, *tarikh tutup* ialah", "*Selasa,* *17 November 2026,*", "tepat jam *12 tengah hari!*"],
    ["Nak *daftar?*", "*Mudah* sahaja!", "Isi *Google Form*", "atau daftar terus di *kaunter*", "*Masjid As-Siddiq* Seri Iskandar."],
    ["*Jangan tunggu lagi!*", "Ajak *keluarga,*", "bawa *sahabat*", "dan *daftar sekarang!*", "Kita jumpa di", "*Briskwalk Masjid Bersama Gen Z 2026!*"],
]

# Ucapan YB Ustaz Ismi — SEMUA audio ucapan yang wujud dalam fail Drive
# (0:12–3:52 dalam fail asal tiada audio). Transkripsi: Whisper large-v3.
SPEAKER = "YB Ustaz Ismi"
SPEAKER_ROLE = "Ahli Parlimen Parit"
SRC = os.path.join(ROOT, "footage", "drive_video.mp4")
CLIPS = [
    dict(scene=2, offset=0.20, seg=(0.00, 12.35),
         chunks=[(0.00, 1.40, "*Assalamualaikum*"),
                 (1.40, 2.30, "warahmatullahi wabarakatuh."),
                 (2.38, 4.15, "*Alhamdulillah,* hari ini saya join"),
                 (4.18, 6.28, "*Fun Run* yang dianjurkan oleh"),
                 (6.30, 7.88, "*Masjid Bandar Universiti,*"),
                 (7.92, 9.45, "*Fun Run 5 km*"),
                 (9.50, 12.30, "oleh masjid-masjid…")]),
    dict(scene=4, offset=0.20, seg=(232.60, 241.05),
         chunks=[(232.75, 234.60, "*Sesama kita,*"),
                 (234.65, 236.65, "saya jemput *orang ramai*"),
                 (236.65, 238.50, "pada *hujung minggu depan*"),
                 (238.50, 240.30, "pada *21 bulan November.*"),
                 (240.35, 241.00, "*Terima kasih.*")]),
]
