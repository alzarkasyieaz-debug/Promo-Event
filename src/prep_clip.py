"""Sediakan frame rakaman sebenar (ucapan YB Ustaz Ismi) untuk scene 4.

- Ambil segmen CLIP["segments"] daripada footage/drive_video.mp4 (464x832, 30 fps), disambung jump-cut
- Segmentasi orang (rembg u2net_human_seg): latar belakang dikaburkan + tint emerald,
  supaya poster lama (yuran/hadiah/jarak yang TIADA dalam poster rasmi) tidak terbaca
- Upscale ke 1080x1920, sharpen ringan, grade hangat sedikit
Output: build/clip/00000.jpg ...
"""
import glob, os, shutil, subprocess

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
from rembg import new_session, remove

from config import BUILD, CLIP, ROOT, W, H

RAW = os.path.join(BUILD, "clip_raw")
OUTD = os.path.join(BUILD, "clip")
for d in (RAW, OUTD):
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)

files = []
for k, (a, b) in enumerate(CLIP["segments"]):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(a), "-to", str(b),
                    "-i", os.path.join(ROOT, CLIP["src"]), "-vf", "fps=30", os.path.join(RAW, f"s{k}_%05d.png")], check=True)
    files += sorted(glob.glob(os.path.join(RAW, f"s{k}_*.png")))

sess = new_session("u2net_human_seg")
tint = None
prev = None
for i, f in enumerate(files):
    im = Image.open(f).convert("RGB")
    m = np.asarray(remove(im, session=sess, only_mask=True).convert("L")).astype(np.float32)
    # lancarkan topeng antara frame (kurang berkelip), kecuali pada jump cut
    if prev is not None and m.shape == prev.shape and np.abs(m - prev).mean() < 25:
        m = 0.6 * m + 0.4 * prev
    prev = m
    mask = Image.fromarray(m.astype(np.uint8)).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(2))
    if tint is None:
        tint = Image.new("RGB", im.size, (6, 60, 40))
    bg = Image.blend(im.filter(ImageFilter.GaussianBlur(24)), tint, 0.45)
    im = Image.composite(im, bg, mask)
    sc = W / im.width
    big = im.resize((W, int(im.height * sc)), Image.LANCZOS)
    y0 = (big.height - H) // 2
    big = big.crop((0, y0, W, y0 + H))
    big = big.filter(ImageFilter.UnsharpMask(radius=2.2, percent=70, threshold=2))
    big = ImageEnhance.Contrast(big).enhance(1.06)
    big = ImageEnhance.Color(big).enhance(1.08)
    arr = np.asarray(big).astype(np.float32)
    arr[..., 0] *= 1.03
    arr[..., 2] *= 0.97
    Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).save(os.path.join(OUTD, f"{i:05d}.jpg"), quality=94)
print(len(files), "frames")
