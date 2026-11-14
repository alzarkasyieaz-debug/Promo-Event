"""KONSEP 2 — elemen vector animasi (tiada imej poster)."""
import math
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from config2 import W, H
from gfx import (clamp, ease_out_cubic, ease_in_cubic, ease_in_out, ease_out_back, vgrad, place, with_alpha,
                 EMERALD, EMERALD_D, GOLD, GOLD_L, YELLOW, WHITE, RED)

TEAL = (40, 220, 160)
NEON_G = (70, 255, 170)


# ------------------------------------------------------------------ latar
@lru_cache(maxsize=None)
def base_grad(kind="emerald"):
    if kind == "red":
        stops = [(60, 6, 10), (24, 4, 8), (8, 4, 6)]
    else:
        stops = [(6, 52, 34), (3, 26, 18), (1, 10, 8)]
    im = Image.fromarray(vgrad(W // 2, H // 2, stops)).convert("RGBA")
    yy, xx = np.mgrid[0:H // 2, 0:W // 2]
    r = np.hypot((xx - W / 4) / (W / 4), (yy - H / 5) / (H / 3))
    a = np.clip(1 - r, 0, 1) ** 1.6
    lay = np.zeros((H // 2, W // 2, 4), np.uint8)
    col = (40, 170, 110) if kind != "red" else (200, 40, 40)
    lay[..., 0], lay[..., 1], lay[..., 2] = col
    lay[..., 3] = (a * 110).astype(np.uint8)
    im.alpha_composite(Image.fromarray(lay, "RGBA"))
    return im


@lru_cache(maxsize=None)
def star_lattice():
    """Corak bintang 8 penjuru (geometri Islamik) — garisan emas nipis, separuh resolusi."""
    S = 1500
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    step = 150
    for gy in range(-1, S // step + 2):
        for gx in range(-1, S // step + 2):
            cx, cy = gx * step, gy * step
            r = step * 0.42
            for rot in (0, math.pi / 4):
                pts = [(cx + r * math.cos(rot + k * math.pi / 2), cy + r * math.sin(rot + k * math.pi / 2)) for k in range(4)]
                d.polygon(pts, outline=(255, 205, 80, 120))
            r2 = step * 0.2
            pts = [(cx + r2 * math.cos(k * math.pi / 4 + math.pi / 8), cy + r2 * math.sin(k * math.pi / 4 + math.pi / 8)) for k in range(8)]
            d.polygon(pts, outline=(120, 255, 190, 90))
            d.line([cx + r, cy, cx + step - r, cy], fill=(255, 205, 80, 70))
            d.line([cx, cy + r, cx, cy + step - r], fill=(255, 205, 80, 70))
    return im


def lattice_layer(t, alpha=0.5, speed=3.0, zoom=1.0):
    L = star_lattice()
    r = L.rotate(t * speed, Image.BILINEAR)
    z = zoom * (1 + 0.05 * math.sin(t * 0.4))
    cw, ch = int(W / 2 / z), int(H / 2 / z)
    x0, y0 = (r.width - cw) // 2, (r.height - ch) // 2
    c = r.crop((x0, y0, x0 + cw, y0 + ch)).resize((W // 2, H // 2), Image.BILINEAR)
    return with_alpha(c, alpha)


@lru_cache(maxsize=None)
def blob(col, size):
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    yy, xx = np.mgrid[0:size, 0:size]
    r = np.hypot(xx - size / 2, yy - size / 2) / (size / 2)
    a = np.clip(1 - r, 0, 1) ** 2 * 160
    arr = np.zeros((size, size, 4), np.uint8)
    arr[..., :3] = col
    arr[..., 3] = a.astype(np.uint8)
    return Image.fromarray(arr, "RGBA")


def light_leaks(c, t, strength=1.0):
    for k, (col, sz, ax, ay, sp) in enumerate([(GOLD, 520, 0.2, 0.25, 0.23), (TEAL, 600, 0.85, 0.6, 0.17), ((255, 140, 40), 420, 0.5, 0.9, 0.29)]):
        x = W / 2 * (ax + 0.25 * math.sin(t * sp * 2 + k)) * 1
        y = H / 2 * (ay + 0.15 * math.cos(t * sp * 1.6 + k * 2))
        place(c, blob(col, sz), x, y, 1, 0.55 * strength)


def vbg(t, kind="emerald", lattice=0.45, leaks=1.0, lat_speed=3.0, lat_zoom=1.0):
    """Latar vector separuh resolusi -> diskala ke penuh."""
    c = base_grad(kind).copy()
    if leaks:
        light_leaks(c, t, leaks)
    if lattice:
        c.alpha_composite(lattice_layer(t, lattice, lat_speed, lat_zoom))
    return c.resize((W, H), Image.BILINEAR)


# ------------------------------------------------------------------ piktogram pejalan
def _seg(d, p0, p1, wdt, col):
    d.line([p0, p1], fill=col, width=int(wdt))
    r = wdt / 2
    d.ellipse([p1[0] - r, p1[1] - r, p1[0] + r, p1[1] + r], fill=col)
    d.ellipse([p0[0] - r, p0[1] - r, p0[0] + r, p0[1] + r], fill=col)


def draw_walker(d, x, y, h, phase, kind="youth", col=(255, 255, 255, 255), back=None, facing=1):
    """Pejalan brisk-walk gaya piktogram. (x,y)=titik tapak kaki; h=tinggi; facing 1=kanan, -1=kiri."""
    if kind == "kid":
        h *= 0.68
    back = back or tuple(int(v * 0.62) for v in col[:3]) + (col[3],)
    f = facing
    ph = 2 * math.pi * phase
    lw = h * 0.085
    bob = -abs(math.sin(ph)) * h * 0.015
    hip = (x, y - h * 0.47 + bob)
    sh = (x + f * h * 0.035, y - h * 0.77 + bob)
    hr = h * (0.1 if kind == "kid" else 0.082)
    head = (x + f * h * 0.055, y - h * 0.87 + bob)

    def leg(off, c):
        a = math.radians(26) * math.sin(ph + off)
        kb = math.radians(34) * max(0, math.sin(ph + off + math.pi / 2))
        k = (hip[0] + f * h * 0.245 * math.sin(a), hip[1] + h * 0.245 * math.cos(a))
        a2 = a - kb
        ft = (k[0] + f * h * 0.235 * math.sin(a2), k[1] + h * 0.235 * math.cos(a2))
        _seg(d, hip, k, lw, c)
        _seg(d, k, ft, lw, c)
        d.line([ft, (ft[0] + f * h * 0.06, ft[1])], fill=c, width=int(lw * 0.9))

    def arm(off, c):
        a = -math.radians(38) * math.sin(ph + off)
        el = (sh[0] + f * h * 0.16 * math.sin(a), sh[1] + h * 0.16 * math.cos(a))
        a2 = a + math.radians(85)
        hd = (el[0] + f * h * 0.15 * math.sin(a2), el[1] + h * 0.15 * math.cos(a2))
        _seg(d, sh, el, lw * 0.9, c)
        _seg(d, el, hd, lw * 0.85, c)

    leg(math.pi, back)
    arm(0, back)
    _seg(d, hip, sh, lw * 1.9, col)
    leg(0, col)
    if kind == "hijab":
        d.polygon([(head[0] - hr * 1.35, head[1]), (head[0] + hr * 1.35, head[1]),
                   (sh[0] + h * 0.09, sh[1] + h * 0.07), (sh[0] - h * 0.09, sh[1] + h * 0.07)], fill=col)
        d.ellipse([head[0] - hr * 1.3, head[1] - hr * 1.3, head[0] + hr * 1.3, head[1] + hr * 1.25], fill=col)
    else:
        d.ellipse([head[0] - hr, head[1] - hr, head[0] + hr, head[1] + hr], fill=col)
        if kind == "elder":
            d.rounded_rectangle([head[0] - hr * 0.9, head[1] - hr * 1.3, head[0] + hr * 0.9, head[1] - hr * 0.6], hr * 0.2, fill=back)
    arm(math.pi, col)


def walkers_layer(specs, glow=True, scale=1.0):
    """specs: [(x, y, h, phase, kind, rgba, facing)] -> RGBA penuh dengan glow."""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for x, y, h, ph, kind, col, fc in specs:
        draw_walker(d, x, y, h, ph, kind, col, None, fc)
    if glow:
        g = lay.resize((W // 4, H // 4), Image.BILINEAR).filter(ImageFilter.GaussianBlur(6)).resize((W, H), Image.BILINEAR)
        out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        out.alpha_composite(g)
        out.alpha_composite(g)
        out.alpha_composite(lay)
        return out
    return lay


GEN_KINDS = ["youth", "hijab", "elder", "kid", "youth", "hijab"]
GEN_COLS = [(255, 255, 255, 255), (255, 214, 90, 255), (120, 255, 190, 255), (255, 240, 200, 255)]


# ------------------------------------------------------------------ siluet masjid (vector generik)
@lru_cache(maxsize=None)
def skyline_path(x0=60, x1=1020, base=1240):
    pts = [(x0, base)]

    def dome(cx, w, hgt, n=24):
        out = []
        for k in range(n + 1):
            a = math.pi * k / n
            px = cx - w / 2 * math.cos(a)
            py = base - hgt * 0.35 - (hgt * 0.65) * math.sin(a) ** 0.8
            if k == n // 2:
                out += [(cx - 4, py), (cx, py - 46), (cx + 4, py)]
            else:
                out.append((px, py))
        return out

    def minaret(cx, w, hgt):
        return [(cx - w / 2, base), (cx - w / 2, base - hgt), (cx, base - hgt - 70), (cx + w / 2, base - hgt), (cx + w / 2, base)]

    pts += [(140, base), (140, base - 120)]
    pts += dome(220, 160, 170)[0:]
    pts += [(300, base - 120), (300, base)]
    pts += minaret(360, 44, 330)
    pts += [(400, base), (400, base - 150)]
    pts += dome(540, 280, 300)
    pts += [(680, base - 150), (680, base)]
    pts += minaret(730, 44, 330)
    pts += [(770, base), (770, base - 110)]
    pts += dome(850, 160, 160)
    pts += [(930, base - 110), (930, base), (x1, base)]
    return pts


def draw_path_progress(d, pts, p, col, wdt):
    segs = list(zip(pts[:-1], pts[1:]))
    lens = [math.dist(a, b) for a, b in segs]
    tot = sum(lens) * clamp(p)
    acc = 0
    for (a, b), l in zip(segs, lens):
        if acc + l <= tot:
            d.line([a, b], fill=col, width=wdt)
        else:
            r = (tot - acc) / l if l else 0
            if r > 0:
                d.line([a, (a[0] + (b[0] - a[0]) * r, a[1] + (b[1] - a[1]) * r)], fill=col, width=wdt)
            return (a[0] + (b[0] - a[0]) * r, a[1] + (b[1] - a[1]) * r)
        acc += l
    return pts[-1]


def neon_path(pts, p, col=(255, 210, 80), wdt=6, dy=0, glow=True):
    pts = [(x, y + dy) for x, y in pts]
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    tip = draw_path_progress(d, pts, p, col + (255,), wdt)
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if glow:
        g = lay.resize((W // 4, H // 4), Image.BILINEAR).filter(ImageFilter.GaussianBlur(5)).resize((W, H), Image.BILINEAR)
        out.alpha_composite(g)
        out.alpha_composite(g)
    out.alpha_composite(lay)
    if p < 1:
        place(out, spark(), tip[0], tip[1], 1, 1)
    return out


@lru_cache(maxsize=None)
def spark(s=90):
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([s * .35, s * .35, s * .65, s * .65], fill=(255, 250, 220, 255))
    im = im.filter(ImageFilter.GaussianBlur(s / 10))
    d = ImageDraw.Draw(im)
    d.ellipse([s * .44, s * .44, s * .56, s * .56], fill=(255, 255, 255, 255))
    return im


# ------------------------------------------------------------------ laluan briskwalk
@lru_cache(maxsize=None)
def route_pts():
    pts = []
    for k in range(120):
        u = k / 119
        x = 160 + 760 * u + 120 * math.sin(u * 7)
        y = 1100 - 700 * u + 90 * math.sin(u * 11 + 1)
        pts.append((x, y))
    return pts


def route_layer(p):
    pts = route_pts()
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    n = int(len(pts) * clamp(p))
    for k in range(0, max(0, n - 1), 2):
        d.line([pts[k], pts[k + 1]], fill=(255, 214, 90, 255), width=10)
    if n > 1:
        x, y = pts[n - 1]
        d.ellipse([x - 16, y - 16, x + 16, y + 16], fill=(255, 255, 255, 255))
    g = lay.resize((W // 4, H // 4), Image.BILINEAR).filter(ImageFilter.GaussianBlur(4)).resize((W, H), Image.BILINEAR)
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    out.alpha_composite(g)
    out.alpha_composite(lay)
    return out


# ------------------------------------------------------------------ efek
def shockwave(c, t, t0, cx, cy, col=(255, 220, 120), maxr=900, dur=0.6, wdt=14):
    p = (t - t0) / dur
    if not 0 <= p <= 1:
        return
    lay = Image.new("RGBA", (W // 2, H // 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    r = maxr * ease_out_cubic(p) / 2
    a = int(230 * (1 - p))
    d.ellipse([cx / 2 - r, cy / 2 - r, cx / 2 + r, cy / 2 + r], outline=col + (a,), width=max(1, int(wdt * (1 - p))))
    c.alpha_composite(lay.resize((W, H), Image.BILINEAR))


def streaks(c, t, strength=1.0, seed=5, vertical=False):
    lay = Image.new("RGBA", (W // 2, H // 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    r = np.random.default_rng(seed)
    for k in range(40):
        x = r.uniform(0, W / 2)
        sp = r.uniform(400, 1100)
        ln = r.uniform(60, 240)
        y = (r.uniform(0, H / 2) + t * sp) % (H / 2 + 300) - 150
        col = (255, 220, 120) if k % 3 else (120, 255, 190)
        if vertical:
            d.line([x, y, x, y - ln], fill=col + (int(150 * strength),), width=2)
        else:
            d.line([y * 0.56, x * 1.77 % (H / 2), y * 0.56 - ln, x * 1.77 % (H / 2)], fill=col + (int(150 * strength),), width=2)
    c.alpha_composite(lay.resize((W, H), Image.BILINEAR))


def stripe_wipe(img, p):
    """Transisi jalur pepenjuru emas/emerald/putih. p: -1..1 (0 = tutup penuh)."""
    if abs(p) >= 1:
        return img
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    cols = [(244, 180, 0), (11, 93, 59), (255, 255, 255), (4, 40, 28), (255, 214, 90)]
    for k, col in enumerate(cols):
        off = (p * 1.0 + (k - 2) * 0.06) * (W + H)
        bw = (W + H) / len(cols) * 1.25
        x0 = off + k * bw * 0.8 - bw * 2
        d.polygon([(x0, H), (x0 + bw, H), (x0 + bw + H * 0.6, 0), (x0 + H * 0.6, 0)], fill=col + (255,))
    out = img.copy()
    out.alpha_composite(lay)
    return out


def glitch(img, amt, seed=0):
    if amt <= 0:
        return img
    a = np.asarray(img).copy()
    r = np.random.default_rng(seed)
    for _ in range(int(6 * amt) + 1):
        y = r.integers(0, H - 80)
        hgt = r.integers(10, 80)
        sh = int(r.integers(-60, 60) * amt)
        a[y:y + hgt] = np.roll(a[y:y + hgt], sh, axis=1)
    a[..., 0] = np.roll(a[..., 0], int(8 * amt), axis=1)
    a[..., 2] = np.roll(a[..., 2], -int(8 * amt), axis=1)
    return Image.fromarray(a, "RGBA")


def rim_light(cut, col=(255, 210, 90), strength=1.0):
    """Cahaya rim pada tepi cutout + glow luar."""
    a = cut.getchannel("A")
    er = a.filter(ImageFilter.MinFilter(9))
    edge = Image.fromarray(np.clip(np.asarray(a).astype(np.int16) - np.asarray(er).astype(np.int16), 0, 255).astype(np.uint8))
    out = Image.new("RGBA", cut.size, (0, 0, 0, 0))
    glow = Image.new("RGBA", cut.size, col + (0,))
    glow.putalpha(a.resize((W // 4, H // 4)).filter(ImageFilter.GaussianBlur(10)).resize(cut.size).point(lambda v: int(v * 0.55 * strength)))
    out.alpha_composite(glow)
    out.alpha_composite(cut)
    rl = Image.new("RGBA", cut.size, col + (0,))
    rl.putalpha(edge.point(lambda v: int(v * 0.8 * strength)))
    out.alpha_composite(rl)
    return out


@lru_cache(maxsize=None)
def ring_progress(size, p_q, col=(255, 214, 90), bg_col=(255, 255, 255, 40), wdt=26):
    p = p_q / 100
    S = size * 2
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([wdt, wdt, S - wdt, S - wdt], outline=bg_col, width=wdt * 2 // 2)
    d.arc([wdt, wdt, S - wdt, S - wdt], -90, -90 + 360 * p, fill=col + (255,), width=wdt)
    im = im.resize((size, size), Image.LANCZOS)
    g = im.filter(ImageFilter.GaussianBlur(8))
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    out.alpha_composite(g)
    out.alpha_composite(im)
    return out
