# Practec · FDE + DevOps Bootcamp — marketing video

A 44-second motion-graphics video for the bootcamp, built from `../course-creative-brief.md`.
Campaign line: **לא רק לפתח. להביא פתרונות לפרודקשן.**

| File in `output/` | What it is |
|---|---|
| `practec-bootcamp-9x16.mp4` | **Primary cut** — 1080×1920, 30 fps, captions burned in, voice-over (Tamar) over the music bed |
| `practec-bootcamp-9x16-music.mp4` | Same picture, music only (no voice) |
| `practec-bootcamp-9x16-silent.mp4` | Same picture, no audio track |
| `practec-bootcamp-16x9*.mp4` | Landscape cut, 1920×1080 (same scenes, two-column layout), in the same three versions |
| `practec-bootcamp-9x16.srt`, `…-16x9.srt` | The captions as a subtitle file (they are already burned into the picture) |
| `practec-bootcamp-9x16-cover.png`, `…-16x9-cover.png` | Cover / thumbnail frames without the caption strip |

## Render

The video is an HTML/CSS/JS composition. Chrome paints it frame by frame (through Playwright), ffmpeg encodes the
frames, the music is synthesized by `tools/music.py`, and the voice lines come from the cache in `voice/`.
Run from the project root (`Practec/`):

```bash
python video/tools/render.py                  # 9:16 primary cut (+ music-only, silent, .srt)   about 1 minute
python video/tools/render.py --format 16x9    # landscape cut
python video/tools/render.py --reuse          # picture unchanged: redo only the audio + .srt
python video/tools/render.py --help           # stills, safe-zone overlay, partial renders, --no-voice …
```

Requirements: Google Chrome, and Python 3.10+ with the packages in `requirements.txt`
(`python3 -m venv video/.venv && video/.venv/bin/pip install -r video/requirements.txt`, then use
`video/.venv/bin/python`). Playwright drives the installed Chrome, so no browser download is needed; ffmpeg comes
from the `imageio-ffmpeg` package unless `ffmpeg` is already on your PATH.

Every frame is a pure function of its timestamp, so the same sources always produce the same video.
Intermediate files go to `build/` (safe to delete). `voice/` is not intermediate: it holds the paid voice lines.

## Voice-over

The captions are the script. `tools/voiceover.py` sends each scene's captions to ElevenLabs as one line, caches the
audio and its word timings in `voice/`, and writes the caption start/end times back into `content.js`, so the
captions and the pictures that follow them (the selection notice, the two dates) stay on the voice.

```bash
python video/tools/voiceover.py --env-file path/to/.env     # only after changing caption text or the voice
python video/tools/render.py                                 # rendering reads the cache; it never calls ElevenLabs
```

- **Voice:** "Tamar" (`p7J75VowGmxi3K0it9lN`) on `eleven_v4` with the style tag `[rapid-fire, energetic]` — the
  same recipe as the Follow Up videos. It is set under `"voice"` in `content.js`.
- **Key and cost:** the key is read from `ELEVENLABS_API_KEY`, `--env-file` or `video/.env`, and is never printed.
  Only new or changed lines are billed (the whole script is about 470 characters).
- **Text for the voice:** a caption's optional `"say"` is what the voice receives when it must differ from what is
  written: numbers as Hebrew words (digits are unreliable), `+` as "פלוס". Keep the same number of words.
- **Another take:** the voice is not deterministic. `"seeds": {"dates": 2}` under `"voice"` asks for a new take of
  that scene's line (billed once).
- **Fit:** the tool prints how each line fits its scene and says when one runs long. The voice is never
  stretched: shorten the text or lengthen the scene.
- **Check without listening:** `--check --whisper <folder of a faster-whisper model>` transcribes every line and
  lists words that differ from the text. It cannot judge stress or tone — listen once before publishing.
- **Mix:** the music drops to about 6 dB under the voice between lines and ducks further while she speaks
  (sidechain, ratio 9); the result is normalised to −14 LUFS. `--vo file.wav` uses a recorded voice instead.

## Preview and edit

Open `composition/index.html` in Chrome for a live preview: **Space** plays, **←/→** steps one frame
(**Shift** = one second), the menu switches 9:16 / 16:9, and "safe zones" shows the platform-UI margins.
After a render the preview also plays the soundtrack.

| To change… | Edit |
|---|---|
| Caption text, scene lengths, the voice, CTA label / note / URL, sound cues | `composition/content.js` |
| Text inside the scenes (titles, numbers, dates, prices, fine print) | `composition/index.html` |
| Colours, fonts, sizes, positions; the 16:9 layout (last section) | `composition/style.css` |
| Motion (what animates when, relative to each scene's start) | `composition/scenes.js` |
| The music and sound effects | `tools/music.py` |

- **CTA link:** the end card shows no URL because none is confirmed. When the public page is live, set
  `"url"` under `"cta"` in `content.js`; it replaces the note under the button. (On the landing page the
  application section is the `#apply` anchor.)
- **Scene lengths:** keep scene boundaries on whole seconds (the music is 120 bpm, one bar per 2 s, and follows
  the scene list). After changing a length, run `voiceover.py` again so the captions move with it.
- **Course facts** appear in `index.html` (scenes 4–7). They follow `../course-creative-brief.md`, with two
  later changes from the owner: the hours are shown as 64 hours = 12 × 3 session hours + practice, and the AIOps
  continuation is shown with its lecturer (גל חבקין) and without a price.

## Timeline

| Time | Scene | Picture | Voice-over = caption |
|---|---|---|---|
| 0–4 s | `hook` | Code and a terminal running on `localhost`, then a "production ?" target | את כבר יודעת לבנות תוכנה. · מוכנה להביא פתרונות עד לפרודקשן? |
| 4–10 s | `brand` | Logo, "FDE + DevOps Bootcamp", campaign line | הכירי את FDE + DevOps Bootcamp של Practec להייטק. |
| 10–18 s | `build` | One system in five stages: צורך עסקי → תכנון הפתרון → בנייה עם AI → פריסה לענן → פרודקשן | שנים עשר שבועות של FDE, פתרונות AI, ענן ו-DevOps · עם פרויקטים מעשיים מקצה לקצה. |
| 18–24 s | `facts` | 12 weeks · 64 hours of sessions and practice · 12 × 3 session hours + practice · up to 20 participants; days, hours, planned location | 64 שעות מפגש, תרגול וליווי מקצועי. · עד 20 משתתפות נבחרות. |
| 24–30 s | `career` | What the track includes; optional AIOps continuation with its lecturer; selection and "אין התחייבות להשמה" | המסלול כולל הכנה מקצועית לקריירה. · הקבלה מותנית במיון; אין התחייבות להשמה. |
| 30–39 s | `dates` | 19.11 selection fee + assignment (350 ₪, non-refundable if not accepted) · 25.11 assessment day | מחזור נובמבר 2026. · מתחילות בתהליך המיון ב-19 בנובמבר, · ויום ההערכה יתקיים ב-25 בנובמבר. |
| 39–44 s | `end` | Logo, programme, organisation, CTA, tuition and selection fee with its qualifier | בדקי התאמה והגישי מועמדות. |

The first two lines are shown as large opening typography instead of the caption strip.

## Safe margins (9:16)

Content sits between y = 280 and 1200, captions between 1230 and 1400, inside a 90 px side margin. The top
250 px and bottom 420 px are left empty for platform UI (TikTok / Reels / Shorts), and right-aligned text stays
clear of the action-button column. Check any frame with
`python video/tools/render.py --stills 8.5,21.5,42 --safe`.

## Assets and licences

- **Logo:** `../assets/practec-logo.svg`, loaded directly and shown whole on light surfaces — not redrawn,
  recoloured or cropped. (`practec-logo-white.svg` is not used: all logo moments are on light backgrounds.)
- **Fonts:** Heebo and JetBrains Mono, both SIL Open Font License (licence texts in `composition/fonts/`).
- **Voice:** generated with ElevenLabs on a paid plan; the audio lives in `voice/`.
- **Music and all graphics:** created in this project (`tools/music.py`; no samples, no third-party recordings).
  No stock footage, testimonials or employer logos.
- **Brief note:** the brief lists mint `#A9FCC1` as "from the logo". The logo SVG contains no mint — that value
  is the start of its gradient's element id (`#a9fcc1bc-…`). It is used here as the brief asks, as a small accent.
