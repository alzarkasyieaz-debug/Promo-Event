"""KONSEP 2 — "NEON VECTOR PULSE": render 1080x1920 @30fps.
Tiada imej poster. Visual = vector animasi + cutout rakaman sebenar YB Ustaz Ismi.
Penggunaan: python3 render_concept2.py [--preview t1,t2,...]
"""
import json, math, os, subprocess, sys
from functools import lru_cache
from multiprocessing import Pool

import numpy as np
import qrcode
from PIL import Image, ImageDraw, ImageFilter

from config2 import (W, H, FPS, BEAT, BAR, SCENES, KINDS, DURATION, URL, BUILD, OUT, CLIPS, SPEAKER, SPEAKER_ROLE)
from gfx import (text3d, flat_text, pill, place, sweep, with_alpha, anim, font, clamp, ease_out_cubic, ease_in_cubic,
                 ease_in_out, ease_out_back, icon_calendar, icon_pin, icon_clock, icon_people, icon_phone, icon_counter,
                 icon_heart, icon_bolt, icon_alert, icon_shoeprint, Particles,
                 F_BLACK_IT, F_BLACK, F_BOLD, F_MONO, EMERALD, EMERALD_D, GOLD, GOLD_L, YELLOW, WHITE, RED)
from gfx2 import (vbg, walkers_layer, GEN_KINDS, GEN_COLS, skyline_path, neon_path, route_layer, shockwave, streaks,
                  stripe_wipe, glitch, rim_light, ring_progress, spark, TEAL)

TIMING = json.load(open(os.path.join(BUILD, "timing.json"), encoding="utf-8"))
CX = 520
PART = Particles(80, 11)
os.makedirs(OUT, exist_ok=True)


def _qr():
    q = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=12, border=2)
    q.add_data(URL)
    q.make(fit=True)
    return q.make_image(fill_color=(4, 40, 28), back_color="white").convert("RGB")


QR = _qr()


def _vig():
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.hypot((xx - W / 2) / (W / 2), (yy - H / 2) / (H / 2))
    out = np.zeros((H, W, 4), np.uint8)
    out[..., 3] = (np.clip((r - 0.7) / 0.6, 0, 1) ** 1.5 * 190).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


VIGNETTE = _vig()


# ------------------------------------------------------------------ pembantu teks
@lru_cache(maxsize=None)
def label_pill(text, size, kind, w=None, h=None, color=WHITE, fpath=F_BLACK_IT):
    txt = flat_text(text, size, color, fpath, shadow=kind not in ("white", "gold"))
    w = w or txt.width + 70
    h = h or int(size * 1.75)
    p = pill(w, h, kind, h // 2, 6).copy()
    p.alpha_composite(txt, ((p.width - txt.width) // 2, (p.height - txt.height) // 2 - 6))
    return p


@lru_cache(maxsize=None)
def url_pill():
    txt = flat_text(URL, 40, EMERALD_D, F_MONO, shadow=False)
    p = pill(txt.width + 30, 104, "white", 52, 6).copy()
    p.alpha_composite(txt, ((p.width - txt.width) // 2, (p.height - txt.height) // 2 - 6))
    return p


def letters(c, word, size, face, cx, cy, t, t0, stagger=0.06, style="drop"):
    f = font(F_BLACK_IT, size)
    total = f.getlength(word)
    x = cx - total / 2
    for i, ch in enumerate(word):
        wch = f.getlength(ch)
        if ch != " ":
            sp = text3d(ch, size, face)
            p = (t - t0 - i * stagger) / 0.32
            if p > 0:
                if style == "drop":
                    dy = -420 * (1 - ease_out_back(p, 1.6))
                    sc = 1
                else:
                    dy = 0
                    sc = 0.2 + 0.8 * ease_out_back(p, 2.5)
                place(c, sp, x + wch / 2, cy + dy, sc, clamp(p * 3))
        x += wch


@lru_cache(maxsize=None)
def lower_third():
    name = flat_text(SPEAKER, 58, EMERALD_D, F_BLACK_IT, shadow=False)
    role = flat_text(SPEAKER_ROLE, 40, WHITE, F_BLACK)
    top = pill(name.width + 60, 96, "gold", 18, 5).copy()
    top.alpha_composite(name, (32, (top.height - name.height) // 2 - 6))
    bot = pill(role.width + 60, 70, "emerald", 14, 4).copy()
    bot.alpha_composite(role, (32, (bot.height - role.height) // 2 - 6))
    out = Image.new("RGBA", (max(top.width, bot.width + 30), top.height + bot.height - 40), (0, 0, 0, 0))
    out.alpha_composite(bot, (30, top.height - 40))
    out.alpha_composite(top, (0, 0))
    return out


@lru_cache(maxsize=None)
def date_panel():
    p = pill(330, 560, "dark", 34, 6).copy()
    p.alpha_composite(icon_calendar(250, "NOVEMBER", "21", "SABTU"), (60, 70))
    y26 = flat_text("2026", 64, GOLD_L, F_BLACK_IT)
    p.alpha_composite(y26, ((p.width - y26.width) // 2, 340))
    for k, s in enumerate(("MASJID AS-SIDDIQ", "SERI ISKANDAR")):
        tx = flat_text(s, 30, WHITE, F_BLACK)
        p.alpha_composite(tx, ((p.width - tx.width) // 2, 430 + 45 * k))
    return p


@lru_cache(maxsize=None)
def info_rows():
    spec = [("cal", "TARIKH PROGRAM", "SABTU • 21 NOVEMBER 2026", "emerald", GOLD_L),
            ("pin", "LOKASI", "MASJID AS-SIDDIQ SERI ISKANDAR", "emerald", GOLD_L),
            ("clock", "TARIKH TUTUP PENDAFTARAN", "SELASA • 17 NOV 2026 • 12.00 TENGAH HARI", "red", WHITE),
            ("ppl", "CARA DAFTAR", "ONLINE: GOOGLE FORM  |  OFFLINE: KAUNTER MASJID", "emerald", WHITE)]
    rows = []
    for ic, lab, val, kind, col in spec:
        p = pill(920, 104, kind, 24, 5).copy()
        icn = {"cal": lambda: icon_calendar(70, "NOV", "21"), "pin": lambda: icon_pin(70),
               "clock": lambda: icon_clock(70, 0.0, 0.0), "ppl": lambda: icon_people(70, 2)}[ic]()
        p.alpha_composite(icn, (38, 20 + (104 - icn.height) // 2))
        p.alpha_composite(flat_text(lab, 25, GOLD_L if kind == "red" else (200, 236, 214), F_BOLD, shadow=False), (92, 6))
        f = 40
        vt = flat_text(val, f, col, F_BLACK)
        while vt.width - 48 > 800 and f > 22:
            f -= 2
            vt = flat_text(val, f, col, F_BLACK)
        p.alpha_composite(vt, (92, 38))
        rows.append(p)
    return rows


# ------------------------------------------------------------------ cutout ucapan
_CUT = {}


def cut_frame(k, i):
    d = os.path.join(BUILD, f"cut{k}")
    n = len(os.listdir(d))
    i = max(0, min(i, n - 1))
    key = (k, i)
    if key not in _CUT:
        if len(_CUT) > 6:
            _CUT.clear()
        _CUT[key] = rim_light(Image.open(os.path.join(d, f"{i:05d}.png")).convert("RGBA"), (255, 210, 90) if k == 0 else (120, 255, 200))
    return _CUT[key]


def ring_deco(c, t, cx, cy, r, col):
    lay = Image.new("RGBA", (W // 2, H // 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for j, (rr, wd, sp, dash) in enumerate([(r, 6, 20, 12), (r * 0.82, 3, -32, 24), (r * 1.12, 2, 12, 40)]):
        rr /= 2
        for k in range(dash):
            a0 = k * 360 / dash + t * sp
            d.arc([cx / 2 - rr, cy / 2 - rr, cx / 2 + rr, cy / 2 + rr], a0, a0 + 360 / dash * 0.55, fill=col + (170,), width=wd)
    g = lay.filter(ImageFilter.GaussianBlur(3))
    c.alpha_composite(g.resize((W, H), Image.BILINEAR))
    c.alpha_composite(lay.resize((W, H), Image.BILINEAR))


def speech_scene(t, k, ring_col):
    L = SCENES[CLIPS[k]["scene"]][1] - SCENES[CLIPS[k]["scene"]][0]
    c = vbg(t + 7 * k, "emerald", lattice=0.35, leaks=1.0, lat_speed=2.0)
    ring_deco(c, t, 540, 760, 820, ring_col)
    t0 = CLIPS[k]["offset"]
    seg = CLIPS[k]["seg"][1] - CLIPS[k]["seg"][0]
    if t >= t0 - 0.05:
        tt = max(0, t - t0)
        cut = cut_frame(k, int(tt * FPS))
        p = ease_out_cubic(tt / 0.45)
        z = 1.0 + 0.015 * tt
        sp = cut if abs(z - 1) < 1e-3 else cut.resize((int(W * z), int(H * z)), Image.BILINEAR)
        place(c, sp, W / 2, H / 2 + (1 - p) * 300 + (sp.height - H) * 0.2, 1, clamp(tt / 0.2))
    s, a, dx, dy = anim(t, 0.3, None, "right", 0.35)
    pnl = date_panel()
    if k == 1:
        ts = t - (t0 + 238.6 - CLIPS[k]["seg"][0])
        if 0 < ts < 1.0:
            pnl = sweep(pnl, ts, 0.1, 140)
    place(c, pnl, 885 + dx, 560 + dy, s, a)
    s, a, dx, dy = anim(t, 0.35, None, "left", 0.3)
    place(c, label_pill("JEMPUTAN KHAS", 34, "emerald", h=70, color=GOLD_L), 250 + dx, 175, s, a)
    s, a, dx, dy = anim(t, 0.6, t0 + seg - 0.35, "left", 0.4, 0.25)
    lt = lower_third()
    place(c, lt, 60 + lt.width / 2 + dx, 1140, 1, a)
    return c


# ------------------------------------------------------------------ SCENES
def s_hook(t):
    c = vbg(t, "emerald", lattice=0.25, leaks=0.6, lat_speed=30, lat_zoom=1.2)
    streaks(c, t, 0.9 if t < 2 * BAR else 0.5, vertical=True)
    # tapak kasut neon ikut beat
    for k in range(8):
        ts = k * BEAT
        if t >= ts and t < 2 * BAR + 0.3:
            al = clamp(1.6 - (t - ts) * 0.9)
            place(c, icon_shoeprint(170, GOLD if k % 2 else (120, 255, 190)), CX + (-120 if k % 2 == 0 else 120),
                  1650 - k * 170 + (t - ts) * 60, 1.25 * (0.6 + 0.4 * ease_out_back((t - ts) / 0.18)), al, rot=-10 if k % 2 == 0 else 10)
    # pejalan gergasi melintas
    if t < 2 * BAR:
        x = -300 + 1700 * (t / (2 * BAR))
        c.alpha_composite(walkers_layer([(x, 980, 820, t / (2 * BEAT), "youth", (255, 214, 90, 255), 1)]))
    s, a, dx, dy = anim(t, 0.05, 2 * BAR - 0.18, "slam", 0.22)
    place(c, text3d("SERI ISKANDAR,", 104, "white", maxw=900), CX + dx, 1040 + dy, s, a)
    s, a, dx, dy = anim(t, 2 * BEAT, 2 * BAR - 0.18, "slam", 0.22)
    place(c, text3d("ARE YOU READY?", 112, "gold", maxw=900), CX + dx, 1185 + dy, s, a)
    if t >= 2 * BAR:
        tt = t - 2 * BAR
        shockwave(c, t, 2 * BAR, CX, 760, maxr=1500)
        PART.draw(c, t, 1.0, burst=ease_out_cubic(tt / 0.6) * 0.6)
        letters(c, "JOM", 170, "white", CX, 620, tt, 0.0, 0.05, "pop")
        letters(c, "BRISKWALK!", 150, "gold", CX, 840, tt, 0.12, 0.04, "pop")
    return c


def s_intro(t):
    L = SCENES[1][1] - SCENES[1][0]
    c = vbg(t + 5, "emerald", lattice=0.45)
    s, a, dx, dy = anim(t, 0.1, None, "up", 0.3)
    place(c, label_pill("MASJID AS-SIDDIQ • SERI ISKANDAR", 40, "dark", h=84, color=GOLD_L), CX + dx, 200 + dy, s, a)
    c.alpha_composite(neon_path(skyline_path(), ease_in_out(t / 1.6), dy=-470))
    if t > 1.2:
        ph = t / (2 * BEAT)
        specs = []
        for k in range(7):
            x = ((t - 1.2) * 110 + k * 165) % 1300 - 130
            specs.append((x, 770, 120, ph + k * 0.13, GEN_KINDS[k % 6], GEN_COLS[k % 4], 1))
        c.alpha_composite(walkers_layer(specs))
    letters(c, "BRISKWALK", 150, "green", CX, 920, t, 0.6, 0.07, "drop")
    s, a, dx, dy = anim(t, 0.6 + 9 * 0.07 + 0.15, None, "left", 0.3)
    place(c, text3d("MASJID BERSAMA", 84, "white", maxw=900), CX + dx, 1060 + dy, s, a)
    if t >= 2.0:
        sp = text3d("GEN Z 2026", 124, "gold")
        sp = sweep(sp, (t - 2.6) / 0.9) if 2.6 < t < 3.5 else sp
        s, a, dx, dy = anim(t, 2.0, None, "pop", 0.3)
        lay = Image.new("RGBA", (W, 300), (0, 0, 0, 0))
        place(lay, sp, CX + dx, 150, s, a)
        lay = glitch(lay, clamp(1 - (t - 2.0) / 0.35) * 2, int(t * 30)) if t < 2.35 else lay
        c.alpha_composite(lay, (0, 1195 - 150))
    return c


def s_speechA(t):
    return speech_scene(t, 0, (255, 210, 90))


def s_speechB(t):
    return speech_scene(t, 1, (120, 255, 200))


SLOG = [("AKTIFKAN DIRI!", "gold"), ("AJAK SAHABAT!", "white"), ("ERATKAN UKHUWAH!", "gold"), ("SATUKAN GENERASI!", "white")]


def s_feature(t):
    L = SCENES[3][1] - SCENES[3][0]
    st = L / 4
    k = min(3, int(t / st))
    tt = t - k * st
    c = vbg(t + 20, "emerald", lattice=0.4, lat_speed=6)
    streaks(c, t, 0.7)
    # garisan tanah bergerak (treadmill)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for j in range(14):
        x = (j * 110 - t * 520) % (W + 110) - 110
        d.line([x, 1012, x + 60, 1012], fill=(255, 214, 90, 200), width=6)
    c.alpha_composite(lay)
    ph = t / (2 * BEAT)
    if k == 0:
        specs = [(CX, 1000, 720, ph, "youth", (255, 214, 90, 255), 1)]
        place(c, icon_bolt(190), CX + 300, 420, ease_out_back(tt / 0.3), clamp(tt / 0.15))
    elif k == 1:
        specs = [(CX - 170, 1000, 600, ph, "youth", (255, 255, 255, 255), 1), (CX + 170, 1000, 600, ph + 0.5, "hijab", (120, 255, 190, 255), 1)]
    elif k == 2:
        specs = [(CX - 330 + j * 220, 1000, 440, ph + j * 0.25, GEN_KINDS[j], GEN_COLS[j % 4], 1) for j in range(4)]
        hb = ease_out_back(tt / 0.4)
        place(c, icon_heart(200), CX, 380, hb, clamp(tt / 0.2))
        shockwave(c, t, k * st + 0.1, CX, 380, (255, 120, 120), 700)
    else:
        kinds = ["kid", "youth", "hijab", "elder"]
        specs = [(CX - 330 + j * 220, 1000, 470, ph + j * 0.2, kinds[j], GEN_COLS[j % 4], 1) for j in range(4)]
        shockwave(c, t, k * st + 0.1, CX, 700, (255, 220, 120), 1400)
    c.alpha_composite(walkers_layer(specs))
    txt, face = SLOG[k]
    s, a, dx, dy = anim(tt, 0.05, st - 0.25, "slam" if k % 2 == 0 else "pop", 0.25, 0.18)
    sp = text3d(txt, 104, face, maxw=900)
    sp = sweep(sp, (tt - 0.35) / 0.8) if 0.35 < tt < 1.15 else sp
    place(c, sp, CX + dx, 1185 + dy, s, a)
    return c


def s_urgency(t):
    c = vbg(t + 40, "red", lattice=0.3, leaks=0.4, lat_speed=-4)
    pulse = 0.5 + 0.5 * math.sin(t * 2 * math.pi / (2 * BEAT))
    a1 = 1.8
    if t < a1:
        s, a, dx, dy = anim(t, 0.05, a1 - 0.2, "slam", 0.22)
        place(c, label_pill("PENDAFTARAN", 100, "emerald", w=900, h=170), CX + dx, 760 + dy, s, a)
        s, a, dx, dy = anim(t, 0.05 + 2 * BEAT, a1 - 0.2, "slam", 0.22)
        place(c, text3d("MASIH DIBUKA!", 136, "yellow", maxw=900), CX + dx, 960 + dy, s, a)
        return c
    tt = t - a1
    land = 2 * BAR + BAR / 2 - a1
    place(c, label_pill("PENDAFTARAN MASIH DIBUKA!", 52, "emerald", w=860, h=100, color=YELLOW), CX, 190, 1, clamp(tt / 0.2))
    s, a, dx, dy = anim(tt, 0.0, None, "slam", 0.22)
    place(c, label_pill("TARIKH TUTUP PENDAFTARAN", 54, "red", w=860, h=110), CX + dx, 330 + dy, s, a)
    p = clamp(tt / land)
    n = 1 + int(16 * ease_in_out(p)) if tt < land else 17
    shake = int(18 * math.exp(-(tt - land) * 10) * math.sin((tt - land) * 90)) if tt >= land else 0
    ring = ring_progress(560, int(100 * ease_in_out(p)), (255, 214, 10))
    place(c, ring, CX + shake, 680, 1 + (0.04 * pulse if tt >= land else 0), clamp(tt / 0.2))
    num = text3d(str(n), 230, "yellow")
    place(c, num, CX + shake, 650, 1.0 if tt < land else 1 + 0.25 * math.exp(-(tt - land) * 8), 1)
    place(c, flat_text("NOVEMBER", 46, WHITE, F_BLACK), CX + shake, 790, 1, 1)
    if tt >= land:
        k = tt - land
        shockwave(c, t, a1 + land, CX, 680, (255, 214, 10), 1500)
        s, a, dx, dy = anim(k, 0.0, None, "slam", 0.22)
        sp = text3d("17 NOVEMBER 2026", 112, "yellow", maxw=900)
        sp = sweep(sp, (k - 0.5) / 0.9) if 0.5 < k < 1.4 else sp
        place(c, sp, CX + dx + shake, 1035 + dy, s, a)
        s, a, dx, dy = anim(k, 2 * BEAT, None, "pop", 0.3)
        place(c, label_pill("SELASA • 12.00 TENGAH HARI", 60, "white", w=900, h=120, color=RED, fpath=F_BLACK), CX + dx, 1195 + dy, s, a)
        ang = ease_out_cubic(clamp(k / 0.6)) * 2 * math.pi * 2
        place(c, icon_clock(150, ang, ang / 12), CX - 360, 680, ease_out_back(k / 0.3), clamp(k / 0.15))
        place(c, icon_alert(130), CX + 360, 680, ease_out_back((k - 0.15) / 0.3), clamp((k - 0.15) / 0.15), rot=8 * math.sin(t * 14))
    return c


def s_howto(t):
    L = SCENES[6][1] - SCENES[6][0]
    c = vbg(t + 50, "emerald", lattice=0.4)
    s, a, dx, dy = anim(t, 0.05, None, "slam", 0.22)
    place(c, text3d("CARA DAFTAR", 96, "gold"), CX + dx, 190 + dy, s, a)
    s, a, dx, dy = anim(t, 0.15, None, "left", 0.35)
    place(c, icon_phone(330, 640, clamp((t - 0.6) / 2.6)), 275 + dx, 640 + dy, s, a)
    place(c, label_pill("ONLINE", 56, "emerald", w=330, h=96), 275 + dx, 1010 + dy, s, a)
    place(c, flat_text("GOOGLE FORM", 40, GOLD_L, F_BLACK), 275 + dx, 1085 + dy, s, a)
    s, a, dx, dy = anim(t, 2.4, None, "right", 0.35)
    place(c, icon_counter(380), 775 + dx, 600 + dy, s, a)
    place(c, label_pill("OFFLINE", 56, "emerald", w=330, h=96), 775 + dx, 1010 + dy, s, a)
    place(c, flat_text("KAUNTER MASJID", 40, GOLD_L, F_BLACK), 775 + dx, 1085 + dy, s, a)
    # garis "ATAU"
    s, a, dx, dy = anim(t, 2.6, None, "pop", 0.3)
    place(c, label_pill("ATAU", 34, "gold", w=130, h=64, color=EMERALD_D), 525, 640, s, a)
    if t >= 0.8:
        s, a, dx, dy = anim(t, 0.8, None, "up", 0.3)
        up = url_pill()
        up = sweep(up, (t - 1.2) / 1.0, 0.1, 90) if 1.2 < t < 2.2 else up
        place(c, up, CX + dx, 1215 + dy, s, a)
    return c


def s_cta(t):
    L = SCENES[7][1] - SCENES[7][0]
    T1, T2, T3 = 3.0, 5.2, 7.3
    hit = L - 2.4
    if t < T1:
        c = vbg(t + 60, "emerald", lattice=0.35, lat_speed=12, lat_zoom=1 + 0.3 * t / T1)
        streaks(c, t, 1.0, vertical=True)
        specs = []
        for j in range(9):
            row = j // 3
            depth = ((t * 0.45 + row * 0.33) % 1.0)
            h = 120 + 760 * depth ** 2
            x = CX + (j % 3 - 1) * (180 + 420 * depth ** 2)
            y = 700 + 520 * depth ** 2
            specs.append((x, y, h, t / (2 * BEAT) + j * 0.17, GEN_KINDS[j % 6], GEN_COLS[j % 4], 1))
        specs.sort(key=lambda s: s[2])
        c.alpha_composite(walkers_layer(specs))
        s, a, dx, dy = anim(t, 0.1, T1 - 0.2, "slam", 0.22)
        place(c, text3d("JANGAN TUNGGU", 116, "white", maxw=900), CX + dx, 1110 + dy, s, a)
        s, a, dx, dy = anim(t, 0.1 + 2 * BEAT, T1 - 0.2, "slam", 0.22)
        place(c, text3d("LAGI!", 160, "gold"), CX + dx, 1255 + dy, s, a)
        return c
    if t < T2:
        tt = t - T1
        c = vbg(t + 60, "red", lattice=0.3)
        shockwave(c, t, T1 + 0.1, CX, 760, (255, 214, 10), 1500)
        place(c, ring_progress(620, 100, (255, 214, 10)), CX, 740, 1 + 0.03 * math.sin(t * 8), 1)
        place(c, icon_calendar(330, "NOVEMBER", "17", "SELASA"), CX, 740, ease_out_back(tt / 0.3), clamp(tt / 0.15))
        s, a, dx, dy = anim(tt, 0.1, T2 - T1 - 0.2, "slam", 0.22)
        place(c, label_pill("DAFTAR SEBELUM", 70, "red", w=760, h=130), CX + dx, 1100 + dy, s, a)
        s, a, dx, dy = anim(tt, 0.1 + 2 * BEAT, T2 - T1 - 0.2, "slam", 0.22)
        place(c, text3d("17 NOVEMBER!", 130, "yellow", maxw=900), CX + dx, 1250 + dy, s, a)
        return c
    if t < T3:
        tt = t - T2
        c = vbg(t + 60, "emerald", lattice=0.45)
        c.alpha_composite(neon_path(skyline_path(), ease_in_out(tt / 0.9), dy=-640))
        letters(c, "BRISKWALK", 150, "green", CX, 780, tt, 0.1, 0.05, "pop")
        s, a, dx, dy = anim(tt, 0.6, None, "left", 0.3)
        place(c, text3d("MASJID BERSAMA", 88, "white", maxw=900), CX + dx, 915 + dy, s, a)
        s, a, dx, dy = anim(tt, 0.8, None, "pop", 0.3)
        place(c, text3d("GEN Z 2026", 124, "gold"), CX + dx, 1045 + dy, s, a)
        s, a, dx, dy = anim(tt, 1.0, None, "up", 0.3)
        place(c, label_pill("21 NOVEMBER 2026 | MASJID AS-SIDDIQ", 46, "emerald", w=960, h=104, color=GOLD_L), CX + dx, 1205 + dy, s, a)
        return c
    # KAD INFO AKHIR
    tt = t - T3
    c = vbg(t + 60, "emerald", lattice=0.4)
    if t >= hit:
        PART.draw(c, t, 1.0, burst=ease_out_cubic((t - hit) / 0.8) * 0.5)
        shockwave(c, t, hit, CX, 700, (255, 220, 120), 1600)
    s, a, dx, dy = anim(tt, 0.0, None, "slam", 0.22)
    place(c, text3d("BRISKWALK", 112, "green", maxw=880), CX + dx, 255 + dy, s, a)
    s, a, dx, dy = anim(tt, 0.1, None, "up", 0.25)
    place(c, text3d("MASJID BERSAMA GEN Z 2026", 58, "gold", maxw=880, depth=5), CX + dx, 355 + dy, s, a)
    for k, row in enumerate(info_rows()):
        s, a, dx, dy = anim(tt, 0.25 + k * 0.14, None, "left" if k % 2 == 0 else "right", 0.3)
        place(c, row, CX + dx, 470 + k * 114 + dy, s, a)
    s, a, dx, dy = anim(tt, 0.85, None, "pop", 0.3)
    qr = pill(250, 250, "white", 22, 5).copy()
    qr.alpha_composite(QR.resize((222, 222), Image.NEAREST).convert("RGBA"), (34, 34))
    place(c, qr, CX, 1010 + dy, s, a)
    s, a, dx, dy = anim(tt, 0.95, None, "up", 0.3)
    place(c, url_pill(), CX + dx, 1200 + dy, s, a)
    vo_end = TIMING["vo"][-1]["end"] - SCENES[7][0]
    pul = 1 + 0.05 * max(0, math.sin(tt * 2 * math.pi / BEAT))
    s, a, dx, dy = anim(t, vo_end + 0.05, None, "pop", 0.3)
    place(c, label_pill("DAFTAR SEKARANG!", 62, "gold", w=640, h=118, color=EMERALD_D), CX + dx, 1395 + dy, s * pul, a)
    return c


FN = {"hook": s_hook, "intro": s_intro, "speechA": s_speechA, "feature": s_feature, "speechB": s_speechB,
      "urgency": s_urgency, "howto": s_howto, "cta": s_cta}


# ------------------------------------------------------------------ subtitle
def draw_subs(canvas, t):
    for sb in TIMING["subs"]:
        if sb["start"] <= t < sb["end"] + 0.05:
            words, n = sb["words"], len(sb["words"])
            dur = sb["end"] - sb["start"]
            f = font(F_BLACK, 60)
            lines, cur = [], []
            for w in words:
                if cur and f.getlength(" ".join(x["w"] for x in cur + [w])) > 860:
                    lines.append(cur)
                    cur = [w]
                else:
                    cur.append(w)
            lines.append(cur)
            lh = 78
            lay = Image.new("RGBA", (W, 300), (0, 0, 0, 0))
            d = ImageDraw.Draw(lay)
            idx = 0
            for li, ln in enumerate(lines):
                txt = " ".join(x["w"] for x in ln)
                x = CX - f.getlength(txt) / 2
                y = 150 + (li - (len(lines) - 1) / 2) * lh
                for w in ln:
                    ws = sb["start"] + dur * 0.55 * idx / max(1, n)
                    if t >= ws:
                        pop = ease_out_back((t - ws) / 0.15, 3)
                        d.text((x, y + (1 - pop) * 14), w["w"], font=f, fill=(YELLOW if w["hl"] else WHITE) + (255,),
                               anchor="lm", stroke_width=7, stroke_fill=(0, 0, 0, 255))
                    x += f.getlength(w["w"] + " ")
                    idx += 1
            sh = Image.new("RGBA", lay.size, (0, 0, 0, 0))
            sh.putalpha(lay.getchannel("A").filter(ImageFilter.GaussianBlur(8)).point(lambda v: int(v * 0.6)))
            canvas.alpha_composite(sh, (0, 1395 - 150 + 6))
            canvas.alpha_composite(lay, (0, 1395 - 150))
            return


CUTS = [a for a, b in SCENES[1:]]
FLASH = CUTS + [2 * BAR, SCENES[5][0] + 2 * BAR + BAR / 2, SCENES[7][0] + 3.0, SCENES[7][1] - 2.4]
SHAKE = [0.0, 2 * BAR, SCENES[5][0] + 2 * BAR + BAR / 2, SCENES[7][1] - 2.4] + CUTS


def frame_at(t):
    si = next((i for i, (a, b) in enumerate(SCENES) if a <= t < b), len(SCENES) - 1)
    tau = t - SCENES[si][0]
    kind = KINDS[si]
    img = FN[kind](tau)
    if kind in ("hook", "feature") or (kind == "cta" and tau < 7.3):
        z = 1 + 0.02 * math.exp(-((tau % BEAT) / BEAT) * 6)
        big = img.resize((int(W * z), int(H * z)), Image.BILINEAR)
        ox, oy = (big.width - W) // 2, (big.height - H) // 2
        img = big.crop((ox, oy, ox + W, oy + H))
    for st in SHAKE:
        d = t - st
        if 0 <= d < 0.35:
            m = 22 * math.exp(-d * 12)
            img = img.transform(img.size, Image.AFFINE, (1, 0, -int(m * math.sin(d * 97)), 0, 1, -int(m * math.cos(d * 73))), Image.BILINEAR)
    img.alpha_composite(VIGNETTE)
    draw_subs(img, t)
    for ct in CUTS:
        d = t - ct
        if -0.2 <= d < 0.2:
            img = stripe_wipe(img, d / 0.2)
    for ft in FLASH:
        d = t - ft
        if 0 <= d < 0.14:
            img = Image.blend(img, Image.new("RGBA", img.size, (255, 250, 230, 255)), 0.7 * (1 - d / 0.14))
    if t < 0.08:
        img = Image.blend(Image.new("RGBA", img.size, (0, 0, 0, 255)), img, t / 0.08)
    return img.convert("RGB")


def render_range(args):
    i0, i1, path = args
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "17",
                          "-pix_fmt", "yuv420p", path], stdin=subprocess.PIPE)
    for i in range(i0, i1):
        p.stdin.write(frame_at(i / FPS).tobytes())
    p.stdin.close()
    p.wait()
    return path


def main():
    a = sys.argv[1:]
    if a and a[0] == "--preview":
        for t in [float(x) for x in a[1].split(",")]:
            frame_at(t).save(os.path.join(BUILD, f"prev_{t:06.2f}.png"))
        return
    nf = int(round(DURATION * FPS))
    edges = np.linspace(0, nf, 17).astype(int)
    jobs = [(edges[k], edges[k + 1], os.path.join(BUILD, f"seg_{k:02}.mp4")) for k in range(16)]
    with Pool(int(os.environ.get("WORKERS", os.cpu_count() or 4))) as pool:
        for pth in pool.imap(render_range, jobs):
            print("done", pth, flush=True)
    with open(os.path.join(BUILD, "segs.txt"), "w") as f:
        for _, _, pth in jobs:
            f.write(f"file '{pth}'\n")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", os.path.join(BUILD, "segs.txt"),
                    "-c", "copy", os.path.join(BUILD, "video_silent.mp4")], check=True)
    print("video_silent.mp4 OK")


if __name__ == "__main__":
    main()
