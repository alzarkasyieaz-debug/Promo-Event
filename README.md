# Promo Video — BRISKWALK MASJID BERSAMA GEN Z 2026

Video promosi 9:16 (1080×1920, 30 fps, 74.5 s) untuk program anjuran Masjid As-Siddiq Seri Iskandar.

- `output/BRISKWALK_GenZ2026_Promo_9x16_noVO.mp4` — master (muzik + SFX, ruang untuk VO sebenar)
- `output/BRISKWALK_GenZ2026_Promo_9x16_guideVO.mp4` — dengan VO panduan TTS (draf timing)
- `output/subtitles_BM.srt`, `output/qr_pendaftaran.png`, `output/stems/`
- `docs/PAKEJ_SUNTINGAN.md` — skrip VO, timeline, subtitle, B-roll, prompt AI, SFX, muzik, arahan CapCut/Premiere
- `assets/poster_rasmi.jpg` — sumber fakta & visual
- `src/` — kod penjanaan (audio sintetik asli + render motion graphics)

## Bina semula
```bash
# perlu footage/drive_video.mp4 (video Drive, tidak di-commit kerana >100 MB)
cd src && python3 build_audio.py && python3 prep_clip.py && python3 render_video.py && cd ..
for v in guideVO noVO; do
  ffmpeg -y -i build/video_silent.mp4 -i build/mix_$v.wav -map 0:v -map 1:a -c:v copy \
    -af "loudnorm=I=-14:TP=-1.0:LRA=11" -ar 48000 -c:a aac -b:a 256k -shortest -movflags +faststart \
    output/BRISKWALK_GenZ2026_Promo_9x16_$v.mp4
done
```
