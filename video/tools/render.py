"""Render the Practec FDE + DevOps Bootcamp video.

Chrome (driven by Playwright) paints composition/index.html one frame at a time (window.__seek(t)); the PNG
sequence is encoded with ffmpeg; the music bed is synthesized by music.py and the voice comes from voiceover.py's cache
(run voiceover.py after changing caption text). The mix is loudness-normalised (EBU R128, -14 LUFS) and muxed in. Everything is deterministic: the same files always give the same video.

    python video/tools/render.py                        # 9:16 primary cut -> video/output/practec-bootcamp-9x16.mp4
                                                        #   (voice + music; also -music.mp4, -silent.mp4 and .srt)
    python video/tools/render.py --format 16x9          # landscape cut    -> video/output/practec-bootcamp-16x9.mp4
    python video/tools/render.py --reuse                # picture unchanged: keep the video, redo the audio + captions file
    python video/tools/render.py --reuse --vo vo.wav    # use a recorded voice-over file instead of the ElevenLabs lines
    python video/tools/render.py --range 10 20          # only 10-20 s     -> video/output/preview-9x16-10-20.mp4
    python video/tools/render.py --stills 1.2,6,19.4    # QA stills        -> video/build/stills/9x16/ (+ sheet.png)
    python video/tools/render.py --stills 6 --safe      # ... with the social safe-zone overlay drawn on top
    python video/tools/render.py --stills 8.5 --no-captions   # clean frame, e.g. for a cover image

Requirements: Google Chrome; Python 3.10+ with playwright, numpy, pillow and (unless ffmpeg is on PATH) imageio-ffmpeg.
"""
import argparse
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
VIDEO_DIR = HERE.parent
COMP = VIDEO_DIR / "composition" / "index.html"
BUILD = VIDEO_DIR / "build"
OUT = VIDEO_DIR / "output"
SIZES = {"9x16": (1080, 1920), "16x9": (1920, 1080)}
LOUDNORM = "loudnorm=I=-14:TP=-1.5:LRA=11"
sys.path.insert(0, str(HERE))


def ffmpeg_bin():
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        sys.exit("ffmpeg not found: `brew install ffmpeg` or `pip install imageio-ffmpeg`")


def run(cmd):
    cmd = [str(c) for c in cmd]
    r = subprocess.run(cmd, text=True, capture_output=True)
    if r.returncode:
        sys.exit(f"command failed ({r.returncode}): {' '.join(cmd)}\n{r.stderr[-3000:]}")
    return r


def load_video():
    src = (VIDEO_DIR / "composition" / "content.js").read_text(encoding="utf-8")
    body = re.split(r"^window\.VIDEO\s*=", src, maxsplit=1, flags=re.M)[1].strip().rstrip(";")
    return json.loads(body)


def open_page(p, fmt, query=""):
    W, H = SIZES[fmt]
    browser = p.chromium.launch(channel="chrome", headless=True,
                                args=["--force-device-scale-factor=1", "--hide-scrollbars", "--font-render-hinting=none"])
    page = browser.new_context(viewport={"width": W, "height": H}, device_scale_factor=1).new_page()
    problems = []
    page.on("pageerror", lambda e: problems.append(f"pageerror: {e}"))
    page.on("console", lambda m: problems.append(f"console.error: {m.text}") if m.type == "error" else None)
    page.goto(COMP.as_uri() + "?render&format=" + fmt + query)
    info = page.evaluate("() => window.__ready")
    return browser, page, info, problems


def shoot(job):
    """worker: paint and save a list of (t, path) frames in one Chrome"""
    fmt, query, frames = job
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser, page, info, problems = open_page(p, fmt, query)
        for t, path in frames:
            for attempt in range(4):             # a busy machine can stall one capture: try again, same frame
                try:
                    page.evaluate("t => window.__seek(t)", t)
                    page.screenshot(path=path, type="png", timeout=20000)
                    break
                except Exception:
                    if attempt == 3:
                        raise
        browser.close()
    return info, problems


def report(info, problems):
    families = sorted({f.rsplit(" ", 2)[0] for f in info.get("fonts", [])})
    print(f"page ready · {info['format']} · {info['fps']:g} fps · {info['duration']:g} s · fonts: {', '.join(families) or 'NONE'}")
    if problems:
        print("page problems:\n  " + "\n  ".join(problems))


def sheet(paths, out, cols=4):
    from PIL import Image
    ims = [Image.open(p) for p in paths]
    w, h = ims[0].size
    tw = 405 if w < h else 640
    th = round(h * tw / w)
    rows = math.ceil(len(ims) / cols)
    S = Image.new("RGB", (cols * tw, rows * th), "#2A2A2A")
    for i, im in enumerate(ims):
        S.paste(im.convert("RGB").resize((tw, th), Image.LANCZOS), ((i % cols) * tw, (i // cols) * th))
    S.save(out)


def voice_track(V, vo_file=None):
    """the voice-over as a wav on the video's timeline: a recorded file, or the cached ElevenLabs lines"""
    if vo_file:
        return Path(vo_file)
    if not V.get("voice"):
        return None
    import voiceover
    return voiceover.write_track(V, voiceover.build(V, allow_api=False))     # cache only: rendering never bills


def make_audio(V, ff, vo=None):
    """music bed, with the voice on top when `vo` is given (the music ducks under it) -> loudness-normalised wav"""
    import music
    adir = BUILD / "audio"
    adir.mkdir(parents=True, exist_ok=True)
    src = music.build(V, adir / "music.wav")
    if vo:
        bed = adir / "music+vo.wav"
        run([ff, "-y", "-hide_banner", "-loglevel", "error", "-i", src, "-i", vo, "-filter_complex",
             "[0:a]volume=0.2[m];"                 # between lines the music sits about 7 dB under the voice
             "[1:a]aresample=48000,aformat=channel_layouts=stereo,asplit=2[vo][key];"
             "[m][key]sidechaincompress=threshold=0.02:ratio=9:attack=15:release=400:makeup=1[bed];"
             f"[bed][vo]amix=inputs=2:duration=longest:normalize=0,apad=whole_dur={V['duration']}[m2]",
             "-map", "[m2]", "-t", str(V["duration"]), "-c:a", "pcm_s16le", bed])
        src = bed
    r = run([ff, "-hide_banner", "-nostats", "-i", src, "-af", LOUDNORM + ":print_format=json", "-f", "null", "-"])
    m, _ = json.JSONDecoder().raw_decode(r.stderr[r.stderr.rindex("{"):])     # ffmpeg prints more after the JSON
    mix = adir / ("mix.wav" if vo or not V.get("voice") else "mix-music.wav")   # mix.wav is what the browser preview plays
    run([ff, "-y", "-hide_banner", "-loglevel", "error", "-i", src, "-af",
         f"{LOUDNORM}:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
         f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true",
         "-ar", "48000", "-t", str(V["duration"]), "-c:a", "pcm_s16le", mix])
    print(f"audio: {'voice + music' if vo else 'music bed'} {m['input_i']} LUFS -> -14 LUFS (true peak <= -1.5 dBTP)")
    return mix


def write_srt(V, path, t0=0.0, t1=None):
    def ts(s):
        ms = int(round(s * 1000))
        return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"
    t1 = V["duration"] if t1 is None else t1
    rows, k = [], 0
    for c in V["captions"]:
        a, b = max(c["start"], t0) - t0, min(c["end"], t1) - t0
        if b <= a:
            continue
        k += 1
        rows += [str(k), f"{ts(a)} --> {ts(b)}", c["text"].replace("*", ""), ""]
    path.write_text("\n".join(rows), encoding="utf-8")


def contact_sheet(mp4, out, fmt, ff):
    cols, w = (11, 216) if fmt == "9x16" else (8, 320)
    rows = math.ceil(load_video()["duration"] * 2 / cols)
    run([ff, "-y", "-hide_banner", "-loglevel", "error", "-i", mp4, "-vf", f"fps=2,scale={w}:-2,tile={cols}x{rows}",
         "-frames:v", "1", out])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--format", choices=SIZES, default="9x16")
    ap.add_argument("--fps", type=float, help="default: fps in content.js")
    ap.add_argument("--range", nargs=2, type=float, metavar=("FROM", "TO"), help="render only this part (seconds)")
    ap.add_argument("--stills", help="comma-separated seconds: save PNG stills instead of a video")
    ap.add_argument("--safe", action="store_true", help="draw the social safe-zone overlay (QA only)")
    ap.add_argument("--no-captions", action="store_true", help="hide the caption strip (clean stills / cover)")
    ap.add_argument("--silent", action="store_true", help="only the version without an audio track")
    ap.add_argument("--vo", help="use this recorded voice-over file (aligned to 0:00) instead of the ElevenLabs lines")
    ap.add_argument("--no-voice", action="store_true", help="skip the voice-over: only the music and silent versions")
    ap.add_argument("--reuse", action="store_true", help="picture unchanged: reuse output/...-silent.mp4, redo audio + .srt only")
    ap.add_argument("--keep-frames", action="store_true", help="keep build/frames (about 1.5 GB of PNGs) after encoding")
    ap.add_argument("--workers", type=int, default=max(1, min(8, (os.cpu_count() or 4) - 2)))
    ap.add_argument("--crf", type=int, default=17)
    a = ap.parse_args()

    V = load_video()
    fps = a.fps or V.get("fps", 30)
    fmt = a.format
    ff = ffmpeg_bin()
    query = ("&safe" if a.safe else "") + ("&nocap" if a.no_captions else "")

    if a.stills:
        d = BUILD / "stills" / fmt
        d.mkdir(parents=True, exist_ok=True)
        suffix = ("-safe" if a.safe else "") + ("-clean" if a.no_captions else "")
        frames = [(t, str(d / f"t{t:06.2f}{suffix}.png")) for t in (float(x) for x in a.stills.split(","))]
        info, problems = shoot((fmt, query, frames))
        report(info, problems)
        sheet([f for _, f in frames], d / f"sheet{suffix}.png")
        print("stills ->", d)
        return

    t0, t1 = a.range or (0.0, float(V["duration"]))
    n = int(round((t1 - t0) * fps))
    OUT.mkdir(exist_ok=True)
    stem = f"practec-bootcamp-{fmt}" if not a.range else f"preview-{fmt}-{t0:g}-{t1:g}"
    silent = OUT / f"{stem}-silent.mp4"

    if a.reuse and silent.exists():
        print(f"reusing the picture of {silent.name}")
    else:
        frames_dir = BUILD / "frames" / fmt
        shutil.rmtree(frames_dir, ignore_errors=True)
        frames_dir.mkdir(parents=True)
        frames = [(t0 + i / fps, str(frames_dir / f"{i:05d}.png")) for i in range(n)]
        workers = max(1, min(a.workers, n))
        jobs = [(fmt, query, frames[i::workers]) for i in range(workers)]      # interleaved: balanced, order-independent
        started = time.time()
        print(f"rendering {n} frames · {fmt} · {fps:g} fps · {workers} Chrome workers")
        with ProcessPoolExecutor(workers) as ex:
            results = list(ex.map(shoot, jobs))
        report(*results[0])
        for _, problems in results[1:]:
            if problems:
                print("  " + "\n  ".join(problems))
        print(f"frames done in {time.time() - started:.0f} s")
        # sRGB frames -> BT.709 limited-range 4:2:0, tagged so every player decodes the brand colours the same way
        run([ff, "-y", "-hide_banner", "-loglevel", "error", "-framerate", f"{fps:g}", "-i", frames_dir / "%05d.png",
             "-vf", "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p,"
                    "setparams=colorspace=bt709:color_primaries=bt709:color_trc=bt709:range=tv",
             "-c:v", "libx264", "-preset", "slow", "-crf", str(a.crf), "-profile:v", "high", "-level", "4.2",
             "-r", f"{fps:g}", "-movflags", "+faststart", silent])
        if not a.keep_frames:
            shutil.rmtree(frames_dir, ignore_errors=True)
        if not a.range:
            contact_sheet(silent, BUILD / f"sheet-{fmt}.png", fmt, ff)

    def mux(mix, name):
        out = OUT / name
        run([ff, "-y", "-hide_banner", "-loglevel", "error", "-i", silent, "-ss", f"{t0:g}", "-t", f"{t1 - t0:g}", "-i", mix,
             "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out])
        return out

    made = [silent]
    if not a.silent:
        vo = None if a.no_voice else voice_track(V, a.vo)
        if vo:                                   # main file: voice + music; the music-only cut is kept beside it
            made.insert(0, mux(make_audio(V, ff, None), f"{stem}-music.mp4"))
            made.insert(0, mux(make_audio(V, ff, vo), f"{stem}.mp4"))
        else:
            made.insert(0, mux(make_audio(V, ff, None), f"{stem}{'-music' if V.get('voice') else ''}.mp4"))
    write_srt(V, OUT / f"{stem}.srt", t0, t1)
    for f in made:
        print("->", f, f"({f.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
