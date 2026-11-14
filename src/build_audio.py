"""Bina semua audio: muzik asli (sintesis, 132 BPM, bebas hak cipta), SFX,
VO panduan (TTS espeak-ng, lelaki BM), masa subtitle (SRT + JSON) dan mix akhir.

Output (dalam build/ dan output/):
  music.wav, sfx.wav, vo_guide.wav            - stem berasingan
  mix_guideVO.wav                             - muzik+SFX+VO panduan (ducking -10 dB)
  mix_noVO.wav                                - muzik+SFX, ruang VO (ducking -5 dB) untuk VO sebenar
  timing.json, subtitles_BM.srt
"""
import json, os, re, subprocess, wave
import numpy as np
from scipy.signal import butter, sosfilt

from config import (BEAT, BAR, SCENES, DURATION, VO, SUB_CHUNKS, BUILD, OUT)

SR = 44100
N = int(np.ceil((DURATION + 1.5) * SR))
rng = np.random.default_rng(2026)
os.makedirs(BUILD, exist_ok=True)
os.makedirs(OUT, exist_ok=True)


# ------------------------------------------------------------------ utils
def filt(x, kind, f, order=2):
    if kind == "bp":
        sos = butter(order, [f[0] / (SR / 2), f[1] / (SR / 2)], btype="band", output="sos")
    else:
        sos = butter(order, f / (SR / 2), btype=kind, output="sos")
    return sosfilt(sos, x)


def env_exp(n, tau):
    return np.exp(-np.arange(n) / (tau * SR))


def add(buf, sig, t, gain=1.0, pan=0.0):
    """Tambah isyarat mono/stereo ke buf stereo pada masa t (saat)."""
    i = int(round(t * SR))
    if i >= buf.shape[0] or i + len(sig) <= 0:
        return
    if sig.ndim == 1:
        l = np.cos((pan + 1) * np.pi / 4)
        r = np.sin((pan + 1) * np.pi / 4)
        sig = np.stack([sig * l * 1.414, sig * r * 1.414], 1)
    j = min(buf.shape[0], i + len(sig))
    s0 = max(0, -i)
    buf[max(i, 0):j] += sig[s0:j - i] * gain


def note_hz(n):  # MIDI -> Hz
    return 440.0 * 2 ** ((n - 69) / 12)


def saw(freq, n, phase=0.0):
    t = np.arange(n) / SR
    p = (freq * t + phase) % 1.0
    return 2 * p - 1


# ------------------------------------------------------------------ instrumen
def kick():
    n = int(0.45 * SR)
    t = np.arange(n) / SR
    f = 45 + 110 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) * env_exp(n, 0.16)
    click = filt(rng.standard_normal(n), "hp", 2500) * env_exp(n, 0.004) * 0.4
    return np.tanh((s + click) * 1.6) * 0.9


def clap():
    n = int(0.35 * SR)
    no = rng.standard_normal(n)
    e = np.zeros(n)
    for k, d in enumerate([0, 0.011, 0.022]):
        i = int(d * SR)
        e[i:] += env_exp(n - i, 0.006 if k < 2 else 0.09)
    return filt(no * e, "bp", (900, 3500)) * 0.9


def hat(open_=False):
    n = int((0.25 if open_ else 0.06) * SR)
    return filt(rng.standard_normal(n), "hp", 7000) * env_exp(n, 0.07 if open_ else 0.012) * 0.35


def supersaw(freq, n, voices=5, det=0.012):
    out = np.zeros(n)
    for v in range(voices):
        d = 1 + det * (v - (voices - 1) / 2) / ((voices - 1) / 2)
        out += saw(freq * d, n, rng.random())
    return out / voices


def stab(notes, dur, cutoff=2500):
    n = int(dur * SR)
    s = sum(supersaw(note_hz(m), n) for m in notes) / len(notes)
    a = np.minimum(1, np.arange(n) / (0.005 * SR))
    s = filt(s, "lp", cutoff) * a * env_exp(n, dur * 0.45)
    return s


def pad(notes, dur, cutoff=1400):
    n = int(dur * SR)
    s = sum(supersaw(note_hz(m), n, 7, 0.018) for m in notes) / len(notes)
    a = np.minimum(1, np.arange(n) / (0.25 * SR)) * np.minimum(1, (n - np.arange(n)) / (0.2 * SR))
    return filt(s, "lp", cutoff) * a


def bass_note(m, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = 0.6 * np.sin(2 * np.pi * note_hz(m) * t) + 0.4 * filt(saw(note_hz(m), n), "lp", 500)
    a = np.minimum(1, np.arange(n) / (0.004 * SR)) * np.minimum(1, (n - np.arange(n)) / (0.01 * SR))
    return s * a


def pluck(m, dur=0.3):
    n = int(dur * SR)
    s = filt(saw(note_hz(m), n) + 0.5 * saw(note_hz(m + 12), n), "lp", 3000) * env_exp(n, 0.09)
    return s


# ------------------------------------------------------------------ SFX
def boom(dur=2.2):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 30 + 70 * np.exp(-t * 6)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(n, 0.6)
    crash = filt(rng.standard_normal(n), "hp", 1500) * env_exp(n, 0.5) * 0.35
    thud = filt(rng.standard_normal(n), "lp", 300) * env_exp(n, 0.08) * 1.2
    return np.tanh((s + crash + thud) * 1.4)


def impact():
    n = int(1.0 * SR)
    t = np.arange(n) / SR
    f = 40 + 120 * np.exp(-t * 15)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(n, 0.25)
    nz = filt(rng.standard_normal(n), "bp", (200, 4000)) * env_exp(n, 0.12) * 0.6
    return np.tanh((s + nz) * 1.5) * 0.9


def whoosh(dur=0.55, up=True):
    n = int(dur * SR)
    no = rng.standard_normal(n)
    out = np.zeros(n)
    seg = 8
    for k in range(seg):
        a, b = k * n // seg, (k + 1) * n // seg
        fr = k / (seg - 1)
        fc = 400 + 3500 * (fr if up else 1 - fr)
        out[a:b] = filt(no[a:b + 0], "bp", (fc * 0.6, fc * 1.6))
    w = np.sin(np.pi * np.arange(n) / n) ** 2
    return out * w * 1.2


def riser(dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    no = rng.standard_normal(n)
    out = np.zeros(n)
    seg = 24
    for k in range(seg):
        a, b = k * n // seg, (k + 1) * n // seg
        fc = 300 * (20 ** (k / seg))
        out[a:b] = filt(no[a:b], "bp", (fc * 0.7, min(fc * 1.5, 18000)))
    f = 200 * (8 ** (t / dur))
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.25
    return (out * 0.8 + tone) * (t / dur) ** 2


def footstep():
    n = int(0.12 * SR)
    th = filt(rng.standard_normal(n), "lp", 180) * env_exp(n, 0.02) * 2.0
    gr = filt(rng.standard_normal(n), "bp", (1500, 6000)) * env_exp(n, 0.015) * 0.35
    return th + gr


def shutter():
    n = int(0.18 * SR)
    s = np.zeros(n)
    for d in (0.0, 0.07):
        i = int(d * SR)
        m = int(0.02 * SR)
        s[i:i + m] += filt(rng.standard_normal(m), "hp", 2000) * env_exp(m, 0.004)
    return s * 0.9


def tick():
    n = int(0.03 * SR)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * 3200 * t) * env_exp(n, 0.004) * 0.5


def cheer(dur=3.0):
    """Sorakan orang ramai sintetik (bukan rakaman)."""
    n = int(dur * SR)
    out = np.zeros((n, 2))
    for v in range(40):
        fc = rng.uniform(500, 1800)
        x = filt(rng.standard_normal(n), "bp", (fc * 0.8, fc * 1.25))
        am = 0.5 + 0.5 * np.sin(2 * np.pi * rng.uniform(3, 7) * np.arange(n) / SR + rng.random() * 6)
        p = rng.uniform(-0.8, 0.8)
        out[:, 0] += x * am * (1 - p) / 2
        out[:, 1] += x * am * (1 + p) / 2
    for c in range(60):  # tepukan
        i = int(rng.uniform(0, dur - 0.1) * SR)
        cl = clap()[: int(0.1 * SR)] * 0.25
        p = rng.uniform(-1, 1)
        out[i:i + len(cl), 0] += cl * (1 - p) / 2
        out[i:i + len(cl), 1] += cl * (1 + p) / 2
    e = np.minimum(1, np.arange(n) / (0.3 * SR)) * np.minimum(1, (n - np.arange(n)) / (1.0 * SR))
    out *= e[:, None]
    return out / np.abs(out).max() * 0.6


# ------------------------------------------------------------------ MUZIK
def build_music():
    mus = np.zeros((N, 2))
    sc = np.ones(N)  # sidechain envelope
    # I-V-vi-IV in C : C G Am F
    prog = [(48, [60, 64, 67, 72]), (43, [59, 62, 67, 71]), (45, [60, 64, 69, 72]), (41, [60, 65, 69, 72])]
    K, CL, HC, HO = kick(), clap(), hat(), hat(True)
    total_bars = int(round(DURATION / BAR))
    scene_of_bar = []
    for b in range(total_bars):
        t = b * BAR + 1e-6
        scene_of_bar.append(next(i for i, (a, z) in enumerate(SCENES) if a <= t < z))

    # profil tenaga setiap scene
    prof = {
        0: dict(kick=1, clap=1, hat=2, bass=1, stab=1, pad=0, arp=0, cut=3200),
        1: dict(kick=1, clap=1, hat=1, bass=1, stab=0, pad=1, arp=1, cut=2000),
        2: dict(kick=1, clap=1, hat=2, bass=1, stab=1, pad=1, arp=1, cut=4200),
        3: dict(kick=1, clap=1, hat=1, bass=1, stab=0, pad=1, arp=0, cut=1800),
        4: dict(kick=1, clap=0, hat=2, bass=2, stab=0, pad=1, arp=1, cut=1200),
        5: dict(kick=1, clap=1, hat=2, bass=1, stab=1, pad=0, arp=1, cut=3000),
        6: dict(kick=1, clap=1, hat=2, bass=1, stab=1, pad=1, arp=1, cut=5000),
    }
    arp_pat = [0, 2, 1, 3, 2, 1, 3, 2]
    for b in range(total_bars):
        s = scene_of_bar[b]
        p = prof[s]
        t0 = b * BAR
        root, ch = prog[b % 4]
        last_bar = b == total_bars - 1
        if last_bar:
            break
        for beat in range(4):
            tb = t0 + beat * BEAT
            # kick (four-on-the-floor); scene 4 (urgency) kick setengah masa di bar pertama
            if p["kick"]:
                add(mus, K, tb, 0.95)
                i = int(tb * SR)
                n = int(0.3 * SR)
                sc[i:i + n] = np.minimum(sc[i:i + n], 1 - 0.65 * np.exp(-np.arange(min(n, N - i)) / (0.08 * SR)))
            if p["clap"] and beat in (1, 3):
                add(mus, CL, tb, 0.55, 0.05)
            if p["hat"]:
                add(mus, HO if p["hat"] == 2 and beat % 2 == 1 else HC, tb + BEAT / 2, 0.55, 0.3)
                if p["hat"] == 2:
                    add(mus, HC, tb + BEAT / 4, 0.3, -0.3)
                    add(mus, HC, tb + 3 * BEAT / 4, 0.3, -0.3)
            # bass: off-beat 8th (gaya festival) atau 16th pulsing (scene urgency)
            if p["bass"] == 1:
                add(mus, bass_note(root, BEAT / 2 * 0.9), tb + BEAT / 2, 0.55)
            elif p["bass"] == 2:
                for q in range(4):
                    add(mus, bass_note(root, BEAT / 4 * 0.8), tb + q * BEAT / 4, 0.42)
            if p["stab"] and beat in (0, 2):
                add(mus, stab(ch, BEAT * 0.9, p["cut"]), tb + (BEAT / 2 if beat == 2 else 0), 0.30, -0.15)
                add(mus, stab([c + 12 for c in ch], BEAT * 0.6, p["cut"]), tb + BEAT * 1.5, 0.16, 0.2)
        if p["pad"]:
            add(mus, pad(ch, BAR, p["cut"]), t0, 0.22)
        if p["arp"]:
            for k in range(8):
                m = ch[arp_pat[k]] + 12
                add(mus, pluck(m, BEAT * 0.45), t0 + k * BEAT / 2, 0.13, 0.4 if k % 2 else -0.4)
    # akhir: chord besar + hit
    tend = SCENES[-1][1] - BAR
    add(mus, K, tend, 1.0)
    add(mus, pad([48, 55, 60, 64, 67, 72], 2.4, 3000), tend, 0.35)
    add(mus, stab([60, 64, 67, 72, 76], 1.4, 5000), tend, 0.45)
    add(mus, bass_note(36, 1.2) * env_exp(int(1.2 * SR), 0.5), tend, 0.7)
    mus *= sc[:, None]
    return mus


# ------------------------------------------------------------------ SFX timeline
def build_sfx():
    sfx = np.zeros((N, 2))
    S = SCENES
    # Scene 1 hook
    add(sfx, boom(), 0.0, 0.9)
    for k in range(8):                       # tapak kaki ikut beat
        add(sfx, footstep(), 0.2 + k * BEAT, 0.7, -0.3 if k % 2 else 0.3)
    add(sfx, whoosh(0.45), 1.6, 0.6, 0.6)
    add(sfx, impact(), 2 * BAR + 0.0 - 0.0, 0.7)   # "JOM BRISKWALK!"
    add(sfx, whoosh(0.4), 2 * BAR - 0.35, 0.6, -0.6)
    # transisi setiap scene: riser + whoosh + impact
    for i in range(1, len(S)):
        t = S[i][0]
        add(sfx, riser(BAR), t - BAR, 0.35)
        add(sfx, whoosh(0.5), t - 0.3, 0.7, 0.5 if i % 2 else -0.5)
        add(sfx, impact(), t, 0.75)
    # Scene 2: shutter pada reveal poster & tajuk
    add(sfx, shutter(), S[1][0] + 0.2, 0.6, 0.4)
    add(sfx, shutter(), S[1][0] + 4 * BEAT, 0.5, -0.4)
    # Scene 3: whoosh setiap teks + sorakan
    for k in range(4):
        add(sfx, whoosh(0.35), S[2][0] + 0.3 + k * 2 * BEAT * 1.25 - 0.15, 0.45, (-1) ** k * 0.5)
    add(sfx, cheer(4.0), S[2][0] + 5.5, 0.30)
    for k in range(6):
        add(sfx, footstep(), S[2][0] + 0.2 + k * BEAT, 0.35, (-1) ** k * 0.4)
    # Scene 4: pop kalendar & pin
    add(sfx, shutter(), S[3][0] + 0.4, 0.4)
    add(sfx, whoosh(0.35), S[3][0] + 4 * BEAT - 0.1, 0.4, 0.5)
    # Scene 5: jam berdetik + flip
    for k in range(int((S[4][1] - S[4][0]) / BEAT * 2)):
        add(sfx, tick(), S[4][0] + k * BEAT / 2, 0.35 if k % 2 == 0 else 0.2)
    add(sfx, impact(), S[4][0] + 3 * BAR, 0.6)
    # Scene 6: tap telefon
    for k in range(5):
        add(sfx, shutter()[: int(0.03 * SR)] * 1.5, S[5][0] + 1.0 + k * BEAT, 0.4)
    # Scene 7: sorakan + hit akhir
    add(sfx, cheer(5.0), S[6][0] + 0.5, 0.35)
    add(sfx, cheer(4.0), S[6][1] - BAR - 0.5, 0.40)
    add(sfx, boom(3.0), S[6][1] - BAR, 0.9)
    add(sfx, shutter(), S[6][1] - BAR + 0.1, 0.5)
    return sfx


# ------------------------------------------------------------------ VO panduan + timing
def read_wav(path):
    with wave.open(path) as w:
        sr = w.getframerate()
        x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float64) / 32768
    if sr != SR:
        idx = np.arange(0, len(x), sr / SR)
        x = np.interp(idx, np.arange(len(x)), x)
    return x


def trim(x, thr=0.01):
    nz = np.where(np.abs(x) > thr)[0]
    return x[nz[0]:nz[-1] + 1] if len(nz) else x


def build_vo():
    vo = np.zeros((N, 2))
    windows, lines = [], []
    for k, line in enumerate(VO):
        p = os.path.join(BUILD, f"vo_{k}.wav")
        subprocess.run(["espeak-ng", "-v", "ms+m3", "-s", "168", "-p", "38", "-a", "160",
                        "-w", p, line["tts"]], check=True)
        x = trim(read_wav(p))
        # sedikit EQ supaya lebih hangat
        x = filt(x, "hp", 90) + 0.25 * filt(x, "lp", 300)
        x = x / np.abs(x).max() * 0.9
        start = SCENES[line["scene"]][0] + line["offset"]
        dur = len(x) / SR
        limit = SCENES[line["scene"]][1] - 0.15
        assert start + dur <= limit, f"VO {k} terlalu panjang: {start + dur:.2f} > {limit:.2f}"
        add(vo, x, start, 0.95)
        windows.append((start, start + dur))
        lines.append(dict(start=start, end=start + dur))
    return vo, windows, lines


def chunk_timing(lines):
    subs = []
    for k, (ln, chunks) in enumerate(zip(lines, SUB_CHUNKS)):
        plain = " ".join(c.replace("*", "") for c in chunks)
        assert plain == VO[k]["text"], f"Subtitle tidak sepadan dengan VO {k}:\n{plain}\n{VO[k]['text']}"
        weights = [len(c.replace("*", "")) + 6 for c in chunks]   # +6 ~ jeda frasa
        tot = sum(weights)
        t = ln["start"]
        span = ln["end"] - ln["start"]
        for c, w in zip(chunks, weights):
            d = span * w / tot
            words = []
            hl = False
            for tok in re.findall(r"\*?[^\s*]+\*?|\S", c):
                pass
            # pecah perkataan + tanda highlight
            for seg in re.split(r"(\*[^*]+\*)", c):
                if not seg.strip():
                    continue
                hl = seg.startswith("*")
                for wd in seg.strip("*").split():
                    words.append(dict(w=wd, hl=hl))
            subs.append(dict(scene=VO[k]["scene"], start=round(t, 3), end=round(t + d, 3), words=words))
            t += d
    return subs


def srt_time(s):
    ms = int(round(s * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    sec, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{sec:02},{ms:03}"


def write_wav(path, x):
    x = np.clip(x, -1, 1)
    y = (x * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(y.tobytes())


def duck_env(windows, depth_db):
    g = np.ones(N)
    lo = 10 ** (depth_db / 20)
    att, rel = 0.12, 0.35
    for a, b in windows:
        ia, ib = int((a - att) * SR), int((b + rel) * SR)
        seg = np.full(ib - ia, lo)
        ra = int(att * SR)
        rr = int(rel * SR)
        seg[:ra] = np.linspace(1, lo, ra)
        seg[-rr:] = np.linspace(lo, 1, rr)
        g[ia:ib] = np.minimum(g[ia:ib], seg)
    return g


def master(x):
    x = x.copy()
    x[-int(1.2 * SR):] *= np.linspace(1, 0, int(1.2 * SR))[:, None] ** 2
    peak = np.abs(x).max()
    x = np.tanh(x / peak * 1.25) / np.tanh(1.25) * 0.93
    return x[: int(DURATION * SR) + int(0.0 * SR)]


def main():
    music = build_music()
    sfx = build_sfx()
    vo, windows, lines = build_vo()
    subs = chunk_timing(lines)

    music_n = music / np.abs(music).max() * 0.55
    sfx_n = sfx / np.abs(sfx).max() * 0.55
    write_wav(os.path.join(BUILD, "music.wav"), music_n)
    write_wav(os.path.join(BUILD, "sfx.wav"), sfx_n)
    write_wav(os.path.join(BUILD, "vo_guide.wav"), vo)

    g_vo = duck_env(windows, -10)[:, None]
    g_no = duck_env(windows, -4)[:, None]
    write_wav(os.path.join(BUILD, "mix_guideVO.wav"), master(music_n * g_vo + sfx_n * (0.6 + 0.4 * g_vo) + vo * 1.15))
    write_wav(os.path.join(BUILD, "mix_noVO.wav"), master(music_n * g_no + sfx_n))

    with open(os.path.join(BUILD, "timing.json"), "w") as f:
        json.dump(dict(vo=lines, subs=subs), f, indent=1, ensure_ascii=False)
    with open(os.path.join(OUT, "subtitles_BM.srt"), "w", encoding="utf-8") as f:
        for i, s in enumerate(subs, 1):
            f.write(f"{i}\n{srt_time(s['start'])} --> {srt_time(s['end'])}\n{' '.join(w['w'] for w in s['words'])}\n\n")
    for k, ln in enumerate(lines):
        print(f"VO{k+1}: {ln['start']:.2f}-{ln['end']:.2f} ({ln['end']-ln['start']:.2f}s) scene {SCENES[k][0]:.2f}-{SCENES[k][1]:.2f}")


if __name__ == "__main__":
    main()
