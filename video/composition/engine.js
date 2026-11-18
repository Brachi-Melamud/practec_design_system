/* Practec video engine — deterministic, time-driven rendering (no CSS animations or transitions).
   window.__seek(t) paints the frame at t seconds; tools/render.py screenshots every frame.
   Preview: open index.html in Chrome. Space = play/pause, ←/→ = ±1 frame (shift: ±1 s).
   URL options: ?format=16x9  ?t=12.5  ?safe  ?nocap  (render mode: ?render) */
(() => {
  'use strict';
  const V = window.VIDEO;
  const root = document.documentElement;
  const qs = new URLSearchParams(location.search);
  const RENDER = qs.has('render');
  const FORMAT = qs.get('format') === '16x9' ? '16x9' : '9x16';
  root.dataset.format = FORMAT;
  if (RENDER) root.classList.add('render');
  if (qs.has('safe')) root.classList.add('safe');
  if (qs.has('nocap')) root.classList.add('nocap');          // hide the caption strip (cover stills)

  /* ---------- helpers (shared with scenes.js through window.K) ---------- */
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];
  const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
  const lerp = (a, b, p) => a + (b - a) * p;
  const ease = {
    lin: p => p,
    in: p => p * p * p,
    out: p => 1 - (1 - p) ** 3,
    inOut: p => (p < .5 ? 4 * p * p * p : 1 - (-2 * p + 2) ** 3 / 2),
    outExpo: p => (p >= 1 ? 1 : 1 - 2 ** (-10 * p)),
    outBack: p => 1 + 2.4 * (p - 1) ** 3 + 1.4 * (p - 1) ** 2,
  };
  /** eased 0→1 progress of t between a and b */
  const prog = (t, a, b, e = ease.out) => e(clamp((t - a) / (b - a)));

  /** set opacity / transform / filter on an element. Only the given groups are touched. */
  function set(el, o) {
    if (!el) return;
    const s = el.style;
    if ('o' in o) s.opacity = String(+clamp(o.o).toFixed(4));
    if (['x', 'y', 's', 'sx', 'sy', 'r'].some(k => k in o)) {
      const tf = [];
      if (o.x || o.y) tf.push(`translate(${(o.x || 0).toFixed(2)}px,${(o.y || 0).toFixed(2)}px)`);
      if (o.r) tf.push(`rotate(${o.r.toFixed(3)}deg)`);
      if ('s' in o && o.s !== 1) tf.push(`scale(${o.s.toFixed(4)})`);
      if ('sx' in o) tf.push(`scaleX(${o.sx.toFixed(4)})`);
      if ('sy' in o) tf.push(`scaleY(${o.sy.toFixed(4)})`);
      s.transform = tf.length ? tf.join(' ') : 'none';
    }
    if ('blur' in o) s.filter = o.blur > .05 ? `blur(${o.blur.toFixed(2)}px)` : 'none';
  }

  const esc = s => s.replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  /** caption markup: *accent* → <em> */
  const capHTML = text => esc(text).replace(/\*([^*]+)\*/g, '<em>$1</em>');

  /** split text into word spans (for kinetic type). *accent* words get class "acc". */
  function words(el, text) {
    const out = [];
    text.split('*').forEach((part, i) => part.split(/\s+/).filter(Boolean).forEach(w => {
      const sp = document.createElement('span');
      sp.className = i % 2 ? 'w acc' : 'w';
      sp.textContent = w;
      el.appendChild(sp);
      out.push(sp);
    }));
    return out;
  }

  /** rounded-rect path (pathLength-friendly, starts top-left) */
  const rr = (x, y, w, h, r) =>
    `M${x + r} ${y}H${x + w - r}A${r} ${r} 0 0 1 ${x + w} ${y + r}V${y + h - r}A${r} ${r} 0 0 1 ${x + w - r} ${y + h}` +
    `H${x + r}A${r} ${r} 0 0 1 ${x} ${y + h - r}V${y + r}A${r} ${r} 0 0 1 ${x + r} ${y}Z`;
  /** database cylinder: top ellipse + body */
  const cyl = (x, y, w, h, ry) => {
    const rx = w / 2;
    return `M${x} ${y}A${rx} ${ry} 0 1 0 ${x + w} ${y}A${rx} ${ry} 0 1 0 ${x} ${y}V${y + h}A${rx} ${ry} 0 0 0 ${x + w} ${y + h}V${y}`;
  };
  const along = (path, p) => path.getPointAtLength(clamp(p) * path.getTotalLength());
  const hex = h => [1, 3, 5].map(i => parseInt(h.slice(i, i + 2), 16));
  const mix = (a, b, p) => { const A = hex(a), B = hex(b); return `rgb(${A.map((v, i) => Math.round(lerp(v, B[i], clamp(p)))).join(',')})`; };

  /* ---------- scenes & transitions ---------- */
  const DEFS = {};
  const define = (id, def) => { DEFS[id] = def; };
  const TRANS = [];
  const transition = tr => TRANS.push(tr);

  const stage = $('#stage');
  const bgEls = $$('#bgs .bg');
  const edge = $('#wipe-edge');
  const scale = () => stage.getBoundingClientRect().width / stage.offsetWidth;
  /** centre of an element in stage pixels */
  function center(sel) {
    const s = stage.getBoundingClientRect(), r = $(sel).getBoundingClientRect(), k = scale();
    return { x: (r.left + r.width / 2 - s.left) / k, y: (r.top + r.height / 2 - s.top) / k };
  }

  function backgrounds(T) {
    const W = stage.offsetWidth, H = stage.offsetHeight;
    const active = new Set();
    let top = 0;
    edge.style.opacity = 0;
    for (const tr of TRANS) {
      const bg = bgEls[tr.bg];
      const p = prog(T, tr.at, tr.at + tr.dur, ease.inOut);
      bg.style.clipPath = 'none';
      if (p <= 0) { bg.style.display = 'none'; continue; }
      bg.style.display = '';
      if (p >= 1) { top = Math.max(top, tr.bg); continue; }
      const outEl = $('#' + tr.out), inEl = $('#' + tr.in);
      active.add(outEl); active.add(inEl);
      if (tr.type === 'circle') {
        const c = tr.c || (tr.c = center(tr.from));
        const R = Math.max(.5, Math.hypot(Math.max(c.x, W - c.x), Math.max(c.y, H - c.y)) * p);
        const circle = `circle(${R.toFixed(1)}px at ${c.x.toFixed(1)}px ${c.y.toFixed(1)}px)`;
        bg.style.clipPath = circle;
        inEl.style.clipPath = circle;
        const m = `radial-gradient(circle ${R.toFixed(1)}px at ${c.x.toFixed(1)}px ${c.y.toFixed(1)}px, transparent ${R.toFixed(1)}px, #000 ${(R + 1).toFixed(1)}px)`;
        outEl.style.webkitMaskImage = outEl.style.maskImage = m;
      } else {               // wipe: the new surface enters from the left (forward in RTL)
        const x = p * W;
        bg.style.clipPath = inEl.style.clipPath = `inset(0 ${(W - x).toFixed(1)}px 0 0)`;
        outEl.style.clipPath = `inset(0 0 0 ${x.toFixed(1)}px)`;
        edge.style.opacity = String(Math.sin(Math.PI * p).toFixed(3));
        edge.style.transform = `translateX(${x.toFixed(1)}px)`;
      }
    }
    bgEls.forEach((b, i) => { if (i < top) b.style.display = 'none'; else if (i === top) b.style.display = ''; });
    for (const s of V.scenes) {
      const el = $('#' + s.id);
      if (!active.has(el)) { el.style.clipPath = 'none'; el.style.webkitMaskImage = el.style.maskImage = 'none'; }
    }
    // slow drift of the grid texture (seamless: period = tile size)
    bgEls.forEach(b => {
      const per = b.classList.contains('dark') ? 40 : 48;
      b.firstElementChild.style.transform = `translate3d(0,${(-(T * 10) % per).toFixed(2)}px,0)`;
    });
  }

  const capWrap = $('#captions'), capEl = $('#captions .cap');
  const CAPS = V.captions.filter(c => !c.hero);
  let capShown = null;
  function captions(T) {
    const i = CAPS.findIndex(c => T >= c.start && T < c.end);
    if (i < 0) { capWrap.style.opacity = 0; return; }
    const c = CAPS[i], prev = CAPS[i - 1], next = CAPS[i + 1];
    if (capShown !== c) {                 // new caption: set the text, then shrink the box to its widest line
      capEl.style.width = '';
      capEl.innerHTML = `<span>${capHTML(c.text)}</span>`;
      capEl.style.width = `${Math.ceil(capEl.firstElementChild.getBoundingClientRect().width / scale()) + 68}px`;
      capShown = c;
    }
    const joinIn = prev && Math.abs(prev.end - c.start) < .05;
    const joinOut = next && Math.abs(next.start - c.end) < .05;
    const pin = prog(T, c.start, c.start + (joinIn ? .14 : .2), ease.out);
    const pout = joinOut ? 1 : 1 - prog(T, c.end - .14, c.end, ease.inOut);
    capWrap.style.opacity = String(Math.min(joinIn ? .4 + .6 * pin : pin, pout).toFixed(3));
    capWrap.style.transform = `translateY(${((1 - pin) * (joinIn ? 8 : 18)).toFixed(2)}px)`;
  }

  function render(T) {
    T = clamp(T, 0, V.duration);
    const gone = new Set(TRANS.filter(tr => T >= tr.at + tr.dur).map(tr => tr.out));    // covered by a finished transition
    const live = V.scenes.filter(s => { const d = DEFS[s.id]; return d && !gone.has(s.id) && T >= s.start - (d.lead || 0) && T < s.end + (d.tail || 0); });
    for (const s of V.scenes) $('#' + s.id).style.display = live.includes(s) ? '' : 'none';
    backgrounds(T);                       // transitions measure elements, so the live scenes are shown first
    for (const s of live) DEFS[s.id].update(T - s.start, T);
    captions(T);
  }

  /* ---------- safe-zone overlay (preview / QA stills) ---------- */
  function buildSafe() {
    const el = $('#safe');
    const Z = FORMAT === '9x16'
      ? [[0, 0, 1080, 250, 'platform UI (top)'], [0, 1500, 1080, 420, 'platform UI (caption / CTA)'],
         [0, 250, 90, 1250, ''], [990, 250, 90, 1250, ''], [930, 1000, 60, 500, 'buttons']]
      : [[0, 0, 1920, 54, 'title-safe 5%'], [0, 1026, 1920, 54, ''], [0, 54, 96, 972, ''], [1824, 54, 96, 972, '']];
    el.innerHTML = Z.map(([x, y, w, h, l]) =>
      `<i style="left:${x}px;top:${y}px;width:${w}px;height:${h}px"></i>${l ? `<b style="left:${x + 12}px;top:${y + 12}px">${l}</b>` : ''}`).join('');
  }

  /* ---------- preview player ---------- */
  let t = clamp(+(qs.get('t') || 0), 0, V.duration), playing = false, last = 0;
  const audio = RENDER ? null : new Audio('../build/audio/mix.wav');   // present after a render; optional
  function fit() {
    if (RENDER) return;
    const vp = $('#viewport'), W = stage.offsetWidth, H = stage.offsetHeight;
    const k = Math.min(vp.clientWidth / W, vp.clientHeight / H) * .97;
    stage.style.transform = `translate(${(vp.clientWidth - W * k) / 2}px,${(vp.clientHeight - H * k) / 2}px) scale(${k})`;
    TRANS.forEach(tr => { delete tr.c; });
  }
  function paint() {
    render(t);
    if (!RENDER) { $('#scrub').value = t; $('#clock').textContent = t.toFixed(2); $('#play').textContent = playing ? '❚❚' : '▶'; }
  }
  function loop(now) {
    if (playing) {
      t = audio && !audio.paused && audio.readyState > 2 ? audio.currentTime : t + (now - last) / 1000;
      if (t >= V.duration) { t = V.duration; playing = false; audio?.pause(); }
    }
    last = now;
    paint();
    requestAnimationFrame(loop);
  }
  function toggle() {
    if (t >= V.duration) t = 0;
    playing = !playing;
    if (audio) { if (playing) { audio.currentTime = t; audio.play().catch(() => {}); } else audio.pause(); }
  }
  function initUI() {
    const scrub = $('#scrub');
    scrub.max = V.duration;
    scrub.addEventListener('input', () => { t = +scrub.value; playing = false; audio?.pause(); });
    $('#play').addEventListener('click', toggle);
    $('#fmt').value = FORMAT;
    $('#fmt').addEventListener('change', e => { qs.set('format', e.target.value); qs.set('t', t.toFixed(3)); location.search = qs.toString(); });
    $('#safe-t').checked = root.classList.contains('safe');
    $('#safe-t').addEventListener('change', e => root.classList.toggle('safe', e.target.checked));
    addEventListener('keydown', e => {
      if (e.code === 'Space') { e.preventDefault(); toggle(); }
      if (e.code === 'ArrowRight' || e.code === 'ArrowLeft') {
        playing = false; audio?.pause();
        t = clamp(t + (e.code === 'ArrowRight' ? 1 : -1) * (e.shiftKey ? 1 : 1 / V.fps), 0, V.duration);
      }
    });
    addEventListener('resize', fit);
    fit();
    requestAnimationFrame(loop);
  }

  window.K = { $, $$, clamp, lerp, ease, prog, set, words, capHTML, rr, cyl, along, mix, define, transition, V, FORMAT };

  /** resolves when fonts + images are ready and every scene is initialised */
  window.__ready = (async () => {
    // scenes.js registers the scenes after this file runs — wait for every script before initialising
    if (document.readyState === 'loading') await new Promise(r => document.addEventListener('DOMContentLoaded', r, { once: true }));
    await document.fonts.ready;
    await Promise.all(['900 90px Heebo', '800 80px Heebo', '700 50px Heebo', '600 40px Heebo', '500 36px Heebo',
      '500 28px "JetBrains Mono"', '600 30px "JetBrains Mono"'].map(f => document.fonts.load(f, 'אבג abc 0123')));
    await Promise.all($$('img').map(i => i.decode().catch(() => {})));
    buildSafe();
    for (const s of V.scenes) {
      const el = $('#' + s.id);
      if (!el || !DEFS[s.id]) throw new Error(`scene "${s.id}" from content.js is missing in index.html or scenes.js`);
      el.style.display = '';
      DEFS[s.id].init?.();
      el.style.display = 'none';
    }
    if (!RENDER) initUI();
    render(t);
    const fonts = [...document.fonts].filter(f => f.status === 'loaded').map(f => `${f.family} ${f.weight}`);
    return { fonts, duration: V.duration, fps: V.fps, format: FORMAT };
  })();
  window.__seek = T => { render(T); return true; };
})();
