(function () {
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Language menu: close on outside click or Escape.
  var langs = document.querySelector('.langs');
  if (langs) {
    document.addEventListener('click', function (e) { if (!langs.contains(e.target)) langs.open = false; });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') langs.open = false; });
  }

  // The video plays only while it is on screen.
  var videos = [].slice.call(document.querySelectorAll('video[data-loop]'));
  if (reduce || !('IntersectionObserver' in window)) {
    videos.forEach(function (v) { v.controls = true; });
  } else {
    var seen = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.play().catch(function () {}); } else { e.target.pause(); }
      });
    }, { threshold: 0.25 });
    videos.forEach(function (v) { seen.observe(v); });
  }

  // What's inside: each part of the app shows its own screen.
  var shot = document.getElementById('shot');
  var parts = [].slice.call(document.querySelectorAll('.inside button'));
  parts.forEach(function (b) {
    b.addEventListener('click', function () {
      parts.forEach(function (p) { p.removeAttribute('aria-current'); });
      b.setAttribute('aria-current', 'true');
      shot.src = b.dataset.shot;
    });
  });

  // A side view of the court. The ring is where you aim; let go and the ball flies.
  // The one rule to feel: over the net, floor first, then the glass.
  var deck = document.getElementById('deck');
  if (!deck) return;
  var aim = document.getElementById('aim'), ball = document.getElementById('ball'), arc = document.getElementById('arc');
  var spot = document.getElementById('spot'), say = document.getElementById('say');
  var W = 520, H = 230, FLOOR = 200, NET = 260, NET_TOP = 179, WALL = 500, WALL_TOP = 104, G = 235;
  var start = { x: 110, y: 172 }, target = { x: 198, y: 92 }, raf = 0;

  function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, v)); }

  // Flies the ball from the start toward the ring. Returns the path and what happened.
  function fly() {
    var x = start.x, y = start.y, vx = (target.x - x) * 2.2, vy = (target.y - y) * 2.2;
    var dt = 1 / 120, pts = [[x, y]], result = '', at = 0, bounces = 0, land = null;
    for (var i = 0; i < 120 * 5; i++) {
      var px = x;
      vy += G * dt; x += vx * dt; y += vy * dt;
      if (!result && px < NET && x >= NET && y > NET_TOP) { result = 'net'; at = i; x = NET; vx = -vx * 0.15; }
      if (x >= WALL && y > WALL_TOP) {
        if (!result) { result = 'glass'; at = i; }
        x = WALL; vx = -vx * 0.55;
      }
      if (x > W + 20 && !result) { result = 'glass'; at = i; }
      if (y >= FLOOR) {
        y = FLOOR; bounces++;
        if (!result) { result = x < NET ? 'short' : 'in'; at = i; land = x; }
        vy = -vy * 0.62; vx *= 0.8;
        if (bounces > 1 || Math.abs(vy) < 30) { pts.push([x, y]); break; }
      }
      if (x < 22) { x = 22; vx = -vx * 0.4; }
      pts.push([x, y]);
      if (x > W + 60) break;
    }
    return { pts: pts, result: result || 'glass', at: at, land: land };
  }

  function place() {
    aim.style.left = (target.x / W * 100) + '%';
    aim.style.top = (target.y / H * 100) + '%';
  }
  function preview() {
    var f = fly(), cut = f.pts.slice(0, Math.max(2, f.at + 1));
    arc.setAttribute('points', cut.filter(function (_, i) { return i % 4 === 0; }).map(function (p) { return p[0].toFixed(1) + ',' + p[1].toFixed(1); }).join(' '));
    spot.setAttribute('cx', f.result === 'in' || f.result === 'short' ? f.land : -40);
  }
  function rest() {
    cancelAnimationFrame(raf);
    ball.setAttribute('cx', start.x); ball.setAttribute('cy', start.y);
    arc.style.visibility = 'visible';
    preview();
  }
  function hit() {
    cancelAnimationFrame(raf);
    var f = fly(), t0 = performance.now(), told = false;
    arc.style.visibility = 'hidden';
    function tell() { if (!told) { told = true; say.textContent = say.dataset[f.result]; } }
    if (reduce) {
      var last = f.pts[f.pts.length - 1];
      ball.setAttribute('cx', last[0]); ball.setAttribute('cy', last[1]);
      return tell();
    }
    (function frame(now) {
      var i = Math.floor((now - t0) / 1000 * 120 * 1.15);
      if (i >= f.at) tell();
      var p = f.pts[Math.min(i, f.pts.length - 1)];
      ball.setAttribute('cx', p[0]); ball.setAttribute('cy', p[1]);
      if (i < f.pts.length - 1) raf = requestAnimationFrame(frame);
    })(t0);
  }
  function point(e) {
    var r = deck.getBoundingClientRect();
    target.x = clamp((e.clientX - r.left) / r.width * W, start.x + 24, WALL - 6);
    target.y = clamp((e.clientY - r.top) / r.height * H, 14, FLOOR - 14);
    place(); preview();
  }

  var dragging = false;
  aim.addEventListener('pointerdown', function (e) {
    dragging = true; aim.setPointerCapture(e.pointerId);
    rest(); say.textContent = say.dataset.idle; e.preventDefault();
  });
  aim.addEventListener('pointermove', function (e) { if (dragging) point(e); });
  aim.addEventListener('pointerup', function () { if (dragging) { dragging = false; hit(); } });
  aim.addEventListener('pointercancel', function () { dragging = false; });
  aim.addEventListener('click', function (e) { e.stopPropagation(); });
  deck.addEventListener('click', function (e) { rest(); point(e); hit(); });
  aim.addEventListener('keydown', function (e) {
    var step = { ArrowLeft: [-8, 0], ArrowRight: [8, 0], ArrowUp: [0, -8], ArrowDown: [0, 8] }[e.key];
    if (step) {
      e.preventDefault(); rest();
      target.x = clamp(target.x + step[0], start.x + 24, WALL - 6);
      target.y = clamp(target.y + step[1], 14, FLOOR - 14);
      place(); preview(); say.textContent = say.dataset.idle;
    } else if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); rest(); hit(); }
  });
  place(); preview();
})();
