/* Practec · FDE + DevOps Bootcamp — marketing video script (single source for text + timing).

   scenes    start/end in seconds, on the beat of the 120 bpm music (whole seconds; 2 s = one bar).
             tools/music.py follows the scenes; the animations in scenes.js are scene-relative.
   voice     the ElevenLabs voice that speaks the captions (tools/voiceover.py). All captions of a scene are
             spoken as one line that starts "lead" seconds into the scene. "seeds": {"dates": 2} asks for
             another take of that scene's line.
   captions  burned-in Hebrew captions = the voice-over script. *text* marks an accent colour.
             "say"  what the voice receives when it must differ from the caption (numbers as words, + as פלוס).
             "hero" shown as the big opening typography instead of the caption strip.
             "id"   lets a picture or sound follow this caption (see "cue" below and scenes.js).
             start/end are written by tools/voiceover.py from the voice's word timings — do not edit by hand.
   sfx       sound cues: seconds after the scene start, or after the caption named by "cue".
   cta       end-card button. Leave "url" empty until there is a real public page — nothing is invented.

   The Python tools read everything after the assignment below as strict JSON:
   double quotes only, no comments or trailing commas inside the object, one caption per line. */
window.VIDEO = {
  "title": "Practec FDE + DevOps Bootcamp",
  "fps": 30,
  "duration": 44.0,
  "bpm": 120,
  "scenes": [
    {"id": "hook",   "start": 0.0,  "end": 4.0,  "music": "intro"},
    {"id": "brand",  "start": 4.0,  "end": 10.0, "music": "lift"},
    {"id": "build",  "start": 10.0, "end": 18.0, "music": "groove"},
    {"id": "facts",  "start": 18.0, "end": 24.0, "music": "groove"},
    {"id": "career", "start": 24.0, "end": 30.0, "music": "break"},
    {"id": "dates",  "start": 30.0, "end": 39.0, "music": "groove"},
    {"id": "end",    "start": 39.0, "end": 44.0, "music": "outro"}
  ],
  "voice": {
    "name": "Tamar (ElevenLabs)",
    "voice_id": "p7J75VowGmxi3K0it9lN",
    "model": "eleven_v4",
    "prefix": "[rapid-fire, energetic]",
    "lead": 0.3,
    "leads": {"hook": 0.0},
    "seeds": {}
  },
  "captions": [
    {"scene": "hook",   "start": 0.06,   "end": 1.59,   "hero": true, "text": "את כבר יודעת לבנות תוכנה."},
    {"scene": "hook",   "start": 1.59,   "end": 3.95,  "hero": true, "text": "מוכנה להביא פתרונות עד *לפרודקשן?*"},
    {"scene": "brand",  "start": 4.36,   "end": 8.33,   "text": "הכירי את FDE + DevOps Bootcamp של Practec להייטק.", "say": "הכירי את FDE פלוס DevOps Bootcamp של Practec להייטק."},
    {"scene": "build",  "start": 10.43,  "end": 14.46,  "text": "שנים עשר שבועות של FDE, פתרונות AI, ענן ו-DevOps", "say": "שנים עשר שבועות של FDE, פתרונות AI, ענן ו-DevOps,"},
    {"scene": "build",  "start": 14.46,  "end": 17.13, "text": "עם פרויקטים מעשיים *מקצה לקצה.*"},
    {"scene": "facts",  "start": 18.30,  "end": 21.50,  "text": "*64 שעות* מפגש, תרגול וליווי מקצועי.", "say": "שישים וארבע שעות מפגש, תרגול וליווי מקצועי."},
    {"scene": "facts",  "start": 21.50,  "end": 23.85,  "text": "עד *20 משתתפות* נבחרות.", "say": "עד עשרים משתתפות נבחרות."},
    {"scene": "career", "start": 24.29,  "end": 26.54,  "text": "המסלול כולל *הכנה מקצועית לקריירה.*"},
    {"scene": "career", "start": 26.54,  "end": 29.93,  "id": "notice", "text": "הקבלה מותנית במיון; אין התחייבות להשמה.", "say": "הקבלה מותנית במיון. אין התחייבות להשמה."},
    {"scene": "dates",  "start": 30.28,  "end": 32.52,  "text": "מחזור *נובמבר 2026.*", "say": "מחזור נובמבר אלפיים עשרים ושש."},
    {"scene": "dates",  "start": 32.52,  "end": 35.32,  "id": "date1", "text": "מתחילות בתהליך המיון *ב-19 בנובמבר,*", "say": "מתחילות בתהליך המיון בתשעה עשר בנובמבר,"},
    {"scene": "dates",  "start": 35.32,  "end": 38.95,  "id": "date2", "text": "ויום ההערכה יתקיים *ב-25 בנובמבר.*", "say": "ויום ההערכה יתקיים בעשרים וחמישה בנובמבר."},
    {"scene": "end",    "start": 39.30, "end": 41.73,  "text": "בדקי התאמה *והגישי מועמדות.*"}
  ],
  "sfx": [
    {"scene": "hook",   "at": 0.55,  "type": "keys", "dur": 1.1},
    {"scene": "hook",   "at": 1.62,  "type": "keys", "dur": 0.28},
    {"scene": "hook",   "at": 1.95,  "type": "tick"},
    {"scene": "hook",   "at": 2.5,   "type": "blip"},
    {"scene": "hook",   "at": 3.0,   "type": "riser", "dur": 1.0},
    {"scene": "brand",  "at": 0.02,  "type": "impact"},
    {"scene": "brand",  "at": 2.1,   "type": "shimmer"},
    {"scene": "build",  "at": 0.0,   "type": "swoosh"},
    {"scene": "build",  "at": 1.5,   "type": "swoosh"},
    {"scene": "build",  "at": 3.0,   "type": "swoosh"},
    {"scene": "build",  "at": 4.5,   "type": "swoosh"},
    {"scene": "build",  "at": 6.0,   "type": "swoosh"},
    {"scene": "build",  "at": 0.27,  "type": "drop"},
    {"scene": "build",  "at": 4.88,  "type": "check", "step": 0},
    {"scene": "build",  "at": 5.25,  "type": "check", "step": 1},
    {"scene": "build",  "at": 5.63,  "type": "check", "step": 2},
    {"scene": "build",  "at": 6.25,  "type": "success"},
    {"scene": "build",  "at": 7.0,   "type": "riser", "dur": 1.0},
    {"scene": "facts",  "at": 0.0,   "type": "impact", "gain": 0.6},
    {"scene": "facts",  "at": 0.4,   "type": "tick"},
    {"scene": "facts",  "at": 0.52,  "type": "tick"},
    {"scene": "facts",  "at": 0.64,  "type": "tick"},
    {"scene": "facts",  "at": 0.76,  "type": "tick"},
    {"scene": "career", "at": 0.4,   "type": "check", "step": 0},
    {"scene": "career", "at": 0.75,  "type": "check", "step": 1},
    {"scene": "career", "at": 1.1,   "type": "check", "step": 2},
    {"cue": "notice",   "at": 0.0,   "type": "blip"},
    {"scene": "career", "at": 5.55,  "type": "swoosh"},
    {"cue": "date1",    "at": 0.0,   "type": "blip"},
    {"cue": "date2",    "at": 0.0,   "type": "blip"},
    {"scene": "dates",  "at": 8.0,   "type": "riser", "dur": 1.0},
    {"scene": "end",    "at": 0.02,  "type": "impact", "gain": 0.8},
    {"scene": "end",    "at": 0.8,   "type": "pop"},
    {"scene": "end",    "at": 2.6,   "type": "shimmer", "gain": 0.6}
  ],
  "cta": {
    "label": "הגישי מועמדות",
    "note": "להרשמה לתהליך המיון — בעמוד הקורס",
    "url": ""
  }
};
