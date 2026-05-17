/* ─────────────────────────────────────────────────────
   PhishGuard – Landing Page JavaScript
   ───────────────────────────────────────────────────── */

// ── Particle System ──────────────────────────────────
(function initParticles() {
  const canvas = document.getElementById('particles-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  let W, H, particles = [];

  function resize() {
    W = canvas.width  = canvas.offsetWidth;
    H = canvas.height = canvas.offsetHeight;
  }

  function createParticle() {
    return {
      x:   Math.random() * W,
      y:   Math.random() * H,
      r:   Math.random() * 1.8 + 0.4,
      vx:  (Math.random() - 0.5) * 0.4,
      vy:  -Math.random() * 0.6 - 0.2,
      alpha: Math.random() * 0.5 + 0.1,
      color: Math.random() > 0.5 ? '99,102,241' : '129,140,248',
    };
  }

  function initParticlesArr() {
    particles = [];
    for (let i = 0; i < 80; i++) particles.push(createParticle());
  }

  function drawParticle(p) {
    ctx.beginPath();
    ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
    ctx.fillStyle = `rgba(${p.color},${p.alpha})`;
    ctx.fill();
  }

  function updateParticle(p) {
    p.x += p.vx;
    p.y += p.vy;
    p.alpha += (Math.random() - 0.5) * 0.01;
    p.alpha = Math.max(0.05, Math.min(0.65, p.alpha));
    if (p.y < -10 || p.x < -10 || p.x > W + 10) {
      Object.assign(p, createParticle());
      p.y = H + 5;
    }
  }

  function loop() {
    ctx.clearRect(0, 0, W, H);
    particles.forEach(p => { updateParticle(p); drawParticle(p); });
    // Draw connections
    particles.forEach((a, i) => {
      particles.slice(i + 1).forEach(b => {
        const dx = a.x - b.x, dy = a.y - b.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < 100) {
          ctx.beginPath();
          ctx.moveTo(a.x, a.y);
          ctx.lineTo(b.x, b.y);
          ctx.strokeStyle = `rgba(99,102,241,${0.06 * (1 - dist / 100)})`;
          ctx.lineWidth = 0.5;
          ctx.stroke();
        }
      });
    });
    requestAnimationFrame(loop);
  }

  resize();
  initParticlesArr();
  loop();
  window.addEventListener('resize', () => { resize(); initParticlesArr(); });
})();


// ── Smooth scroll for CTA ────────────────────────────
document.querySelectorAll('a[href="/analyzer"]').forEach(btn => {
  btn.addEventListener('click', (e) => {
    // Navigate normally — just add a small visual press effect
    btn.style.transform = 'scale(0.97)';
    setTimeout(() => btn.style.transform = '', 150);
  });
});


// ── Intersection Observer — fade-up on scroll ─────────
const observerOpts = { threshold: 0.15 };
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.style.animation = 'fade-up 0.6s ease forwards';
      observer.unobserve(entry.target);
    }
  });
}, observerOpts);

document.querySelectorAll('.feature-card, .step, .cta-inner').forEach(el => {
  el.style.opacity = '0';
  observer.observe(el);
});


// ── Animated counter for stats ────────────────────────
function animateCounter(el, target, suffix = '') {
  let current = 0;
  const duration = 2000;
  const step = target / (duration / 16);
  const timer = setInterval(() => {
    current = Math.min(current + step, target);
    el.textContent = Math.floor(current) + suffix;
    if (current >= target) clearInterval(timer);
  }, 16);
}

const statsObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const el = entry.target;
      const target = parseInt(el.dataset.target, 10);
      const suffix = el.dataset.suffix || '';
      animateCounter(el, target, suffix);
      statsObserver.unobserve(el);
    }
  });
}, { threshold: 0.5 });

document.querySelectorAll('[data-target]').forEach(el => statsObserver.observe(el));
