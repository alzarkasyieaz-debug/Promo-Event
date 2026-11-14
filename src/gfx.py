"""Primitif grafik: teks 3D extruded, pill/box, ikon animasi, kad poster, partikel."""
import math
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from config import W, H

FD = "/usr/share/fonts/opentype/inter/"
F_BLACK_IT = FD + "InterDisplay-BlackItalic.otf"
F_BLACK = FD + "InterDisplay-Black.otf"
F_XB = FD + "InterDisplay-ExtraBold.otf"
F_BOLD = FD + "InterDisplay-Bold.otf"
F_MONO = "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-ExtraBold.ttf"

EMERALD = (11, 93, 59)
EMERALD_D = (4, 40, 28)
GOLD = (244, 180, 0)
GOLD_L = (255, 226, 130)
YELLOW = (255, 214, 10)
WHITE = (255, 255, 255)
RED = (214, 32, 40)

FACES = {
    "gold": [(255, 246, 196), (255, 212, 77), (227, 150, 10)],
    "white": [(255, 255, 255), (246, 252, 248), (214, 236, 224)],
    "yellow": [(255, 245, 140), (255, 214, 10), (247, 170, 0)],
    "green": [(46, 150, 96), (14, 102, 62), (6, 60, 36)],
    "red": [(255, 110, 100), (232, 40, 46), (160, 12, 20)],
}
EXTRUDE = {
    "gold": ((120, 70, 0), (50, 28, 0)),
    "white": ((10, 90, 56), (2, 34, 22)),
    "yellow": ((120, 70, 0), (50, 28, 0)),
    "green": ((120, 80, 0), (40, 25, 0)),
    "red": ((110, 10, 14), (40, 0, 4)),
}
STROKE = {"gold": (6, 48, 31), "white": (6, 48, 31), "yellow": (6, 48, 31), "green": (255, 205, 60), "red": (255, 235, 180)}


def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def ease_out_cubic(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def ease_in_cubic(x):
    x = clamp(x)
    return x ** 3


def ease_in_out(x):
    x = clamp(x)
    return 3 * x * x - 2 * x * x * x


def ease_out_back(x, s=2.2):
    x = clamp(x)
    x -= 1
    return x * x * ((s + 1) * x + s) + 1


def vgrad(w, h, stops):
    """Gradien menegak (h x w x 3) daripada senarai warna."""
    ys = np.linspace(0, 1, h)[:, None]
    n = len(stops) - 1
    out = np.zeros((h, 1, 3))
    for i in range(n):
        a, b = np.array(stops[i], float), np.array(stops[i + 1], float)
        m = (ys >= i / n) & (ys <= (i + 1) / n)
        f = (ys - i / n) * n
        out = np.where(m[..., None], a + (b - a) * f[..., None], out)
    return np.repeat(out, w, 1).astype(np.uint8)


@lru_cache(maxsize=None)
def font(path, size):
    return ImageFont.truetype(path, size)


@lru_cache(maxsize=None)
def text3d(text, size, face="gold", fpath=F_BLACK_IT, depth=None, stroke=None, glow=True, maxw=None):
    """Teks 3D: glow emas + extrusion + outline + muka gradien. Pulang RGBA."""
    f = font(fpath, size)
    if maxw:
        while f.getlength(text) > maxw and size > 20:
            size -= 2
            f = font(fpath, size)
    depth = depth if depth is not None else max(4, size // 10)
    sw = stroke if stroke is not None else max(3, size // 16)
    l, t, r, b = f.getbbox(text, stroke_width=sw)
    pad = depth + 40
    w, h = r - l + 2 * pad, b - t + 2 * pad
    org = (pad - l, pad - t)

    def mask(stw):
        m = Image.new("L", (w, h), 0)
        ImageDraw.Draw(m).text(org, text, font=f, fill=255, stroke_width=stw, stroke_fill=255)
        return m

    m_stroke, m_face = mask(sw), mask(0)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    if glow:
        g = m_stroke.filter(ImageFilter.GaussianBlur(size / 7))
        gl = Image.new("RGBA", (w, h), (255, 196, 40, 0))
        gl.putalpha(g.point(lambda v: int(v * 0.75)))
        out.alpha_composite(gl)
    c0, c1 = EXTRUDE[face]
    for i in range(depth, 0, -1):
        k = i / depth
        col = tuple(int(c0[j] * (1 - k) + c1[j] * k) for j in range(3))
        lay = Image.new("RGBA", (w, h), col + (255,))
        lay.putalpha(m_stroke)
        out.alpha_composite(lay, (int(i * 0.55), i))
    st = Image.new("RGBA", (w, h), STROKE[face] + (255,))
    st.putalpha(m_stroke)
    out.alpha_composite(st)
    fc = Image.fromarray(vgrad(w, h, FACES[face])).convert("RGBA")
    fc.putalpha(m_face)
    out.alpha_composite(fc)
    return out


@lru_cache(maxsize=None)
def flat_text(text, size, color=WHITE, fpath=F_BLACK, stroke=0, stroke_color=(0, 0, 0), shadow=True):
    f = font(fpath, size)
    l, t, r, b = f.getbbox(text, stroke_width=stroke)
    pad = 24
    w, h = r - l + 2 * pad, b - t + 2 * pad
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    if shadow:
        m = Image.new("L", (w, h), 0)
        ImageDraw.Draw(m).text((pad - l + 3, pad - t + 5), text, font=f, fill=200, stroke_width=stroke + 2, stroke_fill=200)
        sh = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        sh.putalpha(m.filter(ImageFilter.GaussianBlur(5)))
        out.alpha_composite(sh)
    d = ImageDraw.Draw(out)
    d.text((pad - l, pad - t), text, font=f, fill=color + (255,), stroke_width=stroke, stroke_fill=stroke_color + (255,))
    return out


@lru_cache(maxsize=None)
def pill(w, h, kind="emerald", radius=None, border=6):
    radius = radius if radius is not None else h // 2
    grads = {
        "emerald": [(22, 128, 80), (10, 88, 54), (4, 52, 32)],
        "red": [(240, 60, 60), (205, 22, 32), (140, 6, 14)],
        "white": [(255, 255, 255), (250, 250, 245), (236, 240, 236)],
        "gold": [(255, 236, 150), (250, 196, 30), (214, 140, 0)],
        "dark": [(8, 44, 30), (5, 32, 22), (3, 22, 15)],
    }
    S = 2
    sw, sh = (w + 40) * S, (h + 40) * S
    out = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    # bayang
    sm = Image.new("L", (sw, sh), 0)
    ImageDraw.Draw(sm).rounded_rectangle([20 * S + 6 * S, 20 * S + 12 * S, (20 + w) * S + 6 * S, (20 + h) * S + 12 * S], radius * S, fill=150)
    shd = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    shd.putalpha(sm.filter(ImageFilter.GaussianBlur(12 * S)))
    out.alpha_composite(shd)
    if border:
        bm = Image.new("L", (sw, sh), 0)
        ImageDraw.Draw(bm).rounded_rectangle([20 * S, 20 * S, (20 + w) * S, (20 + h) * S], radius * S, fill=255)
        bl = Image.fromarray(vgrad(sw, sh, [(255, 240, 170), (240, 176, 20), (180, 110, 0)])).convert("RGBA")
        bl.putalpha(bm)
        out.alpha_composite(bl)
    b = border * S
    fm = Image.new("L", (sw, sh), 0)
    ImageDraw.Draw(fm).rounded_rectangle([20 * S + b, 20 * S + b, (20 + w) * S - b, (20 + h) * S - b], max(1, radius * S - b), fill=255)
    fl = Image.fromarray(vgrad(sw, sh, grads[kind])).convert("RGBA")
    fl.putalpha(fm)
    out.alpha_composite(fl)
    # kilauan atas
    gm = Image.new("L", (sw, sh), 0)
    ImageDraw.Draw(gm).rounded_rectangle([20 * S + b * 2, 20 * S + b * 2, (20 + w) * S - b * 2, 20 * S + int(h * 0.45) * S], max(1, radius * S - b * 2), fill=40 if kind != "white" else 0)
    gl = Image.new("RGBA", (sw, sh), (255, 255, 255, 0))
    gl.putalpha(gm)
    out.alpha_composite(gl)
    return out.resize((w + 40, h + 40), Image.LANCZOS)


def compose_on(base, items):
    """items: [(sprite, cx, cy)] tampal di tengah relatif kepada base RGBA (salinan)."""
    out = base.copy()
    for sp, cx, cy in items:
        out.alpha_composite(sp, (int(cx - sp.width / 2), int(cy - sp.height / 2)))
    return out


# ------------------------------------------------------------------ ikon
def _canvas(s):
    return Image.new("RGBA", (s * 2, s * 2), (0, 0, 0, 0))


def _fin(im, s):
    return im.resize((s, s), Image.LANCZOS)


@lru_cache(maxsize=None)
def icon_shoeprint(s=120, col=GOLD):
    im = _canvas(s)
    d = ImageDraw.Draw(im)
    S = s * 2
    d.ellipse([S * 0.28, S * 0.02, S * 0.72, S * 0.58], fill=col + (255,))
    d.ellipse([S * 0.32, S * 0.64, S * 0.66, S * 0.98], fill=col + (255,))
    for k in range(3):
        y = S * (0.14 + k * 0.13)
        d.line([S * 0.36, y, S * 0.64, y], fill=EMERALD_D + (255,), width=max(2, S // 40))
    return _fin(im, s)


@lru_cache(maxsize=None)
def icon_calendar(s, top, num, sub=""):
    im = _canvas(s)
    d = ImageDraw.Draw(im)
    S = s * 2
    d.rounded_rectangle([S * .04, S * .12, S * .96, S * .96], S * .08, fill=(255, 255, 255, 255), outline=GOLD + (255,), width=S // 40)
    d.rounded_rectangle([S * .04, S * .12, S * .96, S * .36], S * .08, fill=RED + (255,))
    d.rectangle([S * .04, S * .26, S * .96, S * .36], fill=RED + (255,))
    for x in (.28, .72):
        d.rounded_rectangle([S * (x - .04), S * .03, S * (x + .04), S * .2], S * .03, fill=(60, 60, 60, 255))
    f1 = font(F_BLACK, int(S * .15))
    d.text((S / 2, S * .245), top, font=f1, fill=WHITE + (255,), anchor="mm")
    f2 = font(F_BLACK, int(S * .40))
    d.text((S / 2, S * .63), num, font=f2, fill=EMERALD_D + (255,), anchor="mm")
    if sub:
        f3 = font(F_BLACK, int(S * .10))
        d.text((S / 2, S * .88), sub, font=f3, fill=RED + (255,), anchor="mm")
    return _fin(im, s)


@lru_cache(maxsize=None)
def icon_pin(s=200):
    im = _canvas(s)
    d = ImageDraw.Draw(im)
    S = s * 2
    d.polygon([(S * .2, S * .45), (S * .8, S * .45), (S * .5, S * .98)], fill=GOLD + (255,))
    d.ellipse([S * .14, S * .04, S * .86, S * .76], fill=GOLD + (255,), outline=(255, 240, 180, 255), width=S // 50)
    d.ellipse([S * .33, S * .23, S * .67, S * .57], fill=EMERALD + (255,))
    return _fin(im, s)


@lru_cache(maxsize=None)
def icon_bolt(s=150):
    im = _canvas(s)
    d = ImageDraw.Draw(im)
    S = s * 2
    d.polygon([(S * .58, S * .02), (S * .18, S * .56), (S * .46, S * .56), (S * .36, S * .98), (S * .82, S * .4), (S * .52, S * .4)], fill=YELLOW + (255,), outline=(120, 70, 0, 255))
    return _fin(im, s)


def _person(d, cx, top, h, col):
    r = h * .17
    d.ellipse([cx - r, top, cx + r, top + 2 * r], fill=col)
    d.rounded_rectangle([cx - h * .27, top + 2.25 * r, cx + h * .27, top + h], h * .16, fill=col)


@lru_cache(maxsize=None)
def icon_people(s=150, n=2, sizes=None):
    im = _canvas(s)
    d = ImageDraw.Draw(im)
    S = s * 2
    sizes = sizes or (1.0,) * n
    xs = np.linspace(S * .25, S * .75, n) if n > 1 else [S / 2]
    cols = [WHITE + (255,), GOLD_L + (255,), (200, 240, 215, 255)]
    for i, (x, k) in enumerate(zip(xs, sizes)):
        h = S * .8 * k
        _person(d, x, S * .95 - h, h, cols[i % 3])
    return _fin(im, s)


@lru_cache(maxsize=None)
def icon_heart(s=150):
    im = _canvas(s)
    d = ImageDraw.Draw(im)
    S = s * 2
    d.ellipse([S * .08, S * .14, S * .54, S * .6], fill=(255, 92, 92, 255))
    d.ellipse([S * .46, S * .14, S * .92, S * .6], fill=(255, 92, 92, 255))
    d.polygon([(S * .11, S * .48), (S * .89, S * .48), (S * .5, S * .92)], fill=(255, 92, 92, 255))
    d.ellipse([S * .2, S * .22, S * .34, S * .34], fill=(255, 210, 210, 255))
    return _fin(im, s)


@lru_cache(maxsize=None)
def icon_alert(s=160):
    im = _canvas(s)
    d = ImageDraw.Draw(im)
    S = s * 2
    d.polygon([(S * .5, S * .05), (S * .97, S * .92), (S * .03, S * .92)], fill=YELLOW + (255,), outline=(120, 70, 0, 255))
    d.rounded_rectangle([S * .45, S * .3, S * .55, S * .66], S * .03, fill=(30, 20, 0, 255))
    d.ellipse([S * .44, S * .72, S * .56, S * .84], fill=(30, 20, 0, 255))
    return _fin(im, s)


def icon_clock(s, ang_min, ang_hr):
    im = _canvas(s)
    d = ImageDraw.Draw(im)
    S = s * 2
    c = S / 2
    d.ellipse([S * .04, S * .04, S * .96, S * .96], fill=(255, 255, 255, 255), outline=GOLD + (255,), width=S // 22)
    for k in range(12):
        a = k * math.pi / 6
        r1, r2 = S * .38, S * (.32 if k % 3 == 0 else .35)
        d.line([c + r1 * math.sin(a), c - r1 * math.cos(a), c + r2 * math.sin(a), c - r2 * math.cos(a)], fill=EMERALD_D + (255,), width=S // 40)
    for ang, ln, wd, col in ((ang_hr, .22, S // 22, EMERALD_D), (ang_min, .33, S // 34, RED)):
        d.line([c, c, c + S * ln * math.sin(ang), c - S * ln * math.cos(ang)], fill=col + (255,), width=wd)
    d.ellipse([c - S * .04, c - S * .04, c + S * .04, c + S * .04], fill=RED + (255,))
    return _fin(im, s)


def icon_phone(w, h, prog):
    """Telefon dengan borang digital generik; prog 0..1 mengisi medan & tekan HANTAR."""
    S = 2
    im = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    W2, H2 = w * S, h * S
    d.rounded_rectangle([0, 0, W2 - 1, H2 - 1], 60 * S, fill=(18, 22, 20, 255), outline=GOLD + (255,), width=4 * S)
    m = 18 * S
    d.rounded_rectangle([m, m, W2 - m, H2 - m], 44 * S, fill=(245, 247, 246, 255))
    d.rounded_rectangle([W2 * .38, m + 10 * S, W2 * .62, m + 26 * S], 8 * S, fill=(18, 22, 20, 255))
    # header borang
    d.rectangle([m, m + 60 * S, W2 - m, m + 180 * S], fill=EMERALD + (255,))
    d.text((W2 / 2, m + 100 * S), "BORANG PENDAFTARAN", font=font(F_BLACK, 26 * S), fill=WHITE + (255,), anchor="mm")
    d.text((W2 / 2, m + 145 * S), "Briskwalk Masjid Bersama Gen Z 2026", font=font(F_BOLD, 18 * S), fill=GOLD_L + (255,), anchor="mm")
    labels = ["Nama", "No. Telefon", "Umur", "Kategori"]
    y = m + 220 * S
    for i, lb in enumerate(labels):
        d.text((m + 30 * S, y), lb, font=font(F_BOLD, 22 * S), fill=(60, 70, 64, 255))
        fy = y + 36 * S
        d.rounded_rectangle([m + 30 * S, fy, W2 - m - 30 * S, fy + 56 * S], 12 * S, fill=WHITE + (255,), outline=(190, 200, 194, 255), width=2 * S)
        fill_p = clamp(prog * 5 - i)
        if fill_p > 0:
            d.rounded_rectangle([m + 44 * S, fy + 22 * S, m + 44 * S + (W2 - 2 * m - 90 * S) * fill_p * .7, fy + 34 * S], 6 * S, fill=(150, 170, 160, 255))
        y += 112 * S
    bp = clamp(prog * 5 - 4)
    bc = EMERALD if bp < .5 else (20, 160, 90)
    by = y + 20 * S
    d.rounded_rectangle([m + 30 * S, by, W2 - m - 30 * S, by + 80 * S], 40 * S, fill=bc + (255,))
    d.text((W2 / 2, by + 40 * S), "HANTAR ✓" if bp >= .5 else "HANTAR", font=font(F_BLACK, 30 * S), fill=WHITE + (255,), anchor="mm")
    return im.resize((w, h), Image.LANCZOS)


@lru_cache(maxsize=None)
def icon_counter(s=520):
    im = _canvas(s)
    d = ImageDraw.Draw(im)
    S = s * 2
    _person(d, S * .5, S * .12, S * .5, WHITE + (255,))
    d.rounded_rectangle([S * .08, S * .55, S * .92, S * .95], S * .04, fill=(250, 250, 245, 255), outline=GOLD + (255,), width=S // 60)
    d.rectangle([S * .08, S * .55, S * .92, S * .66], fill=EMERALD + (255,))
    d.text((S * .5, S * .78), "KAUNTER", font=font(F_BLACK, int(S * .1)), fill=EMERALD_D + (255,), anchor="mm")
    d.text((S * .5, S * .885), "PENDAFTARAN", font=font(F_BLACK, int(S * .055)), fill=(120, 90, 0, 255), anchor="mm")
    return _fin(im, s)


# ------------------------------------------------------------------ efek
def sweep(sprite, p, width=0.12, strength=210):
    """Light sweep pepenjuru merentasi sprite, p 0..1."""
    a = np.asarray(sprite).astype(np.float32)
    h, w = a.shape[:2]
    xs = np.arange(w)[None, :] / w
    ys = np.arange(h)[:, None] / h
    pos = -0.3 + p * 1.6
    band = np.exp(-(((xs + ys * 0.35) - pos) / width) ** 2)
    a[..., :3] = np.minimum(255, a[..., :3] + band[..., None] * strength * (a[..., 3:4] / 255))
    return Image.fromarray(a.astype(np.uint8), "RGBA")


def with_alpha(sprite, alpha):
    if alpha >= 0.999:
        return sprite
    a = np.asarray(sprite).copy()
    a[..., 3] = (a[..., 3].astype(np.float32) * clamp(alpha)).astype(np.uint8)
    return Image.fromarray(a, "RGBA")


def scaled(sprite, sc):
    if abs(sc - 1) < 1e-3:
        return sprite
    w, h = max(1, int(sprite.width * sc)), max(1, int(sprite.height * sc))
    return sprite.resize((w, h), Image.BILINEAR)


def place(canvas, sprite, cx, cy, sc=1.0, alpha=1.0, rot=0.0):
    if alpha <= 0.01 or sc <= 0.01:
        return
    sp = scaled(sprite, sc)
    if rot:
        sp = sp.rotate(rot, Image.BILINEAR, expand=True)
    sp = with_alpha(sp, alpha)
    canvas.alpha_composite(sp, (int(cx - sp.width / 2), int(cy - sp.height / 2))) if _inside(canvas, sp, cx, cy) else _safe_paste(canvas, sp, cx, cy)


def _inside(canvas, sp, cx, cy):
    x, y = int(cx - sp.width / 2), int(cy - sp.height / 2)
    return x >= 0 and y >= 0 and x + sp.width <= canvas.width and y + sp.height <= canvas.height


def _safe_paste(canvas, sp, cx, cy):
    x, y = int(cx - sp.width / 2), int(cy - sp.height / 2)
    x0, y0 = max(0, -x), max(0, -y)
    x1, y1 = min(sp.width, canvas.width - x), min(sp.height, canvas.height - y)
    if x1 <= x0 or y1 <= y0:
        return
    canvas.alpha_composite(sp.crop((x0, y0, x1, y1)), (x + x0, y + y0))


def anim(t, t_in, t_out=None, style="pop", dur=0.28, out_dur=0.2):
    """Pulang (scale, alpha, dx, dy) untuk animasi masuk/keluar."""
    if t < t_in or (t_out is not None and t >= t_out + out_dur):
        return 0, 0, 0, 0
    p = (t - t_in) / dur
    if style == "pop":
        sc, al, dx, dy = 0.3 + 0.7 * ease_out_back(p), clamp(p * 2), 0, 0
    elif style == "slam":
        sc, al, dx, dy = 1 + 1.8 * (1 - ease_out_cubic(p * 1.6)), clamp(p * 3), 0, 0
    elif style == "left":
        sc, al, dx, dy = 1, clamp(p * 2), -900 * (1 - ease_out_cubic(p)), 0
    elif style == "right":
        sc, al, dx, dy = 1, clamp(p * 2), 900 * (1 - ease_out_cubic(p)), 0
    elif style == "up":
        sc, al, dx, dy = 1, clamp(p * 2), 0, 160 * (1 - ease_out_cubic(p))
    elif style == "drop":
        sc, al, dx, dy = 1, clamp(p * 3), 0, -700 * (1 - ease_out_back(p, 1.4))
    else:
        sc, al, dx, dy = 1, clamp(p), 0, 0
    if t_out is not None and t >= t_out:
        q = (t - t_out) / out_dur
        sc *= 1 + 0.35 * ease_in_cubic(q)
        al *= 1 - clamp(q)
    return sc, al, dx, dy


class Particles:
    def __init__(self, n=70, seed=7):
        r = np.random.default_rng(seed)
        self.x = r.uniform(0, W, n)
        self.y = r.uniform(0, H, n)
        self.v = r.uniform(30, 160, n)
        self.s = r.integers(0, 4, n)
        self.ph = r.uniform(0, 6.28, n)
        self.sprites = []
        for sz in (10, 16, 26, 44):
            im = Image.new("RGBA", (sz * 3, sz * 3), (0, 0, 0, 0))
            d = ImageDraw.Draw(im)
            d.ellipse([sz, sz, sz * 2, sz * 2], fill=(255, 220, 120, 255))
            im = im.filter(ImageFilter.GaussianBlur(sz / 2.2))
            d = ImageDraw.Draw(im)
            d.ellipse([sz * 1.3, sz * 1.3, sz * 1.7, sz * 1.7], fill=(255, 250, 220, 255))
            self.sprites.append(im)

    def draw(self, canvas, t, intensity=1.0, burst=0.0):
        for i in range(len(self.x)):
            y = (self.y[i] - self.v[i] * t) % (H + 100) - 50
            x = self.x[i] + 30 * math.sin(t * 0.8 + self.ph[i])
            if burst > 0:
                dx, dy = x - W / 2, y - H * 0.42
                x += dx * burst * 0.8
                y += dy * burst * 0.8
            a = intensity * (0.55 + 0.45 * math.sin(t * 3 + self.ph[i]))
            place(canvas, self.sprites[self.s[i]], x, y, 1.0, a)
