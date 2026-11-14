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
    ["*Pendaftaran masih dibuka!*", "Tapi ingat, *tarikh tutup* ialah", "*Selasa,* *17 November 2026,*", "tepat jam *12 tengah hari!*"],
    ["Nak *daftar?*", "*Mudah* sahaja!", "Isi *Google Form*", "atau daftar terus di *kaunter*", "*Masjid As-Siddiq* Seri Iskandar."],
    ["*Jangan tunggu lagi!*", "Ajak *keluarga,*", "bawa *sahabat*", "dan *daftar sekarang!*", "Kita jumpa di", "*Briskwalk Masjid Bersama Gen Z 2026!*"],
]

# ---- Rakaman sebenar (video Drive): ucapan YB Ustaz Ismi ----
# Sumber: footage/drive_video.mp4 (464x832, 30 fps, 4:04).
# Audio yang wujud dalam fail: 0:00-0:12 dan 3:52-4:01 sahaja (0:12-3:52 tiada suara, hanya dengung -50 dB).
# Digunakan: salam (0:00-0:02.9) + jemputan penuh (3:52.6-4:01.05).
# Tidak digunakan: 0:03-0:12 (sebut "5 km"/larian, tidak jelas & tiada dalam poster rasmi).
# Latar belakang (poster lama: yuran RM15/cabutan bertuah/5KM) dikaburkan sepenuhnya melalui segmentasi orang.
CLIP = dict(
    src="footage/drive_video.mp4",
    scene=3, offset=0.12,           # mula dalam scene 4
    speaker="YB Ustaz Ismi",
    speaker_role="Ahli Parlimen Parit",
    segments=[(0.00, 2.92), (232.60, 241.05)],
    text="Assalamualaikum warahmatullahi wabarakatuh. Sesama kita, saya jemput orang ramai pada hujung minggu depan pada 21 bulan November. Terima kasih.",
    # (mula, tamat) dalam masa SUMBER (Whisper word timestamps)
    chunks=[(0.00, 1.45, "*Assalamualaikum*"),
            (1.45, 2.86, "warahmatullahi wabarakatuh."),
            (232.75, 234.60, "*Sesama kita,*"),
            (234.65, 236.65, "saya jemput *orang ramai*"),
            (236.65, 238.50, "pada *hujung minggu depan*"),
            (238.50, 240.30, "pada *21 bulan November.*"),
            (240.35, 241.00, "*Terima kasih.*")],
)


def clip_src_to_local(src_t):
    """Masa sumber -> masa relatif kepada mula klip dalam video (segmen disambung jump-cut)."""
    acc = 0.0
    for a, b in CLIP["segments"]:
        if a <= src_t <= b + 1e-6:
            return acc + (src_t - a)
        acc += b - a
    raise ValueError(src_t)


CLIP_LEN = sum(b - a for a, b in CLIP["segments"])
