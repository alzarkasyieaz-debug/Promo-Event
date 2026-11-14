"""Audio KONSEP 2: muzik asli 132 BPM (profil ikut jenis scene), SFX, VO panduan, ucapan YB Ustaz Ismi,
subtitle & mix. Guna semula instrumen sintetik daripada build_audio.py."""
import json, os, re, subprocess

import numpy as np

import build_audio as BA
from build_audio import (SR, kick, clap, hat, stab, pad, bass_note, pluck, boom, impact, whoosh, riser,
                         footstep, shutter, tick, cheer, read_wav, trim, filt, env_exp, srt_time, write_wav)
from config2 import (BEAT, BAR, HALF, SCENES, KINDS, DURATION, VO, SUB_CHUNKS, CLIPS, SRC, BUILD, OUT)

N = int(np.ceil((DURATION + 1.5) * SR))
os.makedirs(BUILD, exist_ok=True)
os.makedirs(OUT, exist_ok=True)
add = BA.add


def scene_at(t):
    return next((i for i, (a, b) in enumerate(SCENES) if a <= t < b), len(SCENES) - 1)


PROF = {
    "hook":    dict(kick=1, clap=1, hat=2, bass=1, stab=1, pad=0, arp=0, cut=3400),
    "intro":   dict(kick=1, clap=1, hat=1, bass=1, stab=1, pad=1, arp=1, cut=2600),
    "speechA": dict(kick=1, clap=0, hat=1, bass=1, stab=0, pad=1, arp=0, cut=1100),
    "feature": dict(kick=1, clap=1, hat=2, bass=1, stab=1, pad=1, arp=1, cut=4500),
    "speechB": dict(kick=1, clap=0, hat=1, bass=1, stab=0, pad=1, arp=1, cut=1300),
    "urgency": dict(kick=1, clap=0, hat=2, bass=2, stab=0, pad=1, arp=1, cut=1200),
    "howto":   dict(kick=1, clap=1, hat=2, bass=1, stab=1, pad=0, arp=1, cut=3000),
    "cta":     dict(kick=1, clap=1, hat=2, bass=1, stab=1, pad=1, arp=1, cut=5200),
}


def build_music():
    mus = np.zeros((N, 2))
    sc = np.ones(N)
    prog = [(48, [60, 64, 67, 72]), (43, [59, 62, 67, 71]), (45, [60, 64, 69, 72]), (41, [60, 65, 69, 72])]
    K, CL, HC, HO = kick(), clap(), hat(), hat(True)
    nbeats = int(DURATION / BEAT)
    arp_pat = [0, 2, 1, 3, 2, 1, 3, 2]
    for bi in range(nbeats - 4):
        tb = bi * BEAT
        p = PROF[KINDS[scene_at(tb + 1e-6)]]
        root, ch = prog[(bi // 4) % 4]
        beat = bi % 4
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
        if p["bass"] == 1:
            add(mus, bass_note(root, BEAT / 2 * 0.9), tb + BEAT / 2, 0.55)
        elif p["bass"] == 2:
            for q in range(4):
                add(mus, bass_note(root, BEAT / 4 * 0.8), tb + q * BEAT / 4, 0.42)
        if p["stab"] and beat in (0, 2):
            add(mus, stab(ch, BEAT * 0.9, p["cut"]), tb + (BEAT / 2 if beat == 2 else 0), 0.30, -0.15)
            add(mus, stab([c + 12 for c in ch], BEAT * 0.6, p["cut"]), tb + BEAT * 1.5, 0.16, 0.2)
        if p["pad"] and beat == 0:
            add(mus, pad(ch, BAR, p["cut"]), tb, 0.22)
        if p["arp"]:
            for k in range(2):
                m = ch[arp_pat[(beat * 2 + k) % 8]] + 12
                add(mus, pluck(m, BEAT * 0.45), tb + k * BEAT / 2, 0.13, 0.4 if k else -0.4)
    tend = SCENES[-1][1] - 2.4
    add(mus, K, tend, 1.0)
    add(mus, pad([48, 55, 60, 64, 67, 72], 2.4, 3000), tend, 0.35)
    add(mus, stab([60, 64, 67, 72, 76], 1.4, 5000), tend, 0.45)
    add(mus, bass_note(36, 1.2) * env_exp(int(1.2 * SR), 0.5), tend, 0.7)
    mus *= sc[:, None]
    return mus


def build_sfx():
    sfx = np.zeros((N, 2))
    S = SCENES
    add(sfx, boom(), 0.0, 0.9)
    for k in range(8):
        add(sfx, footstep(), 0.15 + k * BEAT, 0.7, -0.3 if k % 2 else 0.3)
    add(sfx, impact(), 2 * BAR, 0.75)
    add(sfx, whoosh(0.4), 2 * BAR - 0.35, 0.6, -0.6)
    for i in range(1, len(S)):
        t = S[i][0]
        add(sfx, riser(min(BAR, S[i][0] - S[i - 1][0] - 0.2)), t - min(BAR, S[i][0] - S[i - 1][0] - 0.2), 0.3)
        add(sfx, whoosh(0.5), t - 0.3, 0.75, 0.5 if i % 2 else -0.5)
        add(sfx, impact(), t, 0.7)
    # intro: huruf jatuh
    for k in range(9):
        add(sfx, tick() * 2, S[1][0] + 0.6 + k * 0.07, 0.6, (k - 4) / 5)
    add(sfx, impact(), S[1][0] + 0.6 + 9 * 0.07, 0.5)
    # feature: whoosh slogan + tapak kaki + sorakan
    st = (S[3][1] - S[3][0]) / 4
    for k in range(4):
        add(sfx, whoosh(0.35), S[3][0] + k * st, 0.45, (-1) ** k * 0.5)
    for k in range(16):
        add(sfx, footstep(), S[3][0] + k * BEAT, 0.3, (-1) ** k * 0.4)
    add(sfx, cheer(3.5), S[3][0] + 3 * st - 0.3, 0.3)
    # urgency: detik jam + impact pada slam tarikh
    for k in range(int((S[5][1] - S[5][0]) / BEAT * 2)):
        add(sfx, tick(), S[5][0] + k * BEAT / 2, 0.35 if k % 2 == 0 else 0.2)
    add(sfx, impact(), S[5][0] + 2 * BAR + BAR / 2, 0.6)
    # howto: tap telefon
    for k in range(5):
        add(sfx, shutter()[: int(0.03 * SR)] * 1.5, S[6][0] + 0.8 + k * BEAT, 0.4)
    # cta
    add(sfx, cheer(4.5), S[7][0] + 0.4, 0.33)
    add(sfx, boom(3.0), S[7][1] - 2.4, 0.9)
    add(sfx, cheer(3.0), S[7][1] - 2.9, 0.35)
    return sfx


def build_vo():
    vo = np.zeros((N, 2))
    windows, lines = [], []
    for k, line in enumerate(VO):
        p = os.path.join(BUILD, f"vo_{k}.wav")
        subprocess.run(["espeak-ng", "-v", "ms+m3", "-s", "168", "-p", "38", "-a", "160", "-w", p, line["tts"]], check=True)
        x = trim(read_wav(p))
        x = filt(x, "hp", 90) + 0.25 * filt(x, "lp", 300)
        x = x / np.abs(x).max() * 0.9
        start = SCENES[line["scene"]][0] + line["offset"]
        dur = len(x) / SR
        limit = SCENES[line["scene"]][1] - 0.12
        assert start + dur <= limit, f"VO {k} terlalu panjang: {start + dur:.2f} > {limit:.2f}"
        add(vo, x, start, 0.95)
        windows.append((start, start + dur))
        lines.append(dict(start=start, end=start + dur))
    return vo, windows, lines


def words_of(c):
    words = []
    for seg in re.split(r"(\*[^*]+\*)", c):
        if seg.strip():
            for wd in seg.strip("*").split():
                words.append(dict(w=wd, hl=seg.startswith("*")))
    return words


def vo_subs(lines):
    subs = []
    for k, (ln, chunks) in enumerate(zip(lines, SUB_CHUNKS)):
        plain = " ".join(c.replace("*", "") for c in chunks)
        assert plain == VO[k]["text"], (plain, VO[k]["text"])
        weights = [len(c.replace("*", "")) + 6 for c in chunks]
        tot, t, span = sum(weights), ln["start"], ln["end"] - ln["start"]
        for c, w in zip(chunks, weights):
            d = span * w / tot
            subs.append(dict(start=round(t, 3), end=round(t + d, 3), words=words_of(c)))
            t += d
    return subs


def build_clips():
    buf = np.zeros((N, 2))
    wins, subs, meta = [], [], []
    for k, cl in enumerate(CLIPS):
        a, b = cl["seg"]
        p = os.path.join(BUILD, f"clip_voice_{k}.wav")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(a), "-to", str(b), "-i", SRC,
                        "-ac", "1", "-ar", str(SR), "-af",
                        "highpass=f=90,afftdn=nf=-25,acompressor=threshold=-24dB:ratio=3:attack=5:release=120,"
                        "equalizer=f=3000:t=q:w=1.2:g=3", "-acodec", "pcm_s16le", p], check=True)
        x = read_wav(p)
        x = x / (np.sqrt(np.mean(x ** 2)) + 1e-9) * 0.12
        x = np.clip(x, -0.95, 0.95)
        f = int(0.05 * SR)
        x[:f] *= np.linspace(0, 1, f)
        x[-f:] *= np.linspace(1, 0, f)
        t0 = SCENES[cl["scene"]][0] + cl["offset"]
        add(buf, x, t0, 1.0)
        m = lambda s: t0 + (s - a)
        wins.append((m(cl["chunks"][0][0]), m(cl["chunks"][-1][1])))
        for ca, cb, c in cl["chunks"]:
            subs.append(dict(start=round(m(ca), 3), end=round(m(cb), 3), words=words_of(c), real=True))
        meta.append(dict(t0=t0, t1=t0 + (b - a)))
    return buf, wins, subs, meta


def duck_env(windows, depth_db):
    g = np.ones(N)
    lo = 10 ** (depth_db / 20)
    att, rel = 0.12, 0.35
    for a, b in windows:
        ia, ib = int((a - att) * SR), int((b + rel) * SR)
        seg = np.full(ib - ia, lo)
        ra, rr = int(att * SR), int(rel * SR)
        seg[:ra] = np.linspace(1, lo, ra)
        seg[-rr:] = np.linspace(lo, 1, rr)
        g[ia:ib] = np.minimum(g[ia:ib], seg)
    return g


def master(x):
    x = x.copy()
    x[-int(1.2 * SR):] *= np.linspace(1, 0, int(1.2 * SR))[:, None] ** 2
    x = np.tanh(x / np.abs(x).max() * 1.25) / np.tanh(1.25) * 0.93
    return x[: int(DURATION * SR)]


def main():
    music, sfx = build_music(), build_sfx()
    vo, windows, lines = build_vo()
    clipv, cwins, csubs, cmeta = build_clips()
    subs = sorted(vo_subs(lines) + csubs, key=lambda d: d["start"])
    music_n = music / np.abs(music).max() * 0.55
    sfx_n = sfx / np.abs(sfx).max() * 0.55
    os.makedirs(os.path.join(OUT, "stems"), exist_ok=True)
    for nm, x in (("music", music_n), ("sfx", sfx_n), ("vo_guide", vo), ("ucapan_YB_Ustaz_Ismi", clipv)):
        write_wav(os.path.join(OUT, "stems", f"{nm}.wav"), x[: int(DURATION * SR)])
    gc = duck_env(cwins, -13)[:, None]
    g_vo = np.minimum(duck_env(windows, -10)[:, None], gc)
    g_no = np.minimum(duck_env(windows, -4)[:, None], gc)
    write_wav(os.path.join(BUILD, "mix_guideVO.wav"), master(music_n * g_vo + sfx_n * (0.6 + 0.4 * g_vo) + vo * 1.15 + clipv * 1.15))
    write_wav(os.path.join(BUILD, "mix_noVO.wav"), master(music_n * g_no + sfx_n * (0.6 + 0.4 * gc) + clipv * 1.15))
    json.dump(dict(vo=lines, subs=subs, clips=cmeta), open(os.path.join(BUILD, "timing.json"), "w"), indent=1, ensure_ascii=False)
    with open(os.path.join(OUT, "subtitles_BM_konsep2.srt"), "w", encoding="utf-8") as f:
        for i, s in enumerate(subs, 1):
            f.write(f"{i}\n{srt_time(s['start'])} --> {srt_time(s['end'])}\n{' '.join(w['w'] for w in s['words'])}\n\n")
    for k, ln in enumerate(lines):
        print(f"VO{k+1}: {ln['start']:.2f}-{ln['end']:.2f}")
    for m in cmeta:
        print(f"CLIP: {m['t0']:.2f}-{m['t1']:.2f}")
    print("DURATION", round(DURATION, 2))


if __name__ == "__main__":
    main()
