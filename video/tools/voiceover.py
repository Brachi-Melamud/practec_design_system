"""Voice-over for the Practec video: ElevenLabs speaks the captions, and the captions follow the voice.

    python video/tools/voiceover.py                  # speak new/changed lines, time the captions to the voice,
                                                     #   write build/audio/vo.wav and report how each line fits its scene
    python video/tools/voiceover.py --check          # also transcribe every line with a local Whisper model and
                                                     #   compare it with the text (catches skipped or misread words)
    python video/tools/voiceover.py --no-sync        # leave the caption timings in content.js untouched

How it works
- content.js: "voice" holds the voice id, model and style tag; every caption names its "scene". All captions of a
  scene are spoken as one line. "say" (optional) is what the voice receives when it must differ from the caption:
  numbers as Hebrew words, "+" as "פלוס". Captions keep the written form.
- Each spoken line is cached in video/voice/ (mp3 + word timings), keyed by voice + model + tag + text + seed, so a
  line is paid for once. render.py only reads this cache; it never calls ElevenLabs.
- A line starts "lead" seconds into its scene. Caption start/end are taken from the word timings (0.08 s before the
  first word, 0.35 s after the last) and written back into content.js.
- To get another take of a line, give its scene a seed: "seeds": {"dates": 2}.

The API key is read from the ELEVENLABS_API_KEY environment variable, or from --env-file, or from video/.env.
It is never printed.
"""
import argparse
import base64
import difflib
import hashlib
import json
import os
import re
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
VIDEO_DIR = HERE.parent
CONTENT = VIDEO_DIR / "composition" / "content.js"
CACHE = VIDEO_DIR / "voice"
BUILD = VIDEO_DIR / "build"
API = "https://api.elevenlabs.io/v1"
SR = 48000
LEAD_IN, TAIL_OUT = 0.08, 0.35          # a caption appears just before its first word and lingers after its last
sys.path.insert(0, str(HERE))


def load_video():
    src = CONTENT.read_text(encoding="utf-8")
    body = re.split(r"^window\.VIDEO\s*=", src, maxsplit=1, flags=re.M)[1].strip().rstrip(";")
    return json.loads(body)


def ffmpeg_bin():
    import shutil
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def api_key(env_file=None):
    key = os.environ.get("ELEVENLABS_API_KEY")
    for f in ([Path(env_file)] if env_file else []) + [VIDEO_DIR / ".env"]:
        if key or not f.exists():
            continue
        for row in f.read_text(encoding="utf-8").splitlines():
            if row.strip().startswith("ELEVENLABS_API_KEY="):
                key = row.split("=", 1)[1].strip().strip("'\"")
    return key


def spoken(caption):
    return caption.get("say") or caption["text"].replace("*", "")


def lines(V):
    """one spoken line per scene: the scene's captions, in order"""
    out = []
    for s in V["scenes"]:
        caps = [c for c in V["captions"] if c.get("scene") == s["id"]]
        if caps:
            out.append({"scene": s, "captions": caps, "text": " ".join(spoken(c) for c in caps)})
    return out


def synthesize(text, voice, seed=None, key=None, allow_api=True):
    """-> (mp3 path, [{"text", "start", "end"}]) for one line; cached"""
    prefix = voice.get("prefix", "")
    ident = [voice["voice_id"], voice["model"], prefix, text] + ([seed] if seed is not None else [])
    name = hashlib.sha1(json.dumps(ident, ensure_ascii=False).encode("utf-8")).hexdigest()[:16]
    mp3, meta = CACHE / f"{name}.mp3", CACHE / f"{name}.json"
    if not (mp3.exists() and meta.exists()):
        if not allow_api:
            sys.exit(f"voice line not in the cache: “{text[:50]}…”\n  run: python video/tools/voiceover.py")
        if not key:
            sys.exit("ELEVENLABS_API_KEY is not set (environment, --env-file, or video/.env)")
        import requests
        try:
            import truststore                       # networks that inspect TLS need the system trust store
            truststore.inject_into_ssl()
        except ImportError:
            pass
        body = {"text": f"{prefix} {text}" if prefix else text, "model_id": voice["model"], "language_code": "he"}
        if seed is not None:
            body["seed"] = seed
        r = requests.post(f"{API}/text-to-speech/{voice['voice_id']}/with-timestamps", headers={"xi-api-key": key},
                          json=body, timeout=180)
        if r.status_code >= 400:
            sys.exit(f"ElevenLabs {r.status_code}: {r.text[:300]}")
        data = r.json()
        al = data.get("alignment") or {}
        words, cur = [], None
        for ch, a, b in zip(al.get("characters", []), al.get("character_start_times_seconds", []),
                            al.get("character_end_times_seconds", [])):
            if ch.isspace():
                if cur:
                    words.append(cur)
                cur = None
            elif cur is None:
                cur = {"text": ch, "start": a, "end": b}
            else:
                cur["text"] += ch
                cur["end"] = b
        if cur:
            words.append(cur)
        words = words[len(prefix.split()):]          # the style tag comes back in the alignment: drop its tokens
        CACHE.mkdir(parents=True, exist_ok=True)
        mp3.write_bytes(base64.b64decode(data["audio_base64"]))
        meta.write_text(json.dumps({"text": text, "voice": voice["voice_id"], "model": voice["model"], "prefix": prefix,
                                    "seed": seed, "words": words}, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"  spoken ({len(text)} characters billed): {text[:60]}")
    return mp3, json.loads(meta.read_text(encoding="utf-8"))["words"]


def decode(path, sr=SR):
    raw = subprocess.run([ffmpeg_bin(), "-nostdin", "-hide_banner", "-loglevel", "error", "-i", str(path),
                          "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).copy()


def build(V, key=None, allow_api=True):
    """speak every line and place it on the timeline -> list of line dicts with audio, word and caption times"""
    voice = V["voice"]
    out = []
    for ln in lines(V):
        sid = ln["scene"]["id"]
        mp3, words = synthesize(ln["text"], voice, (voice.get("seeds") or {}).get(sid), key, allow_api)
        x = decode(mp3)
        loud = np.flatnonzero(np.abs(x) > 0.012)
        cut = max(0, int(loud[0]) - int(0.03 * SR)) if len(loud) else 0      # drop leading silence, keep the whole tail
        x = x[cut:]
        shift = cut / SR
        words = [{"text": w["text"], "start": max(0.0, w["start"] - shift), "end": max(0.0, w["end"] - shift)} for w in words]
        start = ln["scene"]["start"] + (voice.get("leads") or {}).get(sid, voice.get("lead", 0.3))
        counts = [len(spoken(c).split()) for c in ln["captions"]]
        ok = sum(counts) == len(words)
        cues, i = [], 0
        for c, n in zip(ln["captions"], counts):
            if ok:
                a, b = words[i]["start"], words[i + n - 1]["end"]
            else:                                    # timings do not match the text: spread by share of words
                a, b = (len(x) / SR) * i / sum(counts), (len(x) / SR) * (i + n) / sum(counts)
            cues.append([start + a - LEAD_IN, start + b + TAIL_OUT])
            i += n
        for j in range(len(cues) - 1):               # captions of one line follow each other without a gap
            cues[j][1] = cues[j + 1][0]
        cues[0][0] = max(cues[0][0], 0.0)
        cues[-1][1] = min(cues[-1][1], ln["scene"]["end"] - 0.05)      # a caption never outlives its scene
        out.append({**ln, "audio": x, "words": words, "start": start, "duration": len(x) / SR, "cues": cues,
                    "timed": ok, "mp3": mp3})
    return out


def write_track(V, built, path=None):
    path = Path(path or BUILD / "audio" / "vo.wav")
    path.parent.mkdir(parents=True, exist_ok=True)
    n = int(round(V["duration"] * SR))
    track = np.zeros(n, dtype=np.float32)
    for ln in built:
        i = int(round(ln["start"] * SR))
        seg = ln["audio"][:max(0, n - i)]
        track[i:i + len(seg)] += seg
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(track, -1, 1) * 32767).astype("<i2").tobytes())
    return path


def sync_captions(built):
    """write caption start/end (from the voice) back into content.js; every caption sits on its own line there"""
    src = CONTENT.read_text(encoding="utf-8")
    changed = 0
    for ln in built:
        for c, (a, b) in zip(ln["captions"], ln["cues"]):
            needle = '"text": ' + json.dumps(c["text"], ensure_ascii=False)
            rows = [r for r in src.splitlines() if needle in r]
            if len(rows) != 1:
                sys.exit(f"cannot find exactly one caption line for: {c['text']}")
            new = re.sub(r'"start":\s*[\d.]+', f'"start": {a:.2f}', rows[0])
            new = re.sub(r'"end":\s*[\d.]+', f'"end": {b:.2f}', new)
            changed += new != rows[0]
            src = src.replace(rows[0], new)
    CONTENT.write_text(src, encoding="utf-8")
    return changed


NIQQUD = re.compile(r"[֑-ׇ]")
PUNCT = re.compile(r"[^\w֐-׿]+")


def norm(word):
    return PUNCT.sub("", NIQQUD.sub("", word)).lower()


def check(built, model_dir):
    """transcribe each line with a local faster-whisper model and list words that differ from the text"""
    from faster_whisper import WhisperModel
    model = WhisperModel(str(model_dir), device="cpu", compute_type="int8", cpu_threads=8)
    bad_total = 0
    for ln in built:
        segs, _ = model.transcribe(decode(ln["mp3"], 16000), language="he", beam_size=5, vad_filter=False,
                                   condition_on_previous_text=False)
        heard = " ".join(s.text.strip() for s in segs)
        a, b = [norm(w) for w in ln["text"].split()], [norm(w) for w in heard.split()]
        diffs = [(" ".join(a[i1:i2]) or "—", " ".join(b[j1:j2]) or "—")
                 for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(a=a, b=b, autojunk=False).get_opcodes() if tag != "equal"]
        bad_total += len(diffs)
        print(f"\n[{ln['scene']['id']}] sent : {ln['text']}\n{' ' * (len(ln['scene']['id']) + 3)}heard: {heard}")
        for want, got in diffs:
            print(f"      differs: “{want}” -> “{got}”")
    print(f"\n{bad_total} difference(s). Latin terms and numbers are often written differently by the transcriber; read them by eye.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--env-file", help="a .env file that holds ELEVENLABS_API_KEY")
    ap.add_argument("--no-sync", action="store_true", help="do not rewrite caption timings in content.js")
    ap.add_argument("--check", action="store_true", help="transcribe the lines and compare with the text")
    ap.add_argument("--whisper", default=os.environ.get("WHISPER_MODEL", ""), help="folder of a faster-whisper model (for --check)")
    a = ap.parse_args()

    V = load_video()
    if "voice" not in V:
        sys.exit('content.js has no "voice" section')
    built = build(V, api_key(a.env_file))
    if not a.no_sync:
        n = sync_captions(built)
        print(f"caption timings: {n} updated in content.js" if n else "caption timings: already in sync")
    track = write_track(V, built)
    print(f"\n{'scene':8} {'starts':>7} {'voice':>6} {'ends':>7} {'scene ends':>10}  fit")
    for ln in built:
        end, limit = ln["start"] + ln["duration"], ln["scene"]["end"]
        rate = len(ln["words"]) / max(ln["words"][-1]["end"] - ln["words"][0]["start"], 0.1) if ln["words"] else 0
        note = "ok" if end <= limit - 0.1 else "ok (tight)" if end <= limit else f"RUNS {end - limit:.2f} s PAST ITS SCENE"
        if not ln["timed"]:
            note += " · word timings do not match the text (captions spread evenly)"
        print(f"{ln['scene']['id']:8} {ln['start']:7.2f} {ln['duration']:6.2f} {end:7.2f} {limit:10.2f}  {note}  ({rate:.1f} words/s)")
    print(f"\n-> {track}")
    if a.check:
        if not a.whisper:
            sys.exit("--check needs --whisper <folder of a faster-whisper model> (or WHISPER_MODEL)")
        check(built, a.whisper)


if __name__ == "__main__":
    main()
