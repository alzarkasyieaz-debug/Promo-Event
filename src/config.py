"""Timeline & fakta tunggal (single source of truth) untuk video promo
BRISKWALK MASJID BERSAMA GEN Z 2026.

Semua fakta di bawah disalin terus daripada poster rasmi (assets/poster_rasmi.jpg).
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")
OUT = os.path.join(ROOT, "output")
BUILD = os.environ.get("BUILD_DIR", os.path.join(ROOT, "build"))

W, H, FPS = 1080, 1920, 30
BPM = 132
BEAT = 60.0 / BPM          # 0.4545 s
BAR = 4 * BEAT             # 1.818 s

# ---- Fakta poster (JANGAN UBAH) ----
URL = "https://forms.gle/b9Hx6iZRGFn2xLuS6"
EVENT = "BRISKWALK MASJID BERSAMA GEN Z 2026"
VENUE = "MASJID AS-SIDDIQ SERI ISKANDAR"
EVENT_DATE = "21 NOVEMBER 2026"
EVENT_DAY = "SABTU"
CLOSE_DATE = "17 NOVEMBER 2026"
CLOSE_DAY_TIME = "SELASA • 12.00 TENGAH HARI"

# ---- Scene (mula, tamat) dalam saat, dijajarkan pada bar muzik (132 BPM) ----
def bars(n):
    return n * BAR

_S = [3, 5, 5, 7, 7, 6, 8]            # bilangan bar setiap scene (jumlah 41 bar = 74.5 s)
SCENES = []
_t = 0.0
for _n in _S:
    SCENES.append((_t, _t + bars(_n)))
    _t += bars(_n)
DURATION = _t                          # ~72.73 s

# ---- Skrip VO (ejaan untuk subtitle) & bentuk fonetik untuk TTS panduan ----
# offset = saat selepas scene bermula
VO = [
    dict(scene=0, offset=0.35,
         text="Warga Seri Iskandar! Dah bersedia untuk bergerak bersama?",
         tts="Warga Seri Iskandar! Dah bersedia untuk bergerak bersama?"),
    dict(scene=1, offset=0.45,
         text="Jom sertai Briskwalk Masjid Bersama Gen Z 2026 di Masjid As-Siddiq Seri Iskandar!",
         tts="Jom sertai, Brisk wok Masjid Bersama, Jen Zed, dua ribu dua puluh enam, di Masjid As Siddiq, Seri Iskandar!"),
    dict(scene=2, offset=0.10,
         text="Bukan sekadar berjalan! Inilah peluang untuk aktif, mengeratkan ukhuwah dan mencipta kenangan bersama keluarga serta rakan-rakan!",
         tts="Bukan sekadar berjalan! Inilah peluang untuk aktif, mengeratkan ukhuwah, dan mencipta kenangan bersama keluarga serta rakan rakan!"),
    dict(scene=3, offset=0.20, limit=1.55,
         text="Catat tarikh!",
         tts="Catat tarikh!"),
    dict(scene=3, offset=9.05,
         text="Bertempat di Masjid As-Siddiq Seri Iskandar.",
         tts="Bertempat di Masjid As Siddiq, Seri Iskandar."),
    dict(scene=4, offset=0.60,
         text="Pendaftaran masih dibuka! Tapi ingat, tarikh tutup ialah Selasa, 17 November 2026, tepat jam 12 tengah hari!",
         tts="Pendaftaran masih dibuka! Tapi ingat, tarikh tutup ialah Selasa, tujuh belas November, dua ribu dua puluh enam, tepat jam dua belas tengah hari!"),
    dict(scene=5, offset=0.45,
         text="Nak daftar? Mudah sahaja! Isi Google Form atau daftar terus di kaunter Masjid As-Siddiq Seri Iskandar.",
         tts="Nak daftar? Mudah sahaja! Isi Gugel Form, atau daftar terus di kaunter Masjid As Siddiq, Seri Iskandar."),
    dict(scene=6, offset=0.50,
         text="Jangan tunggu lagi! Ajak keluarga, bawa sahabat dan daftar sekarang! Kita jumpa di Briskwalk Masjid Bersama Gen Z 2026!",
         tts="Jangan tunggu lagi! Ajak keluarga, bawa sahabat, dan daftar sekarang! Kita jumpa di Brisk wok Masjid Bersama Jen Zed, dua ribu dua puluh enam!"),
]

# Pecahan subtitle (frasa pendek). Perkataan dalam *bintang* = highlight kuning.
SUB_CHUNKS = [
    ["*Warga Seri Iskandar!*", "Dah *bersedia*", "untuk bergerak bersama?"],
    ["*Jom sertai*", "*Briskwalk Masjid* Bersama", "*Gen Z 2026*", "di *Masjid As-Siddiq*", "Seri Iskandar!"],
    ["Bukan sekadar *berjalan!*", "Inilah peluang untuk *aktif,*", "mengeratkan *ukhuwah*", "dan mencipta *kenangan*", "bersama *keluarga*", "serta *rakan-rakan!*"],
    ["*Catat tarikh!*"],
    ["Bertempat di", "*Masjid As-Siddiq* Seri Iskandar."],
    ["*Pendaftaran masih dibuka!*", "Tapi ingat, *tarikh tutup* ialah", "*Selasa,* *17 November 2026,*", "tepat jam *12 tengah hari!*"],
    ["Nak *daftar?*", "*Mudah* sahaja!", "Isi *Google Form*", "atau daftar terus di *kaunter*", "*Masjid As-Siddiq* Seri Iskandar."],
    ["*Jangan tunggu lagi!*", "Ajak *keluarga,*", "bawa *sahabat*", "dan *daftar sekarang!*", "Kita jumpa di", "*Briskwalk Masjid Bersama Gen Z 2026!*"],
]

# ---- Rakaman sebenar (video Drive): petikan jemputan ustaz/AJK ----
# Sumber: footage/drive_video.mp4 (464x832, 30 fps). Hanya ayat ini digunakan kerana
# poster lama di latar belakang menyebut yuran/hadiah/jarak yang tiada dalam poster rasmi
# (kawasan itu dikaburkan & ditutup panel kalendar).
CLIP = dict(
    src="footage/drive_video.mp4",
    scene=3, offset=1.60,           # mula dalam scene 4
    src_start=232.95, src_end=240.25,
    text="Saya jemput orang ramai pada hujung minggu depan pada 21 bulan November.",
    # (mula, tamat) dalam masa sumber, daripada transkripsi Whisper (word timestamps)
    chunks=[(233.38, 235.72, "Saya jemput *orang ramai*"),
            (235.72, 238.56, "pada *hujung minggu depan*"),
            (238.56, 240.10, "pada *21 bulan November.*")],
)
