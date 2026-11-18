/* Practec · DevOps Bootcamp + FDE Practitioner — marketing video script (single source for text + timing).

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
   nowrap    phrases a caption must never break inside (the programme name).
   sfx       sound cues: seconds after the scene start, or after the caption named by "cue".
   cta       end-card button. Leave "url" empty until there is a real public page — nothing is invented.

   The Python tools read everything after the assignment below as strict JSON:
   double quotes only, no comments or trailing commas inside the object, one caption per line. */
window.VIDEO = {
  "title": "Practec DevOps Bootcamp + FDE Practitioner",
  "nowrap": ["+ FDE Practitioner", "FDE Practitioner", "DevOps Bootcamp", "של Practec להייטק."],
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
    {"scene": "brand",  "start": 4.30,   "end": 9.21,   "text": "הכירי את DevOps Bootcamp + FDE Practitioner של Practec להייטק.", "say": "הכירי את DevOps Bootcamp פלוס FDE Practitioner של Practec להייטק."},
    {"scene": "build",  "start": 10.30,  "end": 12.22,  "text": "*8 שבועות* של DevOps Bootcamp,", "say": "שמונה שבועות של DevOps Bootcamp,"},
    {"scene": "build",  "start": 12.22,  "end": 17.21,  "text": "ו-*6 שבועות* של FDE Practitioner — *עד לפרודקשן אצל לקוח אמיתי.*", "say": "ושישה שבועות של FDE Practitioner, עד לפרודקשן אצל לקוח אמיתי."},
    {"scene": "facts",  "start": 18.29,  "end": 21.18,  "text": "הרצאה שבועית ו-*6 שעות* עבודת צוות על הפרויקט.", "say": "הרצאה שבועית ושש שעות עבודת צוות על הפרויקט."},
    {"scene": "facts",  "start": 21.18,  "end": 23.53,  "text": "עד *20 משתתפות* נבחרות.", "say": "עד עשרים משתתפות נבחרות."},
    {"scene": "career", "start": 24.29,  "end": 26.54,  "text": "המסלול כולל *הכנה מקצועית לקריירה.*"},
    {"scene": "career", "start": 26.54,  "end": 29.93,  "id": "notice", "text": "הקבלה מותנית במיון; אין התחייבות להשמה.", "say": "הקבלה מותנית במיון. אין התחייבות להשמה."},
    {"scene": "dates",  "start": 30.30,  "end": 33.26,  "id": "date1", "text": "משימת המיון מתפרסמת *ב-29 בנובמבר,*", "say": "משימת המיון מתפרסמת בעשרים ותשעה בנובמבר,"},
    {"scene": "dates",  "start": 33.26,  "end": 35.66,  "id": "date2", "text": "וההגשה עד *6 בדצמבר.*", "say": "וההגשה עד השישה בדצמבר."},
    {"scene": "dates",  "start": 35.66,  "end": 38.49,  "id": "date3", "text": "הקורס נפתח *ב-13 בדצמבר.*", "say": "הקורס נפתח בשלושה עשר בדצמבר."},
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
    {"cue": "date3",    "at": 0.0,   "type": "blip"},
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
