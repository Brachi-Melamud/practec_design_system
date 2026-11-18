/* Scene choreography. Every update(t) is a pure function of scene-local time t (seconds since the scene's start),
   so any frame can be rendered in any order. Scene start/end times come from content.js. */
(() => {
  'use strict';
  const { $, $$, clamp, ease, prog, set, words, rr, cyl, along, mix, define, transition, V } = window.K;
  const at = id => V.scenes.find(s => s.id === id).start;
  const len = id => { const s = V.scenes.find(s => s.id === id); return s.end - s.start; };
  /** scene-local time of the caption with this id, so a picture can follow the voice (fallback if there is none) */
  const cue = (scene, id, fallback) => { const c = V.captions.find(c => c.id === id); return c ? c.start - at(scene) : fallback; };
  const INK = '#0E1428', PAPER = '#F5F1EA', CARD = '#FFFDF8', WHITE = '#FFFFFF';

  /* background changes: dark → light (circle from the "production" pill) → dark (circle from "Live") → light (wipe, RTL-forward) */
  transition({ bg: 1, out: 'hook', in: 'brand', at: at('brand') - .45, dur: .65, type: 'circle', from: '#hook .env-pill' });
  transition({ bg: 2, out: 'build', in: 'facts', at: at('facts') - .45, dur: .65, type: 'circle', from: '#build .live .dot' });
  transition({ bg: 3, out: 'career', in: 'dates', at: at('dates') - .45, dur: .65, type: 'wipe' });

  /** show the first n characters of a monospace line */
  const typeLine = (el, n) => { el.style.clipPath = `inset(0 calc(100% - ${n}ch) 0 0)`; };

  /** break a wrapping row of word spans into two lines of similar width (flex-wrap alone leaves orphans) */
  function balance(el, ws) {
    const gap = parseFloat(getComputedStyle(el).columnGap) || 0;
    const w = ws.map(s => s.offsetWidth);
    const total = w.reduce((a, b) => a + b, 0) + gap * (ws.length - 1);
    if (total <= el.clientWidth) return;
    let best = 0, bestDiff = Infinity, first = 0;
    for (let i = 1; i < ws.length; i++) {
      first += w[i - 1] + (i > 1 ? gap : 0);
      const rest = total - first - gap;
      if (Math.max(first, rest) <= el.clientWidth && Math.abs(first - rest) < bestDiff) { bestDiff = Math.abs(first - rest); best = i; }
    }
    if (!best) return;
    const br = document.createElement('i');
    br.style.cssText = 'flex-basis:100%;height:0';
    el.insertBefore(br, ws[best]);
  }

  /* ---------- 1 · HOOK ---------- */
  define('hook', {
    lead: 0, tail: .3,
    init() {
      const r = $('#hook'), hero = $('.hero', r);
      hero.textContent = '';
      this.lines = V.captions.filter(c => c.hero).map(c => {
        const el = document.createElement('div');
        el.className = 'hero-line';
        hero.appendChild(el);
        const ws = words(el, c.text);
        balance(el, ws);
        return { c, ws };
      });
      this.win = $('.window', r);
      this.code = $$('.code .ln', r); this.codeN = this.code.map(l => l.textContent.length);
      this.term = $$('.term .ln', r); this.termN = this.term.map(l => l.textContent.length);
      this.cursor = $('.cursor', r); this.wire = $('.wire', r); this.pill = $('.env-pill', r); this.ring = $('.env-pill .ring', r);
    },
    update(t) {
      this.lines.forEach(({ c, ws }, li) => {
        const last = li === this.lines.length - 1;
        ws.forEach((w, k) => {
          // the first line is already arriving on frame 0, so the video never opens on an empty frame
          const a = c.start + (li ? .04 : -.12) + k * .06, b = c.end - .2 + k * .02;
          const pin = prog(t, a, a + .55, ease.outExpo);
          const pout = last ? 0 : prog(t, b, b + .2, ease.in);
          set(w, { o: pin * (1 - pout), y: (1 - pin) * 48 - pout * 36, blur: (1 - pin) * 8 + pout * 4 });
        });
      });
      const pw = prog(t, -.12, .5, ease.outExpo);
      set(this.win, { o: pw, y: (1 - pw) * 70, s: .96 + .04 * pw });
      const seq = [[.55, .92], [.92, 1.3], [1.3, 1.66]];
      let cur = { i: 0, n: 0 };
      this.code.forEach((ln, i) => {
        const n = Math.round(prog(t, seq[i][0], seq[i][1], ease.lin) * this.codeN[i]);
        typeLine(ln, n);
        if (t >= seq[i][0]) cur = { i, n };
      });
      const lh = 29 * 1.62;
      this.cursor.style.left = `calc(34px + ${cur.n}ch)`;
      this.cursor.style.top = `${(26 + cur.i * lh + (lh - 36) / 2).toFixed(1)}px`;
      const typing = t >= .55 && t <= 1.7;
      set(this.cursor, { o: t > 2.0 ? 0 : pw * (typing || Math.floor(t * 2.4) % 2 === 0 ? 1 : 0) });
      typeLine(this.term[0], Math.round(prog(t, 1.68, 1.92, ease.lin) * this.termN[0]));
      const p2 = prog(t, 1.95, 2.25, ease.outExpo);
      set(this.term[1], { o: p2, x: (1 - p2) * -18 });
      set(this.wire, { sy: prog(t, 2.2, 2.55, ease.inOut) });
      this.wire.style.backgroundPosition = `0 ${(t * 36).toFixed(1)}px`;
      const pp = prog(t, 2.45, 2.95, ease.outBack);
      set(this.pill, { o: clamp(pp * 1.6), s: .82 + .18 * pp });
      const ph = t > 2.95 ? ((t - 2.95) % .8) / .8 : -1;
      set(this.ring, ph < 0 ? { o: 0 } : { o: (1 - ph) * .75, s: 1 + ph * .4 });
    },
  });

  /* ---------- 2 · BRAND ---------- */
  define('brand', {
    lead: .45, tail: 0,
    init() {
      const r = $('#brand'); this.r = r;
      this.logo = $('.logo-c', r); this.lines = $$('.title .l', r); this.tw = $$('.tagline .w', r);
      this.u = $('.u', r); this.sub = $('.sub', r);
    },
    update(t) {
      const pl = prog(t, -.12, .65, ease.outExpo);          // already arriving inside the reveal circle
      set(this.logo, { o: pl, y: (1 - pl) * 34, s: .94 + .06 * pl });
      this.lines.forEach((l, i) => { const p = prog(t, .3 + i * .14, 1.0 + i * .14, ease.outExpo); set(l, { y: (1 - p) * 160 }); });
      this.tw.forEach((w, k) => {
        const a = (k < 3 ? 1.2 : 1.4) + k * .07;
        const p = prog(t, a, a + .55, ease.outExpo);
        set(w, { o: p, y: (1 - p) * 34, blur: (1 - p) * 5 });
      });
      this.u.style.setProperty('--p', prog(t, 2.1, 2.75, ease.inOut).toFixed(4));
      const ps = prog(t, 2.55, 3.15, ease.out); set(this.sub, { o: ps, y: (1 - ps) * 22 });
      const ex = prog(t, len('brand') - .5, len('brand') - .05, ease.in); set(this.r, { o: 1 - ex, y: -ex * 60 });
    },
  });

  /* ---------- 3 · BUILD: need → design → AI build → deploy → production (5 × 2 s, one bar each) ---------- */
  define('build', {
    lead: 0, tail: .3,
    init() {
      const r = $('#build'); this.r = r;
      $$('[data-rr]', r).forEach(p => p.setAttribute('d', rr(...p.dataset.rr.split(',').map(Number))));
      $$('[data-cyl]', r).forEach(p => p.setAttribute('d', cyl(...p.dataset.cyl.split(',').map(Number))));
      $$('.ci .tick', r).forEach(p => p.setAttribute('pathLength', '1'));
      this.head = $('.head', r); this.n = $('.step .n', r); this.titles = $$('.titles h2', r); this.bars = $$('.progress i', r);
      this.sk = $$('.dg .sk', r); this.cn = $$('.dg .cn:not(.link)', r); this.ah = $$('.dg .ah', r); this.cnci = $$('.dg .cn.link', r);
      this.boxDash = $('.box-dash', r); this.boxSolid = $('.box-solid', r); this.ragFill = $('.rag-fill', r);
      this.pkMain = $('#pk-main', r); this.pkRag = $('#pk-rag', r); this.pk = $$('.packets circle', r);
      this.ticket = $('.ticket', r); this.tkCard = $('.tk-card', r); this.tkStack = $$('.tk-stack', r);
      this.input = $('.node.input', r); this.nodes = $$('.node.nd', r); this.ragLbl = $('.rag-lbl', r); this.ragCap = $('.rag-cap', r);
      this.code = $('.code-card', r); this.codeLn = $$('.code-card .ln', r); this.codeN = this.codeLn.map(l => l.textContent.length);
      this.docker = $('.docker', r); this.ciLabel = $('.ci-label', r); this.ci = $$('.ci', r);
      this.live = $('.live', r); this.pulse = $('.live .pulse', r); this.ok = $('.ok200', r); this.spark = $('.spark', r);
      // the choreography below is written for five 2-second stages; warp real time onto it so the scene can be
      // any length: four equal stages (3/16 of the scene each, on the beat) and a longer last one
      const d = len('build'), real = [0, 3 / 16 * d, 6 / 16 * d, 9 / 16 * d, 12 / 16 * d, d];
      this.warp = t => {
        if (t <= 0) return t;
        for (let i = 0; i < 5; i++) if (t < real[i + 1]) return 2 * i + 2 * (t - real[i]) / (real[i + 1] - real[i]);
        return 10 + t - d;
      };
    },
    update(t) {
      t = this.warp(t);
      const ST = [0, 2, 4, 6, 8];
      const k = clamp(Math.floor(t / 2), 0, 4);
      const ph = prog(t, 0, .45, ease.outExpo);
      set(this.head, { o: ph, y: (1 - ph) * 30 });
      this.n.textContent = String(k + 1).padStart(2, '0');
      this.titles.forEach((h, i) => {
        const a = i ? ST[i] : .05;
        const pin = prog(t, a, a + .45, ease.outExpo);
        const pout = i === 4 ? 0 : prog(t, ST[i + 1] - .04, ST[i + 1] + .22, ease.in);
        set(h, { o: pin * (1 - pout), y: (1 - pin) * 60 - pout * 44 });
      });
      this.bars.forEach((b, i) => set(b, { sx: prog(t, ST[i], ST[i] + 2, ease.lin) }));

      // 1 · business need — a request lands on a pile, then shrinks into the system's input
      const pt = prog(t, .12, .7, ease.outExpo);
      const morph = prog(t, 2.0, 2.5, ease.inOut);
      set(this.ticket, { x: 345 * morph, y: -151 * morph, s: 1 - .736 * morph, o: 1 - prog(t, 2.22, 2.5, ease.lin) });
      set(this.tkCard, { o: pt, y: (1 - pt) * 80 });
      this.tkStack.forEach((s, i) => {
        const p = prog(t, .32 + i * .14, .82 + i * .14, ease.outBack);
        set(s, { o: clamp(p * 2) * .95, y: (1 - p) * -70 + (i + 1) * 16, r: i ? 2.6 : -3.4 });
      });
      const pi = prog(t, 2.28, 2.6, ease.outBack);
      set(this.input, { o: clamp(pi * 1.8), s: .86 + .14 * pi });

      // 2 · design — sketch the architecture
      const SK = [[2.3, 2.75], [2.42, 2.87], [2.54, 2.99], [2.66, 3.2]];
      const fillP = i => prog(t, 4.05 + i * .08, 4.45 + i * .08, ease.inOut);
      this.sk.forEach((p, i) => {
        p.style.strokeDashoffset = (1 - prog(t, SK[i][0], SK[i][1], ease.inOut)).toFixed(4);
        if (i < 3) p.style.opacity = (1 - fillP(i)).toFixed(3);
      });
      this.nodes.forEach((n, i) => {
        const q = fillP(i);
        set(n.querySelector('.fill'), { o: q });
        const sp = n.querySelector('span');
        sp.style.opacity = prog(t, SK[i][0] + .2, SK[i][0] + .5).toFixed(3);
        sp.style.color = mix(INK, WHITE, q);
        set(n, { s: 1 + .07 * Math.sin(Math.PI * q) });
      });
      const qr = prog(t, 4.3, 4.7, ease.inOut);
      this.ragFill.style.opacity = qr.toFixed(3);
      this.sk[3].style.stroke = mix(INK, PAPER, qr);
      this.ragLbl.style.opacity = prog(t, SK[3][0] + .25, SK[3][0] + .55).toFixed(3);
      this.ragLbl.style.color = mix(INK, PAPER, qr);
      this.ragCap.style.opacity = prog(t, 3.0, 3.4).toFixed(3);
      const CN = [[2.7, 2.95], [2.85, 3.1], [3.0, 3.25], [3.1, 3.4]];
      this.cn.forEach((p, i) => {
        p.style.strokeDashoffset = (1 - prog(t, CN[i][0], CN[i][1], ease.inOut)).toFixed(4);
        this.ah[i].style.opacity = prog(t, CN[i][1] - .06, CN[i][1] + .1).toFixed(3);
      });

      // 3 · AI build — nodes become real, requests flow through API → Agent → LLM, Agent ↔ RAG
      const pk = prog(t, 4.4, 4.8);
      const main = this.pk.length - 2;      // the last two packets shuttle between the Agent and RAG
      this.pk.forEach((c, i) => {
        let p, o = 1;
        if (i < main) {
          const f = ((((t - 4.4) * .45 + i / main) % 1) + 1) % 1;
          p = along(this.pkMain, f); o = Math.min(1, f * 10, (1 - f) * 10);
        } else {
          const f = ((((t - 4.6) * .6 + (i - main) / 2) % 1) + 1) % 1;
          p = along(this.pkRag, f < .5 ? f * 2 : 2 - f * 2);
        }
        c.setAttribute('cx', p.x.toFixed(1)); c.setAttribute('cy', p.y.toFixed(1));
        c.style.opacity = (pk * o).toFixed(3);
      });
      const pcIn = prog(t, 4.3, 4.8, ease.outExpo), pcOut = prog(t, 5.95, 6.3, ease.in);
      set(this.code, { o: pcIn * (1 - pcOut), y: (1 - pcIn) * 40 + pcOut * 30 });
      this.codeLn.forEach((ln, i) => typeLine(ln, Math.round(prog(t, 4.45 + i * .2, 4.75 + i * .2, ease.lin) * this.codeN[i])));

      // 4 · cloud deployment — container + CI/CD checks
      const pdk = prog(t, 6.1, 6.55, ease.outExpo);
      this.boxDash.style.opacity = (pdk * (1 - prog(t, 8.3, 8.75))).toFixed(3);
      const pdc = prog(t, 6.3, 6.7, ease.outBack); set(this.docker, { o: clamp(pdc * 1.5), s: .8 + .2 * pdc });
      const pl = prog(t, 6.3, 6.7); set(this.ciLabel, { o: pl, y: (1 - pl) * 12 });
      this.ci.forEach((c, i) => {
        const pin = prog(t, 6.35 + i * .08, 6.8 + i * .08, ease.outExpo);
        set(c, { o: pin, y: (1 - pin) * 26 });
        const done = prog(t, 6.5 + i * .5, 6.72 + i * .5, ease.out);
        c.style.background = mix(CARD, INK, done);
        c.style.color = mix(INK, PAPER, done);
        const spin = c.querySelector('.spin');
        spin.style.transform = `rotate(${((t * 520) % 360).toFixed(1)}deg)`;
        spin.style.opacity = (1 - done).toFixed(3);
        c.querySelector('.tick').style.strokeDashoffset = (1 - prog(t, 6.55 + i * .5, 6.85 + i * .5)).toFixed(4);
      });
      this.cnci.forEach((p, i) => { p.style.strokeDashoffset = (1 - prog(t, 6.6 + i * .5, 6.9 + i * .5, ease.inOut)).toFixed(4); });

      // 5 · production — solid boundary, Live, health check, traffic
      this.boxSolid.style.strokeDashoffset = (1 - prog(t, 8.05, 8.8, ease.inOut)).toFixed(4);
      const pv = prog(t, 8.2, 8.6, ease.outBack); set(this.live, { o: clamp(pv * 1.6), s: .8 + .2 * pv });
      const pp = t > 8.6 ? ((t - 8.6) % .9) / .9 : -1;
      set(this.pulse, pp < 0 ? { o: 0 } : { o: (1 - pp) * .9, s: 1 + pp * 1.8 });
      const po = prog(t, 8.4, 8.85); set(this.ok, { o: po, y: (1 - po) * 10 });
      this.spark.style.strokeDashoffset = (1 - prog(t, 8.5, 9.4, ease.inOut)).toFixed(4);
    },
  });

  /* ---------- 4 · FACTS ---------- */
  define('facts', {
    lead: .45, tail: 0,
    init() {
      const r = $('#facts'); this.r = r;
      this.eb = $('.eyebrow', r); this.h = $('.h', r); this.tiles = $$('.tile', r); this.cnt = $$('.cnt', r); this.rows = $$('.sched .row', r);
    },
    update(t) {
      const pe = prog(t, -.08, .4, ease.outExpo); set(this.eb, { o: pe, y: (1 - pe) * 20 });
      const ph = prog(t, 0, .55, ease.outExpo); set(this.h, { o: ph, y: (1 - ph) * 40 });
      this.tiles.forEach((tl, i) => {
        const p = prog(t, .3 + i * .12, .9 + i * .12, ease.outExpo);
        set(tl, { o: p, y: (1 - p) * 60, s: .96 + .04 * p });
        const c = $('.cnt', tl);
        if (c) c.textContent = String(Math.round(+c.dataset.to * prog(t, .4 + i * .12, 1.3 + i * .12, ease.out)));
      });
      this.rows.forEach((rw, i) => { const p = prog(t, 1.5 + i * .15, 2.0 + i * .15, ease.outExpo); set(rw, { o: p, x: (1 - p) * 40 }); });
      const ex = prog(t, len('facts') - .45, len('facts') - .05, ease.in); set(this.r, { o: 1 - ex, y: -ex * 50 });
    },
  });

  /* ---------- 5 · CAREER ---------- */
  define('career', {
    lead: 0, tail: .3,
    init() {
      const r = $('#career'); this.r = r;
      $$('.ck .ic path', r).forEach(p => p.setAttribute('pathLength', '1'));
      this.eb = $('.eyebrow', r); this.h = $('.h', r); this.card = $('.checks', r); this.cks = $$('.ck', r); this.notice = $('.notice', r);
    },
    update(t) {
      const pe = prog(t, .05, .5, ease.outExpo); set(this.eb, { o: pe, y: (1 - pe) * 20 });
      const ph = prog(t, .12, .6, ease.outExpo); set(this.h, { o: ph, y: (1 - ph) * 40 });
      const pc = prog(t, .2, .65, ease.outExpo); set(this.card, { o: pc, y: (1 - pc) * 40 });
      this.cks.forEach((c, i) => {
        const a = .4 + i * .35;
        const p = prog(t, a - .1, a + .35, ease.outExpo);
        set(c.querySelector('.tx'), { o: p, x: (1 - p) * 40 });
        const m = c.querySelector('.meta'); if (m) set(m, { o: prog(t, a + .1, a + .5) });
        const pi = prog(t, a, a + .3, ease.outBack);
        set(c.querySelector('.ic'), { o: clamp(pi * 2), s: .6 + .4 * pi });
        c.querySelector('.ic path').style.strokeDashoffset = (1 - prog(t, a + .05, a + .35)).toFixed(4);
      });
      const nt = cue('career', 'notice', 3.0);           // the notice arrives with the line that states it
      const pn = prog(t, nt - .05, nt + .4, ease.outExpo); set(this.notice, { o: pn, y: (1 - pn) * 30 });
    },
  });

  /* ---------- 6 · DATES ---------- */
  define('dates', {
    lead: .45, tail: 0,
    init() {
      const r = $('#dates'); this.r = r;
      this.eb = $('.eyebrow', r); this.h = $('.h', r); this.track = $('.spine', r); this.spine = $('.spine i', r); this.items = $$('.item', r);
      // the spine runs from the first node to the last; each segment fills as its date is spoken
      const tops = this.items.map(it => it.offsetTop);
      this.track.style.height = `${tops[tops.length - 1] - tops[0]}px`;
      this.seg = tops.slice(1).map((y, i) => (y - tops[i]) / (tops[tops.length - 1] - tops[0]));
    },
    update(t) {
      const pe = prog(t, .02, .5, ease.outExpo); set(this.eb, { o: pe, y: (1 - pe) * 20 });
      const ph = prog(t, .1, .64, ease.outExpo); set(this.h, { o: ph, y: (1 - ph) * 40 });
      set(this.track, { o: prog(t, .6, 1.0) });
      const when = this.items.map((_, i) => cue('dates', `date${i + 1}`, .3 + 2.2 * i));      // each date arrives as it is spoken
      set(this.spine, { sy: this.seg.reduce((s, f, i) => s + f * prog(t, when[i + 1] - .4, when[i + 1] + .05, ease.inOut), 0) });
      this.items.forEach((it, i) => {
        const a = when[i];
        const node = $('.node', it);
        const pn = prog(t, a, a + .35, ease.outBack);
        set(node, { o: clamp(pn * 2), s: .4 + .6 * pn });
        node.style.background = mix(PAPER, ['#B4373D', '#B33884', '#B23ACB'][i % 3], prog(t, a + .1, a + .4));
        [...it.children].filter(c => c !== node).forEach((c, k) => {
          const p = prog(t, a + .05 + k * .1, a + .55 + k * .1, ease.outExpo);
          set(c, { o: p, x: (1 - p) * 40 });
        });
      });
      const ex = prog(t, len('dates') - .45, len('dates') - .05, ease.in); set(this.r, { o: 1 - ex, y: -ex * 50 });
    },
  });

  /* ---------- 7 · END CARD ---------- */
  define('end', {
    lead: 0, tail: 0,
    init() {
      const r = $('#end'); this.r = r;
      this.logo = $('.logo-c', r); this.title = $('.title', r); this.org = $('.org', r); this.cta = $('.cta', r);
      this.shine = $('.shine', r); this.note = $('.cta-note', r); this.card = $('.prices .card', r); this.rows = $$('.pr', r); this.foot = $('.foot', r);
      $('.cta .lbl', r).textContent = V.cta.label;
      if (V.cta.url) { this.note.textContent = V.cta.url; this.note.classList.add('url'); } else this.note.textContent = V.cta.note;
    },
    update(t) {
      const pl = prog(t, .1, .75, ease.outExpo); set(this.logo, { o: pl, y: (1 - pl) * 30, s: .95 + .05 * pl });
      const pt = prog(t, .32, .85, ease.outExpo); set(this.title, { o: pt, y: (1 - pt) * 30 });
      const po = prog(t, .45, .95, ease.outExpo); set(this.org, { o: po, y: (1 - po) * 24 });
      const pc = prog(t, .7, 1.15, ease.outBack); set(this.cta, { o: clamp(pc * 1.6), s: .86 + .14 * pc });
      const pn = prog(t, .95, 1.4); set(this.note, { o: pn, y: (1 - pn) * 14 });
      const pk = prog(t, 1.2, 1.7, ease.outExpo); set(this.card, { o: pk, y: (1 - pk) * 40 });
      this.rows.forEach((rw, i) => { const p = prog(t, 1.35 + i * .12, 1.8 + i * .12, ease.outExpo); set(rw, { o: p, x: (1 - p) * 30 }); });
      set(this.foot, { o: prog(t, 1.9, 2.3) });
      const sw = [2.6, 4.4].map(a => prog(t, a, a + .7, ease.inOut)).find(p => p > 0 && p < 1) || 0;
      this.shine.style.left = `${(-160 + sw * (this.cta.offsetWidth + 320)).toFixed(1)}px`;
    },
  });
})();
