"""KONSEP 2: cutout RGBA YB Ustaz Ismi (latar dibuang sepenuhnya) untuk diletak atas latar vector.
Output: build2/cut{k}/00000.png (1080x1920 RGBA)"""
import glob, os, shutil, subprocess

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
from rembg import new_session, remove

from config2 import BUILD, CLIPS, SRC, W, H

sess = new_session("u2net_human_seg")
for k, cl in enumerate(CLIPS):
    raw = os.path.join(BUILD, f"raw{k}")
    out = os.path.join(BUILD, f"cut{k}")
    for d in (raw, out):
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(d)
    a, b = cl["seg"]
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(a), "-to", str(b), "-i", SRC,
                    "-vf", "fps=30", os.path.join(raw, "%05d.png")], check=True)
    prev = None
    for i, f in enumerate(sorted(glob.glob(os.path.join(raw, "*.png")))):
        im = Image.open(f).convert("RGB")
        m = np.asarray(remove(im, session=sess, only_mask=True).convert("L")).astype(np.float32)
        if prev is not None:
            m = 0.65 * m + 0.35 * prev
        prev = m
        sc = W / im.width
        size = (W, int(im.height * sc))
        y0 = (size[1] - H) // 2
        big = im.resize(size, Image.LANCZOS).crop((0, y0, W, y0 + H))
        big = big.filter(ImageFilter.UnsharpMask(radius=2.2, percent=70, threshold=2))
        big = ImageEnhance.Contrast(big).enhance(1.07)
        big = ImageEnhance.Color(big).enhance(1.08)
        mk = Image.fromarray(m.astype(np.uint8)).resize(size, Image.BILINEAR).crop((0, y0, W, y0 + H))
        mk = mk.point(lambda v: 0 if v < 40 else min(255, int((v - 40) * 1.4)))
        mk = mk.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.6))
        rgba = big.convert("RGBA")
        rgba.putalpha(mk)
        rgba.save(os.path.join(out, f"{i:05d}.png"), compress_level=1)
    print(k, i + 1, "frames")
