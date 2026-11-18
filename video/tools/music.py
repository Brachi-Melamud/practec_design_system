"""Original music bed + sound design for the Practec video — synthesized here with numpy, so it is license-free.

Follows composition/content.js: 120 bpm (one bar = 2 s = one scene-grid step), one chord per bar
(Am–F–C–G, resolving F–G–C on the end card), a section style per scene ("intro", "lift", "groove", "break",
"outro") and the scene-relative "sfx" cues (typing, CI checks, risers into the brand reveal and the end card…).

    python video/tools/music.py      ->  video/build/audio/music.wav   (48 kHz stereo, 16-bit, peak -1 dBFS)

render.py calls build() and then loudness-normalises the result with ffmpeg (EBU R128, -14 LUFS).
"""
import json
import re
import sys
import wave
from pathlib import Path

import numpy as np

SR = 48000
VIDEO_DIR = Path(__file__).resolve().parents[1]
rng = np.random.default_rng(1911)


def load_video():
    src = (VIDEO_DIR / "composition" / "content.js").read_text(encoding="utf-8")
    body = re.split(r"^window\.VIDEO\s*=", src, maxsplit=1, flags=re.M)[1].strip().rstrip(";")
    return json.loads(body)


# ---------------------------------------------------------------- basics
def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def secs(n):
    return np.arange(n) / SR


def place(buf, sig, t0, gain=1.0, pan=0.0):
    """add mono (n,) or stereo (2, n) `sig` into stereo `buf` at time t0 (equal-power pan, -1 = left)."""
    if sig.ndim == 1:
        a = (pan + 1) * np.pi / 4
        sig = np.vstack([sig * np.cos(a), sig * np.sin(a)]) * np.sqrt(2)
    i = int(round(t0 * SR))
    if i < 0:
        sig, i = sig[:, -i:], 0
    j = min(buf.shape[1], i + sig.shape[1])
    if j > i:
        buf[:, i:j] += gain * sig[:, :j - i]


def _filt(x, H):
    f = np.maximum(np.fft.rfftfreq(x.shape[-1], 1 / SR), 1e-3)
    return np.fft.irfft(np.fft.rfft(x, axis=-1) * H(f), x.shape[-1], axis=-1)


def lowpass(x, fc, order=2):
    return _filt(x, lambda f: 1 / np.sqrt(1 + (f / fc) ** (2 * order)))


def highpass(x, fc, order=2):
    return _filt(x, lambda f: 1 / np.sqrt(1 + (fc / f) ** (2 * order)))


def bandpass(x, lo, hi, order=2):
    return highpass(lowpass(x, hi, order), lo, order)


def norm(x, peak=1.0):
    m = np.abs(x).max()
    return x * (peak / m) if m > 0 else x


# ---------------------------------------------------------------- instruments
def pad_chord(notes, dur):
    """soft detuned additive pad (band-limited, ~saw with a steep roll-off), stereo."""
    n = int(dur * SR)
    t = secs(n)
    out = np.zeros((2, n))
    for m in notes:
        for v, (cents, pan) in enumerate(((-7, -.7), (0, 0), (7, .7))):
            f = mtof(m) * 2 ** (cents / 1200)
            ph = rng.uniform(0, 2 * np.pi)
            w = sum(k ** -1.4 * np.sin(2 * np.pi * f * k * t + ph * k) for k in range(1, 12) if f * k < 9000)
            a = (pan + 1) * np.pi / 4
            out[0] += w * np.cos(a)
            out[1] += w * np.sin(a)
    env = np.clip(t / .45, 0, 1) ** 1.5 * np.clip((dur - t) / .6, 0, 1)
    return out * env / len(notes)


def pluck(m, dur=.7, vel=1.0):
    n = int(dur * SR)
    t = secs(n)
    f = mtof(m)
    w = sum((1 / k) * np.exp(-t * (5 + 3.4 * k)) * np.sin(2 * np.pi * f * k * t) for k in range(1, 9) if f * k < 12000)
    return vel * w * np.clip(t / .0015, 0, 1) * np.clip((dur - t) / .02, 0, 1)


def bass(m, dur, vel=1.0):
    n = int(dur * SR)
    t = secs(n)
    f = mtof(m)
    # upper harmonics keep the bass line audible on phone speakers, which reproduce little below ~300 Hz
    w = sum(a * np.sin(2 * np.pi * f * k * t) for k, a in ((1, 1), (2, .55), (3, .34), (4, .2), (5, .1)))
    env = np.clip(t / .006, 0, 1) * (.55 + .45 * np.exp(-t / .16)) * np.clip((dur - t) / .04, 0, 1)
    return vel * w * env


def kick():
    n = int(.42 * SR)
    t = secs(n)
    f = 46 + 110 * np.exp(-t / .032)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / .17)
    click = highpass(rng.standard_normal(n), 2500) * np.exp(-t / .0022) * .25
    return body + click


_HAT = highpass(rng.standard_normal(int(.25 * SR)), 7000, 3)


def hat(open_=False):
    n = int((.24 if open_ else .07) * SR)
    t = secs(n)
    return norm(_HAT[:n]) * np.exp(-t / (.07 if open_ else .016))


def clap():
    n = int(.3 * SR)
    t = secs(n)
    nz = bandpass(rng.standard_normal(n), 1100, 5200)
    bursts = sum(np.exp(-np.clip(t - o, 0, None) / .007) * (t >= o) for o in (0, .012, .024))
    body = .3 * np.sin(2 * np.pi * 190 * t) * np.exp(-t / .03)
    return norm(nz) * (bursts + .5 * np.exp(-t / .09)) * .6 + body


def bell(m, dur=1.4, vel=1.0):
    n = int(dur * SR)
    t = secs(n)
    f = mtof(m)
    parts = ((1, 1, 1.0), (2.0, .28, .55), (2.76, .22, .38), (5.4, .06, .2))
    s = sum(a * np.exp(-t / (d * dur * .55)) * np.sin(2 * np.pi * f * r * t) for r, a, d in parts if f * r < 16000)
    return vel * s * np.clip(t / .0015, 0, 1)


# ---------------------------------------------------------------- sound effects
def sfx_keys(dur):
    n = int(dur * SR) + SR // 10
    out = np.zeros(n)
    cn = int(.012 * SR)
    tc = secs(cn)
    t = 0.0
    while t < dur:
        c = bandpass(rng.standard_normal(cn), 1500, 7000) * np.exp(-tc / .0024) * 2.2
        c += .5 * np.sin(2 * np.pi * 170 * tc) * np.exp(-tc / .006)
        i = int(t * SR)
        out[i:i + cn] += rng.uniform(.5, 1.0) * c
        t += rng.uniform(.045, .085)
    return out


def _sweep_noise(dur, fc_of_p, width=.45, seed=0):
    """noise through a moving log-gaussian band (STFT overlap-add)."""
    r = np.random.default_rng(seed)
    n = int(dur * SR)
    win, hop = 2048, 512
    x = r.standard_normal(n + win)
    out = np.zeros(n + win)
    w = np.hanning(win)
    fr = np.maximum(np.fft.rfftfreq(win, 1 / SR), 1)
    for s in range(0, n, hop):
        H = np.exp(-.5 * (np.log(fr / fc_of_p(s / n)) / width) ** 2)
        out[s:s + win] += np.fft.irfft(np.fft.rfft(x[s:s + win] * w) * H, win) * w
    return norm(out[:n])


def sfx_riser(dur):
    n = int(dur * SR)
    t = secs(n)
    p = t / dur
    nz = np.vstack([_sweep_noise(dur, lambda q: 350 * 20 ** q, seed=s) for s in (1, 2)])
    sweep = .3 * np.sin(2 * np.pi * np.cumsum(220 * 4 ** p) / SR)
    env = p ** 2.4 * np.clip((dur - t) / .025, 0, 1)
    return (nz + sweep) * env


def sfx_swoosh(dur=.42):
    n = int(dur * SR)
    t = secs(n)
    p = t / dur
    nz = _sweep_noise(dur, lambda q: 700 + 2600 * np.sin(np.pi * q), .5, seed=3)
    env = np.sin(np.pi * p) ** 1.6
    return np.vstack([nz * env * p, nz * env * (1 - p)]) * 1.3      # right → left: forward in RTL


def sfx_impact():
    n = int(2.4 * SR)
    t = secs(n)
    boom = np.sin(2 * np.pi * np.cumsum(38 + 45 * np.exp(-t / .09)) / SR) * np.exp(-t / .5)
    air = lowpass(rng.standard_normal(n), 2200) * np.exp(-t / .22) * .5
    return boom + norm(air) * .35


def sfx_tick():
    n = int(.06 * SR)
    t = secs(n)
    return (np.sin(2 * np.pi * 2300 * t) + .3 * np.sin(2 * np.pi * 4600 * t)) * np.exp(-t / .012)


def sfx_blip():
    a, b = bell(83, .5, .8), bell(88, .7, .9)
    out = np.zeros(int(.8 * SR))
    out[:len(a)] += a
    out[int(.06 * SR):int(.06 * SR) + len(b)] += b
    return out


def sfx_check(step=0):
    m = (83, 88, 92)[step % 3]
    out, octave = bell(m, 1.0), bell(m + 12, .6)
    out[:len(octave)] += .35 * octave
    return out


def sfx_arp(notes, gap, dur=1.6):
    out = np.zeros(int((dur + gap * len(notes)) * SR))
    for i, m in enumerate(notes):
        b = bell(m, dur, .8)
        j = int(i * gap * SR)
        out[j:j + len(b)] += b
    return out


def sfx_pop():
    n = int(.1 * SR)
    t = secs(n)
    return np.sin(2 * np.pi * np.cumsum(520 + 600 * np.exp(-t / .02)) / SR) * np.exp(-t / .03)


def sfx_drop():
    n = int(.25 * SR)
    t = secs(n)
    thud = np.sin(2 * np.pi * np.cumsum(70 + 80 * np.exp(-t / .03)) / SR) * np.exp(-t / .06)
    paper = lowpass(rng.standard_normal(n), 3000) * np.exp(-t / .02) * .15
    return thud + paper


# ---------------------------------------------------------------- arrangement
CHORDS = {
    "Am": dict(bass=45, pad=[57, 60, 64, 67], arp=[69, 72, 76, 79]),
    "F": dict(bass=41, pad=[53, 57, 60, 64], arp=[65, 69, 72, 76]),
    "C": dict(bass=48, pad=[55, 60, 64, 67], arp=[67, 72, 76, 79]),
    "G": dict(bass=43, pad=[55, 59, 62, 69], arp=[67, 71, 74, 79]),
}
LOOP = ["Am", "F", "C", "G"]
OUTRO = {1: ["C"], 2: ["F", "C"], 3: ["F", "G", "C"]}       # end-card bars: always resolve to C


def reverb(x, rt60=1.5):
    n = int(rt60 * SR)
    t = secs(n)
    ir = lowpass(np.random.default_rng(5).standard_normal((2, n)) * np.exp(-6.91 * t / rt60), 5500)
    ir = np.hstack([np.zeros((2, int(.02 * SR))), ir])
    ir /= np.sqrt((ir ** 2).sum(axis=1, keepdims=True))
    size = 1 << int(np.ceil(np.log2(x.shape[1] + ir.shape[1])))
    y = np.fft.irfft(np.fft.rfft(x, size, axis=1) * np.fft.rfft(ir, size, axis=1), size, axis=1)
    return y[:, :x.shape[1]]


def build(V=None, out_path=None):
    V = V or load_video()
    D = float(V["duration"])
    N = int(round(D * SR))
    beat = 60 / V.get("bpm", 120)
    bar = 4 * beat
    scenes = V["scenes"]
    start = {s["id"]: s["start"] for s in scenes}

    def section(t):
        for s in scenes:
            if s["start"] - 1e-6 <= t < s["end"] - 1e-6:
                return s.get("music", "groove")
        return "outro"

    buses = {k: np.zeros((2, N)) for k in ("pad", "bass", "pluck", "kick", "hat", "clap", "sfx", "send")}
    kicks = []
    outro_i = 0
    pads = {}
    nbars = int(np.ceil(D / bar))
    outro = OUTRO[min(3, max(1, sum(section(b * bar) == "outro" for b in range(nbars))))]
    cue_at = {c["id"]: c["start"] for c in V.get("captions", []) if c.get("id")}
    for b in range(nbars):
        t0 = b * bar
        sec = section(t0)
        if sec == "outro":
            name = outro[min(outro_i, len(outro) - 1)]
            outro_i += 1
        else:
            name = LOOP[b % 4]
        ch = CHORDS[name]
        last = b == nbars - 1
        # pad (cached per chord)
        key = (name, last)
        if key not in pads:
            notes = ch["pad"] + ([72, 74] if last and sec == "outro" else [])
            pads[key] = pad_chord(notes, bar + (2.5 if last else .7))
        place(buses["pad"], pads[key], t0, {"intro": .7, "break": 1.0, "outro": 1.0}.get(sec, .85))
        r = ch["bass"]
        if sec == "intro":
            if b == 1:
                place(buses["bass"], bass(r, bar, .45), t0)
            for i in range(8):
                place(buses["hat"], hat(), t0 + i * beat / 2, .35 + .25 * b + .05 * i, pan=.3)
        elif sec == "lift":
            for i in range(4):
                place(buses["bass"], bass(r, beat * .85, .9), t0 + i * beat)
                place(buses["pluck"], pluck(ch["arp"][(0, 1, 2, 1)[i]], .9, .8), t0 + i * beat, pan=(-.35, .35)[i % 2])
            for i in (0, 2):
                place(buses["kick"], kick(), t0 + i * beat); kicks.append(t0 + i * beat)
            for i in range(8):
                place(buses["hat"], hat(), t0 + i * beat / 2, .6 if i % 2 else .35, pan=.3)
        elif sec in ("groove", "break"):
            soft = sec == "break"
            live = lambda te: section(te) == sec        # a scene may end mid-bar: stop the groove there
            if section(t0 + bar / 2) == "outro":        # ...and hold the chord into the end card
                place(buses["bass"], bass(r, bar / 2 + .1, .8), t0 + bar / 2)
                for m in ch["arp"]:
                    place(buses["pluck"], pluck(m, 1.4, .6), t0 + bar / 2)
            for i in range(8):
                if not live(t0 + i * beat / 2):
                    continue
                place(buses["bass"], bass(r, beat * .45, .85 if i % 2 == 0 else .65), t0 + i * beat / 2)
                if not soft or i % 2 == 0:
                    place(buses["pluck"], pluck(ch["arp"][(0, 1, 2, 3, 2, 1, 2, 1)[i]], .7, .65 if soft else .8),
                          t0 + i * beat / 2, pan=(-.4, .4)[i % 2])
                place(buses["hat"], hat(open_=(i == 7 and not soft)), t0 + i * beat / 2, (.8 if i % 2 else .3) * (.7 if soft else 1), pan=.3)
            first_break_bar = soft and section(t0 - bar) != "break"
            for i in range(4):
                if (soft and (first_break_bar or i % 2)) or not live(t0 + i * beat):
                    continue
                place(buses["kick"], kick(), t0 + i * beat); kicks.append(t0 + i * beat)
            if not soft:
                for i in (1, 3):
                    if live(t0 + i * beat):
                        place(buses["clap"], clap(), t0 + i * beat, pan=-.1)
        elif sec == "outro":
            dur = bar + (2.5 if last else 0)
            place(buses["bass"], bass(r, dur, .8), t0)
            if outro_i == 1:            # first end-card bar: chord stab
                for m in ch["arp"]:
                    place(buses["pluck"], pluck(m, 1.6, .7), t0)
            if last:                    # resolve: bell chord rings out
                for i, m in enumerate([72, 76, 79, 84]):
                    place(buses["send"], bell(m, 3.0, .35), t0 + i * .05)
                    place(buses["sfx"], bell(m, 3.0, .35), t0 + i * .05)

    # sidechain pulse: bass and pad dip after every kick
    t = secs(N)
    duck = np.ones(N)
    for k in kicks:
        i = int(k * SR)
        m = min(N - i, int(.4 * SR))
        duck[i:i + m] = np.minimum(duck[i:i + m], 1 - .55 * np.exp(-secs(m) / .11))
    buses["bass"] *= duck
    buses["pad"] *= .6 + .4 * duck

    # sound effects from content.js
    for c in V.get("sfx", []):
        t0 = (cue_at[c["cue"]] if "cue" in c else start[c["scene"]]) + c.get("at", 0)
        g = c.get("gain", 1.0)
        kind = c["type"]
        if kind == "keys":
            place(buses["sfx"], sfx_keys(c.get("dur", .5)), t0, .22 * g, pan=-.2)
        elif kind == "tick":
            place(buses["sfx"], sfx_tick(), t0, .3 * g, pan=.2)
        elif kind == "blip":
            s = sfx_blip(); place(buses["sfx"], s, t0, .22 * g); place(buses["send"], s, t0, .2 * g)
        elif kind == "riser":
            d = c.get("dur", 1.0); place(buses["sfx"], sfx_riser(d), t0, .2 * g)
        elif kind == "impact":
            s = sfx_impact(); place(buses["sfx"], s, t0, .55 * g); place(buses["send"], s, t0, .25 * g)
        elif kind == "swoosh":
            place(buses["sfx"], sfx_swoosh(), t0 - .12, .2 * g)
        elif kind == "drop":
            place(buses["sfx"], sfx_drop(), t0, .5 * g)
        elif kind == "check":
            s = sfx_check(c.get("step", 0)); place(buses["sfx"], s, t0, .2 * g); place(buses["send"], s, t0, .25 * g)
        elif kind == "success":
            s = sfx_arp([81, 85, 88, 93], .07); place(buses["sfx"], s, t0, .2 * g); place(buses["send"], s, t0, .35 * g)
        elif kind == "shimmer":
            s = sfx_arp([84, 88, 91, 96], .045, 1.2); place(buses["sfx"], s, t0, .14 * g); place(buses["send"], s, t0, .3 * g)
        elif kind == "pop":
            place(buses["sfx"], sfx_pop(), t0, .35 * g)

    # mix (bus levels in dB) + reverb send
    # balanced for small speakers: the melodic layers carry the bed, bass and kick only support it
    lv = {"pad": -14.5, "bass": -17, "pluck": -14, "kick": -14, "hat": -21, "clap": -18, "sfx": -7}
    mix = sum(norm(buses[k]) * 10 ** (db / 20) for k, db in lv.items() if np.abs(buses[k]).max() > 0)
    send = norm(buses["pad"]) * .25 + norm(buses["pluck"]) * .35 + norm(buses["clap"]) * .15 + norm(buses["send"]) * .4
    mix = mix + reverb(send) * .3
    mix = highpass(mix, 40, 2)
    fade = np.clip(t / .015, 0, 1) * np.clip((D - t) / 1.4, 0, 1)
    mix = np.tanh(1.15 * mix * fade / np.abs(mix).max()) / np.tanh(1.15)
    mix = norm(mix, 10 ** (-1 / 20))

    out_path = Path(out_path or VIDEO_DIR / "build" / "audio" / "music.wav")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    pcm = (mix.T * 32767).astype("<i2")
    with wave.open(str(out_path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    return out_path


if __name__ == "__main__":
    p = build(out_path=sys.argv[1] if len(sys.argv) > 1 else None)
    print(p)
