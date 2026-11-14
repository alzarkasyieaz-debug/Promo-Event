"""Render video 1080x1920 @30fps untuk BRISKWALK MASJID BERSAMA GEN Z 2026.

Semua visual dibina daripada poster rasmi + motion graphics (tiada footage AI).
Penggunaan:  python3 render_video.py [--preview t1,t2,...] [--start S --end E]
"""
import json, math, os, subprocess, sys
from multiprocessing import Pool

import numpy as np
import qrcode
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

from config import (W, H, FPS, BEAT, BAR, SCENES, DURATION, URL, ASSETS, BUILD, OUT)
from gfx import *  # noqa

os.makedirs(BUILD, exist_ok=True)
TIMING = json.load(open(os.path.join(BUILD, "timing.json"), encoding="utf-8"))
CX = 520  # paksi tengah sedikit ke kiri (elak butang UI TikTok/Reels di kanan)

# ------------------------------------------------------------------ aset poster
POSTER = Image.open(os.path.join(ASSETS, "poster_rasmi.jpg")).convert("RGB")
P2 = POSTER.resize((POSTER.width * 2, POSTER.height * 2), Image.LANCZOS).filter(
    ImageFilter.UnsharpMask(radius=2, percent=80, threshold=2))
CROPS = {  # koordinat poster asal (853x1280)
    "masjid": (0, 288, 440, 447),
    "walk": (455, 298, 853, 470),
    "walk_c": (560, 290, 790, 470),
    "walk_l": (440, 320, 640, 480),
    "walk_r": (680, 300, 853, 470),
    "logo": (300, 0, 550, 113),
}


def crop2(key):
    l, t, r, b = CROPS[key]
    return P2.crop((l * 2, t * 2, r * 2, b * 2))


LOGO = crop2("logo").convert("RGBA")


def _backdrop():
    sc = H / POSTER.height
    bp = POSTER.resize((int(POSTER.width * sc), H), Image.LANCZOS)
    x0 = (bp.width - W) // 2
    bp = bp.crop((x0, 0, x0 + W, H)).filter(ImageFilter.GaussianBlur(28))
    g = Image.fromarray(vgrad(W, H, [(6, 70, 44), (3, 40, 26), (2, 26, 17)]))
    return Image.blend(bp, g, 0.78).convert("RGBA")


BACKDROP = _backdrop()
DARK = Image.fromarray(vgrad(W, H, [(4, 46, 30), (2, 22, 14), (1, 12, 8)])).convert("RGBA")


def _rays():
    s = 1300
    im = Image.new("L", (s, s), 0)
    d = ImageDraw.Draw(im)
    for k in range(18):
        a = k * 2 * math.pi / 18
        a2 = a + 0.09
        d.polygon([(s / 2, s / 2), (s / 2 + s * math.cos(a), s / 2 + s * math.sin(a)), (s / 2 + s * math.cos(a2), s / 2 + s * math.sin(a2))], fill=255)
    im = im.filter(ImageFilter.GaussianBlur(10))
    yy, xx = np.mgrid[0:s, 0:s]
    r = np.hypot(xx - s / 2, yy - s / 2) / (s / 2)
    a = np.asarray(im).astype(np.float32) * np.clip(1 - r, 0, 1) ** 1.2 * 0.22
    out = np.zeros((s, s, 4), np.uint8)
    out[..., 0], out[..., 1], out[..., 2] = 255, 210, 90
    out[..., 3] = a.astype(np.uint8)
    return Image.fromarray(out, "RGBA")


RAYS = _rays()


def _vignette():
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.hypot((xx - W / 2) / (W / 2), (yy - H / 2) / (H / 2))
    a = np.clip((r - 0.75) / 0.6, 0, 1) ** 1.5 * 170
    out = np.zeros((H, W, 4), np.uint8)
    out[..., 3] = a.astype(np.uint8)
    return Image.fromarray(out, "RGBA")


VIGNETTE = _vignette()


def _red_vig():
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.hypot((xx - W / 2) / (W / 2), (yy - H / 2) / (H / 2))
    a = np.clip((r - 0.55) / 0.7, 0, 1) * 200
    out = np.zeros((H, W, 4), np.uint8)
    out[..., 0], out[..., 1], out[..., 2] = 210, 20, 30
    out[..., 3] = a.astype(np.uint8)
    return Image.fromarray(out, "RGBA")


RED_VIG = _red_vig()
PART = Particles()


def _qr():
    q = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=12, border=2)
    q.add_data(URL)
    q.make(fit=True)
    img = q.make_image(fill_color=(4, 40, 28), back_color="white").convert("RGB")
    return img


QR = _qr()
QR.save(os.path.join(OUT, "qr_pendaftaran.png"))


# ------------------------------------------------------------------ helpers
def bg(t, kind="backdrop", rays=True, parts=1.0, rot_speed=6):
    base = (BACKDROP if kind == "backdrop" else DARK).copy()
    if rays:
        r = RAYS.rotate(t * rot_speed, Image.BILINEAR)
        r = r.resize((int(r.width * 1.9), int(r.height * 1.9)), Image.BILINEAR)
        place(base, r, W / 2, H * 0.42)
    if parts:
        PART.draw(base, t, parts)
    return base


def card(key, out_w, out_h, zoom=1.0, px=0.5, py=0.5, radius=34, border=6, fade_top=False, gray=0.0, bright=1.0):
    src = crop2(key)
    sw, sh = src.size
    asp = out_w / out_h
    if sw / sh > asp:
        ch, cw = sh, sh * asp
    else:
        cw, ch = sw, sw / asp
    cw, ch = cw / zoom, ch / zoom
    x0 = (sw - cw) * px
    y0 = (sh - ch) * py
    im = src.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((out_w, out_h), Image.BICUBIC)
    if gray:
        im = Image.blend(im, im.convert("L").convert("RGB"), gray)
    if bright != 1.0:
        im = ImageEnhance.Brightness(im).enhance(bright)
    im = im.convert("RGBA")
    if fade_top:
        a = np.asarray(im).copy()
        f = np.clip(np.arange(out_h) / (out_h * 0.22), 0, 1)[:, None]
        a[..., :3] = (a[..., :3] * f[..., None] + np.array(EMERALD_D) * (1 - f[..., None])).astype(np.uint8)
        im = Image.fromarray(a, "RGBA")
    S = out_w + 2 * border + 60, out_h + 2 * border + 60
    out = Image.new("RGBA", S, (0, 0, 0, 0))
    sh_ = Image.new("L", S, 0)
    ImageDraw.Draw(sh_).rounded_rectangle([30 + 8, 30 + 16, 30 + out_w + 2 * border + 8, 30 + out_h + 2 * border + 16], radius, fill=170)
    shadow = Image.new("RGBA", S, (0, 0, 0, 0))
    shadow.putalpha(sh_.filter(ImageFilter.GaussianBlur(14)))
    out.alpha_composite(shadow)
    bm = Image.new("L", S, 0)
    ImageDraw.Draw(bm).rounded_rectangle([30, 30, 30 + out_w + 2 * border, 30 + out_h + 2 * border], radius, fill=255)
    bl = Image.fromarray(vgrad(S[0], S[1], [(255, 240, 170), (240, 176, 20), (180, 110, 0)])).convert("RGBA")
    bl.putalpha(bm)
    out.alpha_composite(bl)
    m = Image.new("L", (out_w, out_h), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, out_w - 1, out_h - 1], max(2, radius - border), fill=255)
    im.putalpha(m)
    out.alpha_composite(im, (30 + border, 30 + border))
    return out


def poster_card(width, tilt=0.0, sweep_p=None):
    h = int(width * POSTER.height / POSTER.width)
    im = POSTER.resize((width, h), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.2, 60, 2)).convert("RGBA")
    b = 6
    out = Image.new("RGBA", (width + 2 * b + 60, h + 2 * b + 60), (0, 0, 0, 0))
    sh_ = Image.new("L", out.size, 0)
    ImageDraw.Draw(sh_).rounded_rectangle([38, 46, 38 + width + 2 * b, 46 + h + 2 * b], 22, fill=190)
    shadow = Image.new("RGBA", out.size, (0, 0, 0, 0))
    shadow.putalpha(sh_.filter(ImageFilter.GaussianBlur(16)))
    out.alpha_composite(shadow)
    bm = Image.new("L", out.size, 0)
    ImageDraw.Draw(bm).rounded_rectangle([30, 30, 30 + width + 2 * b, 30 + h + 2 * b], 22, fill=255)
    bl = Image.fromarray(vgrad(out.width, out.height, [(255, 240, 170), (240, 176, 20), (180, 110, 0)])).convert("RGBA")
    bl.putalpha(bm)
    out.alpha_composite(bl)
    m = Image.new("L", im.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, width - 1, h - 1], 16, fill=255)
    im.putalpha(m)
    out.alpha_composite(im, (30 + b, 30 + b))
    if sweep_p is not None and 0 <= sweep_p <= 1:
        out = sweep(out, sweep_p, 0.08, 120)
    if tilt:
        out = perspective(out, tilt)
    return out


def perspective(im, tilt):
    """Condong 3D sekitar paksi menegak; tilt -1..1."""
    w, h = im.size
    k = tilt * 0.22
    # sisi kiri dikecilkan (tilt>0) — pemetaan quad ke segi empat
    dy = h * abs(k) / 2
    if k > 0:
        quad = (0, -dy, 0, h + dy, w, h, w, 0)
    else:
        quad = (0, 0, 0, h, w, h + dy, w, -dy)
    return im.transform((w, h), Image.QUAD, quad, Image.BILINEAR)


@lru_cache(maxsize=None)
def url_pill(scale_w=880):
    txt = flat_text(URL, 40, EMERALD_D, F_MONO, shadow=False)
    w = max(scale_w, txt.width + 30)
    p = pill(w, 104, "white", 52, 6).copy()
    p.alpha_composite(txt, ((p.width - txt.width) // 2, (p.height - txt.height) // 2 - 6))
    return p


@lru_cache(maxsize=None)
def label_pill(text, size, kind, w=None, h=None, color=WHITE, fpath=F_BLACK_IT):
    txt = flat_text(text, size, color, fpath, shadow=kind not in ("white", "gold"))
    w = w or txt.width + 70
    h = h or int(size * 1.75)
    p = pill(w, h, kind, h // 2, 6).copy()
    p.alpha_composite(txt, ((p.width - txt.width) // 2, (p.height - txt.height) // 2 - 6))
    return p


def speed_lines(canvas, t, strength=1.0, cx=W / 2, cy=H * 0.45, seed=3):
    if strength <= 0:
        return
    lay = Image.new("RGBA", (W // 2, H // 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    r = np.random.default_rng(seed + int(t * 15))
    for _ in range(46):
        a = r.uniform(0, 2 * math.pi)
        r1 = r.uniform(260, 520)
        r2 = r1 + r.uniform(200, 600)
        wdt = int(r.uniform(1, 4))
        d.line([cx / 2 + r1 * math.cos(a), cy / 2 + r1 * math.sin(a), cx / 2 + r2 * math.cos(a), cy / 2 + r2 * math.sin(a)],
               fill=(255, 236, 170, int(150 * strength)), width=wdt)
    canvas.alpha_composite(lay.resize((W, H), Image.BILINEAR))


def footprints(canvas, t, n_steps, t0=0.0):
    """Tapak kasut melangkah ke atas mengikut beat."""
    for k in range(n_steps):
        ts = t0 + k * BEAT
        if t < ts:
            break
        p = (t - ts) / 0.18
        x = CX + (-120 if k % 2 == 0 else 120)
        y = 1650 - k * 190 + (t - t0) * 120
        al = clamp(1.6 - (t - ts) * 0.9)
        sc = 0.6 + 0.4 * ease_out_back(p)
        place(canvas, icon_shoeprint(170), x, y, sc * 1.25, al, rot=-10 if k % 2 == 0 else 10)


# ------------------------------------------------------------------ SCENES
def scene1(t):  # 0–5.45 HOOK
    c = bg(t, "dark", rays=True, parts=0.6, rot_speed=40)
    # smash cuts B-roll poster setiap 2 beat selepas beat 2
    cuts = [(2 * BEAT, 4 * BEAT, "walk", 0.5), (4 * BEAT, 6 * BEAT, "masjid", 0.5), (6 * BEAT, 8 * BEAT, "walk_c", 0.35)]
    for a, b, key, px in cuts:
        if a <= t < b:
            p = (t - a) / (b - a)
            cd = card(key, 960, 640, zoom=1.25 - 0.2 * p, px=px, py=0.4)
            place(c, cd, CX, 560, 1.0 + 0.04 * (1 - p))
    footprints(c, t, 8 if t < 8 * BEAT else 0)
    speed_lines(c, t, 0.9 if t < 2 * BAR else 0.5)
    s, a, dx, dy = anim(t, 0.05, 2 * BAR - 0.18, "slam", 0.22)
    place(c, text3d("SERI ISKANDAR,", 104, "white", maxw=900), CX + dx, 1040 + dy, s, a)
    s, a, dx, dy = anim(t, 2 * BEAT, 2 * BAR - 0.18, "slam", 0.22)
    place(c, text3d("ARE YOU READY?", 112, "gold", maxw=900), CX + dx, 1185 + dy, s, a)
    if t >= 2 * BAR:
        tt = t - 2 * BAR
        PART.draw(c, t, 1.0, burst=ease_out_cubic(tt / 0.6) * 0.6)
        s, a, dx, dy = anim(tt, 0.0, None, "slam", 0.2)
        place(c, text3d("JOM", 170, "white"), CX + dx, 640 + dy, s, a)
        s, a, dx, dy = anim(tt, 0.12, None, "slam", 0.22)
        sp = text3d("BRISKWALK!", 190, "gold", maxw=900)
        sp = sweep(sp, (tt - 0.4) / 0.9) if 0.4 < tt < 1.3 else sp
        place(c, sp, CX + dx, 860 + dy, s, a)
    return c


def scene2(t):  # 5.45–14.55 PERKENALKAN ACARA
    L = SCENES[1][1] - SCENES[1][0]
    c = bg(t + 10, "backdrop", parts=0.9)
    if t < 3.4:
        p = ease_out_cubic(t / 0.9)
        tilt = (1 - p) * 0.9
        pc = poster_card(820, tilt=tilt, sweep_p=(t - 1.0) / 1.4)
        place(c, pc, CX, 700 + (1 - p) * 300, 0.75 + 0.25 * p + 0.02 * t, clamp(t / 0.25))
        return c
    tt = t - 3.4
    # logo reveal
    s, a, dx, dy = anim(tt, 0.0, None, "pop", 0.35)
    lg = sweep(LOGO, (tt - 0.3) / 0.8, 0.12, 160) if 0.3 < tt < 1.1 else LOGO
    lgp = pill(560, 270, "white", 40, 6).copy()
    lgp.alpha_composite(lg.resize((500, 226), Image.LANCZOS), (50, 42))
    place(c, lgp, CX, 250, s * 0.85, a)
    # B-roll: masjid "aerial-style" (zoom-out perlahan) lalu peserta
    if tt < 2.7:
        cd = card("masjid", 960, 440, zoom=1.35 - 0.25 * (tt / 2.7), px=0.4, py=0.6, fade_top=False)
    else:
        q = (tt - 2.7) / (L - 3.4 - 2.7)
        cd = card("walk", 960, 440, zoom=1.15 + 0.1 * q, px=0.3 + 0.3 * q, py=0.3)
    place(c, cd, CX, 640, 1.0, clamp(tt / 0.2))
    # tajuk 3D berurutan ikut beat
    s, a, dx, dy = anim(tt, 0.25, None, "slam", 0.22)
    sp = text3d("BRISKWALK", 150, "green", maxw=900)
    sp = sweep(sp, (tt - 0.6) / 1.0) if 0.6 < tt < 1.6 else sp
    place(c, sp, CX + dx, 960 + dy, s, a)
    s, a, dx, dy = anim(tt, 0.25 + 2 * BEAT, None, "left", 0.3)
    place(c, text3d("MASJID BERSAMA", 84, "white", maxw=900), CX + dx, 1090 + dy, s, a)
    s, a, dx, dy = anim(tt, 0.25 + 4 * BEAT, None, "pop", 0.3)
    sp = text3d("GEN Z 2026", 120, "gold")
    sp = sweep(sp, (tt - 2.4) / 0.9) if 2.4 < tt < 3.3 else sp
    place(c, sp, CX + dx, 1215 + dy, s, a)
    return c


SLOGANS = [("AKTIFKAN DIRI!", "bolt"), ("AJAK SAHABAT!", "friends"), ("ERATKAN UKHUWAH!", "heart"), ("SATUKAN GENERASI!", "gen")]


def slogan_icon(kind):
    return {"bolt": icon_bolt(170), "friends": icon_people(190, 2), "heart": icon_heart(170),
            "gen": icon_people(220, 3, (0.7, 1.0, 0.85))}[kind]


def scene3(t):  # 14.55–25.45 TARIKAN UTAMA
    L = SCENES[2][1] - SCENES[2][0]
    c = bg(t + 20, "backdrop", parts=1.0, rot_speed=10)
    seq = [("walk", 0.0, 0.3), ("walk_l", 0.1, 0.3), ("walk_c", 0.5, 0.3), ("walk_r", 0.5, 0.3), ("masjid", 0.4, 0.6), ("walk", 0.9, 0.3)]
    seg = 2 * BEAT * 2   # tukar B-roll setiap 4 beat
    i = min(int(t / seg), len(seq) - 1)
    key, px, py = seq[i % len(seq)]
    p = (t - i * seg) / seg
    zoom = 1.08 + 0.18 * p if i % 2 == 0 else 1.26 - 0.18 * p
    pxx = clamp(px + (0.25 * p if i % 2 else -0.15 * p) + 0.1)
    cd = card(key, 960, 700, zoom=zoom, px=pxx, py=py)
    place(c, cd, CX, 610, 1.0)
    # slogan berurutan (setiap 6 beat)
    step = L / 4
    for k, (txt, ic) in enumerate(SLOGANS):
        a0 = k * step + 0.15
        if a0 <= t < (k + 1) * step + 0.05:
            tt = t - a0
            s, a, dx, dy = anim(tt, 0, step - 0.35, "slam" if k % 2 == 0 else "pop", 0.25, 0.18)
            place(c, slogan_icon(ic), CX + dx, 1040 + dy, s, a)
            sp = text3d(txt, 104, "gold" if k % 2 == 0 else "white", maxw=900)
            sp = sweep(sp, (tt - 0.35) / 0.8) if 0.35 < tt < 1.15 else sp
            place(c, sp, CX + dx, 1210 + dy, s, a)
    return c


def scene4(t):  # 25.45–34.55 BUTIRAN ACARA
    L = SCENES[3][1] - SCENES[3][0]
    c = bg(t + 30, "backdrop", parts=0.8)
    split = 4.4
    if t < split:
        # kalendar flip ke 21
        flip_end = 1.0
        if t < flip_end:
            n = 1 + int(20 * ease_out_cubic(t / flip_end))
            ph = (t * 18) % 1
            sy = abs(math.cos(ph * math.pi))
        else:
            n, sy = 21, 1.0
        cal = icon_calendar(470, "NOVEMBER", str(n), "SABTU" if n == 21 else "")
        s, a, dx, dy = anim(t, 0.0, split - 0.2, "pop", 0.35)
        cal_s = cal.resize((cal.width, max(2, int(cal.height * (0.55 + 0.45 * sy)))), Image.BILINEAR)
        place(c, cal_s, CX + dx, 560 + dy, s, a)
        s, a, dx, dy = anim(t, flip_end, split - 0.2, "slam", 0.22)
        sp = text3d("21 NOVEMBER 2026", 108, "gold", maxw=900)
        sp = sweep(sp, (t - 1.4) / 0.9) if 1.4 < t < 2.3 else sp
        place(c, sp, CX + dx, 960 + dy, s, a)
        s, a, dx, dy = anim(t, flip_end + 2 * BEAT, split - 0.2, "pop", 0.3)
        place(c, label_pill("SABTU", 86, "red", w=420, h=140), CX + dx, 1135 + dy, s, a)
    else:
        tt = t - split
        q = tt / (L - split)
        cd = card("masjid", 960, 560, zoom=1.3 - 0.2 * q, px=0.45, py=0.7)
        place(c, cd, CX, 560, 1.0, clamp(tt / 0.15))
        s, a, dx, dy = anim(tt, 0.15, None, "drop", 0.45)
        place(c, icon_pin(210), CX + dx, 470 + dy, s, a)
        # tarikh kecil kekal sebagai ringkasan
        place(c, label_pill("SABTU • 21 NOVEMBER 2026", 50, "emerald", w=760, h=96, color=GOLD_L), CX, 190, 1, clamp(tt / 0.2))
        s, a, dx, dy = anim(tt, 0.5, None, "slam", 0.22)
        place(c, text3d("MASJID AS-SIDDIQ", 112, "gold", maxw=900), CX + dx, 960 + dy, s, a)
        s, a, dx, dy = anim(tt, 0.5 + 2 * BEAT, None, "up", 0.3)
        place(c, text3d("SERI ISKANDAR", 96, "white", maxw=900), CX + dx, 1110 + dy, s, a)
    return c


def scene5(t):  # 34.55–47.27 URGENCY
    c = bg(t + 40, "dark", rays=True, parts=0.5, rot_speed=4)
    pulse = 0.5 + 0.5 * math.sin(t * 2 * math.pi / (2 * BEAT))
    c.alpha_composite(with_alpha(RED_VIG, 0.35 + 0.35 * pulse))
    a1 = 2 * BAR  # 3.64
    if t < a1:
        s, a, dx, dy = anim(t, 0.05, a1 - 0.2, "slam", 0.22)
        place(c, label_pill("PENDAFTARAN", 100, "emerald", w=900, h=170, color=WHITE), CX + dx, 760 + dy, s, a)
        s, a, dx, dy = anim(t, 0.05 + 2 * BEAT, a1 - 0.2, "slam", 0.22)
        sp = text3d("MASIH DIBUKA!", 136, "yellow", maxw=900)
        sp = sweep(sp, (t - 1.3) / 0.9) if 1.3 < t < 2.2 else sp
        place(c, sp, CX + dx, 960 + dy, s, a)
        return c
    tt = t - a1
    # header kecil kekal
    place(c, label_pill("PENDAFTARAN MASIH DIBUKA!", 52, "emerald", w=860, h=100, color=YELLOW), CX, 190, 1, clamp(tt / 0.2))
    # kalendar flip 1 -> 17 (countdown visual) kemudian slam pada 3 bar
    land = 3 * BAR - a1   # 1.82
    if tt < land:
        n = 1 + int(16 * ease_in_out(tt / land))
        ph = (tt * 14) % 1
        sy = 0.55 + 0.45 * abs(math.cos(ph * math.pi))
    else:
        n, sy = 17, 1.0
    shake = 0
    if tt >= land:
        k = (tt - land)
        shake = int(18 * math.exp(-k * 10) * math.sin(k * 90))
    cal = icon_calendar(400, "NOVEMBER", str(n), "SELASA" if n == 17 else "")
    cal = cal.resize((cal.width, int(cal.height * sy)), Image.BILINEAR)
    place(c, cal, CX - 250 + shake, 520, 1.0 if tt >= land else 0.95, 1)
    # jam bergerak ke 12.00
    cp = clamp(tt / (land + 0.6))
    ang = ease_out_cubic(cp) * 2 * math.pi * 3
    place(c, icon_clock(330, ang, ang / 12 * 2.5 + (2 * math.pi - 2.5 * 2 * math.pi / 12) * ease_out_cubic(cp)), CX + 250 - shake, 520, 1, 1)
    # amaran
    if tt >= land:
        k = tt - land
        s, a, dx, dy = anim(k, 0, None, "slam", 0.2)
        box = label_pill("TARIKH TUTUP PENDAFTARAN", 54, "red", w=900, h=110, color=WHITE)
        place(c, box, CX + dx + shake, 840 + dy, s, a)
        sp = text3d("17 NOVEMBER 2026", 112, "yellow", maxw=900)
        sp = sweep(sp, (k - 0.5) / 0.9) if 0.5 < k < 1.4 else sp
        s, a, dx, dy = anim(k, 0.1, None, "slam", 0.22)
        place(c, sp, CX + dx + shake, 1000 + dy, s * (1 + 0.03 * pulse), a)
        s, a, dx, dy = anim(k, 0.1 + 2 * BEAT, None, "pop", 0.3)
        place(c, label_pill("SELASA • 12.00 TENGAH HARI", 60, "white", w=900, h=120, color=RED, fpath=F_BLACK), CX + dx, 1165 + dy, s, a)
        s, a, dx, dy = anim(k, 0.4, None, "pop", 0.3)
        wob = 8 * math.sin(t * 14)
        place(c, icon_alert(110), CX + 18, 520, s, a, rot=wob)
    return c


def scene6(t):  # 47.27–58.18 CARA MENDAFTAR
    L = SCENES[5][1] - SCENES[5][0]
    c = bg(t + 50, "backdrop", parts=0.7)
    s, a, dx, dy = anim(t, 0.05, None, "slam", 0.22)
    place(c, text3d("CARA DAFTAR", 96, "gold"), CX + dx, 190 + dy, s, a)
    t1, t2 = 4.3, 6.6
    if t < t1:
        s, a, dx, dy = anim(t, 0.1, t1 - 0.2, "up", 0.35)
        ph = icon_phone(400, 780, clamp((t - 0.6) / 2.8))
        place(c, ph, CX - 230 + dx, 700 + dy, s, a)
        s, a, dx, dy = anim(t, 0.3, t1 - 0.2, "right", 0.3)
        place(c, label_pill("ONLINE", 74, "emerald", w=430, h=130, color=WHITE), CX + 250 + dx, 560 + dy, s, a)
        s, a, dx, dy = anim(t, 0.3 + 2 * BEAT, t1 - 0.2, "right", 0.3)
        place(c, text3d("GOOGLE", 82, "white", depth=6), CX + 250 + dx, 720 + dy, s, a)
        place(c, text3d("FORM", 82, "gold", depth=6), CX + 250 + dx, 820 + dy, s, a)
    elif t < t2:
        tt = t - t1
        s, a, dx, dy = anim(tt, 0.0, t2 - t1 - 0.2, "pop", 0.3)
        place(c, icon_counter(470), CX, 610 + dy, s, a)
        s, a, dx, dy = anim(tt, 0.15, t2 - t1 - 0.2, "left", 0.3)
        place(c, label_pill("OFFLINE", 74, "emerald", w=460, h=130, color=WHITE), CX + dx, 880 + dy, s, a)
        s, a, dx, dy = anim(tt, 0.15 + 2 * BEAT, t2 - t1 - 0.2, "slam", 0.22)
        place(c, text3d("KAUNTER MASJID", 96, "gold", maxw=900), CX + dx, 1020 + dy, s, a)
    else:
        tt = t - t2
        s, a, dx, dy = anim(tt, 0.0, None, "left", 0.3)
        place(c, label_pill("ONLINE — GOOGLE FORM", 50, "emerald", w=860, h=100, color=WHITE), CX + dx, 330 + dy, s, a)
        s, a, dx, dy = anim(tt, 0.12, None, "right", 0.3)
        place(c, label_pill("OFFLINE — KAUNTER MASJID", 50, "emerald", w=860, h=100, color=WHITE), CX + dx, 450 + dy, s, a)
        s, a, dx, dy = anim(tt, 0.3, None, "pop", 0.35)
        qr = pill(420, 420, "white", 30, 6).copy()
        qr.alpha_composite(QR.resize((380, 380), Image.NEAREST).convert("RGBA"), (40, 40))
        place(c, qr, CX, 790 + dy, s, a)
        place(c, flat_text("IMBAS QR ATAU TAIP PAUTAN", 40, GOLD_L, F_BLACK), CX, 1040, 1, clamp((tt - 0.5) / 0.3))
    # URL kekal besar & lama (dari 0.9s hingga hujung scene ≈ 10 s)
    if t >= 0.9:
        s, a, dx, dy = anim(t, 0.9, None, "up", 0.3)
        up = url_pill()
        up = sweep(up, (t - 1.3) / 1.0, 0.1, 90) if 1.3 < t < 2.3 else up
        place(c, up, CX + dx, 1185 + dy, s, a)
    return c


def scene7(t):  # 58.18–72.73 FINAL CTA
    L = SCENES[6][1] - SCENES[6][0]
    t_freeze, t_lock, t_end = 2 * BAR, 3.5 * BAR, 10.3
    if t < t_freeze:
        c = bg(t + 60, "backdrop", parts=1.0, rot_speed=14)
        p = t / t_freeze
        cd = card("walk", 980, 800, zoom=1.0 + 0.45 * ease_in_cubic(p), px=0.5, py=0.4)
        place(c, cd, CX, 620, 1.0 + 0.06 * p)
        speed_lines(c, t, 0.4 + 0.6 * p, cy=620)
        s, a, dx, dy = anim(t, 0.1, None, "slam", 0.22)
        place(c, text3d("JANGAN TUNGGU", 116, "white", maxw=900), CX + dx, 1110 + dy, s, a)
        s, a, dx, dy = anim(t, 0.1 + 2 * BEAT, None, "slam", 0.22)
        place(c, text3d("LAGI!", 150, "gold"), CX + dx, 1250 + dy, s, a)
        return c
    if t < t_lock:
        tt = t - t_freeze
        c = bg(t + 60, "backdrop", parts=0.6)
        g = clamp(1 - tt / 0.5)
        cd = card("walk", 980, 800, zoom=1.45, px=0.5, py=0.4, gray=0.6 * g, bright=1 + 0.6 * clamp(1 - tt / 0.15))
        place(c, cd, CX, 620, 1.06 + 0.02 * tt, 1, rot=-2.0)
        s, a, dx, dy = anim(tt, 0.1, None, "slam", 0.22)
        box = label_pill("DAFTAR SEBELUM", 70, "red", w=760, h=130, color=WHITE)
        place(c, box, CX + dx, 1080 + dy, s, a)
        s, a, dx, dy = anim(tt, 0.1 + 2 * BEAT, None, "slam", 0.22)
        sp = text3d("17 NOVEMBER!", 130, "yellow", maxw=900)
        sp = sweep(sp, (tt - 1.2) / 0.9) if 1.2 < tt < 2.1 else sp
        place(c, sp, CX + dx, 1240 + dy, s, a)
        return c
    if t < t_end:
        tt = t - t_lock
        c = bg(t + 60, "backdrop", parts=1.0)
        lgp = pill(500, 240, "white", 36, 6).copy()
        lgp.alpha_composite(LOGO.resize((450, 204), Image.LANCZOS), (45, 38))
        s, a, dx, dy = anim(tt, 0.0, None, "pop", 0.3)
        place(c, lgp, CX, 330, s * 0.9, a)
        s, a, dx, dy = anim(tt, 0.15, None, "slam", 0.22)
        sp = text3d("BRISKWALK", 160, "green", maxw=900)
        sp = sweep(sp, (tt - 0.6) / 1.0) if 0.6 < tt < 1.6 else sp
        place(c, sp, CX + dx, 600 + dy, s, a)
        s, a, dx, dy = anim(tt, 0.15 + 2 * BEAT, None, "left", 0.3)
        place(c, text3d("MASJID BERSAMA", 88, "white", maxw=900), CX + dx, 740 + dy, s, a)
        s, a, dx, dy = anim(tt, 0.15 + 3 * BEAT, None, "pop", 0.3)
        place(c, text3d("GEN Z 2026", 124, "gold"), CX + dx, 870 + dy, s, a)
        s, a, dx, dy = anim(tt, 0.15 + 5 * BEAT, None, "up", 0.3)
        place(c, label_pill("21 NOVEMBER 2026 | MASJID AS-SIDDIQ", 46, "emerald", w=960, h=104, color=GOLD_L), CX + dx, 1040 + dy, s, a)
        return c
    # END CARD: poster + URL + CTA
    tt = t - t_end
    hit = (L - BAR) - t_end
    c = bg(t + 60, "backdrop", parts=1.0)
    if tt >= hit:
        PART.draw(c, t, 1.0, burst=ease_out_cubic((tt - hit) / 0.8) * 0.5)
    p = ease_out_cubic(tt / 0.6)
    pc = poster_card(700, tilt=(1 - p) * -0.8, sweep_p=(tt - 0.7) / 1.2)
    place(c, pc, CX, 640 + (1 - p) * 200, 0.85 + 0.15 * p, clamp(tt / 0.2))
    s, a, dx, dy = anim(tt, 0.4, None, "up", 0.3)
    place(c, url_pill(), CX + dx, 1250 + dy, s, a)
    pul = 1 + 0.05 * max(0, math.sin(tt * 2 * math.pi / BEAT))
    s, a, dx, dy = anim(tt, 0.7, None, "pop", 0.3)
    place(c, label_pill("DAFTAR SEKARANG!", 62, "gold", w=640, h=118, color=EMERALD_D), CX + dx, 1385 + dy, s * pul, a)
    s, a, dx, dy = anim(tt, 1.0, None, "fade", 0.3)
    place(c, flat_text("Tutup: Selasa, 17 Nov 2026 • 12.00 tengah hari", 38, WHITE, F_BLACK), CX, 1478, 1, a)
    return c


SCENE_FN = [scene1, scene2, scene3, scene4, scene5, scene6, scene7]


# ------------------------------------------------------------------ subtitle
SUB_Y = 1395


def draw_subs(canvas, t):
    for sb in TIMING["subs"]:
        if sb["start"] <= t < sb["end"] + 0.05:
            words = sb["words"]
            n = len(words)
            dur = sb["end"] - sb["start"]
            f = font(F_BLACK, 60)
            # bina baris (wrap ≤ 860px)
            lines, cur = [], []
            for w in words:
                test = " ".join(x["w"] for x in cur + [w])
                if cur and f.getlength(test) > 860:
                    lines.append(cur)
                    cur = [w]
                else:
                    cur.append(w)
            lines.append(cur)
            lh = 78
            y0 = SUB_Y - (len(lines) - 1) * lh / 2
            idx = 0
            lay = Image.new("RGBA", (W, 300), (0, 0, 0, 0))
            d = ImageDraw.Draw(lay)
            for li, ln in enumerate(lines):
                txt = " ".join(x["w"] for x in ln)
                x = CX - f.getlength(txt) / 2
                y = 150 + (li - (len(lines) - 1) / 2) * lh
                for w in ln:
                    ws = sb["start"] + dur * 0.55 * idx / max(1, n)
                    if t >= ws:
                        pop = ease_out_back((t - ws) / 0.15, 3)
                        col = YELLOW if w["hl"] else WHITE
                        yy = y + (1 - pop) * 14
                        d.text((x, yy), w["w"], font=f, fill=col + (255,), anchor="lm", stroke_width=7, stroke_fill=(0, 0, 0, 255))
                    x += f.getlength(w["w"] + " ")
                    idx += 1
            sh = lay.getchannel("A").filter(ImageFilter.GaussianBlur(8))
            shadow = Image.new("RGBA", lay.size, (0, 0, 0, 0))
            shadow.putalpha(sh.point(lambda v: int(v * 0.6)))
            canvas.alpha_composite(shadow, (0, int(y0 - 150) + 6))
            canvas.alpha_composite(lay, (0, int(y0 - 150)))
            return


# ------------------------------------------------------------------ global FX
CUT_TIMES = [a for a, b in SCENES[1:]]
FLASHES = CUT_TIMES + [2 * BAR, SCENES[4][0] + 3 * BAR, SCENES[6][0] + 2 * BAR, SCENES[6][1] - BAR]
SHAKES = [0.0, 2 * BAR, SCENES[4][0] + 3 * BAR, SCENES[6][1] - BAR] + CUT_TIMES


def whip(img, amount, direction=1):
    """Whip pan: anjakan + motion blur mendatar."""
    a = np.asarray(img.convert("RGB")).astype(np.float32)
    shift = int(direction * amount * W)
    k = 9
    acc = np.zeros_like(a)
    for i in range(k):
        acc += np.roll(a, shift + int((i - k / 2) * amount * 140), axis=1)
    return Image.fromarray((acc / k).astype(np.uint8)).convert("RGBA")


def frame_at(t):
    si = next((i for i, (a, b) in enumerate(SCENES) if a <= t < b), len(SCENES) - 1)
    a, b = SCENES[si]
    tau = t - a
    img = SCENE_FN[si](tau)
    # beat pulse (scene bertenaga)
    if si in (0, 2, 6) and not (si == 6 and tau > 10.3):
        bp = (tau % BEAT) / BEAT
        z = 1 + 0.018 * math.exp(-bp * 6)
        if z > 1.001:
            big = img.resize((int(W * z), int(H * z)), Image.BILINEAR)
            ox, oy = (big.width - W) // 2, (big.height - H) // 2
            img = big.crop((ox, oy, ox + W, oy + H))
    # whip pan sekitar sempadan scene
    for i, ct in enumerate(CUT_TIMES):
        d = t - ct
        if -0.12 <= d < 0.12:
            amt = (1 - abs(d) / 0.12) * 0.35
            img = whip(img, amt, 1 if d < 0 else -1)
            if d < 0:
                img = img  # keluar ke kanan
    # shake
    for st in SHAKES:
        d = t - st
        if 0 <= d < 0.35:
            m = 22 * math.exp(-d * 12)
            ox, oy = int(m * math.sin(d * 97)), int(m * math.cos(d * 73))
            img = img.transform(img.size, Image.AFFINE, (1, 0, -ox, 0, 1, -oy), Image.BILINEAR)
    img.alpha_composite(VIGNETTE)
    draw_subs(img, t)
    # flash
    for ft in FLASHES:
        d = t - ft
        if 0 <= d < 0.16:
            al = 0.75 * (1 - d / 0.16)
            img = Image.blend(img, Image.new("RGBA", img.size, (255, 250, 230, 255)), al)
    # fade in/out
    if t < 0.08:
        img = Image.blend(Image.new("RGBA", img.size, (0, 0, 0, 255)), img, t / 0.08)
    return img.convert("RGB")


def render_range(args):
    i0, i1, path = args
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                          "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium",
                          "-crf", "16", "-pix_fmt", "yuv420p", path], stdin=subprocess.PIPE)
    for i in range(i0, i1):
        p.stdin.write(frame_at(i / FPS).tobytes())
    p.stdin.close()
    p.wait()
    return path


def main():
    args = sys.argv[1:]
    if args and args[0] == "--preview":
        ts = [float(x) for x in args[1].split(",")]
        for t in ts:
            frame_at(t).save(os.path.join(BUILD, f"prev_{t:06.2f}.png"))
        return
    nf = int(round(DURATION * FPS))
    workers = int(os.environ.get("WORKERS", os.cpu_count() or 4))
    chunks = 16
    edges = np.linspace(0, nf, chunks + 1).astype(int)
    jobs = [(edges[k], edges[k + 1], os.path.join(BUILD, f"seg_{k:02}.mp4")) for k in range(chunks)]
    with Pool(workers) as pool:
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
