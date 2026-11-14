"""Sediakan frame rakaman sebenar (petikan jemputan ustaz) untuk scene 4.

- Potong src_start..src_end daripada footage/drive_video.mp4 (464x832, 30 fps)
- Kaburkan poster lama di latar belakang (yuran/hadiah/jarak yang TIADA dalam poster rasmi)
- Upscale ke 1080x1920, sharpen ringan, grade hangat sedikit
Output: build/clip/00000.jpg ...
"""
import glob, os, subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

from config import BUILD, CLIP, ROOT, W, H

RAW = os.path.join(BUILD, "clip_raw")
OUTD = os.path.join(BUILD, "clip")
os.makedirs(RAW, exist_ok=True)
os.makedirs(OUTD, exist_ok=True)

subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(CLIP["src_start"]), "-to", str(CLIP["src_end"]),
                "-i", os.path.join(ROOT, CLIP["src"]), "-vf", "fps=30", os.path.join(RAW, "%05d.png")], check=True)

# Poligon kawasan poster lama (koordinat sumber 464x832), di kanan kepala & bahu.
POLY = [(286, 70), (464, 70), (464, 680), (418, 680), (420, 600), (410, 515), (390, 448), (362, 398), (334, 376), (298, 356), (286, 330)]
mask = Image.new("L", (464, 832), 0)
ImageDraw.Draw(mask).polygon(POLY, fill=255)
mask = mask.filter(ImageFilter.GaussianBlur(6))
tint = Image.new("RGB", (464, 832), (6, 60, 40))

files = sorted(glob.glob(os.path.join(RAW, "*.png")))
for i, f in enumerate(files):
    im = Image.open(f).convert("RGB")
    bl = im.filter(ImageFilter.GaussianBlur(22))
    bl = Image.blend(bl, tint, 0.45)
    im = Image.composite(bl, im, mask)
    sc = W / im.width
    big = im.resize((W, int(im.height * sc)), Image.LANCZOS)
    y0 = (big.height - H) // 2
    big = big.crop((0, y0, W, y0 + H))
    big = big.filter(ImageFilter.UnsharpMask(radius=2.2, percent=70, threshold=2))
    big = ImageEnhance.Contrast(big).enhance(1.06)
    big = ImageEnhance.Color(big).enhance(1.08)
    a = np.asarray(big).astype(np.float32)
    a[..., 0] *= 1.03
    a[..., 2] *= 0.97
    Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(os.path.join(OUTD, f"{i:05d}.jpg"), quality=94)
print(len(files), "frames")
