"""Build the syllabus in English and Hebrew from syllabus/content.py, as HTML and as A4 PDFs (Google Chrome via Playwright).

    python syllabus/build_pdf.py          (from the Practec folder)

  -> syllabus/syllabus.html + practec-syllabus.pdf        (English)
  -> syllabus/syllabus-he.html + practec-syllabus-he.pdf  (Hebrew, RTL)

The HTML files are generated; edit content.py (texts) or the CSS below (design), then rebuild.
Requirements: Google Chrome and the Python package playwright.
"""
import datetime as dt
import html
import re
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import content as C  # noqa: E402

UI = {  # interface words: (English, Hebrew)
    "syllabus": ("Syllabus", "סילבוס"), "course": ("Course", "קורס"), "week": ("Week", "שבוע"),
    "length": ("Length", "משך"), "tuition": ("Tuition", "שכר לימוד"), "dates": ("Dates", "מועדים"),
    "admission": ("Admission", "קבלה"), "weeks": ("weeks", "שבועות"),
    "lede": ("Two separate courses, 14 weeks in total, for experienced developers who want to take software all the way to production—and to a real client.",
             "שני קורסים נפרדים, 14 שבועות בסך הכול, למפתחות מנוסות שרוצות להביא תוכנה עד לפרודקשן — ועד ללקוח אמיתי."),
    "lecture_h": ("lecture", "הרצאה"), "team_h": ("team work", "עבודת צוות"), "roles_h": ("Team roles", "תפקידים בצוות"),
    "lecture_sub": ("Every week · lecturer: ", "בכל שבוע · מרצה: "),
    "team_sub": ("Every week · internship on the team's primary project", "בכל שבוע · התנסות מעשית על הפרויקט המרכזי של הצוות"),
    "roles_sub": ("Developers and one responsible DevOps engineer per primary project", "מפתחות, ואחראית DevOps אחת לכל פרויקט מרכזי"),
    "project_h": ("The primary project", "הפרויקט המרכזי"),
    "project": ("Each team launches its primary project in DevOps Bootcamp week 3—ideally from the team's own idea, with one or two placeholder projects available. It must integrate external APIs. Over the two courses it is containerized, deployed, secured, and AI-enabled, and in FDE Practitioner it is delivered to a real client by a deadline. CI/CD and Kubernetes exercises run on a shared practice project.",
                "כל צוות משיק את הפרויקט המרכזי שלו בשבוע 3 של DevOps Bootcamp — רצוי מרעיון של הצוות עצמו, ויש גם פרויקט מוכן אחד או שניים לבחירה. הפרויקט חייב לכלול אינטגרציה עם APIs חיצוניים. לאורך שני הקורסים הוא עובר קונטיינריזציה, פריסה, אבטחה ושילוב AI, וב-FDE Practitioner הוא נמסר ללקוח אמיתי עד מועד יעד. תרגילי CI/CD ו-Kubernetes נעשים על פרויקט תרגול משותף."),
    "know_h": ("Good to know", "טוב לדעת"),
    "know": [("Cloud and AI services needed for practice are not included in tuition; estimated services and costs are shared in advance.",
              "עלויות שירותי הענן וה-AI הנדרשים לתרגול אינן כלולות בשכר הלימוד; הערכת השירותים והעלויות תימסר מראש."),
             ("Career support and relevant opportunity connections are offered, but employment or placement is not guaranteed.",
              "מוצעים ליווי לקריירה וחיבור להזדמנויות רלוונטיות, אך אין התחייבות לתעסוקה או להשמה.")],
    "cal_h": ("Session calendar", "לוח המפגשים"),
    "cal_sub": ("Planned timetable. Every week: a lecture on Sunday and a team session on Wednesday. The final calendar is shared before each course.",
                "לוח זמנים מתוכנן. בכל שבוע: הרצאה ביום ראשון ומפגש צוות ביום רביעי. הלוח הסופי יישלח לפני כל קורס."),
    "cal_cols": (("Week", "Course · week", "Lecture · Sunday 17:00–19:30", "Team session · Wednesday 17:00–21:00", "Module"),
                 ("שבוע", "קורס · שבוע", "הרצאה · יום ראשון 17:00–19:30", "מפגש צוות · יום רביעי 17:00–21:00", "נושא")),
    "plus_indep": ("Plus 2 hours of independent team work every week.", "ובנוסף שעתיים של עבודת צוות עצמאית בכל שבוע."),
    "agenda": ("Lecture", "הרצאה"), "team": ("Team work", "עבודת צוות"), "deliverable": ("Deliverable", "תוצר"),
    "done": ("Done when", "הושלם כאשר"), "draft": ("Weekly agenda: draft for review", "סדר יום שבועי: טיוטה לבדיקה"),
    "lecturer": ("Lecturer", "מרצה"), "practice": ("practice", "תרגול"), "ideation": ("ideation", "גיבוש רעיון"),
    "planned": ("planned", "מתוכנן"), "page_footer": ("Practec · DevOps Bootcamp + FDE Practitioner · Syllabus", "סילבוס · Practec · DevOps Bootcamp + FDE Practitioner"),
}
MONTHS_EN = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def t(pair, he):
    return pair[1] if he else pair[0]


def esc(s):
    return html.escape(s, quote=False)


def ltr(s, he):
    """isolate a Latin phrase inside Hebrew text"""
    return f'<bdi dir="ltr">{esc(s)}</bdi>' if he else esc(s)


def date_txt(d, he):
    return f"{d.day}.{d.month}.{d.year}" if he else f"{d.day} {MONTHS_EN[d.month - 1]} {d.year}"


def logo():
    # the supplied SVG, placed whole; the viewBox is its visible mark (x 40–260, y 111.5–188.5 of the 300×300 canvas)
    # plus 4 units of margin, so its transparent canvas never spills past the page margins
    return ('<svg class="logo" viewBox="36 107.5 228 85" role="img" aria-label="Practec">'
            '<image href="../assets/practec-logo.svg" width="300" height="300"/></svg>')


def calendar(he):
    rows, n = [], 0
    for c in C.COURSES:
        sun = dt.date(*c["first_sunday"])
        for i, w in enumerate(c["weeks_detail"]):
            n += 1
            s, wed = sun + dt.timedelta(weeks=i), sun + dt.timedelta(weeks=i, days=3)
            note = C.NOTES.get(s.isoformat())
            note_html = f'<span class="note">{esc(t(note, he))}</span>' if note else ""
            rows.append(f'<tr class="{c["key"]}"><td class="n">{n}</td><td><bdi dir="ltr" class="nw">{esc(c["name"])}</bdi>'
                        f'<span class="cw">{esc(t(UI["week"], he))} {i + 1}</span></td>'
                        f'<td>{date_txt(s, he)}{note_html}</td><td>{date_txt(wed, he)}</td><td>{esc(t(w["title"], he))}</td></tr>')
    head = "".join("<th>" + re.sub(r"(\d\d:\d\d–\d\d:\d\d)", r'<span class="nw">\1</span>', esc(x)) + "</th>"
                   for x in t(UI["cal_cols"], he))
    return (f'<section class="calendar"><h2>{esc(t(UI["cal_h"], he))}</h2><p class="sub">{esc(t(UI["cal_sub"], he))}</p>'
            f'<table><thead><tr>{head}</tr></thead><tbody>{"".join(rows)}</tbody></table>'
            f'<p class="sub small">{esc(t(UI["plus_indep"], he))} {esc(t(C.LOCATION, he))}.</p></section>')


def week_html(c, i, w, he):
    sun = dt.date(*c["first_sunday"]) + dt.timedelta(weeks=i)
    wed = sun + dt.timedelta(days=3)
    blocks = []
    for time, kind in C.BLOCKS:
        if kind in ("part1", "part2", "lab"):
            txt, cls = t(w[kind], he), "topic"
        elif kind == "open" and i == 0:
            txt, cls = t(c["opening"], he), "aux"
        else:
            txt, cls = t(C.GENERIC[kind], he), "aux"
        blocks.append(f'<tr class="{cls}"><td class="tm" dir="ltr">{time}</td><td>{esc(txt)}</td></tr>')
    leads = "".join(f'<span class="tag lead">{esc(name)} · {esc(t(UI[role], he))}</span>' for name, role in w.get("leads", []))
    role = f'<span class="tag role">{esc(t(w["role"], he))}</span>' if w.get("role") else ""
    when_l = f'{t(("Sunday", "יום ראשון"), he)} {date_txt(sun, he)}'
    when_t = f'{t(("Wednesday", "יום רביעי"), he)} {date_txt(wed, he)}'
    prop = " proposed" if w.get("proposed") else ""
    return f"""<article class="week">
  <div class="wk"><small>{esc(t(UI["week"], he))}</small><b>{i + 1}</b></div>
  <div class="wbody">
    <h3>{esc(t(w["title"], he))}</h3>
    <div class="cols">
      <div class="lec"><div class="lab">{esc(t(UI["agenda"], he))} · {esc(when_l)}</div><table class="agenda">{"".join(blocks)}</table></div>
      <div class="tw{prop}"><div class="lab">{esc(t(UI["team"], he))} · {esc(when_t)}</div>
        <p>{esc(t(w["team"], he))}{role}{leads}</p>
        <p><span class="k">{esc(t(UI["deliverable"], he))}</span>{esc(t(w["deliverable"], he))}</p>
        <p><span class="k">{esc(t(UI["done"], he))}</span>{esc(t(w["done"], he))}</p>
      </div>
    </div>
  </div>
</article>"""


def course_cards(he):
    out = []
    for k, c in enumerate(C.COURSES, 1):
        adm = esc(t(c["admission"], he)).replace("DevOps Bootcamp", ltr("DevOps Bootcamp", he) if he else "DevOps Bootcamp")
        out.append(f"""<div class="course-card"><div class="kicker">{esc(t(UI["course"], he))} {k}</div><h2 dir="ltr">{c["name"]}</h2>
<dl class="facts"><dt>{esc(t(UI["length"], he))}</dt><dd>{c["weeks"]} {esc(t(UI["weeks"], he))}</dd>
<dt>{esc(t(UI["tuition"], he))}</dt><dd><span class="price">{c["price"] + " ₪" if he else "₪" + c["price"]}</span></dd>
<dt>{esc(t(UI["dates"], he))}</dt><dd>{esc(t(c["dates"], he))}</dd>
<dt>{esc(t(UI["admission"], he))}</dt><dd>{adm}</dd></dl></div>""")
    return "".join(out)


def page(he):
    lecturer = (f'{ltr("Rivky Ollech", he)}, {esc("מפתחת DevOps ב-")}{ltr("Varonis", he)} '
                f'({esc("בתהליך רכישה על ידי ")}{ltr("Proofpoint", he)})') if he else esc(C.LECTURER[0])
    sections = []
    for k, c in enumerate(C.COURSES, 1):
        price = c["price"] + " ₪" if he else "₪" + c["price"]
        intro = f'<p class="course-intro">{esc(t(c["intro"], he))}</p>' if c.get("intro") else ""
        weeks = "".join(week_html(c, i, w, he) for i, w in enumerate(c["weeks_detail"]))
        sections.append(f"""<section class="course">
  <div class="course-head"><div><span class="kicker">{esc(t(UI["course"], he))} {k}</span><h2 dir="ltr">{c["name"]}</h2></div>
    <div class="meta"><b>{c["weeks"]} {esc(t(UI["weeks"], he))} · {price}</b>{esc(t(c["dates"], he))}<br><span class="draft">{esc(t(UI["draft"], he))}</span></div></div>
  {intro}{weeks}</section>""")
    know = "".join(f"<li>{esc(t(x, he))}</li>" for x in UI["know"])
    project = esc(t(UI["project"], he))
    if he:
        for name in ("DevOps Bootcamp", "FDE Practitioner"):
            project = project.replace(name, ltr(name, True))
    return f"""<!doctype html>
<html lang="{'he' if he else 'en'}" dir="{'rtl' if he else 'ltr'}">
<head><meta charset="utf-8"><title>Practec {esc(t(UI["syllabus"], he))}</title>
<!-- GENERATED by build_pdf.py from content.py — edit those, not this file. -->
<style>{CSS}{CSS_HE if he else ""}</style></head>
<body>
<header class="top">{logo()}<div class="doc-label"><b>{esc(t(UI["syllabus"], he))} · 2026–2027</b>{ltr("Practec", he)} <bdi dir="rtl">להייטק (ע״ר)</bdi></div></header>
<div class="rule"></div>
<h1 dir="ltr">DevOps Bootcamp <span class="plus">+</span> FDE Practitioner</h1>
<p class="lede">{esc(t(UI["lede"], he))}</p>
<p class="campaign" dir="rtl" lang="he">לא רק לפתח. להביא פתרונות לפרודקשן.</p>
<section class="courses">{course_cards(he)}</section>
<section class="week-format">
  <div class="wf"><b><span class="mint">2.5 {'שעות' if he else 'h'}</span> {esc(t(UI["lecture_h"], he))}</b><span>{esc(t(UI["lecture_sub"], he))}{lecturer}</span></div>
  <div class="wf"><b><span class="mint">6 {'שעות' if he else 'h'}</span> {esc(t(UI["team_h"], he))}</b><span>{esc(t(UI["team_sub"], he))}</span></div>
  <div class="wf"><b>{esc(t(UI["roles_h"], he))}</b><span>{esc(t(UI["roles_sub"], he))}</span></div>
</section>
<section class="project"><h3>{esc(t(UI["project_h"], he))}</h3><p>{project}</p></section>
<section class="notes"><b>{esc(t(UI["know_h"], he))}</b><ul>{know}</ul></section>
{calendar(he)}
{"".join(sections)}
</body></html>"""


CSS = """
@font-face { font-family: "Heebo"; src: url("../video/composition/fonts/Heebo-Variable.ttf") format("truetype"); font-weight: 100 900; }
@font-face { font-family: "JetBrains Mono"; src: url("../video/composition/fonts/JetBrainsMono-Variable.ttf") format("truetype"); font-weight: 100 800; }
@page { size: A4; margin: 15mm 15mm 17mm; }
:root { --ink: #0E1428; --mute: #555C75; --soft: #858A9E; --line: #E6E1D8; --card: #FAF8F4;
  --red: #B4373D; --mag: #B23ACB; --mint: #A9FCC1; --grad: linear-gradient(90deg, #B4373D, #B23ACB); }
* { box-sizing: border-box; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { margin: 0; font: 400 12.5px/1.5 "Heebo", Arial, sans-serif; color: var(--ink); background: #fff; }
.top { display: flex; align-items: flex-start; justify-content: space-between; }
.logo { display: block; width: 197px; height: 72.5px; }
.doc-label { text-align: end; font: 600 12px/1.6 "Heebo", sans-serif; color: var(--mute); }
.doc-label b { display: block; font: 500 10.5px/1.6 "JetBrains Mono", monospace; color: var(--soft); letter-spacing: .3px; text-transform: uppercase; }
.rule { height: 3px; border-radius: 3px; background: var(--grad); margin: 14px 0 20px; }
h1 { margin: 0; font: 800 31px/1.12 "Heebo", sans-serif; letter-spacing: -.6px; text-align: start; }
h1 .plus { color: #B33884; }
.lede { margin: 8px 0 0; font-size: 14px; color: var(--mute); max-width: 640px; }
.campaign { margin: 6px 0 0; font: 800 14px/1.4 "Heebo", sans-serif; text-align: start; }
.courses { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin: 20px 0 14px; }
.course-card { border-radius: 14px; padding: 15px 18px 13px; background: var(--card); box-shadow: inset 0 0 0 1.5px var(--line); position: relative; overflow: hidden; }
.course-card::before { content: ""; position: absolute; inset-inline-start: 0; top: 0; bottom: 0; width: 5px; background: var(--grad); }
.kicker { font: 600 10px/1 "JetBrains Mono", monospace; letter-spacing: .6px; text-transform: uppercase; color: var(--soft); }
.course-card h2 { margin: 6px 0 9px; font: 800 20px/1.15 "Heebo", sans-serif; text-align: start; }
.facts { display: grid; grid-template-columns: auto 1fr; gap: 3px 12px; margin: 0; font-size: 12px; }
.facts dt { color: var(--soft); } .facts dd { margin: 0; font-weight: 500; }
.price { font: 800 21px/1 "Heebo", sans-serif; }
.week-format { display: grid; grid-template-columns: 1.25fr 1fr 1fr; gap: 10px; margin: 0 0 14px; }
.wf { border-radius: 12px; padding: 11px 14px; background: #0E1428; color: #F6F3EE; }
.wf b { display: block; font: 800 17px/1.25 "Heebo", sans-serif; } .wf b .mint { color: var(--mint); }
.wf span { font-size: 11.5px; color: #B9BED1; }
.project { border-radius: 12px; padding: 11px 16px; box-shadow: inset 0 0 0 1.5px var(--line); }
.project h3 { margin: 0 0 3px; font: 700 13.5px/1.3 "Heebo", sans-serif; } .project p { margin: 0; color: var(--mute); }
.notes { margin-top: 14px; padding: 10px 16px; border-radius: 12px; background: var(--card); font-size: 11.5px; color: var(--mute); break-inside: avoid; }
.notes ul { margin: 3px 0 0; padding-inline-start: 18px; } .notes b { color: var(--ink); }

.calendar { break-before: page; }
.calendar h2 { margin: 0; font: 800 24px/1.2 "Heebo", sans-serif; }
.calendar .sub { margin: 4px 0 12px; color: var(--mute); }
.calendar .sub.small { margin-top: 10px; font-size: 11.5px; }
.calendar table { width: 100%; border-collapse: collapse; font-size: 12px; }
.calendar th { text-align: start; font: 700 10.5px/1.3 "Heebo", sans-serif; color: var(--soft); padding: 6px 8px; border-bottom: 2px solid var(--ink); }
.calendar td { padding: 7px 8px; border-bottom: 1px solid var(--line); vertical-align: top; }
.calendar td.n { font-weight: 800; width: 34px; }
.calendar tr.fde td { background: #FBF7FC; }
.calendar tr.fde:first-of-type td, .calendar tr.devops + tr.fde td { border-top: 2px solid var(--mag); }
.calendar .cw { display: block; font-size: 10.5px; color: var(--soft); }
.nw { white-space: nowrap; }
.calendar .note { display: block; font-size: 10.5px; color: var(--red); font-weight: 600; }

.course { break-before: page; }
.course-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; padding-bottom: 10px; margin-bottom: 2px; border-bottom: 2px solid var(--ink); }
.course-head h2 { margin: 0; font: 800 24px/1.15 "Heebo", sans-serif; text-align: start; }
.course-head .kicker { display: block; margin-bottom: 4px; }
.course-head .meta { text-align: end; font-size: 12px; color: var(--mute); white-space: nowrap; }
.course-head .meta b { display: block; font: 800 18px/1.2 "Heebo", sans-serif; color: var(--ink); }
.course-head .draft { display: inline-block; margin-top: 4px; padding: 1px 8px; border-radius: 99px; background: #FFF3D6; color: #7A5200; font-size: 10.5px; font-weight: 700; }
.course-intro { margin: 8px 0 2px; font-size: 12px; color: var(--mute); }
.week { display: grid; grid-template-columns: 50px 1fr; gap: 12px; padding: 12px 0; border-bottom: 1px solid var(--line); break-inside: avoid; }
.wk { width: 44px; height: 44px; border-radius: 12px; background: var(--card); box-shadow: inset 0 0 0 1.5px var(--line); display: grid; place-items: center; align-content: center; text-align: center; }
.wk small { display: block; font: 600 8.5px/1 "JetBrains Mono", monospace; letter-spacing: .5px; color: var(--soft); text-transform: uppercase; }
.wk b { display: block; font: 800 18px/1.1 "Heebo", sans-serif; }
.week h3 { margin: 0 0 6px; font: 700 15px/1.3 "Heebo", sans-serif; }
.cols { display: grid; grid-template-columns: 1.1fr 1fr; gap: 14px; }
.lab { font: 700 9.5px/1.3 "JetBrains Mono", monospace; letter-spacing: .4px; text-transform: uppercase; color: #B33884; margin-bottom: 4px; }
.agenda { width: 100%; border-collapse: collapse; font-size: 11.5px; }
.agenda td { padding: 2.5px 0; vertical-align: top; }
.agenda td.tm { width: 82px; font: 500 10.5px/1.55 "JetBrains Mono", monospace; color: var(--soft); white-space: nowrap; padding-inline-end: 8px; }
.agenda tr.aux td:last-child { color: var(--soft); }
.tw { border-radius: 10px; padding: 8px 11px; background: var(--card); font-size: 11.5px; }
.tw.proposed { box-shadow: inset 0 0 0 1.5px #F2D58A; background: #FFFBF0; }
.tw p { margin: 0 0 5px; } .tw p:last-child { margin: 0; }
.tw .k { display: block; font: 700 9.5px/1.3 "JetBrains Mono", monospace; letter-spacing: .4px; text-transform: uppercase; color: var(--soft); }
.tag { display: inline-block; margin-inline-start: 6px; padding: 0 7px; border-radius: 99px; font: 600 10px/1.7 "Heebo", sans-serif; }
.tag.lead { background: var(--mint); color: var(--ink); } .tag.role { background: #EEEAF6; color: #5B2A73; }
"""

CSS_HE = """
body { font-size: 13px; }
.kicker, .doc-label b, .wk small, .lab, .tw .k { font-family: "Heebo", sans-serif; letter-spacing: 0; text-transform: none; }
.kicker { font-size: 11px; font-weight: 700; } .lab, .tw .k { font-size: 11px; } .wk small { font-size: 9.5px; }
.doc-label b { font-size: 12px; font-weight: 700; color: var(--mute); }
h1, .course-card h2, .course-head h2 { text-align: right; }
.agenda { font-size: 12px; } .tw { font-size: 12px; }
.agenda td.tm { padding-inline-end: 0; padding-left: 10px; }   /* the time cell is LTR inside an RTL row: its gap goes on the left */
"""


def footer(he):
    return (f'<div style="width:100%;padding:0 15mm;font:8px Arial,sans-serif;color:#858A9E;display:flex;justify-content:space-between;'
            f'direction:{"rtl" if he else "ltr"}"><span>{t(UI["page_footer"], he)}</span>'
            f'<span dir="ltr"><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>')


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome")
        for he, name in ((False, "syllabus"), (True, "syllabus-he")):
            src = HERE / f"{name}.html"
            src.write_text(page(he), encoding="utf-8")
            pg = browser.new_page()
            pg.goto(src.as_uri())
            pg.evaluate("() => document.fonts.ready")
            pg.evaluate("() => Promise.all([...document.images].map(i => i.decode()))")
            out = HERE / ("practec-syllabus-he.pdf" if he else "practec-syllabus.pdf")
            pg.pdf(path=str(out), format="A4", print_background=True, prefer_css_page_size=True,
                   display_header_footer=True, header_template="<div></div>", footer_template=footer(he))
            pg.close()
            print(out)
        browser.close()


if __name__ == "__main__":
    main()
