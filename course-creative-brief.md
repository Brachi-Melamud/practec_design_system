# Practec FDE + DevOps Bootcamp
## Creative direction and production prompts

### The course theme

**From software developer to engineer who brings solutions to life.**

Hebrew campaign line: **לא רק לפתח. להביא פתרונות לפרודקשן.**

The bootcamp helps experienced women developers extend their technical strengths into Forward Deployed Engineering, applied AI, and DevOps. The story is about connecting business needs to working systems: understand the problem, design the solution, build it, deploy it, and prepare it for production.

This is a selective, hands-on professional training program—not a promise of a job or guaranteed placement. Keep the tone ambitious, grounded, technically credible, and welcoming. Speak directly to technically strong women developers without suggesting they need to start their careers over.

### Message hierarchy

1. **Core promise:** Expand your software engineering skill set to design, build, and deploy real-world AI-enabled solutions.
2. **Program:** 12 weeks, 64 live hours across sixteen 4-hour sessions, up to 20 selected participants.
3. **Learning:** FDE and solution engineering; applied AI (LLMs, agents, RAG, APIs, automations); cloud and DevOps (Docker, CI/CD, GitHub Actions, deployment); production readiness; end-to-end projects.
4. **Additional value:** Career-readiness support; optional two-week AIOps continuation.
5. **Application:** Selection includes a take-home assignment and a professional assessment day.
6. **Expectation-setting:** Career support and relevant opportunity connections are offered, but employment or placement is not guaranteed.

Suggested headline: **לא רק לפתח. להביא פתרונות לפרודקשן.**

Suggested supporting line: **בוטקאמפ מעשי וסלקטיבי למפתחות תוכנה שרוצות להרחיב את היכולות שלהן ב-FDE, DevOps ו-AI.**

### Brand and visual direction

- Use the supplied Practec logo assets: `assets/practec-logo.svg` for light backgrounds and `assets/practec-logo-white.svg` for dark backgrounds. Keep the original SVG proportions and colors; do not redraw, recolor, crop, or replace it with a text approximation.
- Practec logo gradient: warm red `#B4373D` to magenta-purple `#B23ACB`. Supporting mint from the logo: `#A9FCC1`.
- Build the visual system around the logo gradient, deep ink/navy, generous white or warm-neutral space, and restrained mint accents. The gradient should be an accent—not a substitute logo or an excuse for a generic neon/AI aesthetic.
- Use a clear Hebrew-first RTL layout; keep technical terms such as FDE, DevOps, AI, LLMs, RAG, Docker, and CI/CD in their familiar Latin form.
- Prefer diagrams, terminal-inspired details, system maps, deployment flows, and abstract product-interface visuals. Do not use fabricated student testimonials, employer logos, instructor identities, salary figures, or placement statistics.

### Confirmed course details

- Main program: 12 weeks / 64 live hours / sixteen 4-hour sessions / up to 20 participants.
- Sessions are planned for Sundays and/or Wednesdays, 17:00–21:00; the full session calendar will be shared in advance. Planned location: Nachlaot, Jerusalem.
- Tuition: ₪4,500. Selection and assessment fee: ₪350, non-refundable if not accepted. The selection process includes a project and interview that provide practice in their own right.
- AI/cloud subscriptions needed for practice are not included; disclose estimated services and costs in advance.
- Selection timeline: Thursday, 19 November 2026 — payment of the ₪350 selection fee and receipt of the selection assignment; Wednesday, 25 November 2026 — professional assessment day.
- Optional AIOps continuation: two additional weeks, ₪1,500.
- Employment support is optional and success-based: placement through Practec costs two monthly salaries, paid over four monthly installments; independently finding a job costs one monthly salary if the placement happens within three months after the bootcamp. Do not imply this is included in tuition.
- Organization: Practec להייטק (ע"ר).

## Prompt 1 — Codex: build the landing page

```text
Build or revise the Practec FDE + DevOps Bootcamp landing page in this project. First inspect the existing files, scripts, and assets; preserve the real Practec logo and the working project setup. The course creative direction is in course-creative-brief.md—treat it as the source of truth.

Campaign theme: “לא רק לפתח. להביא פתרונות לפרודקשן.” Present the course as the next professional step for technically strong women software developers: connecting business needs to real, deployed AI-enabled systems through FDE, applied AI, DevOps, production readiness, and end-to-end projects. Use an ambitious, credible, human tone. This is training and career preparation, not a job guarantee.

Requirements:
- Hebrew-first, fully RTL, responsive landing page with a strong first screen and a clear, repeated application CTA.
- Build a coherent information hierarchy: hero and program facts; what participants will learn; practical projects and differentiators; weekly schedule/location; tuition and selection costs; selection dates; optional AIOps continuation; optional success-based employment support; FAQ/expectation-setting; application/contact CTA.
- Keep all course information, costs, dates, eligibility, and terms accurate to course-creative-brief.md. Clearly state that placement is not guaranteed, cloud/AI subscriptions are extra, and the ₪350 selection fee is non-refundable if not accepted. Do not invent instructors, testimonials, partner companies, outcomes, or job statistics.
- Use `assets/practec-logo.svg` on light surfaces and `assets/practec-logo-white.svg` on dark surfaces. Do not recreate, crop, stretch, or recolor the logo. Apply the logo palette (#B4373D, #B23ACB, #A9FCC1) as restrained accents, complemented by ink/navy and clean neutral surfaces. Avoid generic neon gradients and cliché AI imagery.
- Hebrew text must be natural and correctly RTL; keep standard technical names (FDE, DevOps, AI, LLMs, RAG, Docker, CI/CD) readable.
- Make navigation, mobile menu, anchor links, and application interaction work. Do not show a success state for a form that is not actually connected to a submission service; make any integration status explicit and keep secrets out of client code.
- Use semantic HTML, accessible labels/focus states, sensible contrast, responsive layouts, and appropriate page metadata.
- Validate the result with available project checks and a local browser preview if available. Fix issues caused by the changes and report files changed and any remaining setup needed.
```

## Prompt 2 — Claude Code: produce the marketing video

```text
Create a polished marketing video for Practec’s FDE + DevOps Bootcamp, using the course facts and visual direction in course-creative-brief.md. Inspect the current project and available tools first, then implement the simplest reliable video workflow supported by this environment. If there is no video framework yet, do not assume one is installed—use available tools and document any required renderer/export step. Keep source files editable and save the final video project/output within this project.

Creative concept: “לא רק לפתח. להביא פתרונות לפרודקשן.” Follow one clear transformation: a business challenge becomes a designed solution, then an AI-enabled build, a cloud deployment, and a production-ready result. Show the engineering work—not a guaranteed career outcome. Confident, practical, focused, and empowering; avoid hype, stock-like fake office footage, fabricated testimonials, employer logos, or implied job guarantees.

Use the real assets `assets/practec-logo.svg` and `assets/practec-logo-white.svg` as supplied, maintaining their proportions and original colors. Brand palette: #B4373D to #B23ACB gradient, mint #A9FCC1 as a small accent, with deep ink/navy and light neutral backgrounds. Do not redraw or recolor the mark. Use Hebrew captions and RTL-aware composition; retain FDE, DevOps, AI, LLMs, RAG, Docker, and CI/CD in Latin characters where appropriate.

Deliver a 35–45 second primary cut in 9:16 vertical format, with captions burned in and safe margins for social platforms. Also make the project easy to adapt to a 16:9 cut if the chosen tooling permits. Use subtle motion graphics: architecture sketches, API connections, terminal/CI status, deployment flow, and clean kinetic typography. Use only assets available in the project or clearly licensed/created assets; no unlicensed music or footage. If audio is unavailable, create a complete captioned silent version and note that voiceover/music are optional additions.

Suggested timed story and Hebrew voiceover:
0–4 sec — “את כבר יודעת לבנות תוכנה. מוכנה להביא פתרונות עד לפרודקשן?”
4–10 sec — “הכירי את FDE + DevOps Bootcamp של Practec להייטק.”
10–20 sec — “שנים עשר שבועות של FDE, פתרונות AI, ענן ו-DevOps—עם פרויקטים מעשיים מקצה לקצה.”
20–28 sec — “64 שעות מפגש, תרגול וליווי מקצועי. עד 20 משתתפות נבחרות.”
28–35 sec — “המסלול כולל הכנה מקצועית לקריירה. הקבלה מותנית במיון; אין התחייבות להשמה.”
35–42 sec — “מחזור נובמבר 2026. מתחילות בתהליך המיון ב-19 בנובמבר, ויום ההערכה יתקיים ב-25 בנובמבר. בדקי התאמה והגישי מועמדות.”
End card — “FDE + DevOps Bootcamp | Practec להייטק (ע״ר)” plus a clear application CTA. If linking to the local page, use `#apply`; do not invent a public URL.

Include the accurate details when they fit: selection fee and assignment on 19 November 2026; professional assessment on 25 November 2026; ₪4,500 tuition and ₪350 non-refundable selection fee; optional two-week AIOps continuation for ₪1,500. Because the cut is short, these may go on a readable end card or companion caption rather than crowding the voiceover. Do not omit the non-refund qualifier when showing the selection fee.

Export or provide a reliable render command, preview the result where possible, and verify RTL captions, logo visibility, safe margins, timing, and legibility. Report the output path, render steps, and any optional assets still needed.
```
